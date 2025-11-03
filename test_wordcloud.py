#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试词云生成模块
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from wordcloud_generator import WordCloudGenerator

def test_wordcloud_generation():
    """测试词云生成功能"""
    print("开始测试词云生成...")
    
    # 创建测试数据
    test_articles = [
        {
            'title': '人工智能技术发展迅速',
            'description': '人工智能在各个领域都有广泛应用，包括机器学习、深度学习等技术'
        },
        {
            'title': '大数据分析助力商业决策',
            'description': '企业通过大数据分析可以更好地理解市场趋势和客户需求'
        },
        {
            'title': '云计算服务日益普及',
            'description': '云计算为企业提供了灵活的计算资源和存储解决方案'
        }
    ]
    
    try:
        # 创建词云生成器实例
        generator = WordCloudGenerator()
        
        # 生成词云
        output_path = generator.generate_wordcloud(test_articles, 'test_wordcloud.png')
        
        if output_path and os.path.exists(output_path):
            print(f"✓ 词云生成成功: {output_path}")
            print(f"✓ 文件大小: {os.path.getsize(output_path)} 字节")
            return True
        else:
            print("✗ 词云生成失败")
            return False
            
    except Exception as e:
        print(f"✗ 词云生成过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    success = test_wordcloud_generation()
    if success:
        print("\n🎉 词云生成测试通过！")
    else:
        print("\n❌ 词云生成测试失败！")
        sys.exit(1)