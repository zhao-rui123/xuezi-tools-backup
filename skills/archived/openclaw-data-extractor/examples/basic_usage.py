"""
OpenClaw 基础使用示例

展示如何使用OpenClaw进行各种数据提取和处理操作。
"""

import json
from pathlib import Path


def example_pdf_extraction():
    """PDF数据提取示例"""
    print("=" * 50)
    print("PDF数据提取示例")
    print("=" * 50)
    
    try:
        from openclaw import PDFExtractor, Config
        
        # 创建提取器
        config = Config().pdf
        config.extract_tables = True
        config.extract_metadata = True
        
        extractor = PDFExtractor(config)
        
        # 提取PDF数据
        # result = extractor.extract("document.pdf")
        
        # 打印结果
        # print(f"页数: {result.metadata.pages}")
        # print(f"文本块数: {len(result.text_blocks)}")
        # print(f"表格数: {len(result.tables)}")
        
        # 保存为JSON
        # with open("output.json", "w", encoding="utf-8") as f:
        #     json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        
        print("PDF提取器已创建，请提供PDF文件路径进行提取")
        
    except ImportError as e:
        print(f"依赖未安装: {e}")


def example_excel_extraction():
    """Excel数据提取示例"""
    print("\n" + "=" * 50)
    print("Excel数据提取示例")
    print("=" * 50)
    
    try:
        from openclaw import ExcelExtractor, Config
        
        # 创建提取器
        config = Config().excel
        config.evaluate_formulas = True
        
        extractor = ExcelExtractor(config)
        
        # 提取Excel数据
        # result = extractor.extract("data.xlsx")
        
        # 打印结果
        # print(f"工作表数: {len(result.sheets)}")
        # for sheet in result.sheets:
        #     print(f"  - {sheet.name}: {sheet.max_row}行 x {sheet.max_col}列")
        
        # 转换为DataFrame
        # df = extractor.to_dataframe("data.xlsx", sheet_name="Sheet1")
        # print(df.head())
        
        print("Excel提取器已创建，请提供Excel文件路径进行提取")
        
    except ImportError as e:
        print(f"依赖未安装: {e}")


def example_image_ocr():
    """图片OCR示例"""
    print("\n" + "=" * 50)
    print("图片OCR示例")
    print("=" * 50)
    
    try:
        from openclaw import ImageExtractor, Config
        
        # 创建提取器
        config = Config().image
        config.language = "chi_sim+eng"
        config.detect_tables = True
        
        extractor = ImageExtractor(config)
        
        # OCR识别
        # result = extractor.extract("screenshot.png")
        
        # 打印结果
        # print(f"识别文本:\n{result.raw_text}")
        # print(f"文本块数: {len(result.text_blocks)}")
        
        # 识别表单字段
        # fields = extractor.extract_form_fields("form.png")
        # for field in fields:
        #     print(f"{field.label}: {field.value}")
        
        print("图片OCR提取器已创建，请提供图片文件路径进行识别")
        
    except ImportError as e:
        print(f"依赖未安装: {e}")


def example_data_cleaning():
    """数据清洗示例"""
    print("\n" + "=" * 50)
    print("数据清洗示例")
    print("=" * 50)
    
    try:
        import pandas as pd
        from openclaw import DataCleaner, Config
        
        # 创建示例数据
        data = {
            "name": ["Alice", "Bob", "Charlie", "Alice", None],
            "age": [25, 30, 35, 25, 28],
            "email": ["alice@example.com", "bob@test.com", "invalid", "alice@example.com", "eve@demo.com"],
            "salary": [50000, 60000, None, 50000, 55000],
        }
        df = pd.DataFrame(data)
        
        print("原始数据:")
        print(df)
        print(f"\n原始数据形状: {df.shape}")
        
        # 创建清洗器
        config = Config().cleaning
        config.remove_duplicates = True
        config.handle_missing = True
        config.missing_strategy = "fill"
        
        cleaner = DataCleaner(config)
        
        # 清洗数据
        df_cleaned = cleaner.clean_dataframe(df)
        
        print("\n清洗后数据:")
        print(df_cleaned)
        print(f"\n清洗后数据形状: {df_cleaned.shape}")
        
        # 获取清洗报告
        report = cleaner.get_report()
        print(f"\n清洗报告:")
        print(f"  - 去除重复行: {report.duplicates_removed}")
        print(f"  - 填充缺失值: {report.missing_values_filled}")
        
    except ImportError as e:
        print(f"依赖未安装: {e}")


