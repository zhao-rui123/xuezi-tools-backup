#!/usr/bin/env python3
"""
OpenClaw CLI - 命令行接口

提供统一的命令行入口，支持各种数据提取和处理操作。

Usage:
    openclaw extract pdf <file> [options]
    openclaw extract excel <file> [options]
    openclaw extract image <file> [options]
    openclaw clean <file> [options]
    openclaw validate <file> [options]
    openclaw convert <file> <format> [options]
    openclaw batch <command> <files...> [options]

Examples:
    # 提取PDF文本和表格
    openclaw extract pdf document.pdf --tables --output result.json
    
    # 提取Excel数据
    openclaw extract excel data.xlsx --sheet Sheet1 --output data.csv
    
    # OCR识别图片
    openclaw extract image screenshot.png --language chi_sim+eng --output text.txt
    
    # 清洗数据
    openclaw clean data.csv --remove-duplicates --fill-missing --output cleaned.csv
    
    # 批量处理
    openclaw batch extract *.pdf --parallel --output-dir ./output
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, List
import os

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("openclaw.cli")


def setup_extract_parser(subparsers):
    """设置提取命令解析器"""
    extract_parser = subparsers.add_parser("extract", help="从文件中提取数据")
    extract_subparsers = extract_parser.add_subparsers(dest="extract_type", help="提取类型")
    
    # PDF提取
    pdf_parser = extract_subparsers.add_parser("pdf", help="提取PDF数据")
    pdf_parser.add_argument("file", help="PDF文件路径")
    pdf_parser.add_argument("--text", action="store_true", default=True, help="提取文本")
    pdf_parser.add_argument("--tables", action="store_true", help="提取表格")
    pdf_parser.add_argument("--images", action="store_true", help="提取图片")
    pdf_parser.add_argument("--forms", action="store_true", help="提取表单")
    pdf_parser.add_argument("--metadata", action="store_true", help="提取元数据")
    pdf_parser.add_argument("--pages", help="页面范围，如 1-5,7,10")
    pdf_parser.add_argument("--ocr", action="store_true", help="使用OCR（扫描版PDF）")
    pdf_parser.add_argument("--ocr-lang", default="chi_sim+eng", help="OCR语言")
    pdf_parser.add_argument("-o", "--output", help="输出文件路径")
    pdf_parser.add_argument("--format", choices=["json", "txt", "csv"], default="json", help="输出格式")
    
    # Excel提取
    excel_parser = extract_subparsers.add_parser("excel", help="提取Excel数据")
    excel_parser.add_argument("file", help="Excel文件路径")
    excel_parser.add_argument("--sheet", help="工作表名称")
    excel_parser.add_argument("--sheet-index", type=int, help="工作表索引")
    excel_parser.add_argument("--header", type=int, default=0, help="表头行号")
    excel_parser.add_argument("--all-sheets", action="store_true", help="提取所有工作表")
    excel_parser.add_argument("-o", "--output", help="输出文件路径")
    excel_parser.add_argument("--format", choices=["json", "csv", "xlsx"], default="json", help="输出格式")
    
    # 图片提取
    image_parser = extract_subparsers.add_parser("image", help="OCR识别图片")
    image_parser.add_argument("file", help="图片文件路径")
    image_parser.add_argument("--language", default="chi_sim+eng", help="OCR语言")
    image_parser.add_argument("--engine", choices=["auto", "tesseract", "paddle", "easyocr"], default="auto", help="OCR引擎")
    image_parser.add_argument("--tables", action="store_true", help="识别表格")
    image_parser.add_argument("--preprocess", action="store_true", default=True, help="图像预处理")
    image_parser.add_argument("-o", "--output", help="输出文件路径")
    image_parser.add_argument("--format", choices=["json", "txt"], default="txt", help="输出格式")


def setup_clean_parser(subparsers):
    """设置清洗命令解析器"""
    clean_parser = subparsers.add_parser("clean", help="清洗数据")
    clean_parser.add_argument("file", help="数据文件路径")
    clean_parser.add_argument("--remove-duplicates", action="store_true", help="去除重复行")
    clean_parser.add_argument("--fill-missing", choices=["mean", "median", "mode", "constant"], help="填充缺失值策略")
    clean_parser.add_argument("--fill-value", help="填充值（用于constant策略）")
    clean_parser.add_argument("--drop-missing", action="store_true", help="删除缺失值行")
    clean_parser.add_argument("--remove-outliers", action="store_true", help="去除异常值")
    clean_parser.add_argument("--standardize-columns", action="store_true", help="标准化列名")
    clean_parser.add_argument("-o", "--output", required=True, help="输出文件路径")
    clean_parser.add_argument("--format", choices=["csv", "xlsx", "json"], help="输出格式")


def setup_validate_parser(subparsers):
    """设置验证命令解析器"""
    validate_parser = subparsers.add_parser("validate", help="验证数据")
    validate_parser.add_argument("file", help="数据文件路径")
    validate_parser.add_argument("--rules", help="验证规则JSON文件")
    validate_parser.add_argument("--schema", help="数据模式JSON文件")
    validate_parser.add_argument("-o", "--output", help="验证报告输出路径")


def setup_convert_parser(subparsers):
    """设置转换命令解析器"""
    convert_parser = subparsers.add_parser("convert", help="转换文件格式")
    convert_parser.add_argument("file", help="输入文件路径")
    convert_parser.add_argument("format", choices=["csv", "xlsx", "json", "parquet"], help="目标格式")
    convert_parser.add_argument("-o", "--output", required=True, help="输出文件路径")
    convert_parser.add_argument("--sheet", help="Excel工作表名称（用于Excel输入）")


def setup_batch_parser(subparsers):
    """设置批量处理命令解析器"""
    batch_parser = subparsers.add_parser("batch", help="批量处理文件")
    batch_parser.add_argument("command", choices=["extract", "clean", "convert"], help="要执行的命令")
    batch_parser.add_argument("files", nargs="+", help="文件路径列表")
    batch_parser.add_argument("--parallel", action="store_true", help="并行处理")
    batch_parser.add_argument("--workers", type=int, default=4, help="并行工作线程数")
    batch_parser.add_argument("--output-dir", required=True, help="输出目录")
    batch_parser.add_argument("--pattern", help="输出文件名模式")


def setup_analyze_parser(subparsers):
    """设置分析命令解析器"""
    analyze_parser = subparsers.add_parser("analyze", help="分析数据结构")
    analyze_parser.add_argument("file", help="数据文件路径")
    analyze_parser.add_argument("--detailed", action="store_true", help="详细分析")
    analyze_parser.add_argument("-o", "--output", help="分析报告输出路径")


def create_parser():
    """创建命令行解析器"""
    parser = argparse.ArgumentParser(
        prog="openclaw",
        description="OpenClaw - 智能数据提取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s extract pdf document.pdf --tables -o result.json
  %(prog)s extract excel data.xlsx --sheet Sheet1 -o data.csv
  %(prog)s extract image screenshot.png -o text.txt
  %(prog)s clean data.csv --remove-duplicates --fill-mean -o cleaned.csv
  %(prog)s batch extract *.pdf --parallel --output-dir ./output
        """,
    )
    
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    parser.add_argument("-q", "--quiet", action="store_true", help="静默模式")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    setup_extract_parser(subparsers)
    setup_clean_parser(subparsers)
    setup_validate_parser(subparsers)
    setup_convert_parser(subparsers)
    setup_batch_parser(subparsers)
    setup_analyze_parser(subparsers)
    
    return parser


