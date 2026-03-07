#!/usr/bin/env python3
"""
通用PDF文本提取器 - 提取PDF中的纯文本内容
补充 pdf-data-extractor 技能包
"""

import os
import sys
from typing import Optional, List

def extract_text_pypdf2(pdf_path: str) -> str:
    """使用PyPDF2提取文本（基础方法）"""
    try:
        import PyPDF2
        
        text = []
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text.append(f"--- Page {page_num} ---\n{page_text}")
        
        return "\n\n".join(text)
    except Exception as e:
        return f"PyPDF2提取失败: {e}"

def extract_text_pdfplumber(pdf_path: str) -> str:
    """使用pdfplumber提取文本（更精准）"""
    try:
        import pdfplumber
        
        text = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text.append(f"--- Page {page_num} ---\n{page_text}")
        
        return "\n\n".join(text)
    except Exception as e:
        return f"pdfplumber提取失败: {e}"

def extract_text_with_layout(pdf_path: str) -> str:
    """保留布局的文本提取"""
    try:
        import pdfplumber
        
        text = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # 按文本块提取，保留布局
                words = page.extract_words()
                if words:
                    lines = {}
                    for word in words:
                        y = round(word['top'])
                        if y not in lines:
                            lines[y] = []
                        lines[y].append(word['text'])
                    
                    page_text = "\n".join(
                        " ".join(lines[y]) for y in sorted(lines.keys())
                    )
                    text.append(f"--- Page {page_num} ---\n{page_text}")
        
        return "\n\n".join(text)
    except Exception as e:
        return f"布局提取失败: {e}"

def extract_pdf_text(pdf_path: str, method: str = 'auto', 
                     output: Optional[str] = None) -> str:
    """
    提取PDF文本
    
    Args:
        pdf_path: PDF文件路径
        method: 提取方法 (auto/pypdf2/pdfplumber/layout)
        output: 输出文件路径（可选）
    
    Returns:
        提取的文本内容
    """
    if not os.path.exists(pdf_path):
        return f"❌ 文件不存在: {pdf_path}"
    
    # 自动选择方法
    if method == 'auto':
        # 优先尝试pdfplumber
        result = extract_text_pdfplumber(pdf_path)
        if not result.startswith("pdfplumber提取失败"):
            method_used = 'pdfplumber'
        else:
            result = extract_text_pypdf2(pdf_path)
            method_used = 'pypdf2'
    elif method == 'pypdf2':
        result = extract_text_pypdf2(pdf_path)
        method_used = 'pypdf2'
    elif method == 'pdfplumber':
        result = extract_text_pdfplumber(pdf_path)
        method_used = 'pdfplumber'
    elif method == 'layout':
        result = extract_text_with_layout(pdf_path)
        method_used = 'layout'
    else:
        return f"❌ 未知方法: {method}"
    
    # 保存到文件
    if output:
        try:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"✅ 已保存到: {output} (使用{method_used}方法)")
        except Exception as e:
            print(f"⚠️ 保存失败: {e}")
    
    return result

def batch_extract_text(input_dir: str, output_dir: str, method: str = 'auto'):
    """批量提取目录下所有PDF"""
    import glob
    
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    
    print(f"📁 找到 {len(pdf_files)} 个PDF文件")
    print(f"💾 输出目录: {output_dir}\n")
    
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        name_without_ext = os.path.splitext(filename)[0]
        output_path = os.path.join(output_dir, f"{name_without_ext}.txt")
        
        print(f"🔄 处理: {filename}")
        extract_pdf_text(pdf_path, method=method, output=output_path)
    
    print(f"\n✅ 批量提取完成")

def search_in_pdf(pdf_path: str, keyword: str) -> List[dict]:
    """在PDF中搜索关键词"""
    text = extract_pdf_text(pdf_path, method='pdfplumber')
    
    results = []
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        if keyword in line:
            results.append({
                'line': line_num,
                'content': line.strip()
            })
    
    return results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='PDF文本提取工具')
    parser.add_argument('pdf_path', help='PDF文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-m', '--method', default='auto', 
                       choices=['auto', 'pypdf2', 'pdfplumber', 'layout'],
                       help='提取方法')
    parser.add_argument('-b', '--batch', action='store_true', 
                       help='批量处理目录')
    parser.add_argument('-s', '--search', help='搜索关键词')
    
    args = parser.parse_args()
    
    if args.batch:
        # 批量处理
        output_dir = args.output or './extracted_texts'
        batch_extract_text(args.pdf_path, output_dir, args.method)
    elif args.search:
        # 搜索模式
        results = search_in_pdf(args.pdf_path, args.search)
        print(f"\n🔍 搜索 '{args.search}' 找到 {len(results)} 处:\n")
        for r in results[:20]:  # 最多显示20条
            print(f"  行 {r['line']}: {r['content']}")
    else:
        # 单文件提取
        result = extract_pdf_text(args.pdf_path, args.method, args.output)
        if not args.output:
            print(result)
