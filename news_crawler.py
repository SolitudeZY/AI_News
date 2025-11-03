import requests
import os
import shutil
from newspaper import Article
import feedparser
from datetime import datetime
import re
import time
import json
from wordcloud_generator import WordCloudGenerator

class NewsCrawler:
    def __init__(self):
        self.keywords = ['科技', '金融', 'AI', '教育', '人工智能', '投资', '创新', '数字化', '区块链', '加密货币', '大数据', '云计算', '物联网', '5G', '元宇宙', '网络安全', '电子商务', '移动支付', '自动驾驶', '生物技术', '医疗健康', '能源', '环保', '可持续发展', '创业', '风险投资', '股票', '债券', '汇率', '通胀', '经济政策', '央行', '美联储','深度学习','机器学习',
                        'technology', 'finance', 'artificial intelligence', 'education', 'blockchain', 'cryptocurrency', 'big data', 'cloud computing', 'IoT', '5G', 'metaverse', 'cybersecurity', 'e-commerce', 'mobile payment', 'autonomous driving', 'biotechnology', 'healthcare', 'energy', 'environment', 'sustainability', 'startup', 'venture capital', 'stock', 'bond', 'exchange rate', 'inflation', 'economic policy', 'central bank', 'Federal Reserve']
        self.news_sources = [
            # 国内新闻源
            'https://www.36kr.com/feed',                  # 36氪
            'https://rss.thepaper.cn/feed',              # 澎湃新闻
            'https://www.jiemian.com/lists/5.xml',       # 界面新闻
            'https://www.yicai.com/feed',                # 第一财经
            'https://rss.caixin.com/markets/finance',    # 财新网财经
            'https://www.huxiu.com/rss/0.xml',           # 虎嗅网
            'https://www.tmtpost.com/rss.xml',           # 钛媒体
            # 国际新闻源
            'https://feeds.bbci.co.uk/news/rss.xml',     # BBC
            'https://techcrunch.com/feed/',              # TechCrunch
            'https://www.wired.com/feed/rss',            # Wired
            'https://www.ft.com/rss/home',               # Financial Times
            'https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml', # NY Times Tech
            'https://feeds.npr.org/1004/rss.xml',        # NPR Business
            'https://www.theguardian.com/international/rss', # The Guardian International
            'https://feeds.arstechnica.com/arstechnica/index' # Ars Technica
        ]
        self.logs_dir = "logs"
        self.data_dir = "data"
        self.setup_logging()
        self.create_directories()
    
    def create_directories(self):
        """创建必要的目录"""
        try:
            os.makedirs(self.logs_dir, exist_ok=True)
            os.makedirs(self.data_dir, exist_ok=True)
            self.log_message(f"已创建目录: {self.logs_dir} 和 {self.data_dir}")
        except OSError as e:
            self.log_message(f"创建目录时出错: {e}")
            raise # Re-raise to indicate a critical error
    
    def setup_logging(self):
        """设置日志记录"""
        self.log_file = os.path.join(self.logs_dir, f"news_crawler_log_{datetime.now().strftime('%Y%m%d')}.txt")
    
    def log_message(self, message):
        """记录日志消息"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        print(log_entry.strip())
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def fetch_news_from_rss(self, rss_url):
        """从RSS源获取新闻（带重试机制）"""
        max_retries = 3
        retry_delay = 1  # 秒
        
        for attempt in range(max_retries):
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                self.log_message(f"尝试 {attempt + 1}/{max_retries}: 抓取 {rss_url}")
                feed = feedparser.parse(rss_url)
                
                if feed.bozo:  # 检查RSS解析错误
                    raise Exception(f"RSS解析错误: {feed.bozo_exception}")
                
                articles = []
                for entry in feed.entries[:100]:  # 增加获取数量到100条
                    title = entry.title
                    link = entry.link
                    published = entry.get('published', '')
                    
                    # 关键词过滤
                    article_data = {
                        'title': title,
                        'description': entry.get('description', '')
                    }
                    if self.filter_by_keywords(article_data):
                        articles.append({
                            'title': title,
                            'link': link,
                            'source': rss_url,
                            'published': published,
                            'description': entry.get('description', '')
                        })
                self.log_message(f"{rss_url}: 成功获取{len(articles)}条相关新闻")
                return articles
            except Exception as e:
                self.log_message(f"尝试 {attempt + 1} 失败: {rss_url} - 错误: {e}")
                if attempt < max_retries - 1:
                    self.log_message(f"{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                else:
                    self.log_message(f"{rss_url}: 经过{max_retries}次尝试后仍然失败")
        return []
    
    def filter_by_keywords(self, article):
        """根据关键词过滤新闻"""
        # 检查标题和描述中是否包含关键词
        title_lower = article.get('title', '').lower()
        description_lower = article.get('description', '').lower()
        
        text_to_check = title_lower + ' ' + description_lower
        for keyword in self.keywords:
            if keyword.lower() in text_to_check:
                return True
        return False
    
    def categorize_news(self, articles):
        """将新闻按关键词分类"""
        categorized = {}
        for keyword in self.keywords:
            categorized[keyword] = []
        
        for article in articles:
            title = article['title'].lower()
            description = article.get('description', '').lower()
            text_to_check = title + ' ' + description
            
            # 为每篇文章设置主要分类
            assigned_category = None
            for keyword in self.keywords:
                if keyword.lower() in text_to_check:
                    categorized[keyword].append(article)
                    if not assigned_category:
                        assigned_category = keyword
            
            # 如果没有匹配到任何分类，设置为"其他"
            if not assigned_category:
                if '其他' not in categorized:
                    categorized['其他'] = []
                categorized['其他'].append(article)
                assigned_category = '其他'
            
            # 为文章设置category字段
            article['category'] = assigned_category
        
        # 移除空分类
        return {k: v for k, v in categorized.items() if v}
    
    def generate_summary_with_deepseek(self, articles):
        """使用DeepSeek API生成新闻摘要"""
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key:
            error_msg = "错误: 未设置DEEPSEEK_API_KEY环境变量。请按以下步骤设置：\n" \
                       "1. 在Windows中: setx DEEPSEEK_API_KEY \"你的API密钥\"\n" \
                       "2. 重启命令行或IDE使环境变量生效\n" \
                       "3. 获取API密钥: https://platform.deepseek.com/\n" \
                       "跳过摘要生成"
            self.log_message(error_msg)
            print(error_msg)
            return ""

        # 准备提示词
        titles = [article['title'] for article in articles]
        news_text = "\n".join(titles)
        
        prompt = f"""请根据以下新闻标题，生成一段300-500字的中文摘要。要求：