def handle_extract_pdf(args):
    """处理PDF提取命令"""
    try:
        from .extractors.pdf_extractor import PDFExtractor
        from .core.config import PDFConfig, Config
        
        config = PDFConfig()
        config.extract_text = args.text
        config.extract_tables = args.tables
        config.extract_images = args.images
        config.extract_forms = args.forms
        config.extract_metadata = args.metadata
        config.page_range = args.pages
        config.use_ocr = args.ocr
        config.ocr_language = args.ocr_lang
        
        extractor = PDFExtractor(config)
        result = extractor.extract(args.file)
        
        # 输出结果
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if args.format == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
            elif args.format == "txt":
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(result.raw_text)
            elif args.format == "csv" and result.tables:
                import csv
                with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
                    if result.tables:
                        writer = csv.writer(f)
                        writer.writerows(result.tables[0].data)
            
            logger.info(f"结果已保存: {output_path}")
        else:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        
        return 0
    
    except Exception as e:
        logger.error(f"PDF提取失败: {e}")
        return 1


def handle_extract_excel(args):
    """处理Excel提取命令"""
    try:
        from .extractors.excel_extractor import ExcelExtractor
        from .core.config import ExcelConfig
        
        config = ExcelConfig()
        config.header_row = args.header
        
        extractor = ExcelExtractor(config)
        
        if args.all_sheets:
            result = extractor.extract(args.file)
        elif args.sheet:
            result = extractor.extract(args.file, sheet_names=[args.sheet])
        elif args.sheet_index is not None:
            result = extractor.extract(args.file, sheet_index=args.sheet_index)
        else:
            result = extractor.extract(args.file)
        
        # 输出结果
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if args.format == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
            elif args.format == "csv":
                import csv
                with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
                    if result.sheets:
                        writer = csv.writer(f)
                        writer.writerows(result.sheets[0].data)
            elif args.format == "xlsx":
                import pandas as pd
                if result.sheets:
                    df = pd.DataFrame(result.sheets[0].data[1:], columns=result.sheets[0].data[0])
                    df.to_excel(output_path, index=False)
            
            logger.info(f"结果已保存: {output_path}")
        else:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        
        return 0
    
    except Exception as e:
        logger.error(f"Excel提取失败: {e}")
        return 1


