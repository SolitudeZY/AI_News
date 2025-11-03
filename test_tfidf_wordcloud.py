#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试TF-IDF词云生成功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from wordcloud_generator import WordCloudGenerator
import json
import time

def test_tfidf_wordcloud():
    """测试TF-IDF词云生成"""
    print("开始测试TF-IDF词云生成功能...")
    
    # 创建测试数据
    test_articles = [
        {
            "title": "人工智能在医疗领域的应用",
            "description": "人工智能技术正在改变医疗行业，通过深度学习算法可以辅助医生进行疾病诊断和治疗方案制定。"
        },
        {
            "title": "机器学习算法的发展趋势",
            "description": "近年来，机器学习算法在计算机视觉、自然语言处理等领域取得了显著进展，推动了人工智能的发展。"
        },
        {
            "title": "深度学习在图像识别中的应用",
            "description": "深度学习模型在图像识别任务中表现出色，特别是在医疗影像分析和自动驾驶等领域。"
        },
        {
            "title": "自然语言处理技术进展",
            "description": "自然语言处理技术通过神经网络模型实现了文本分类、情感分析和机器翻译等功能。"
        },
        {
            "title": "大数据与人工智能结合",
            "description": "大数据技术为人工智能提供了丰富的数据源，促进了机器学习模型的训练和优化。"
        }
    ]
    
    # 测试进度回调函数
    def progress_callback(message, progress):
        print(f"进度: {progress*100:.1f}% - {message}")
    
    try:
        # 创建词云生成器实例
        generator = WordCloudGenerator(
            tfidf_threshold=0.05,  # 较低的阈值以便测试
            top_n_words=50,
            enable_cache=True
        )
        
        print("\n1. 测试TF-IDF词云生成...")
        output_path, tfidf_scores = generator.generate_tfidf_wordcloud(
            test_articles, 
            'test_tfidf_wordcloud.png',
            progress_callback
        )
        
        print(f"词云已生成: {output_path}")
        print(f"图例已生成: {output_path.replace('.png', '_legend.png')}")
        print(f"数据已导出: {output_path.replace('.png', '_data.csv')}")
        
        # 显示TF-IDF分数前10的词语
        print("\nTF-IDF分数最高的10个词语:")
        for i, (word, score) in enumerate(list(tfidf_scores.items())[:10]):
            print(f"  {i+1}. {word}: {score:.4f}")
        
        # 测试缓存功能
        print("\n2. 测试缓存功能...")
        start_time = time.time()
        cached_output, cached_scores = generator.generate_tfidf_wordcloud(
            test_articles, 
            'test_tfidf_wordcloud_cached.png',
            progress_callback
        )
        end_time = time.time()
        print(f"缓存生成时间: {end_time - start_time:.3f}秒")
        
        # 测试传统词云生成（向后兼容）
        print("\n3. 测试传统词云生成...")
        traditional_path = generator.generate_wordcloud(
            test_articles,
            'test_traditional_wordcloud.png',
            use_tfidf=False
        )
        print(f"传统词云已生成: {traditional_path}")
        
        print("\n测试完成！所有功能正常工作。")
        
        # 显示文件大小信息
        import os
        tfidf_size = os.path.getsize('test_tfidf_wordcloud.png')
        traditional_size = os.path.getsize('test_traditional_wordcloud.png')
        print(f"\n文件大小对比:")
        print(f"  TF-IDF词云: {tfidf_size} 字节")
        print(f"  传统词云: {traditional_size} 字节")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

def test_performance():
    """测试性能优化"""
    print("\n开始性能测试...")
    
    # 性能测试
    print("\n开始性能测试...")
    
    # 创建大量测试数据
    large_test_articles = []
    topics = [
        {'title_prefix': '科技前沿：', 'description_template': '这是关于人工智能和机器学习领域最新进展的深度分析。我们探讨了深度学习在图像识别、自然语言处理中的应用，以及神经网络在数据分析和预测模型中的重要作用。文章还涵盖了大数据、云计算、边缘计算等技术如何促进人工智能的发展，并讨论了未来人工智能技术可能面临的挑战和机遇。我们强调了持续学习、模型优化和算法创新的重要性。此外，还提到了人工智能在医疗、金融、教育等行业的广泛应用前景，以及伦理和社会影响的考量。'},
        {'title_prefix': '全球经济：', 'description_template': '全球经济正面临多重挑战与机遇。贸易关系、地缘政治、技术创新和消费者行为都在深刻影响市场。本文分析了当前经济形势，包括通货膨胀、利率政策、供应链韧性以及新兴市场的增长潜力。我们还讨论了数字化转型对传统产业的冲击与赋能，以及可持续发展在经济决策中的日益重要性。'},
        {'title_prefix': '环境保护：', 'description_template': '环境保护是全球共同的责任。气候变化、生物多样性丧失和资源枯竭对地球生态系统构成严重威胁。本文探讨了可再生能源、循环经济、污染防治和生态修复等关键议题。我们强调了国际合作、政策制定和公众参与在应对环境挑战中的关键作用，并展望了绿色技术和可持续生活方式的未来。'},
        {'title_prefix': '社会文化：', 'description_template': '社会文化现象反映了人类文明的演进。从传统习俗到现代潮流，文化多样性丰富了我们的世界。本文分析了社交媒体、流行艺术、教育改革和社区发展等方面的最新趋势。我们探讨了文化交流、身份认同和价值观变迁对社会结构的影响，以及数字时代下文化传承与创新的平衡。'}
    ]

    for i in range(20):
        topic = topics[i % len(topics)]
        large_test_articles.append({
            'title': f"{topic['title_prefix']}{i+1}",
            'description': f"{topic['description_template']} 第{i+1}篇文章。"
        })
    
    generator = WordCloudGenerator(
        tfidf_threshold=0.0001,
        top_n_words=100,
        enable_cache=True
    )

    print("第一次运行（无缓存）...")
    start_time = time.time()
    generator.generate_tfidf_wordcloud(large_test_articles, 'performance_test_1.png')
    first_run_time = time.time() - start_time
    print(f"第一次运行时间: {first_run_time:.3f}秒")
    
    # 第二次运行（有缓存）
    print("第二次运行（有缓存）...")
    start_time = time.time()
    generator.generate_tfidf_wordcloud(large_test_articles, 'performance_test_2.png')
    second_run_time = time.time() - start_time
    print(f"第二次运行时间: {second_run_time:.3f}秒")
    
    print(f"缓存加速效果: {first_run_time/second_run_time:.2f}x")

if __name__ == "__main__":
    import time
    
    # 基本功能测试
    test_tfidf_wordcloud()
    
    # 性能测试
    test_performance()
    
    print("\n所有测试完成！")