def example_data_validation():
    """数据验证示例"""
    print("\n" + "=" * 50)
    print("数据验证示例")
    print("=" * 50)
    
    try:
        from openclaw import DataValidator, ValidationRule
        
        # 创建验证器
        validator = DataValidator()
        
        # 定义验证规则
        rules = [
            ValidationRule("name", "required"),
            ValidationRule("email", "format", {"format": "email"}),
            ValidationRule("age", "range", {"min": 0, "max": 150}),
            ValidationRule("phone", "format", {"format": "phone_cn"}),
        ]
        
        # 验证数据
        record = {
            "name": "张三",
            "email": "zhangsan@example.com",
            "age": 25,
            "phone": "13800138000",
        }
        
        result = validator.validate_record(record, rules)
        
        print(f"验证结果: {'通过' if result.is_valid else '失败'}")
        if result.errors:
            print("错误:")
            for error in result.errors:
                print(f"  - {error.field}: {error.message}")
        
        # 验证无效数据
        invalid_record = {
            "name": "",
            "email": "invalid-email",
            "age": 200,
            "phone": "123",
        }
        
        result = validator.validate_record(invalid_record, rules)
        
        print(f"\n无效数据验证结果: {'通过' if result.is_valid else '失败'}")
        if result.errors:
            print("错误:")
            for error in result.errors:
                print(f"  - {error.field}: {error.message}")
        
    except ImportError as e:
        print(f"依赖未安装: {e}")


def example_batch_processing():
    """批量处理示例"""
    print("\n" + "=" * 50)
    print("批量处理示例")
    print("=" * 50)
    
    try:
        from openclaw import BatchProcessor
        
        # 创建批量处理器
        processor = BatchProcessor(max_workers=4, show_progress=True)
        
        # 定义处理函数
        def process_file(file_path):
            # 模拟处理
            return {"file": str(file_path), "status": "processed"}
        
        # 批量处理文件
        # file_list = ["file1.pdf", "file2.pdf", "file3.pdf"]
        # results = processor.process_files(file_list, process_file, parallel=True)
        
        # 获取处理报告
        # report = processor.get_report()
        # print(f"处理文件数: {report.total_files}")
        # print(f"成功: {report.successful_files}")
        # print(f"失败: {report.failed_files}")
        
        print("批量处理器已创建，请提供文件列表进行处理")
        
    except ImportError as e:
        print(f"依赖未安装: {e}")


def example_smart_recognition():
    """智能识别示例"""
    print("\n" + "=" * 50)
    print("智能识别示例")
    print("=" * 50)
    
    try:
        import pandas as pd
        from openclaw import SmartRecognizer
        
        # 创建示例数据
        data = {
            "user_id": [1, 2, 3, 4, 5],
            "user_name": ["Alice", "Bob", "Charlie", "David", "Eve"],
            "user_email": ["alice@example.com", "bob@test.com", "charlie@demo.com", "david@sample.com", "eve@mail.com"],
            "user_phone": ["13800138001", "13800138002", "13800138003", "13800138004", "13800138005"],
            "created_at": pd.date_range("2024-01-01", periods=5),
            "amount": [100.50, 200.75, 150.25, 300.00, 250.50],
        }
        df = pd.DataFrame(data)
        
        # 创建识别器
        recognizer = SmartRecognizer()
        
        # 识别数据结构
        schema = recognizer.recognize_dataframe(df, table_name="users")
        
        print(f"表名: {schema.table_name}")
        print(f"行数: {schema.row_count}")
        print(f"列数: {len(schema.columns)}")
        
        print("\n列信息:")
        for col in schema.columns:
            print(f"  - {col.name}:")
            print(f"      数据类型: {col.data_type}")
            print(f"      语义类型: {col.semantic_type or 'N/A'}")
            print(f"      建议名称: {col.suggested_name or 'N/A'}")
            print(f"      是否主键: {col.is_primary_key}")
        
        # 数据分类
        categories = recognizer.classify_data(df)
        
        print("\n数据分类:")
        for category, columns in categories.items():
            if columns:
                print(f"  {category}: {', '.join(columns)}")
        
        # 生成描述
        description = recognizer.generate_schema_description(schema)
        print(f"\n结构描述:\n{description}")
        
    except ImportError as e:
        print(f"依赖未安装: {e}")


def example_pipeline():
    """数据处理流程示例"""
    print("\n" + "=" * 50)
    print("数据处理流程示例")
    print("=" * 50)
    
    try:
        from openclaw import DataPipeline, Config
        
        # 创建配置
        config = Config()
        config.pdf.extract_tables = True
        config.cleaning.remove_duplicates = True
        config.cleaning.handle_missing = True
        
        # 创建处理流程
        pipeline = DataPipeline(config)
        
        # 注册处理阶段
        # from openclaw.core.pipeline import StageProcessor, PipelineStage
        # 
        # class ExtractProcessor(StageProcessor):
        #     def process(self, data, context):
        #         # 提取逻辑
        #         return self._create_result(True, data)
        # 
        # pipeline.register_stage(ExtractProcessor(PipelineStage.EXTRACT))
        
        # 处理文件
        # context = pipeline.process_file("data.pdf")
        
        # 保存报告
        # pipeline.save_report(context, "report.json")
        
        print("数据处理流程已创建，请提供文件进行处理")
        
    except ImportError as e:
        print(f"依赖未安装: {e}")


if __name__ == "__main__":
    print("OpenClaw 基础使用示例")
    print("=" * 50)
    
    # 运行示例
    example_pdf_extraction()
    example_excel_extraction()
    example_image_ocr()
    example_data_cleaning()
    example_data_validation()
    example_batch_processing()
    example_smart_recognition()
    example_pipeline()
    
    print("\n" + "=" * 50)
    print("示例运行完成")
    print("=" * 50)