def handle_extract_image(args):
    """处理图片OCR命令"""
    try:
        from .extractors.image_extractor import ImageExtractor
        from .core.config import ImageConfig
        
        config = ImageConfig()
        config.language = args.language
        config.ocr_engine = args.engine
        config.detect_tables = args.tables
        config.preprocess = args.preprocess
        
        extractor = ImageExtractor(config)
        result = extractor.extract(args.file)
        
        # 输出结果
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if args.format == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
            elif args.format == "txt":
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(result.raw_text)
            
            logger.info(f"结果已保存: {output_path}")
        else:
            if args.format == "txt":
                print(result.raw_text)
            else:
                print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        
        return 0
    
    except Exception as e:
        logger.error(f"图片OCR失败: {e}")
        return 1


def handle_clean(args):
    """处理清洗命令"""
    try:
        import pandas as pd
        from .cleaners.data_cleaner import DataCleaner
        from .core.config import DataCleaningConfig
        
        # 读取数据
        file_path = Path(args.file)
        if file_path.suffix.lower() == ".csv":
            df = pd.read_csv(file_path)
        elif file_path.suffix.lower() in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
        else:
            logger.error(f"不支持的文件格式: {file_path.suffix}")
            return 1
        
        # 配置清洗器
        config = DataCleaningConfig()
        config.remove_duplicates = args.remove_duplicates
        config.handle_missing = bool(args.fill_missing or args.drop_missing)
        config.missing_strategy = args.fill_missing if args.fill_missing else "drop" if args.drop_missing else "auto"
        config.fill_value = args.fill_value
        config.handle_outliers = args.remove_outliers
        
        cleaner = DataCleaner(config)
        df_cleaned = cleaner.clean_dataframe(df)
        
        if args.standardize_columns:
            df_cleaned = cleaner.standardize_column_names(df_cleaned)
        
        # 输出结果
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        output_format = args.format
        if not output_format:
            output_format = output_path.suffix.lower().lstrip(".")
        
        if output_format == "csv":
            df_cleaned.to_csv(output_path, index=False, encoding="utf-8-sig")
        elif output_format in ["xlsx", "xls"]:
            df_cleaned.to_excel(output_path, index=False)
        elif output_format == "json":
            df_cleaned.to_json(output_path, orient="records", force_ascii=False, indent=2)
        
        # 输出报告
        report = cleaner.get_report()
        logger.info(f"清洗完成: 原始 {report.rows_before} 行 -> 清洗后 {report.rows_after} 行")
        logger.info(f"结果已保存: {output_path}")
        
        return 0
    
    except Exception as e:
        logger.error(f"数据清洗失败: {e}")
        return 1


