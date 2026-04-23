#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
药品追溯码盘点系统
本机服务器版本
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
import json

# 初始化Flask应用
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# 启用CORS，允许移动端访问
CORS(app)

# 数据库配置 - 使用绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
os.makedirs(INSTANCE_DIR, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(INSTANCE_DIR, "inventory.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

# 初始化数据库
db = SQLAlchemy(app)

# ==================== 数据库模型 ====================

class Shelf(db.Model):
    """货架模型"""
    __tablename__ = 'shelves'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Drug(db.Model):
    """药品模型"""
    __tablename__ = 'drugs'
    id = db.Column(db.Integer, primary_key=True)
    trace_code = db.Column(db.String(100), unique=True, nullable=False)  # 追溯码
    name = db.Column(db.String(200), nullable=False)  # 药品名称
    specification = db.Column(db.String(100))  # 规格
    manufacturer = db.Column(db.String(200))  # 生产厂家
    batch_number = db.Column(db.String(50))  # 批号
    expiry_date = db.Column(db.String(20))  # 有效期
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'trace_code': self.trace_code,
            'name': self.name,
            'specification': self.specification,
            'manufacturer': self.manufacturer,
            'batch_number': self.batch_number,
            'expiry_date': self.expiry_date
        }

class InventoryRecord(db.Model):
    """盘点记录模型"""
    __tablename__ = 'inventory_records'
    id = db.Column(db.Integer, primary_key=True)
    shelf_id = db.Column(db.Integer, db.ForeignKey('shelves.id'), nullable=False)
    drug_id = db.Column(db.Integer, db.ForeignKey('drugs.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  # 实际数量
    operator = db.Column(db.String(50))  # 操作人
    inventory_date = db.Column(db.DateTime, default=datetime.now)  # 盘点日期
    
    # 关联关系
    shelf = db.relationship('Shelf', backref='inventory_records')
    drug = db.relationship('Drug', backref='inventory_records')
    
    def to_dict(self):
        return {
            'id': self.id,
            'shelf_name': self.shelf.name if self.shelf else '',
            'drug_name': self.drug.name if self.drug else '',
            'specification': self.drug.specification if self.drug else '',
            'batch_number': self.drug.batch_number if self.drug else '',
            'quantity': self.quantity,
            'operator': self.operator,
            'inventory_date': self.inventory_date.strftime('%Y-%m-%d %H:%M:%S')
        }

class MaintenanceRecord(db.Model):
    """养护记录模型"""
    __tablename__ = 'maintenance_records'
    id = db.Column(db.Integer, primary_key=True)
    drug_id = db.Column(db.Integer, db.ForeignKey('drugs.id'), nullable=False)
    batch_number = db.Column(db.String(50))  # 批号
    quantity = db.Column(db.Integer, nullable=False)  # 数量
    maintenance_type = db.Column(db.String(50))  # 养护类型
    notes = db.Column(db.Text)  # 备注
    operator = db.Column(db.String(50))  # 操作人
    maintenance_date = db.Column(db.DateTime, default=datetime.now)  # 养护日期
    
    # 关联关系
    drug = db.relationship('Drug', backref='maintenance_records')
    
    def to_dict(self):
        return {
            'id': self.id,
            'drug_name': self.drug.name if self.drug else '',
            'specification': self.drug.specification if self.drug else '',
            'batch_number': self.batch_number,
            'quantity': self.quantity,
            'maintenance_type': self.maintenance_type,
            'notes': self.notes,
            'operator': self.operator,
            'maintenance_date': self.maintenance_date.strftime('%Y-%m-%d %H:%M:%S')
        }

# ==================== 路由 ====================

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/mobile')
def mobile():
    """移动端页面"""
    return render_template('mobile.html')

@app.route('/admin')
def admin():
    """管理后台"""
    return render_template('admin.html')

# ==================== API接口 ====================

@app.route('/api/shelves', methods=['GET', 'POST'])
def shelves():
    """货架管理API"""
    if request.method == 'GET':
        shelves = Shelf.query.all()
        return jsonify({'success': True, 'data': [s.to_dict() for s in shelves]})
    
    elif request.method == 'POST':
        data = request.json
        shelf = Shelf(
            name=data.get('name'),
            description=data.get('description', '')
        )
        db.session.add(shelf)
        db.session.commit()
        return jsonify({'success': True, 'data': shelf.to_dict()})

@app.route('/api/parse-trace-code', methods=['POST'])
def parse_trace_code():
    """解析追溯码API"""
    data = request.json
    trace_code = data.get('trace_code', '')
    
    if not trace_code:
        return jsonify({'success': False, 'message': '追溯码不能为空'})
    
    # 先查询数据库是否已存在
    drug = Drug.query.filter_by(trace_code=trace_code).first()
    
    if drug:
        return jsonify({'success': True, 'data': drug.to_dict(), 'exists': True})
    
    # 解析追溯码（简化版，实际应根据追溯码规则解析）
    # 中国药品追溯码通常为20位数字
    parsed_data = parse_drug_trace_code(trace_code)
    
    return jsonify({'success': True, 'data': parsed_data, 'exists': False})

@app.route('/api/drugs', methods=['POST'])
def create_drug():
    """创建药品记录"""
    data = request.json
    
    drug = Drug(
        trace_code=data.get('trace_code'),
        name=data.get('name'),
        specification=data.get('specification', ''),
        manufacturer=data.get('manufacturer', ''),
        batch_number=data.get('batch_number', ''),
        expiry_date=data.get('expiry_date', '')
    )
    
    db.session.add(drug)
    db.session.commit()
    
    return jsonify({'success': True, 'data': drug.to_dict()})

@app.route('/api/inventory', methods=['POST'])
def create_inventory():
    """创建盘点记录"""
    data = request.json
    
    record = InventoryRecord(
        shelf_id=data.get('shelf_id'),
        drug_id=data.get('drug_id'),
        quantity=data.get('quantity'),
        operator=data.get('operator', '未知')
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({'success': True, 'data': record.to_dict()})

@app.route('/api/inventory/shelf/<int:shelf_id>', methods=['GET'])
def get_inventory_by_shelf(shelf_id):
    """获取指定货架的盘点记录"""
    records = InventoryRecord.query.filter_by(shelf_id=shelf_id).all()
    return jsonify({'success': True, 'data': [r.to_dict() for r in records]})

@app.route('/api/inventory/all', methods=['GET'])
def get_all_inventory():
    """获取所有盘点记录"""
    records = InventoryRecord.query.order_by(InventoryRecord.inventory_date.desc()).all()
    return jsonify({'success': True, 'data': [r.to_dict() for r in records]})

@app.route('/api/maintenance', methods=['POST'])
def create_maintenance():
    """创建养护记录"""
    data = request.json
    
    record = MaintenanceRecord(
        drug_id=data.get('drug_id'),
        batch_number=data.get('batch_number', ''),
        quantity=data.get('quantity'),
        maintenance_type=data.get('maintenance_type', '常规养护'),
        notes=data.get('notes', ''),
        operator=data.get('operator', '未知')
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({'success': True, 'data': record.to_dict()})

@app.route('/api/maintenance/all', methods=['GET'])
def get_all_maintenance():
    """获取所有养护记录"""
    records = MaintenanceRecord.query.order_by(MaintenanceRecord.maintenance_date.desc()).all()
    return jsonify({'success': True, 'data': [r.to_dict() for r in records]})

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """获取统计信息"""
    # 盘点统计
    total_inventory = InventoryRecord.query.count()
    today_inventory = InventoryRecord.query.filter(
        db.func.date(InventoryRecord.inventory_date) == datetime.now().date()
    ).count()
    
    # 养护统计
    total_maintenance = MaintenanceRecord.query.count()
    today_maintenance = MaintenanceRecord.query.filter(
        db.func.date(MaintenanceRecord.maintenance_date) == datetime.now().date()
    ).count()
    
    # 货架统计
    total_shelves = Shelf.query.count()
    
    return jsonify({
        'success': True,
        'data': {
            'total_inventory': total_inventory,
            'today_inventory': today_inventory,
            'total_maintenance': total_maintenance,
            'today_maintenance': today_maintenance,
            'total_shelves': total_shelves
        }
    })

# ==================== 辅助函数 ====================

def parse_drug_trace_code(trace_code):
    """
    解析药品追溯码
    注意：这是简化版，实际应根据国家药品追溯码标准解析
    """
    # 模拟解析结果
    # 实际应用中，这里应该调用追溯码解析API或根据规则解析
    return {
        'trace_code': trace_code,
        'name': '未知药品（请手动输入）',
        'specification': '',
        'manufacturer': '',
        'batch_number': '',
        'expiry_date': ''
    }

def init_db():
    """初始化数据库"""
    with app.app_context():
        db.create_all()
        
        # 添加示例货架
        if not Shelf.query.first():
            sample_shelves = [
                Shelf(name='A01', description='口服药货架1'),
                Shelf(name='A02', description='口服药货架2'),
                Shelf(name='B01', description='注射剂货架1'),
                Shelf(name='B02', description='注射剂货架2'),
                Shelf(name='C01', description='外用药货架'),
            ]
            db.session.add_all(sample_shelves)
            db.session.commit()
            print("✓ 已创建示例货架数据")

# ==================== 启动应用 ====================

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    # 获取本机IP地址
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("\n" + "="*60)
    print("🚀 药品追溯码盘点系统已启动")
    print("="*60)
    print(f"📱 移动端访问: http://{local_ip}:5001/mobile")
    print(f"💻 管理后台: http://{local_ip}:5001/admin")
    print(f"🌐 本机访问: http://127.0.0.1:5001")
    print("="*60)
    print("⚠️  请确保手机和电脑在同一WiFi网络下")
    print("="*60 + "\n")
    
    # 启动服务器（允许外部访问）
    app.run(host='0.0.0.0', port=5001, debug=True)
