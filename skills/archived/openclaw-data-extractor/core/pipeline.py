"""
数据处理流程管道

提供统一的数据处理流程，支持多阶段处理、错误处理、进度跟踪
"""

import time
import logging
from typing import Any, Callable, Dict, List, Optional, Union, Iterator
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json

from .config import Config


class PipelineStage(Enum):
    """处理阶段枚举"""
    EXTRACT = "extract"
    CLEAN = "clean"
    VALIDATE = "validate"
    TRANSFORM = "transform"
    OUTPUT = "output"


@dataclass
class ProcessingResult:
    """处理结果数据类"""
    success: bool
    stage: PipelineStage
    data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    rows_processed: int = 0
    rows_output: int = 0


@dataclass
class PipelineContext:
    """管道上下文"""
    source_path: Optional[Path] = None
    source_type: Optional[str] = None
    config: Config = field(default_factory=Config)
    metadata: Dict[str, Any] = field(default_factory=dict)
    intermediate_results: List[ProcessingResult] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    
    def add_result(self, result: ProcessingResult) -> None:
        """添加中间结果"""
        self.intermediate_results.append(result)
    
    def get_total_duration(self) -> float:
        """获取总处理时间"""
        return time.time() - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "source_path": str(self.source_path) if self.source_path else None,
            "source_type": self.source_type,
            "metadata": self.metadata,
            "total_duration_ms": self.get_total_duration() * 1000,
            "stages": [
                {
                    "stage": r.stage.value,
                    "success": r.success,
                    "duration_ms": r.duration_ms,
                    "rows_processed": r.rows_processed,
                    "rows_output": r.rows_output,
                    "errors": r.errors,
                    "warnings": r.warnings,
                }
                for r in self.intermediate_results
            ],
        }


class StageProcessor:
    """阶段处理器基类"""
    
    def __init__(self, stage: PipelineStage):
        self.stage = stage
        self.logger = logging.getLogger(f"openclaw.pipeline.{stage.value}")
    
    def process(self, data: Any, context: PipelineContext) -> ProcessingResult:
        """处理数据，子类必须实现"""
        raise NotImplementedError
    
    def _create_result(
        self,
        success: bool,
        data: Any = None,
        errors: List[str] = None,
        warnings: List[str] = None,
        duration_ms: float = 0.0,
        rows_processed: int = 0,
        rows_output: int = 0,
    ) -> ProcessingResult:
        """创建处理结果"""
        return ProcessingResult(
            success=success,
            stage=self.stage,
            data=data,
            errors=errors or [],
            warnings=warnings or [],
            duration_ms=duration_ms,
            rows_processed=rows_processed,
            rows_output=rows_output,
        )


