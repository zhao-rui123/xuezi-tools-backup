"""
批量处理模块

提供批量数据处理功能，包括:
- 多文件并行处理
- 数据合并与拆分
- 格式转换
- 进度跟踪
- 错误处理
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union, Callable, Iterator
from pathlib import Path
from dataclasses import dataclass, field
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import time
import hashlib

# 设置日志
logger = logging.getLogger("openclaw.utils.batch_processor")


@dataclass
class BatchProcessingResult:
    """批量处理结果"""
    success: bool
    file_path: Optional[str] = None
    data: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    rows_processed: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "file_path": self.file_path,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "rows_processed": self.rows_processed,
        }


@dataclass
class BatchProcessingReport:
    """批量处理报告"""
    total_files: int = 0
    successful_files: int = 0
    failed_files: int = 0
    total_rows: int = 0
    total_duration_ms: float = 0.0
    results: List[BatchProcessingResult] = field(default_factory=list)
    errors: List[Tuple[str, str]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "summary": {
                "total_files": self.total_files,
                "successful_files": self.successful_files,
                "failed_files": self.failed_files,
                "success_rate": self.success_rate,
                "total_rows": self.total_rows,
                "total_duration_ms": self.total_duration_ms,
            },
            "results": [r.to_dict() for r in self.results],
            "errors": [{"file": f, "error": e} for f, e in self.errors],
        }
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_files == 0:
            return 0.0
        return self.successful_files / self.total_files


class BatchProcessor:
    """
    批量处理器
    
    提供批量数据处理功能。
    
    Example:
        >>> from openclaw import BatchProcessor
        >>> processor = BatchProcessor(max_workers=4)
        >>> 
        >>> # 定义处理函数
        >>> def process_file(file_path):
        ...     # 处理逻辑
        ...     return processed_data
        >>> 
        >>> # 批量处理
        >>> results = processor.process_files(
        ...     file_list,
        ...     process_file,
        ...     parallel=True
        ... )
        >>> 
        >>> # 获取报告
        >>> report = processor.get_report()
    """
    
    def __init__(
        self,
        max_workers: int = 4,
        use_processes: bool = False,
        show_progress: bool = True,
    ):
        """
        初始化批量处理器
        
        Args:
            max_workers: 最大工作线程/进程数
            use_processes: 是否使用进程池（CPU密集型任务）
            show_progress: 是否显示进度
        """
        self.max_workers = max_workers
        self.use_processes = use_processes
        self.show_progress = show_progress
        self.logger = logging.getLogger("openclaw.utils.batch_processor")
        self.report = BatchProcessingReport()
    
    def process_files(
        self,
        file_paths: List[Union[str, Path]],
        process_func: Callable[[Path], Any],
        parallel: bool = True,
    ) -> List[BatchProcessingResult]:
        """
        批量处理文件
        
        Args:
            file_paths: 文件路径列表
            process_func: 处理函数
            parallel: 是否并行处理
        
        Returns:
            处理结果列表
        """
        self.report = BatchProcessingReport()
        self.report.total_files = len(file_paths)
        
        if parallel and len(file_paths) > 1:
            return self._process_parallel(file_paths, process_func)
        else:
            return self._process_sequential(file_paths, process_func)
    
    def _process_sequential(
        self,
        file_paths: List[Union[str, Path]],
        process_func: Callable[[Path], Any],
    ) -> List[BatchProcessingResult]:
        """顺序处理"""
        results = []
        start_time = time.time()
        
        for i, file_path in enumerate(file_paths):
            file_path = Path(file_path)
            
            if self.show_progress:
                self.logger.info(f"处理进度: {i+1}/{len(file_paths)} - {file_path.name}")
            
            result = self._process_single(file_path, process_func)
            results.append(result)
            self.report.results.append(result)
            
            if result.success:
                self.report.successful_files += 1
                self.report.total_rows += result.rows_processed
            else:
                self.report.failed_files += 1
                self.report.errors.append((str(file_path), result.error or "Unknown error"))
        
        self.report.total_duration_ms = (time.time() - start_time) * 1000
        return results
    
    def _process_parallel(
        self,
        file_paths: List[Union[str, Path]],
        process_func: Callable[[Path], Any],
    ) -> List[BatchProcessingResult]:
        """并行处理"""
        results = [None] * len(file_paths)
        start_time = time.time()
        
        ExecutorClass = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor
        
        with ExecutorClass(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_index = {
                executor.submit(self._process_single, Path(fp), process_func): i
                for i, fp in enumerate(file_paths)
            }
            
            # 收集结果
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    result = future.result()
                except Exception as e:
                    result = BatchProcessingResult(
                        success=False,
                        file_path=str(file_paths[idx]),
                        error=str(e),
                    )
                
                results[idx] = result
                self.report.results.append(result)
                
                if result.success:
                    self.report.successful_files += 1
                    self.report.total_rows += result.rows_processed
                else:
                    self.report.failed_files += 1
                    self.report.errors.append((str(file_paths[idx]), result.error or "Unknown error"))
                
                if self.show_progress:
                    completed = sum(1 for r in results if r is not None)
                    self.logger.info(f"处理进度: {completed}/{len(file_paths)}")
        
        self.report.total_duration_ms = (time.time() - start_time) * 1000
        return results
    
    def _process_single(
        self,
        file_path: Path,
        process_func: Callable[[Path], Any],
    ) -> BatchProcessingResult:
        """处理单个文件"""
        start_time = time.time()
        
        try:
            result_data = process_func(file_path)
            
            # 尝试获取行数
            rows = 0
            if isinstance(result_data, list):
                rows = len(result_data)
            elif hasattr(result_data, "__len__"):
                try:
                    rows = len(result_data)
                except:
                    pass
            
            return BatchProcessingResult(
                success=True,
                file_path=str(file_path),
                data=result_data,
                duration_ms=(time.time() - start_time) * 1000,
                rows_processed=rows,
            )
        
        except Exception as e:
            self.logger.error(f"处理文件 {file_path} 失败: {e}")
            return BatchProcessingResult(
                success=False,
                file_path=str(file_path),
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000,
            )
    
    def merge_results(
        self,
        results: List[BatchProcessingResult],
        merge_func: Optional[Callable[[List[Any]], Any]] = None,
    ) -> Any:
        """
        合并处理结果
        
        Args:
            results: 处理结果列表
            merge_func: 合并函数
        
        Returns:
            合并后的结果
        """
        successful_results = [r.data for r in results if r.success and r.data is not None]
        
        if not successful_results:
            return None
        
        if merge_func:
            return merge_func(successful_results)
        
        # 默认合并逻辑
        first_item = successful_results[0]
        
        if isinstance(first_item, list):
            # 合并列表
            merged = []
            for item in successful_results:
                if isinstance(item, list):
                    merged.extend(item)
            return merged
        
        elif isinstance(first_item, dict):
            # 合并字典（假设是记录列表）
            merged = []
            for item in successful_results:
                if isinstance(item, list):
                    merged.extend(item)
                elif isinstance(item, dict):
                    merged.append(item)
            return merged
        
        else:
            return successful_results
    
    def split_data(
        self,
        data: List[Any],
        chunk_size: int,
    ) -> List[List[Any]]:
        """
        拆分数据为多个块
        
        Args:
            data: 数据列表
            chunk_size: 每块大小
        
        Returns:
            数据块列表
        """
        return [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
    
    def get_report(self) -> BatchProcessingReport:
        """获取处理报告"""
        return self.report
    
    def save_report(self, output_path: Union[str, Path]) -> None:
        """保存处理报告"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.report.to_dict(), f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"处理报告已保存: {output_path}")


