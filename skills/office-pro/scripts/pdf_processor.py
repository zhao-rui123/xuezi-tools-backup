#!/usr/bin/env python3
"""
PDF 处理器
支持合并、拆分、提取文本、添加水印
"""

import argparse
import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO


def merge_pdfs(input_files, output_file):
    """合并多个 PDF"""
    merger = PdfMerger()
    
    for pdf_file in input_files:
        if os.path.exists(pdf_file):
            merger.append(pdf_file)
            print(f"添加: {pdf_file}")
    
    merger.write(output_file)
    merger.close()
    print(f"合并完成: {output_file}")


def split_pdf(input_file, output_dir, pages_per_file=1):
    """拆分 PDF"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    reader = PdfReader(input_file)
    total_pages = len(reader.pages)
    
    for i in range(0, total_pages, pages_per_file):
        writer = PdfWriter()
        end_page = min(i + pages_per_file, total_pages)
        
        for page_num in range(i, end_page):
            writer.add_page(reader.pages[page_num])
        
        output_path = os.path.join(output_dir, f'page_{i+1}_{end_page}.pdf')
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        print(f"生成: {output_path}")


def extract_text(input_file, output_file=None):
    """提取 PDF 文本"""
    reader = PdfReader(input_file)
    text = ""
    
    for page in reader.pages:
        text += page.extract_text() + "\n\n"
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"文本已保存: {output_file}")
    else:
        print(text[:2000])  # 打印前2000字符
    
    return text


def add_watermark(input_file, output_file, watermark_text):
    """添加文字水印"""
    reader = PdfReader(input_file)
    writer = PdfWriter()
    
    # 创建水印页
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    c.setFont("Helvetica", 60)
    c.setFillColorRGB(0.5, 0.5, 0.5, alpha=0.3)
    c.saveState()
    c.translate(300, 400)
    c.rotate(45)
    c.drawCentredString(0, 0, watermark_text)
    c.restoreState()
    c.save()
    packet.seek(0)
    
    watermark = PdfReader(packet)
    
    for page in reader.pages:
        page.merge_page(watermark.pages[0])
        writer.add_page(page)
    
    with open(output_file, 'wb') as f:
        writer.write(f)
    
    print(f"水印已添加: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='PDF 处理器')
    parser.add_argument('action', choices=['merge', 'split', 'extract', 'watermark'],
                       help='操作类型')
    parser.add_argument('--input', '-i', nargs='+', required=True, help='输入文件')
    parser.add_argument('--output', '-o', help='输出文件/目录')
    parser.add_argument('--pages', '-p', type=int, default=1, help='每文件页数（拆分用）')
    parser.add_argument('--watermark', '-w', help='水印文字')
    
    args = parser.parse_args()
    
    if args.action == 'merge':
        if not args.output:
            args.output = 'merged.pdf'
        merge_pdfs(args.input, args.output)
    
    elif args.action == 'split':
        if not args.output:
            args.output = './split_output'
        split_pdf(args.input[0], args.output, args.pages)
    
    elif args.action == 'extract':
        extract_text(args.input[0], args.output)
    
    elif args.action == 'watermark':
        if not args.watermark:
            print("错误: 添加水印需要 --watermark 参数")
            return
        if not args.output:
            args.output = 'watermarked.pdf'
        add_watermark(args.input[0], args.output, args.watermark)


if __name__ == '__main__':
    main()
