#!/usr/bin/env python3
"""
Office Chart Suite CLI
命令行工具入口
"""

import argparse
import sys
import os
import json
import pandas as pd
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.smart_chart_recommender import recommend_chart, SmartChartRecommender
from core.document_with_charts import DocumentWithCharts, create_data_driven_report
from core.template_manager import TemplateManager, TemplateBuilder
from core.advanced_charts import create_advanced_chart, AdvancedChartGenerator
from core.html_reporter import create_interactive_report, InteractiveHTMLReporter
from core.excel_generator import ExcelTemplateLibrary, create_excel_with_template, create_professional_excel
from core.ppt_generator import PPTTemplateLibrary, create_ppt_with_template, create_professional_ppt
from core.office_advanced import (
    OfficeFormatConverter, BatchOfficeProcessor, add_word_toc, 
    protect_word_document, excel_add_conditional_format
)
from core.document_optimizer import (
    optimize_word, summarize_document, optimize_excel, optimize_ppt,
    DocumentOptimizer, ExcelOptimizer, PPTOptimizer
)
from data_sources.data_connector import create_data_source, DataSourceManager
from ai.smart_analyzer import analyze_with_ai, generate_smart_report


def cmd_recommend(args):
    data = _load_data(args.input)
    result = recommend_chart(data, args.type)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_generate_report(args):
    output_path = args.output or "report.docx"
    create_data_driven_report(
        data_source=args.input,
        output_path=output_path,
        chart_configs=json.loads(args.charts) if args.charts else None,
        report_title=args.title or "数据报告"
    )
    print(f"报告已生成: {output_path}")


def cmd_interactive(args):
    data = _load_data(args.input)
    create_interactive_report(
        data=data,
        title=args.title or "交互式报告",
        output_path=args.output or "report.html"
    )
    print(f"交互式报告已生成: {args.output or 'report.html'}")


def cmd_analyze(args):
    data = _load_data(args.input)
    result = analyze_with_ai(data, args.prompt)
    print(json.dumps({
        "summary": result.summary,
        "insights": result.insights,
        "charts": result.charts,
        "anomalies": result.anomalies,
        "statistics": result.statistics
    }, ensure_ascii=False, indent=2))


def cmd_smart_report(args):
    data = _load_data(args.input)
    result = generate_smart_report(data, args.prompt)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_advanced_chart(args):
    data = _load_data(args.input)
    output = create_advanced_chart(args.type, data, title=args.title or args.type)
    print(f"图表已生成: {output}")


def cmd_excel_template(args):
    data = _load_data(args.input) if args.input else None
    output = create_excel_with_template(args.template, data, args.output)
    print(f"Excel模板已生成: {output}")


def cmd_excel_professional(args):
    data = _load_data(args.input)
    output = create_professional_excel(data, args.output or "report.xlsx", 
                                      style=args.style or "blue",
                                      title=args.title or "数据报告")
    print(f"Excel已生成: {output}")


def cmd_ppt_template(args):
    output = create_ppt_with_template(args.template, None, args.output)
    print(f"PPT模板已生成: {output}")


def cmd_ppt_professional(args):
    output = create_professional_ppt(args.output or "presentation.pptx",
                                    title=args.title or "演示文稿",
                                    style=args.style or "corporate")
    print(f"PPT已生成: {output}")


def cmd_convert(args):
    converter = OfficeFormatConverter()
    
    if args.action == "excel2word":
        converter.excel_to_word_table(args.input, args.output, title=args.title or "数据表")
        print(f"已转换: {args.output}")
    elif args.action == "excel2ppt":
        converter.excel_to_ppt(args.input, args.output, title=args.title or "数据报告")
        print(f"已转换: {args.output}")
    elif args.action == "word2ppt":
        converter.word_to_ppt(args.input, args.output)
        print(f"已转换: {args.output}")
    elif args.action == "word2excel":
        converter.word_table_to_excel(args.input, args.output)
        print(f"已转换: {args.output}")


def cmd_batch(args):
    processor = BatchOfficeProcessor()
    
    if args.action == "merge-excel":
        processor.batch_merge_excel(
            json.loads(args.input),  # input_files as JSON array
            args.output
        )
        print(f"已合并: {args.output}")
    elif args.action == "batch-reports":
        processor.batch_create_reports(
            args.input,  # data file
            args.template,
            args.output,
            args.prefix or "report"
        )
        print(f"批量报告已生成: {args.output}")


def cmd_word_toc(args):
    output = add_word_toc(args.input, args.output)
    print(f"目录已添加: {output}")


def cmd_word_protect(args):
    output = protect_word_document(args.input, args.output, args.password)
    print(f"文档已保护: {output}")


def cmd_excel_conditional(args):
    output = excel_add_conditional_format(args.input, args.output, args.range)
    print(f"条件格式已添加: {output}")


def cmd_optimize_word(args):
    result = optimize_word(
        args.input,
        args.output,
        fix_format=True,
        fix_spacing=True,
        fix_tables=True,
        add_page_numbers=True,
        compress=True
    )
    print(f"✅ Word文档已优化: {result.output_path}")
    print(f"   已修复: {', '.join(result.issues_fixed)}")


