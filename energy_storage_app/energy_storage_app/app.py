# -*- coding: utf-8 -*-
"""
CALB工商业储能收资清单 - Web应用
支持在线查看、填写、下载Excel模板、导出填写数据
"""

from flask import Flask, render_template, request, send_file, redirect, url_for, flash, session
import pandas as pd
import openpyxl
from notify import send_feishu_notification  # 导入飞书通知
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
import os
import json
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'energy-storage-secret-key-2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('submissions', exist_ok=True)

# Excel模板路径
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '..', 'CALB-工商业储能收资清单.xlsx')
SUBMISSIONS_FILE = 'submissions/submissions.json'


def load_submissions():
    """加载已提交的数据"""
    if os.path.exists(SUBMISSIONS_FILE):
        with open(SUBMISSIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_submission(data):
    """保存提交的数据"""
    submissions = load_submissions()
    data['id'] = str(uuid.uuid4())[:8]
    data['submit_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    submissions.append(data)
    with open(SUBMISSIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(submissions, f, ensure_ascii=False, indent=2)
    return data['id']


def get_form_data():
    """获取表单字段配置"""
    return {
        # 1、基本信息
        'company_name': {'label': '*公司名称', 'type': 'text', 'required': True, 'section': '1、基本信息'},
        'project_name': {'label': '*项目名称', 'type': 'text', 'required': True, 'section': '1、基本信息'},
        'project_location': {'label': '*项目地点', 'type': 'text', 'required': True, 'section': '1、基本信息'},
        'contact_person': {'label': '*对接人', 'type': 'text', 'required': True, 'section': '1、基本信息'},
        'contact_phone': {'label': '*联系方式', 'type': 'tel', 'required': True, 'section': '1、基本信息'},
        'industry': {'label': '项目客户行业', 'type': 'select', 'options': ['冶金', '有色', '机械', '轻工', '纺织', '烟草', '商贸', '其他'], 'section': '1、基本信息'},
        'vehicle_access': {'label': '*车辆吊装路径情况', 'type': 'textarea', 'required': True, 'section': '1、基本信息'},

        # 2、配电信息
        'power_type': {'label': '*企业用电性质', 'type': 'select', 'options': ['大工业', '一般工商业'], 'required': True, 'section': '2、配电信息'},
        'voltage_level': {'label': '*计量电压等级', 'type': 'select', 'options': ['35KV', '10KV', '380V', '220V'], 'required': True, 'section': '2、配电信息'},
        'transformer_capacity': {'label': '*主变容量(kVA)', 'type': 'text', 'required': True, 'section': '2、配电信息'},
        'transformer_count': {'label': '台数', 'type': 'number', 'section': '2、配电信息'},
        'basic_price': {'label': '*基本电价', 'type': 'select', 'options': ['需量 元/kVA×月', '容量 元/kVA×月'], 'required': True, 'section': '2、配电信息'},
        'transformer_status': {'label': '*变压器开备情况', 'type': 'textarea', 'required': True, 'section': '2、配电信息'},
        'usage_days': {'label': '*正常用电天数/年', 'type': 'number', 'required': True, 'section': '2、配电信息'},
        'storage_voltage': {'label': '*储能系统接入电网电压等级', 'type': 'select', 'options': ['10KV', '380V'], 'required': True, 'section': '2、配电信息'},
        'load_max': {'label': '*用电负荷(KW)最大', 'type': 'number', 'required': True, 'section': '2、配电信息'},
        'load_min': {'label': '最小', 'type': 'number', 'section': '2、配电信息'},
        'load_avg': {'label': '平均', 'type': 'number', 'section': '2、配电信息'},
        'usage_uniform': {'label': '全年白天和晚上用电是否均匀', 'type': 'textarea', 'section': '2、配电信息'},
        'maintenance_time': {'label': '设备大修每年停工时间', 'type': 'textarea', 'section': '2、配电信息'},
        'backup_interval': {'label': '有无备用间隔供储能系统接入', 'type': 'textarea', 'section': '2、配电信息'},
        'storage_distance': {'label': '*储能及配电房之间的距离(米)', 'type': 'number', 'required': True, 'section': '2、配电信息'},

        # 3、其他信息
        'other_info': {'label': '其他信息', 'type': 'textarea', 'section': '3、其他信息'},

        # 4、收资清单
        'location_photo': {'label': '*储能系统安装位置照片', 'type': 'file', 'required': True, 'section': '4、项目收资清单', 'note': '图片格式'},
        'location_layout': {'label': '*储能系统安装位置平面布局图', 'type': 'file', 'required': True, 'section': '4、项目收资清单', 'note': 'CAD图纸'},
        'underground_pipeline': {'label': '储能系统安装位置地下管线图', 'type': 'file', 'section': '4、项目收资清单', 'note': 'CAD图纸'},
        'transformer_params': {'label': '*储能系统接入的变压器设备参数', 'type': 'textarea', 'required': True, 'section': '4、项目收资清单'},
        'load_data': {'label': '*以日为单位负载功率数据（最近6个月）', 'type': 'file', 'required': True, 'section': '4、项目收资清单', 'note': '国网app可查看'},
        'electricity_bill': {'label': '*近12个月电费单（基本电费+电度电费）', 'type': 'file', 'required': True, 'section': '4、项目收资清单', 'note': '电业局打印'},
        'electrical_drawing': {'label': '*企业用电电气一次图', 'type': 'file', 'required': True, 'section': '4、项目收资清单', 'note': 'CAD图纸'},
        'distribution_drawing': {'label': '*配电室电气一次接线图', 'type': 'file', 'required': True, 'section': '4、项目收资清单', 'note': 'CAD图纸'},
    }


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/view')
def view():
    """在线查看表格"""
    return render_template('view.html')


@app.route('/form', methods=['GET', 'POST'])
def form():
    """在线填写表单"""
    form_data = get_form_data()

    if request.method == 'POST':
        # 处理表单提交
        submission = {}

        for key, config in form_data.items():
            if config['type'] == 'file':
                file = request.files.get(key)
                if file and file.filename:
                    # 保存文件
                    filename = f"{submission.get('project_name', 'unknown')}_{key}_{file.filename}"
                    filename = "".join(c for c in filename if c.isalnum() or c in '._-')
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    submission[key] = filename
                else:
                    submission[key] = ''
            else:
                submission[key] = request.form.get(key, '')

        # 保存提交
        submit_id = save_submission(submission)
        flash(f'提交成功！提交ID: {submit_id}', 'success')
        
        # 发送飞书通知
        try:
            send_feishu_notification(submission)
        except Exception as e:
            print(f"[WARN] 飞书通知发送失败: {e}")
        
        return redirect(url_for('form'))

    return render_template('form.html', form_data=form_data)


@app.route('/submissions')
def submissions():
    """查看已提交的数据"""
    submissions_list = load_submissions()
    return render_template('submissions.html', submissions=submissions_list)


@app.route('/submissions/export')
def export_submissions():
    """导出所有提交数据为Excel"""
    submissions_list = load_submissions()

    if not submissions_list:
        flash('没有可导出的数据', 'warning')
        return redirect(url_for('submissions'))

    # 创建Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = '提交数据'

    # 写入表头
    headers = ['提交ID', '提交时间', '公司名称', '项目名称', '项目地点', '对接人', '联系方式',
               '企业用电性质', '计量电压等级', '主变容量(kVA)', '变压器台数', '基本电价',
               '正常用电天数/年', '储能接入电压等级', '最大负荷(KW)', '储能距配电房距离(米)', '其他信息']

    form_data = get_form_data()
    header_key_map = {
        '提交ID': 'id', '提交时间': 'submit_time', '公司名称': 'company_name',
        '项目名称': 'project_name', '项目地点': 'project_location', '对接人': 'contact_person',
        '联系方式': 'contact_phone', '企业用电性质': 'power_type', '计量电压等级': 'voltage_level',
        '主变容量(kVA)': 'transformer_capacity', '变压器台数': 'transformer_count',
        '基本电价': 'basic_price', '正常用电天数/年': 'usage_days',
        '储能接入电压等级': 'storage_voltage', '最大负荷(KW)': 'load_max',
        '储能距配电房距离(米)': 'storage_distance', '其他信息': 'other_info'
    }

    # 样式
    header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF', size=11)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = border

    # 写入数据
    for row_idx, sub in enumerate(submissions_list, 2):
        for col_idx, header in enumerate(headers, 1):
            key = header_key_map.get(header, header.lower())
            value = sub.get(key, '')
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.border = border
            cell.alignment = Alignment(vertical='center')

    # 设置列宽
    column_widths = [12, 18, 20, 20, 20, 12, 15, 15, 15, 15, 10, 18, 15, 18, 15, 20, 30]
    for i, width in enumerate(column_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width

    # 保存
    output_path = 'submissions/工商业储能收资清单_导出数据.xlsx'
    wb.save(output_path)

    return send_file(output_path, as_attachment=True, download_name='工商业储能收资清单_导出数据.xlsx')


@app.route('/download/template')
def download_template():
    """下载Excel模板"""
    # 如果模板存在则下载，否则自动生成
    if os.path.exists(TEMPLATE_PATH):
        return send_file(TEMPLATE_PATH, as_attachment=True, download_name='CALB-工商业储能收资清单.xlsx')
    else:
        # 自动生成模板
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = '收资清单'
        
        # 样式
        header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF', size=11)
        border = Border(left=Side(style='thin'), right=Side(style='thin'),
                        top=Side(style='thin'), bottom=Side(style='thin'))
        
        # 表头
        headers = [
            ('A', '公司名称', True),
            ('B', '项目名称', True),
            ('C', '项目地点', True),
            ('D', '对接人', True),
            ('E', '联系方式', True),
            ('F', '企业用电性质', False),
            ('G', '计量电压等级', False),
            ('H', '主变容量(kVA)', False),
            ('I', '变压器台数', False),
            ('J', '基本电价方式', False),
            ('K', '正常用电天数/年', False),
            ('L', '储能接入电压等级', False),
            ('M', '最大负荷(KW)', False),
            ('N', '储能距配电房距离(米)', False),
            ('O', '其他信息', False),
        ]
        
        for col, header, required in headers:
            cell = ws[f'{col}1']
            cell.value = f'{header}{" *" if required else ""}'
            cell.fill = header_fill
            cell.font = header_font
            cell.border = border
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # 设置列宽
        widths = {'A': 20, 'B': 20, 'C': 25, 'D': 12, 'E': 15, 'F': 15, 
                  'G': 15, 'H': 15, 'I': 10, 'J': 18, 'K': 15, 'L': 18, 
                  'M': 15, 'N': 18, 'O': 30}
        for col, width in widths.items():
            ws.column_dimensions[col].width = width
        
        # 添加示例数据行说明
        ws['A2'] = '请在此处填写公司全称'
        ws['F2'] = '大工业/一般工商业'
        ws['G2'] = '35KV/10KV/380V/220V'
        ws['J2'] = '需量/容量'
        ws['L2'] = '10KV/380V'
        
        for row in range(2, 102):
            for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']:
                cell = ws[f'{col}{row}']
                cell.border = border
        
        # 添加说明sheet
        ws2 = wb.create_sheet('填写说明')
        ws2['A1'] = 'CALB工商业储能收资清单 - 填写说明'
        ws2['A1'].font = Font(bold=True, size=14)
        ws2['A3'] = '1. 标 * 的字段为必填项'
        ws2['A4'] = '2. 填写完成后，请将文件保存为 .xlsx 格式'
        ws2['A5'] = '3. CAD图纸、照片等文件请通过网页表单单独上传'
        ws2['A6'] = '4. 如有疑问，请联系项目对接人'
        ws2.column_dimensions['A'].width = 60
        
        # 保存
        output_path = 'submissions/工商业储能收资清单_模板.xlsx'
        wb.save(output_path)
        
        return send_file(output_path, as_attachment=True, download_name='CALB-工商业储能收资清单_模板.xlsx')


@app.route('/import', methods=['GET', 'POST'])
def import_excel():
    """导入Excel文件提交"""
    if request.method == 'POST':
        file = request.files.get('excel_file')
        if not file or not file.filename.endswith('.xlsx'):
            flash('请上传 .xlsx 格式的Excel文件', 'error')
            return redirect(url_for('import_excel'))
        
        try:
            # 读取Excel
            wb = openpyxl.load_workbook(file)
            ws = wb.active
            
            # 读取表头和数据
            headers = [cell.value for cell in ws[1]]
            data_row = [cell.value for cell in ws[2]]  # 取第一行数据
            
            if not data_row or not any(data_row):
                flash('Excel文件中没有数据', 'error')
                return redirect(url_for('import_excel'))
            
            # 映射字段
            header_map = {
                '公司名称': 'company_name', '项目名称': 'project_name',
                '项目地点': 'project_location', '对接人': 'contact_person',
                '联系方式': 'contact_phone', '企业用电性质': 'power_type',
                '计量电压等级': 'voltage_level', '主变容量(kVA)': 'transformer_capacity',
                '变压器台数': 'transformer_count', '基本电价方式': 'basic_price',
                '正常用电天数/年': 'usage_days', '储能接入电压等级': 'storage_voltage',
                '最大负荷(KW)': 'load_max', '储能距配电房距离(米)': 'storage_distance',
                '其他信息': 'other_info'
            }
            
            # 构建提交数据
            submission = {'source': 'excel_import'}
            for header, value in zip(headers, data_row):
                if header in header_map:
                    submission[header_map[header]] = str(value) if value else ''
            
            # 保存并通知
            submit_id = save_submission(submission)
            flash(f'Excel导入成功！提交ID: {submit_id}', 'success')
            
            try:
                send_feishu_notification(submission)
            except Exception as e:
                print(f"[WARN] 飞书通知发送失败: {e}")
            
            return redirect(url_for('submissions'))
            
        except Exception as e:
            flash(f'导入失败: {str(e)}', 'error')
            return redirect(url_for('import_excel'))
    
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Excel批量导入 - CALB储能收资清单</title>
        <style>
            body { font-family: 'Microsoft YaHei', sans-serif; background: #f5f7fa; padding: 50px; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #1a1a2e; margin-bottom: 30px; }
            .info { background: #e8f4fd; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .info h3 { margin-bottom: 10px; color: #366092; }
            .info ol { margin-left: 20px; }
            .form-group { margin-bottom: 20px; }
            input[type=file] { padding: 10px; border: 1px solid #ddd; border-radius: 8px; width: 100%; }
            .btn { padding: 12px 30px; background: linear-gradient(135deg, #00d4ff, #00ff88); color: white; border: none; border-radius: 25px; cursor: pointer; font-size: 1em; }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(0,212,255,0.3); }
            a { color: #00d4ff; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Excel批量导入</h1>
            <div class="info">
                <h3>操作步骤：</h3>
                <ol>
                    <li>先 <a href="/download/template">下载Excel模板</a></li>
                    <li>按照模板格式填写数据</li>
                    <li>保存为 .xlsx 格式</li>
                    <li>上传填写好的文件</li>
                </ol>
            </div>
            <form method="POST" enctype="multipart/form-data">
                <div class="form-group">
                    <input type="file" name="excel_file" accept=".xlsx" required>
                </div>
                <button type="submit" class="btn">📤 导入提交</button>
            </form>
            <p style="margin-top: 20px;"><a href="/">返回首页</a></p>
        </div>
    </body>
    </html>
    """


@app.route('/submissions/<submit_id>')
def submission_detail(submit_id):
    """查看单条提交详情"""
    submissions_list = load_submissions()
    submission = None
    for sub in submissions_list:
        if sub.get('id') == submit_id:
            submission = sub
            break

    if not submission:
        flash('未找到该提交记录', 'error')
        return redirect(url_for('submissions'))

    form_data = get_form_data()
    return render_template('detail.html', submission=submission, form_data=form_data)


if __name__ == '__main__':
    # 运行服务器
    app.run(host='0.0.0.0', port=5000, debug=True)
