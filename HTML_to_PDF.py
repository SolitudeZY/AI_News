#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML到PDF转换工具
使用浏览器打印功能生成PDF
"""

import os
import sys
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from urllib.parse import urlparse
import threading
import json

class PDFGenerator:
    """PDF生成器类 - 使用浏览器打印功能"""
    
    def __init__(self, output_dir='pdf_output'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_pdf_from_html(self, html_content, pdf_filename=None):
        """
        从HTML内容生成PDF文件
        注意：此版本使用浏览器打印功能，实际PDF生成在客户端完成
        
        Args:
            html_content (str): HTML内容
            pdf_filename (str): 输出的PDF文件名
            
        Returns:
            str: 生成的PDF文件路径（模拟）
        """
        try:
            # 生成文件名
            if not pdf_filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                pdf_filename = f'news_dashboard_{timestamp}.pdf'
            
            pdf_path = os.path.join(self.output_dir, pdf_filename)
            
            logging.info(f"PDF生成请求已接收，使用浏览器打印功能: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logging.error(f"PDF生成处理失败: {str(e)}")
            raise

class PDFRequestHandler(BaseHTTPRequestHandler):
    """PDF请求处理器"""
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """处理PDF生成请求"""
        if self.path == '/generate-pdf':
            try:
                # 获取请求内容长度
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                
                # 解析JSON数据
                data = json.loads(post_data.decode('utf-8'))
                html_content = data.get('html', '')
                
                # 生成PDF（模拟）
                pdf_generator = PDFGenerator()
                pdf_path = pdf_generator.generate_pdf_from_html(html_content)
                
                # 返回成功响应
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    'status': 'success',
                    'message': 'PDF生成请求已处理，请使用浏览器打印功能',
                    'pdf_path': pdf_path
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                logging.error(f"PDF生成请求处理失败: {str(e)}")
                self.send_error(500, f"PDF生成失败: {str(e)}")
        else:
            self.send_error(404, "页面未找到")
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        logging.info(f"{self.address_string()} - {format % args}")

def start_pdf_server(port=8080):
    """启动PDF服务器"""
    try:
        server = HTTPServer(('localhost', port), PDFRequestHandler)
        logging.info(f"PDF服务器启动在 http://localhost:{port}")
        print(f"PDF服务器启动在 http://localhost:{port}")
        print("注意：此版本使用浏览器打印功能生成PDF")
        server.serve_forever()
    except Exception as e:
        logging.error(f"服务器启动失败: {str(e)}")
        print(f"服务器启动失败: {str(e)}")

if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 启动服务器
    start_pdf_server()