def cmd_summarize(args):
    output = summarize_document(args.input, args.output)
    print(f"✅ 摘要文档已生成: {output}")


def cmd_optimize_excel(args):
    result = optimize_excel(
        args.input,
        args.output,
        apply_style=args.style or "blue",
        freeze_header=True,
        auto_adjust=True,
        remove_empty=True
    )
    print(f"✅ Excel已优化: {result.output_path}")
    print(f"   已修复: {', '.join(result.issues_fixed)}")


def cmd_optimize_ppt(args):
    result = optimize_ppt(
        args.input,
        args.output,
        apply_theme=args.theme or "corporate",
        normalize_text=True,
        remove_empty=True,
        add_numbers=True
    )
    print(f"✅ PPT已优化: {result.output_path}")
    print(f"   已修复: {', '.join(result.issues_fixed)}")


def cmd_template_list(args):
    if args.target == "excel":
        templates = ExcelTemplateLibrary.list_templates()
        print(f"Excel模板 ({len(templates)}):")
        for t in templates:
            print(f"  - {t['name']}: {t['description']}")
    elif args.target == "ppt":
        templates = PPTTemplateLibrary.list_templates()
        print(f"PPT模板 ({len(templates)}):")
        for t in templates:
            print(f"  - {t['name']}: {t['description']}")
    else:
        manager = TemplateManager()
        templates = manager.list_templates(category=args.category, template_type=args.type)
        print(f"可用模板 ({len(templates)}):")
        for t in templates:
            print(f"  - {t.name} [{t.category}] {t.description}")


def _load_data(input_path: str):
    if input_path.endswith('.csv'):
        return pd.read_csv(input_path)
    elif input_path.endswith(('.xlsx', '.xls')):
        return pd.read_excel(input_path)
    elif input_path.endswith('.json'):
        return pd.read_json(input_path)
    else:
        raise ValueError(f"Unsupported file format: {input_path}")