class DataPipeline:
    """
    数据处理流程管道
    
    提供可配置的多阶段数据处理流程，支持:
    - 灵活的阶段配置
    - 错误处理和恢复
    - 进度跟踪
    - 中间结果保存
    
    Example:
        >>> from openclaw import DataPipeline, Config
        >>> config = Config()
        >>> pipeline = DataPipeline(config)
        >>> 
        >>> # 处理单个文件
        >>> result = pipeline.process_file("data.pdf")
        >>> 
        >>> # 批量处理
        >>> for result in pipeline.process_batch(["1.pdf", "2.xlsx"]):
        ...     print(result)
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.stages: Dict[PipelineStage, StageProcessor] = {}
        self.logger = logging.getLogger("openclaw.pipeline")
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
    
    def register_stage(self, processor: StageProcessor) -> "DataPipeline":
        """注册处理阶段"""
        self.stages[processor.stage] = processor
        return self
    
    def process_file(
        self,
        file_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
    ) -> PipelineContext:
        """
        处理单个文件
        
        Args:
            file_path: 输入文件路径
            output_path: 输出文件路径（可选）
        
        Returns:
            PipelineContext: 处理上下文，包含所有中间结果
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 创建上下文
        context = PipelineContext(
            source_path=file_path,
            source_type=self._detect_source_type(file_path),
            config=self.config,
        )
        
        self.logger.info(f"开始处理文件: {file_path}")
        
        try:
            # 执行各阶段处理
            data = None
            
            # 1. 提取阶段
            if PipelineStage.EXTRACT in self.stages:
                data = self._run_stage(PipelineStage.EXTRACT, data, context)
            
            # 2. 清洗阶段
            if PipelineStage.CLEAN in self.stages and data is not None:
                data = self._run_stage(PipelineStage.CLEAN, data, context)
            
            # 3. 验证阶段
            if PipelineStage.VALIDATE in self.stages and data is not None:
                data = self._run_stage(PipelineStage.VALIDATE, data, context)
            
            # 4. 转换阶段
            if PipelineStage.TRANSFORM in self.stages and data is not None:
                data = self._run_stage(PipelineStage.TRANSFORM, data, context)
            
            # 5. 输出阶段
            if PipelineStage.OUTPUT in self.stages and data is not None:
                output_context = {"output_path": output_path}
                data = self._run_stage(PipelineStage.OUTPUT, data, context, output_context)
            
        except Exception as e:
            self.logger.error(f"处理文件时发生错误: {e}", exc_info=True)
            context.add_result(
                ProcessingResult(
                    success=False,
                    stage=PipelineStage.EXTRACT,
                    errors=[str(e)],
                )
            )
        
        self.logger.info(f"文件处理完成: {file_path}, 总耗时: {context.get_total_duration():.2f}s")
        return context
    
    def process_batch(
        self,
        file_paths: List[Union[str, Path]],
        output_dir: Optional[Union[str, Path]] = None,
    ) -> Iterator[PipelineContext]:
        """
        批量处理文件
        
        Args:
            file_paths: 文件路径列表
            output_dir: 输出目录（可选）
        
        Yields:
            PipelineContext: 每个文件的处理上下文
        """
        output_dir = Path(output_dir) if output_dir else Path(self.config.output.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        total = len(file_paths)
        self.logger.info(f"开始批量处理，共 {total} 个文件")
        
        for i, file_path in enumerate(file_paths, 1):
            self.logger.info(f"处理进度: {i}/{total}")
            
            # 生成输出路径
            output_path = None
            if output_dir:
                file_name = Path(file_path).stem
                ext = self._get_output_extension()
                output_path = output_dir / f"{file_name}_extracted.{ext}"
            
            yield self.process_file(file_path, output_path)
    
    def _run_stage(
        self,
        stage: PipelineStage,
        data: Any,
        context: PipelineContext,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """运行处理阶段"""
        processor = self.stages.get(stage)
        if not processor:
            return data
        
        # 更新上下文
        if extra_context:
            context.metadata.update(extra_context)
        
        self.logger.info(f"执行阶段: {stage.value}")
        start_time = time.time()
        
        result = processor.process(data, context)
        result.duration_ms = (time.time() - start_time) * 1000
        
        context.add_result(result)
        
        if not result.success:
            self.logger.warning(f"阶段 {stage.value} 处理失败: {result.errors}")
            if self.config.processing.on_error == "raise":
                raise RuntimeError(f"阶段 {stage.value} 处理失败: {result.errors}")
        
        return result.data
    
    def _detect_source_type(self, file_path: Path) -> str:
        """检测源文件类型"""
        suffix = file_path.suffix.lower()
        type_map = {
            ".pdf": "pdf",
            ".xlsx": "excel",
            ".xls": "excel",
            ".xlsm": "excel",
            ".csv": "csv",
            ".png": "image",
            ".jpg": "image",
            ".jpeg": "image",
            ".bmp": "image",
            ".tiff": "image",
            ".tif": "image",
            ".webp": "image",
        }
        return type_map.get(suffix, "unknown")
    
    def _get_output_extension(self) -> str:
        """获取输出文件扩展名"""
        format_map = {
            "json": "json",
            "csv": "csv",
            "xlsx": "xlsx",
            "parquet": "parquet",
            "sqlite": "db",
            "auto": "json",
        }
        return format_map.get(self.config.output.format, "json")
    
    def save_report(self, context: PipelineContext, output_path: Union[str, Path]) -> None:
        """保存处理报告"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = context.to_dict()
        report["config"] = self.config.to_dict()
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"处理报告已保存: {output_path}")