def handle_convert(args):
    """处理转换命令"""
    try:
        from .utils.batch_processor import FileConverter
        
        converter = FileConverter()
        
        input_path = Path(args.file)
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        input_ext = input_path.suffix.lower()
        
        if input_ext == ".csv":
            if args.format == "xlsx":
                converter.csv_to_excel(input_path, output_path)
            elif args.format == "json":
                converter.csv_to_json(input_path, output_path)
        elif input_ext in [".xlsx", ".xls"]:
            if args.format == "csv":
                converter.excel_to_csv(input_path, output_path, sheet_name=args.sheet)
            elif args.format == "json":
                converter.excel_to_json(input_path, output_path, sheet_name=args.sheet)
        elif input_ext == ".json":
            if args.format == "csv":
                converter.json_to_csv(input_path, output_path)
        else:
            logger.error(f"不支持的输入格式: {input_ext}")
            return 1
        
        logger.info(f"转换完成: {input_path} -> {output_path}")
        return 0
    
    except Exception as e:
        logger.error(f"格式转换失败: {e}")
        return 1


def handle_analyze(args):
    """处理分析命令"""
    try:
        import pandas as pd
        from .utils.smart_recognizer import SmartRecognizer
        
        # 读取数据
        file_path = Path(args.file)
        if file_path.suffix.lower() == ".csv":
            df = pd.read_csv(file_path)
        elif file_path.suffix.lower() in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
        else:
            logger.error(f"不支持的文件格式: {file_path.suffix}")
            return 1
        
        recognizer = SmartRecognizer()
        schema = recognizer.recognize_dataframe(df, table_name=file_path.stem)
        
        # 分类数据
        categories = recognizer.classify_data(df)
        
        # 生成描述
        description = recognizer.generate_schema_description(schema)
        
        result = {
            "schema": schema.to_dict(),
            "categories": categories,
            "description": description,
        }
        
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"分析报告已保存: {output_path}")
        else:
            print(description)
            print("\n数据分类:")
            for category, columns in categories.items():
                if columns:
                    print(f"  {category}: {', '.join(columns)}")
        
        return 0
    
    except Exception as e:
        logger.error(f"数据分析失败: {e}")
        return 1


def main(args: Optional[List[str]] = None) -> int:
    """主入口函数"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # 设置日志级别
    if parsed_args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif parsed_args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    # 执行命令
    if parsed_args.command == "extract":
        if parsed_args.extract_type == "pdf":
            return handle_extract_pdf(parsed_args)
        elif parsed_args.extract_type == "excel":
            return handle_extract_excel(parsed_args)
        elif parsed_args.extract_type == "image":
            return handle_extract_image(parsed_args)
    
    elif parsed_args.command == "clean":
        return handle_clean(parsed_args)
    
    elif parsed_args.command == "validate":
        logger.error("验证功能暂未实现")
        return 1
    
    elif parsed_args.command == "convert":
        return handle_convert(parsed_args)
    
    elif parsed_args.command == "analyze":
        return handle_analyze(parsed_args)
    
    elif parsed_args.command == "batch":
        logger.error("批量处理功能请使用shell脚本或Python API")
        return 1
    
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