class FileConverter:
    """
    文件格式转换器
    
    提供各种文件格式之间的转换功能。
    
    Example:
        >>> from openclaw import FileConverter
        >>> converter = FileConverter()
        >>> 
        >>> # CSV转Excel
        >>> converter.csv_to_excel("data.csv", "data.xlsx")
        >>> 
        >>> # Excel转CSV
        >>> converter.excel_to_csv("data.xlsx", "data.csv", sheet_name="Sheet1")
        >>> 
        >>> # JSON转CSV
        >>> converter.json_to_csv("data.json", "data.csv")
    """
    
    def __init__(self):
        self.logger = logging.getLogger("openclaw.utils.file_converter")
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """检查依赖库"""
        try:
            import pandas as pd
            self.pandas = pd
        except ImportError:
            self.logger.warning("pandas未安装，格式转换功能受限")
            self.pandas = None
    
    def csv_to_excel(
        self,
        csv_path: Union[str, Path],
        excel_path: Union[str, Path],
        **kwargs,
    ) -> None:
        """
        CSV转Excel
        
        Args:
            csv_path: CSV文件路径
            excel_path: Excel输出路径
            **kwargs: pandas read_csv参数
        """
        if not self.pandas:
            raise RuntimeError("pandas未安装")
        
        df = self.pandas.read_csv(csv_path, **kwargs)
        df.to_excel(excel_path, index=False)
        self.logger.info(f"已转换: {csv_path} -> {excel_path}")
    
    def excel_to_csv(
        self,
        excel_path: Union[str, Path],
        csv_path: Union[str, Path],
        sheet_name: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Excel转CSV
        
        Args:
            excel_path: Excel文件路径
            csv_path: CSV输出路径
            sheet_name: 工作表名称
            **kwargs: pandas read_excel参数
        """
        if not self.pandas:
            raise RuntimeError("pandas未安装")
        
        df = self.pandas.read_excel(excel_path, sheet_name=sheet_name, **kwargs)
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        self.logger.info(f"已转换: {excel_path} -> {csv_path}")
    
    def json_to_csv(
        self,
        json_path: Union[str, Path],
        csv_path: Union[str, Path],
        **kwargs,
    ) -> None:
        """
        JSON转CSV
        
        Args:
            json_path: JSON文件路径
            csv_path: CSV输出路径
            **kwargs: pandas read_json参数
        """
        if not self.pandas:
            raise RuntimeError("pandas未安装")
        
        df = self.pandas.read_json(json_path, **kwargs)
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        self.logger.info(f"已转换: {json_path} -> {csv_path}")
    
    def csv_to_json(
        self,
        csv_path: Union[str, Path],
        json_path: Union[str, Path],
        orient: str = "records",
        **kwargs,
    ) -> None:
        """
        CSV转JSON
        
        Args:
            csv_path: CSV文件路径
            json_path: JSON输出路径
            orient: JSON格式
            **kwargs: pandas read_csv参数
        """
        if not self.pandas:
            raise RuntimeError("pandas未安装")
        
        df = self.pandas.read_csv(csv_path, **kwargs)
        df.to_json(json_path, orient=orient, force_ascii=False, indent=2)
        self.logger.info(f"已转换: {csv_path} -> {json_path}")
    
    def excel_to_json(
        self,
        excel_path: Union[str, Path],
        json_path: Union[str, Path],
        sheet_name: Optional[str] = None,
        orient: str = "records",
        **kwargs,
    ) -> None:
        """
        Excel转JSON
        
        Args:
            excel_path: Excel文件路径
            json_path: JSON输出路径
            sheet_name: 工作表名称
            orient: JSON格式
            **kwargs: pandas read_excel参数
        """
        if not self.pandas:
            raise RuntimeError("pandas未安装")
        
        df = self.pandas.read_excel(excel_path, sheet_name=sheet_name, **kwargs)
        df.to_json(json_path, orient=orient, force_ascii=False, indent=2)
        self.logger.info(f"已转换: {excel_path} -> {json_path}")
    
    def convert_batch(
        self,
        file_paths: List[Union[str, Path]],
        output_dir: Union[str, Path],
        target_format: str,
        **kwargs,
    ) -> List[Path]:
        """
        批量转换文件格式
        
        Args:
            file_paths: 文件路径列表
            output_dir: 输出目录
            target_format: 目标格式 (csv, xlsx, json)
            **kwargs: 转换参数
        
        Returns:
            输出文件路径列表
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_paths = []
        
        for file_path in file_paths:
            file_path = Path(file_path)
            output_path = output_dir / f"{file_path.stem}.{target_format}"
            
            try:
                source_ext = file_path.suffix.lower()
                
                if source_ext == ".csv":
                    if target_format == "xlsx":
                        self.csv_to_excel(file_path, output_path, **kwargs)
                    elif target_format == "json":
                        self.csv_to_json(file_path, output_path, **kwargs)
                
                elif source_ext in [".xlsx", ".xls"]:
                    if target_format == "csv":
                        self.excel_to_csv(file_path, output_path, **kwargs)
                    elif target_format == "json":
                        self.excel_to_json(file_path, output_path, **kwargs)
                
                elif source_ext == ".json":
                    if target_format == "csv":
                        self.json_to_csv(file_path, output_path, **kwargs)
                
                output_paths.append(output_path)
            
            except Exception as e:
                self.logger.error(f"转换 {file_path} 失败: {e}")
        
        return output_paths
