#!/usr/bin/env python3
"""
批量文档处理器
支持批量转换、重命名、合并等操作
"""

import argparse
import os
import glob
from docx import Document
import pandas as pd


def batch_convert(input_dir, output_dir, target_format):
    """批量转换文档"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 支持的格式映射
    format_map = {
        'docx': '*.docx',
        'xlsx': '*.xlsx',
        'pptx': '*.pptx',
        'pdf': '*.pdf'
    }
    
    # 获取源文件
    source_files = []
    for pattern in ['*.docx', '*.xlsx', '*.pptx', '*.csv', '*.json']:
        source_files.extend(glob.glob(os.path.join(input_dir, pattern)))
    
    print(f"找到 {len(source_files)} 个文件")
    
    for file_path in source_files:
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        
        try:
            if target_format == 'txt':
                # 提取文本
                if ext == '.docx':
                    doc = Document(file_path)
                    text = '\n'.join([p.text for p in doc.paragraphs])
                    output_path = os.path.join(output_dir, f'{name}.txt')
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                
                elif ext in ['.xlsx', '.xls']:
                    df = pd.read_excel(file_path)
                    output_path = os.path.join(output_dir, f'{name}.csv')
                    df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            elif target_format == 'csv' and ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
                output_path = os.path.join(output_dir, f'{name}.csv')
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            print(f"✓ {filename}")
            
        except Exception as e:
            print(f"✗ {filename}: {str(e)}")


def batch_rename(input_dir, pattern, replacement):
    """批量重命名"""
    files = os.listdir(input_dir)
    
    for filename in files:
        if pattern in filename:
            new_name = filename.replace(pattern, replacement)
            old_path = os.path.join(input_dir, filename)
            new_path = os.path.join(input_dir, new_name)
            os.rename(old_path, new_path)
            print(f"重命名: {filename} -> {new_name}")


def generate_index(input_dir, output_file):
    """生成文件索引"""
    files = []
    
    for root, dirs, filenames in os.walk(input_dir):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            size = os.path.getsize(file_path)
            files.append({
                '文件名': filename,
                '路径': file_path,
                '大小(字节)': size,
                '类型': os.path.splitext(filename)[1]
            })
    
    df = pd.DataFrame(files)
    
    if output_file.endswith('.xlsx'):
        df.to_excel(output_file, index=False)
    elif output_file.endswith('.csv'):
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
    elif output_file.endswith('.json'):
        df.to_json(output_file, orient='records', force_ascii=False, indent=2)
    
    print(f"索引已生成: {output_file}")
    print(f"共 {len(files)} 个文件")


def main():
    parser = argparse.ArgumentParser(description='批量文档处理器')
    parser.add_argument('action', 
                       choices=['convert', 'rename', 'index'],
                       help='操作类型')
    parser.add_argument('--input-dir', '-i', required=True, help='输入目录')
    parser.add_argument('--output-dir', '-o', help='输出目录')
    parser.add_argument('--format', '-f', help='目标格式 (convert用)')
    parser.add_argument('--pattern', '-p', help='匹配模式 (rename用)')
    parser.add_argument('--replacement', '-r', help='替换内容 (rename用)')
    parser.add_argument('--output-file', help='输出文件 (index用)')
    
    args = parser.parse_args()
    
    if args.action == 'convert':
        if not args.format:
            print("错误: convert 操作需要 --format 参数")
            return
        batch_convert(args.input_dir, args.output_dir or './output', args.format)
    
    elif args.action == 'rename':
        if not args.pattern or args.replacement is None:
            print("错误: rename 操作需要 --pattern 和 --replacement 参数")
            return
        batch_rename(args.input_dir, args.pattern, args.replacement)
    
    elif args.action == 'index':
        if not args.output_file:
            args.output_file = 'file_index.xlsx'
        generate_index(args.input_dir, args.output_file)


if __name__ == '__main__':
    main()