def main():
    parser = argparse.ArgumentParser(description='Office Chart Suite - 智能文档图表工具')
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    recommend_parser = subparsers.add_parser('recommend', help='智能图表推荐')
    recommend_parser.add_argument('--input', '-i', required=True, help='输入数据文件')
    recommend_parser.add_argument('--type', '-t', help='指定图表类型')

    report_parser = subparsers.add_parser('report', help='生成Word报告')
    report_parser.add_argument('--input', '-i', required=True, help='输入数据文件')
    report_parser.add_argument('--output', '-o', help='输出文件路径')
    report_parser.add_argument('--title', '-t', help='报告标题')
    report_parser.add_argument('--charts', '-c', help='图表配置 JSON')

    interactive_parser = subparsers.add_parser('interactive', help='生成交互式HTML报告')
    interactive_parser.add_argument('--input', '-i', required=True, help='输入数据文件')
    interactive_parser.add_argument('--output', '-o', help='输出文件路径')
    interactive_parser.add_argument('--title', '-t', help='报告标题')

    analyze_parser = subparsers.add_parser('analyze', help='AI智能分析')
    analyze_parser.add_argument('--input', '-i', required=True, help='输入数据文件')
    analyze_parser.add_argument('--prompt', '-p', help='分析提示词')

    smart_parser = subparsers.add_parser('smart-report', help='AI智能报告生成')
    smart_parser.add_argument('--input', '-i', required=True, help='输入数据文件')
    smart_parser.add_argument('--prompt', '-p', required=True, help='报告生成提示词')

    chart_parser = subparsers.add_parser('chart', help='生成高级图表')
    chart_parser.add_argument('--input', '-i', required=True, help='输入数据文件')
    chart_parser.add_argument('--type', '-t', required=True, help='图表类型')
    chart_parser.add_argument('--title', help='图表标题')
    chart_parser.add_argument('--output', '-o', help='输出文件路径')

    excel_template_parser = subparsers.add_parser('excel-template', help='使用Excel模板')
    excel_template_parser.add_argument('--template', '-t', required=True, help='模板ID')
    excel_template_parser.add_argument('--input', '-i', help='输入数据文件')
    excel_template_parser.add_argument('--output', '-o', help='输出文件路径')

    excel_pro_parser = subparsers.add_parser('excel', help='生成专业Excel')
    excel_pro_parser.add_argument('--input', '-i', required=True, help='输入数据文件')
    excel_pro_parser.add_argument('--output', '-o', help='输出文件路径')
    excel_pro_parser.add_argument('--style', '-s', help='样式风格')
    excel_pro_parser.add_argument('--title', '-t', help='标题')

    ppt_template_parser = subparsers.add_parser('ppt-template', help='使用PPT模板')
    ppt_template_parser.add_argument('--template', '-t', required=True, help='模板ID')
    ppt_template_parser.add_argument('--output', '-o', help='输出文件路径')

    ppt_pro_parser = subparsers.add_parser('ppt', help='生成专业PPT')
    ppt_pro_parser.add_argument('--output', '-o', help='输出文件路径')
    ppt_pro_parser.add_argument('--style', '-s', help='样式风格')
    ppt_pro_parser.add_argument('--title', '-t', help='标题')

    convert_parser = subparsers.add_parser('convert', help='格式转换')
    convert_parser.add_argument('--action', '-a', required=True,
                               choices=['excel2word', 'excel2ppt', 'word2ppt', 'word2excel'],
                               help='转换类型')
    convert_parser.add_argument('--input', '-i', required=True, help='输入文件')
    convert_parser.add_argument('--output', '-o', required=True, help='输出文件')
    convert_parser.add_argument('--title', '-t', help='标题')

    batch_parser = subparsers.add_parser('batch', help='批量处理')
    batch_parser.add_argument('--action', '-a', required=True,
                            choices=['merge-excel', 'batch-reports'],
                            help='处理类型')
    batch_parser.add_argument('--input', '-i', required=True, help='输入')
    batch_parser.add_argument('--output', '-o', required=True, help='输出目录')
    batch_parser.add_argument('--template', help='模板文件')
    batch_parser.add_argument('--prefix', help='文件前缀')

    word_toc_parser = subparsers.add_parser('word-toc', help='添加Word目录')
    word_toc_parser.add_argument('--input', '-i', required=True, help='输入文件')
    word_toc_parser.add_argument('--output', '-o', help='输出文件')

    word_protect_parser = subparsers.add_parser('word-protect', help='保护Word文档')
    word_protect_parser.add_argument('--input', '-i', required=True, help='输入文件')
    word_protect_parser.add_argument('--output', '-o', help='输出文件')
    word_protect_parser.add_argument('--password', '-p', help='密码')

    excel_cond_parser = subparsers.add_parser('excel-conditional', help='Excel条件格式')
    excel_cond_parser.add_argument('--input', '-i', required=True, help='输入文件')
    excel_cond_parser.add_argument('--output', '-o', help='输出文件')
    excel_cond_parser.add_argument('--range', '-r', required=True, help='范围如 A1:B10')

    optimize_word_parser = subparsers.add_parser('optimize-word', help='优化Word文档')
    optimize_word_parser.add_argument('--input', '-i', required=True, help='输入文件')
    optimize_word_parser.add_argument('--output', '-o', help='输出文件')

    summarize_parser = subparsers.add_parser('summarize', help='精简文档内容')
    summarize_parser.add_argument('--input', '-i', required=True, help='输入文件')
    summarize_parser.add_argument('--output', '-o', help='输出文件')

    optimize_excel_parser = subparsers.add_parser('optimize-excel', help='优化Excel')
    optimize_excel_parser.add_argument('--input', '-i', required=True, help='输入文件')
    optimize_excel_parser.add_argument('--output', '-o', help='输出文件')
    optimize_excel_parser.add_argument('--style', '-s', help='样式风格')

    optimize_ppt_parser = subparsers.add_parser('optimize-ppt', help='优化PPT')
    optimize_ppt_parser.add_argument('--input', '-i', required=True, help='输入文件')
    optimize_ppt_parser.add_argument('--output', '-o', help='输出文件')
    optimize_ppt_parser.add_argument('--theme', '-t', help='主题风格')

    template_parser = subparsers.add_parser('templates', help='列出可用模板')
    template_parser.add_argument('--category', '-c', help='分类筛选')
    template_parser.add_argument('--type', '-t', help='类型筛选')
    template_parser.add_argument('--target', '-tg', choices=['excel', 'ppt', 'all'], default='all')

    args = parser.parse_args()

    if args.command == 'recommend':
        cmd_recommend(args)
    elif args.command == 'report':
        cmd_generate_report(args)
    elif args.command == 'interactive':
        cmd_interactive(args)
    elif args.command == 'analyze':
        cmd_analyze(args)
    elif args.command == 'smart-report':
        cmd_smart_report(args)
    elif args.command == 'chart':
        cmd_advanced_chart(args)
    elif args.command == 'excel-template':
        cmd_excel_template(args)
    elif args.command == 'excel':
        cmd_excel_professional(args)
    elif args.command == 'ppt-template':
        cmd_ppt_template(args)
    elif args.command == 'ppt':
        cmd_ppt_professional(args)
    elif args.command == 'convert':
        cmd_convert(args)
    elif args.command == 'batch':
        cmd_batch(args)
    elif args.command == 'word-toc':
        cmd_word_toc(args)
    elif args.command == 'word-protect':
        cmd_word_protect(args)
    elif args.command == 'excel-conditional':
        cmd_excel_conditional(args)
    elif args.command == 'optimize-word':
        cmd_optimize_word(args)
    elif args.command == 'summarize':
        cmd_summarize(args)
    elif args.command == 'optimize-excel':
        cmd_optimize_excel(args)
    elif args.command == 'optimize-ppt':
        cmd_optimize_ppt(args)
    elif args.command == 'templates':
        cmd_template_list(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
