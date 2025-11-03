# AI新闻爬虫系统

## 功能特性

- 从多个国内外新闻源自动抓取新闻
- 基于关键词过滤和分类新闻
- 集成DeepSeek大语言模型生成新闻摘要
- 生成格式化的Markdown日报

## 系统功能特性

### 新闻源监控与测试
- 自动测试所有新闻源的可用性
- 详细的抓取日志记录在 `news_crawler_log_YYYYMMDD.txt`
- 3次重试机制，提高抓取成功率

### 智能过滤与分类
- 支持60+个中英文关键词过滤
- 自动分类新闻到相关主题
- 可自定义关键词和新闻源

### 深度集成AI摘要
- 使用DeepSeek大模型生成300-500字中文摘要
- 摘要包含整体趋势分析和关键洞察
- 环境变量缺失时提供明确错误提示

## 安装依赖

```bash
pip install requests newspaper3k beautifulsoup4 lxml feedparser lxml_html_clean
```

## 配置DeepSeek API

要启用新闻摘要生成功能，需要设置DeepSeek API密钥：

### Windows系统

1. **临时设置（当前会话有效）**：
   ```cmd
   set DEEPSEEK_API_KEY=your_api_key_here
   ```

2. **永久设置**：
   - 右键点击"此电脑" → "属性" → "高级系统设置"
   - 点击"环境变量"
   - 在"用户变量"或"系统变量"中点击"新建"
   - 变量名：`DEEPSEEK_API_KEY`
   - 变量值：您的DeepSeek API密钥

### 验证环境变量设置
运行以下命令验证环境变量是否设置成功：
```cmd
echo %DEEPSEEK_API_KEY%
```
如果显示您的API密钥，则设置成功。如果显示 `%DEEPSEEK_API_KEY%`，则设置未生效。

### 获取API密钥

1. 访问 [DeepSeek开放平台](https://platform.deepseek.com/)
2. 注册账号并登录
3. 在控制台中创建API密钥
4. 复制密钥并设置为环境变量

## 使用方法

1. 安装依赖：
   ```bash
   pip install requests newspaper3k beautifulsoup4 lxml feedparser lxml_html_clean
   ```

2. 设置DeepSeek API密钥（可选，用于生成摘要）：
   ```cmd
   set DEEPSEEK_API_KEY=your_api_key_here
   ```

3. 运行新闻爬虫：
   ```bash
   python news_crawler.py
   ```

4. 系统会自动：
   - 测试所有新闻源可用性
   - 抓取并过滤相关新闻
   - 生成AI摘要（如果设置了API密钥）
   - 创建Markdown格式的日报文件

5. 查看生成的文件：
   - 日报文件：`news_daily_YYYYMMDD.md`
   - 日志文件：`news_crawler_log_YYYYMMDD.txt`

## 故障排除

### 常见问题

**问题1：某些新闻源返回0条新闻**
- 原因：新闻源可能暂时不可用或需要特殊访问权限
- 解决方案：系统已自动移除有问题的新闻源，保留稳定可用的源

**问题2：DeepSeek API密钥未生效**
- 验证：运行 `echo %DEEPSEEK_API_KEY%`
- 解决方案：重启命令行或IDE，或使用临时设置方法

**问题3：网络连接问题**
- 系统已内置3次重试机制
- 检查网络连接和防火墙设置

## 自定义配置

可在 `news_crawler.py` 中修改：
- `keywords` - 关键词列表
- `news_sources` - 新闻源列表
- 摘要生成提示词

## 注意事项

- 确保网络连接正常以访问新闻源和API
- API调用可能产生费用，请关注使用量
- 程序会自动跳过无法访问的新闻源