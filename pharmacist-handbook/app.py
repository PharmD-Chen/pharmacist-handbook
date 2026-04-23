#!/usr/bin/env python3
"""Flask 应用 - 提供药品手册静态文件服务"""

from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# 静态文件目录
STATIC_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    """首页 - 主界面"""
    return send_from_directory(STATIC_DIR, 'main.html')

@app.route('/<path:path>')
def static_files(path):
    """静态文件"""
    return send_from_directory(STATIC_DIR, path)

if __name__ == '__main__':
    print("=" * 60)
    print("药品手册 Flask 服务")
    print("=" * 60)
    print("\n访问地址:")
    print("  - 本机: http://127.0.0.1:8889")
    print("  - 局域网: http://0.0.0.0:8889")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 60)
    
    # 允许外部访问
    app.run(host='0.0.0.0', port=8889, debug=False)