- 具有整体感，提炼出当日新闻的主要趋势、关注焦点或舆论动向
- 不要机械复述标题，要进行概括与串联
- 风格自然流畅

新闻标题：
{news_text}

摘要："""

        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'model': 'deepseek-chat',
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 1000
            }
            response = requests.post('https://api.deepseek.com/v1/chat/completions', headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            summary = result['choices'][0]['message']['content'].strip()
            return summary
        except Exception as e:
            print(f"生成摘要时出错: {e}")
            return ""
    
    def generate_markdown_report(self, categorized_news, all_articles, summary=None):
        """生成Markdown格式的日报"""
        today = datetime.now().strftime('%Y年%m月%d日')
        
        # 生成摘要（如果未提供）
        if summary is None:
            summary = self.generate_summary_with_deepseek(all_articles)
        
        markdown = f"# 新闻日报 - {today}\n\n"
        if summary:
            markdown += "## 今日导览摘要\n\n"
            markdown += f"{summary}\n\n"
        markdown += "## 今日热点新闻摘要\n\n"
        
        for category, articles in categorized_news.items():
            if articles:
                markdown += f"### {category}\n\n"
                for i, article in enumerate(articles[:5], 1):  # 每个分类最多5条
                    markdown += f"{i}. **{article['title']}**  \n"
                    markdown += f"   [阅读原文]({article['link']})  \n"
                    if article.get('published'):
                        markdown += f"   发布时间: {article['published']}  \n"
                    markdown += "\n"
        
        markdown += "---\n"
        markdown += "*本日报由AI自动生成*\n"
        
        return markdown
    
    def test_news_sources(self):
        """测试所有新闻源的可用性"""
        self.log_message("开始测试新闻源可用性...")
        results = {}
        
        for source in self.news_sources:
            self.log_message(f"测试新闻源: {source}")
            articles = self.fetch_news_from_rss(source)
            results[source] = {
                'status': '成功' if articles else '失败',
                'article_count': len(articles)
            }
        
        # 生成测试报告
        report = "新闻源可用性测试报告\n" + "="*50 + "\n"
        for source, result in results.items():
            report += f"{source}: {result['status']} (获取{result['article_count']}条新闻)\n"
        
        successful_sources = [s for s, r in results.items() if r['status'] == '成功']
        report += f"\n总计: {len(successful_sources)}/{len(self.news_sources)} 个新闻源可用"
        
        self.log_message(report)
        print(report)
        return results
    
    def generate_json_data(self, all_articles, categorized_news, summary=None):
        """生成JSON格式数据供动态仪表板使用"""
        # 统计信息
        total_news = len(all_articles)
        sources_count = {}
        categories_count = {}
        
        for article in all_articles:
            source = article['source']
            sources_count[source] = sources_count.get(source, 0) + 1
        
        for category, articles in categorized_news.items():
            categories_count[category] = len(articles)
        
        # 生成摘要（如果未提供）
        if summary is None:
            summary = self.generate_summary_with_deepseek(all_articles)
        
        # 构建JSON数据结构
        json_data = {
            "statistics": {
                "total_news": total_news,
                "sources_count": len(sources_count),
                "categories_count": len(categories_count),
                "sources_distribution": sources_count,
                "categories_distribution": categories_count,
                "last_updated": datetime.now().isoformat()
            },
            "news": all_articles,
            "categorized_news": categorized_news,
            "summary": summary if summary else ""
        }
        
        return json_data

    def crawl_and_generate_report(self):
        """主函数：抓取新闻并生成报告"""
        self.log_message("开始抓取新闻...")
        
        all_articles = []
        for source in self.news_sources:
            self.log_message(f"正在抓取: {source}")
            articles = self.fetch_news_from_rss(source)
            all_articles.extend(articles)
        
        self.log_message(f"共获取 {len(all_articles)} 条相关新闻")
        
        # 分类新闻
        categorized_news = self.categorize_news(all_articles)
        
        # 生成摘要
        summary = self.generate_summary_with_deepseek(all_articles)
        
        # 生成Markdown报告
        markdown_report = self.generate_markdown_report(categorized_news, all_articles, summary)
        
        # 生成JSON数据
        json_data = self.generate_json_data(all_articles, categorized_news, summary)
        
        # 保存Markdown文件
        md_filename = f"news_daily_{datetime.now().strftime('%Y%m%d')}.md"
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        
        # 保存JSON文件（带时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = os.path.join(self.data_dir, f"news_data_{timestamp}.json")
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        # 同时保存一份最新的news_data.json用于仪表板默认加载
        latest_json_filename = os.path.join(self.data_dir, "news_data.json")
        with open(latest_json_filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        # 生成词云
        wordcloud_generator = WordCloudGenerator()
        wordcloud_filename = wordcloud_generator.generate_from_json(json_filename)
        self.log_message(f"词云已生成: {wordcloud_filename}")
        
        # 保存带时间戳的仪表板副本
        self.save_dashboard_copy()
        
        # 更新历史数据索引
        self.update_history_index()
        
        self.log_message(f"日报已生成: {md_filename}")
        self.log_message(f"JSON数据已生成: {json_filename}")
        return md_filename

    def save_dashboard_copy(self):
        """保存带时间戳的仪表板副本，方便分享"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dashboard_copy = f"news_dashboard_{timestamp}.html"
            
            # 复制仪表板文件
            shutil.copy2('news_dashboard.html', dashboard_copy)
            
            # 复制词云图片
            wordcloud_copy = f"wordcloud_{timestamp}.png"
            if os.path.exists('wordcloud.png'):
                shutil.copy2('wordcloud.png', wordcloud_copy)
            
            self.log_message(f"仪表板副本已保存: {dashboard_copy}")
            self.log_message(f"词云副本已保存: {wordcloud_copy}")
            
        except Exception as e:
            self.log_message(f"保存仪表板副本时出错: {e}")

    def update_history_index(self):
        """更新历史数据索引文件"""
        try:
            # 查找所有历史JSON文件
            history_files = []
            for filename in os.listdir(self.data_dir):
                if filename.startswith('news_data_') and filename.endswith('.json'):
                    # 从文件名提取时间戳
                    timestamp_str = filename.replace('news_data_', '').replace('.json', '')
                    try:
                        # 解析时间戳
                        file_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        history_files.append({
                            'filename': os.path.join(self.data_dir, filename),
                            'timestamp': timestamp_str,
                            'display_time': file_time.strftime("%Y年%m月%d日 %H:%M:%S")
                        })
                    except ValueError:
                        continue
            
            # 按时间戳降序排序
            history_files.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # 保存索引文件
            index_data = {
                'last_updated': datetime.now().strftime("%Y%m%d_%H%M%S"),
                'history_files': history_files
            }
            
            history_index_path = os.path.join(self.data_dir, 'history_index.json')
            with open(history_index_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
            
            self.log_message(f"历史数据索引已更新，共 {len(history_files)} 个文件")
            
        except Exception as e:
            self.log_message(f"更新历史数据索引时出错: {e}")

if __name__ == "__main__":
    crawler = NewsCrawler()
    
    # 测试新闻源可用性
    print("=== 新闻源可用性测试 ===")
    test_results = crawler.test_news_sources()
    
    # 只有有可用新闻源时才生成报告
    successful_sources = [s for s, r in test_results.items() if r['status'] == '成功']
    if successful_sources:
        print("\n=== 开始生成新闻日报 ===")
        crawler.crawl_and_generate_report()
    else:
        print("警告: 没有可用的新闻源，无法生成日报")