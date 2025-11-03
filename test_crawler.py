"""
新闻爬虫测试用例
测试爬虫程序的各项功能
"""
import unittest
import json
import os
from datetime import datetime
from news_crawler import NewsCrawler


class TestNewsCrawler(unittest.TestCase):
    """新闻爬虫测试类"""

    def setUp(self):
        """测试前置设置"""
        self.crawler = NewsCrawler()

    def test_keywords_initialization(self):
        """测试关键词初始化"""
        self.assertIsInstance(self.crawler.keywords, list)
        self.assertGreater(len(self.crawler.keywords), 0)
        # 检查中英文关键词都存在
        chinese_keywords = [kw for kw in self.crawler.keywords if '\u4e00' <= kw[0] <= '\u9fff']
        english_keywords = [kw for kw in self.crawler.keywords if kw[0].isalpha()]
        self.assertGreater(len(chinese_keywords), 0)
        self.assertGreater(len(english_keywords), 0)

    def test_news_sources_initialization(self):
        """测试新闻源初始化"""
        self.assertIsInstance(self.crawler.news_sources, list)
        self.assertGreater(len(self.crawler.news_sources), 0)
        # 检查36kr源是否存在
        self.assertIn('https://www.36kr.com/feed', self.crawler.news_sources)

    def test_filter_by_keywords(self):
        """测试关键词过滤功能"""
        test_articles = [
            {
                'title': '人工智能技术的最新进展',
                'description': '人工智能在医疗领域的应用',
                'link': 'http://example.com/1',
                'published': '2025-10-30',
                'source': 'test_source'
            },
            {
                'title': '普通新闻标题',
                'description': '这是一条普通新闻',
                'link': 'http://example.com/2',
                'published': '2025-10-30',
                'source': 'test_source'
            }
        ]
        
        # 测试单个文章过滤
        filtered_articles = [article for article in test_articles if self.crawler.filter_by_keywords(article)]
        self.assertEqual(len(filtered_articles), 1)
        self.assertEqual(filtered_articles[0]['title'], '人工智能技术的最新进展')

    def test_categorize_news(self):
        """测试新闻分类功能"""
        test_articles = [
            {
                'title': 'AI技术突破',
                'description': '人工智能领域的新突破',
                'link': 'http://example.com/1',
                'published': '2025-10-30',
                'source': 'test_source'
            },
            {
                'title': '新能源汽车发展',
                'description': '电动汽车市场快速增长',
                'link': 'http://example.com/2',
                'published': '2025-10-30',
                'source': 'test_source'
            }
        ]
        
        categorized = self.crawler.categorize_news(test_articles)
        # 检查中文和英文关键词分类
        self.assertIn('AI', categorized)
        self.assertIn('能源', categorized)  # 使用中文关键词
        self.assertEqual(len(categorized['AI']), 1)
        self.assertEqual(len(categorized['能源']), 1)

    def test_generate_json_data(self):
        """测试JSON数据生成功能"""
        test_articles = [
            {
                'title': '测试新闻1',
                'description': '测试描述1',
                'link': 'http://example.com/1',
                'published': '2025-10-30',
                'source': 'test_source1'
            },
            {
                'title': '测试新闻2',
                'description': '测试描述2',
                'link': 'http://example.com/2',
                'published': '2025-10-30',
                'source': 'test_source2'
            }
        ]
        
        categorized_news = {'AI': test_articles, 'Tech': [test_articles[0]]}
        
        json_data = self.crawler.generate_json_data(test_articles, categorized_news)
        
        # 检查数据结构
        self.assertIn('statistics', json_data)
        self.assertIn('news', json_data)
        self.assertIn('categorized_news', json_data)
        
        # 检查统计信息
        stats = json_data['statistics']
        self.assertEqual(stats['total_news'], 2)
        self.assertEqual(stats['sources_count'], 2)
        self.assertEqual(stats['categories_count'], 2)
        self.assertIn('last_updated', stats)

    def test_json_file_creation(self):
        """测试JSON文件创建"""
        # 运行爬虫生成文件
        filename = self.crawler.crawl_and_generate_report()
        
        # 检查JSON文件是否存在
        self.assertTrue(os.path.exists('news_data.json'))
        
        # 检查JSON文件内容
        with open('news_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn('statistics', data)
            self.assertIn('news', data)
            self.assertIn('categorized_news', data)


class TestDashboardFunctionality(unittest.TestCase):
    """仪表板功能测试类"""

    def test_dashboard_html_exists(self):
        """测试仪表板HTML文件存在"""
        self.assertTrue(os.path.exists('news_dashboard.html'))

    def test_json_data_file_exists(self):
        """测试JSON数据文件存在"""
        self.assertTrue(os.path.exists('news_data.json'))

    def test_json_data_structure(self):
        """测试JSON数据结构完整性"""
        if os.path.exists('news_data.json'):
            with open('news_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 检查必需字段
                required_fields = ['statistics', 'news', 'categorized_news']
                for field in required_fields:
                    self.assertIn(field, data)
                
                # 检查统计信息字段
                stats_fields = ['total_news', 'sources_count', 'categories_count', 
                               'sources_distribution', 'categories_distribution', 'last_updated']
                for field in stats_fields:
                    self.assertIn(field, data['statistics'])


class TestThemeFunctionality(unittest.TestCase):
    """主题功能测试类"""

    def test_theme_toggle_exists(self):
        """测试主题切换按钮存在"""
        if os.path.exists('news_daily_20251030.html'):
            with open('news_daily_20251030.html', 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('toggleTheme', content)
                self.assertIn('initTheme', content)

    def test_dashboard_theme_exists(self):
        """测试仪表板主题功能存在"""
        if os.path.exists('news_dashboard.html'):
            with open('news_dashboard.html', 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('toggleTheme', content)
                self.assertIn('initTheme', content)


if __name__ == '__main__':
    # 运行所有测试
    unittest.main(verbosity=2)