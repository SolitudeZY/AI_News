// 主题管理
let currentTheme = 'light';

// 切换主题
function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    // 更新主题图标
    const themeIcon = document.querySelector('.theme-toggle i');
    if (themeIcon) {
        themeIcon.className = currentTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// 初始化主题
function initTheme() {
    currentTheme = 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    // 设置主题图标
    const themeIcon = document.querySelector('.theme-toggle i');
    if (themeIcon) {
        themeIcon.className = 'fas fa-moon';
    }
}

// 新闻数据和统计
let newsData = [];
let categoryStats = {};

// 加载AI总结
async function loadAISummary() {
    const summaryElement = document.getElementById('aiSummaryContent');
    if (!summaryElement) return;
    
    try {
        const response = await fetch('news_data.json');
        if (response.ok) {
            const data = await response.json();
            let summary = '';
            
            // 检查数据格式并提取summary
            if (data && typeof data.summary === 'string') {
                summary = data.summary;
            } else if (data && data.news && typeof data.news.summary === 'string') {
                summary = data.news.summary;
            } else {
                summary = '未找到AI总结内容。';
            }
            
            // 更新显示
            summaryElement.innerHTML = `<p>${summary}</p>`;
            
            logError('从本地加载AI总结成功');
        } else {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
    } catch (error) {
        logError(`加载AI总结失败: ${error.message}`);
        summaryElement.innerHTML = `<p style="color: var(--error-color);">加载AI总结失败: ${error.message}</p>`;
    }
}

// 加载新闻数据（修改为支持两种存储模式）
async function loadNewsData() {
    const storageMode = localStorage.getItem('newsDashboardStorageMode') || 'local';
    
    if (storageMode === 'browser') {
        loadDataFromBrowserStorage();
        return;
    }
    
    // 原有本地存储逻辑
    showLoading();
    let retries = 3;
    
    while (retries > 0) {
        try {
            const response = await fetch('news_data.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            // 处理两种数据格式：数组或包含news数组的对象
            if (Array.isArray(data)) {
                newsData = data;
            } else if (data && Array.isArray(data.news)) {
                newsData = data.news;
            } else {
                throw new Error('无效的数据格式，期望数组或包含news数组的对象');
            }
            updateStatistics();
            renderNewsContent();
            updateChart();
            
            logError('新闻数据加载成功');
            break;
        } catch (error) {
            retries--;
            if (retries === 0) {
                logError(`加载新闻数据失败: ${error.message}`);
                document.getElementById('newsContent').innerHTML = `
                    <div style="text-align: center; padding: 40px; color: var(--text-secondary);">
                        <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 20px;"></i>
                        <p>加载新闻数据失败</p>
                        <p style="font-size: 0.9rem; margin-top: 10px;">${error.message}</p>
                        <button onclick="loadNewsData()" style="margin-top: 15px; padding: 8px 16px; background: var(--primary-color); color: white; border: none; border-radius: 4px; cursor: pointer;">重试</button>
                    </div>
                `;
            } else {
                logError(`加载新闻数据失败，剩余重试次数: ${retries}`);
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化主题
    initTheme();
    
    // 加载AI总结
    loadAISummary();
    
    // 加载历史索引
    loadHistoryIndex();
    
    // 加载词云
    loadWordcloud();
    
    // 绑定词云刷新按钮事件
    document.getElementById('refreshWordcloud').addEventListener('click', refreshWordcloud);
    
    // 设置初始存储模式
    const storageSelect = document.getElementById('storageSelect');
    if (storageSelect) {
        storageSelect.value = 'local';
    }
    document.getElementById('loading').style.display = 'none';
});

// 错误日志记录
function logError(message, level = 'error') {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
    console.log(logEntry);
    
    // 保存到localStorage供调试
    try {
        const existingLogs = localStorage.getItem('newsDashboardLogs') || '[]';
        const logs = JSON.parse(existingLogs);
        logs.push(logEntry);
        // 只保留最近100条日志
        if (logs.length > 100) {
            logs.splice(0, logs.length - 100);
        }
        localStorage.setItem('newsDashboardLogs', JSON.stringify(logs));
    } catch (e) {
        console.error('保存日志失败:', e);
    }
}

// 刷新新闻
function refreshNews() {
    loadNewsData();
}

// 显示/隐藏加载状态
function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}

// 更新统计数据
function updateStatistics() {
    document.getElementById('totalNews').textContent = newsData.length;
    
    // 计算新闻源数量
    const sources = new Set(newsData.map(item => item.source));
    document.getElementById('sourceCount').textContent = sources.size;
    
    // 更新时间
    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString('zh-CN');
}

// 渲染新闻内容
function renderNewsContent() {
    const newsContent = document.getElementById('newsContent');
    
    if (newsData.length === 0) {
        newsContent.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 40px;">暂无新闻数据</div>';
        return;
    }

    // 按类别分组
    const categories = {};
    newsData.forEach(item => {
        if (!categories[item.category]) {
            categories[item.category] = [];
        }
        categories[item.category].push(item);
    });

    let html = '';
    Object.keys(categories).forEach(category => {
        html += `
            <div class="news-section">
                <h2>${category}</h2>
                ${categories[category].map(item => `
                    <div class="news-item">
                        <div class="news-header">
                            <div class="news-title" onclick="openNewsDetailModal('${item.id}')">${item.title}</div>
                            <button class="toggle-details-btn" onclick="toggleNewsDetails(this)">展开</button>
                        </div>
                        <div class="news-meta">
                            <span class="news-source">${getSourceName(item.source)}</span>
                            <span class="news-time">${formatTime(item.published)}</span>
                        </div>
                        <div class="news-summary">${item.summary || (item.description ? item.description.substring(0, 150) + '...' : '')}</div>
                        <div class="news-details" style="display: none;">
                            <a href="${item.link}" target="_blank" class="view-original-btn">查看原文</a>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    });

    newsContent.innerHTML = html;
}

function toggleNewsDetails(button) {
    const newsItem = button.closest('.news-item');
    const details = newsItem.querySelector('.news-details');
    if (details.style.display === 'none') {
        details.style.display = 'block';
        button.textContent = '收起';
    } else {
        details.style.display = 'none';
        button.textContent = '展开';
    }
}

function openNewsDetailModal(newsId) {
    const newsData = window.currentNewsData.find(news => news.id === newsId);
    if (!newsData) {
        console.error('News data not found for ID:', newsId);
        return;
    }

    const modal = document.getElementById('newsDetailModal');
    document.getElementById('modal-news-title').textContent = newsData.title;
    document.getElementById('modal-news-source').textContent = newsData.source;
    document.getElementById('modal-news-time').textContent = newsData.pubDate;
    
    const modalImage = document.getElementById('modal-news-image');
    if (newsData.image) {
        modalImage.src = newsData.image;
        modalImage.style.display = 'block';
    } else {
        modalImage.style.display = 'none';
    }

    document.getElementById('modal-news-summary').textContent = newsData.summary;
    document.getElementById('modal-news-full-content').innerHTML = newsData.fullContent || '暂无详细内容。';
    document.getElementById('modal-news-original-link').href = newsData.link;

    modal.style.display = 'block';
    document.body.classList.add('modal-open'); // Prevent scrolling background
}

function closeNewsDetailModal() {
    const modal = document.getElementById('newsDetailModal');
    modal.style.display = 'none';
    document.body.classList.remove('modal-open');
}

// Add event listener to close button
document.addEventListener('DOMContentLoaded', () => {
    const closeButton = document.querySelector('.news-detail-modal .close-button');
    if (closeButton) {
        closeButton.addEventListener('click', closeNewsDetailModal);
    }
    // ... existing code ...
});

// 获取新闻源名称
function getSourceName(sourceUrl) {
    const sourceMap = {
        'https://www.36kr.com/feed': '36氪',
        'https://rss.thepaper.cn/feed': '澎湃新闻',
        'https://www.jiemian.com/lists/5.xml': '界面新闻',
        'https://www.yicai.com/feed': '第一财经',
        'https://rss.caixin.com/markets/finance': '财新网',
        'https://www.huxiu.com/rss/0.xml': '虎嗅网',
        'https://www.tmtpost.com/rss.xml': '钛媒体',
        'https://feeds.bbci.co.uk/news/rss.xml': 'BBC',
        'https://techcrunch.com/feed/': 'TechCrunch',
        'https://www.wired.com/feed/rss': 'Wired',
        'https://www.ft.com/rss/home': 'Financial Times',
        'https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml': 'NY Times',
        'https://feeds.npr.org/1004/rss.xml': 'NPR',
        'https://www.theguardian.com/international/rss': 'The Guardian',
        'https://feeds.arstechnica.com/arstechnica/index': 'Ars Technica'
    };
    return sourceMap[sourceUrl] || sourceUrl;
}

// 格式化时间
function formatTime(timeString) {
    if (!timeString) return '未知时间';
    try {
        const date = new Date(timeString);
        return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit'});
    } catch (e) {
        return timeString;
    }
}

// 更新图表
function updateChart() {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    // 计算类别统计
    categoryStats = {};
    newsData.forEach(item => {
        categoryStats[item.category] = (categoryStats[item.category] || 0) + 1;
    });

    // 准备图表数据
    const labels = Object.keys(categoryStats);
    const data = Object.values(categoryStats);
    
    // 颜色配置
    const colors = [
        '#3b82f6', '#ef4444', '#10b981', '#f59e0b', 
        '#8b5cf6', '#06b6d4', '#f97316', '#84cc16'
    ];

    // 销毁旧图表实例（如果存在）
    if (window.categoryChartInstance) {
        window.categoryChartInstance.destroy();
    }

    // 创建新图表
    window.categoryChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: getComputedStyle(document.documentElement).getPropertyValue('--background-color')
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false // 隐藏内置图例，使用自定义图例
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });

    // 更新自定义图例
    updateChartLegend(labels, data, colors);
}

// 更新自定义图例
function updateChartLegend(labels, data, colors) {
    const legendContainer = document.getElementById('chartLegend');
    const total = data.reduce((a, b) => a + b, 0);
    
    let legendHTML = '';
    labels.forEach((label, index) => {
        const value = data[index];
        const percentage = Math.round((value / total) * 100);
        legendHTML += `
            <div class="legend-item" style="display: flex; align-items: center; margin-bottom: 8px; font-size: 12px;">
                <span class="legend-color" style="display: inline-block; width: 12px; height: 12px; background-color: ${colors[index]}; border-radius: 50%; margin-right: 8px;"></span>
                <span class="legend-label" style="flex: 1; color: var(--text-primary);">${label}</span>
                <span class="legend-value" style="color: var(--text-secondary);">${value} (${percentage}%)</span>
            </div>
        `;
    });
    
    legendContainer.innerHTML = legendHTML;
}

// 切换大纲视图
function toggleOutlineView() {
    const chartCard = document.querySelector('.chart-card');
    const chartContainer = document.querySelector('.chart-container');
    const legendContainer = document.getElementById('chartLegend');
    const outlineToggle = document.querySelector('.outline-toggle');
    
    chartCard.classList.toggle('outline-view');
    chartContainer.classList.toggle('large');
    
    if (chartCard.classList.contains('outline-view')) {
        outlineToggle.textContent = '详细';
        legendContainer.style.display = 'none';
        // 在大纲视图中显示简化信息
        const totalNews = newsData.length;
        const mainCategories = Object.entries(categoryStats)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3);
        
        let outlineHTML = '<div style="text-align: center; padding: 20px; color: var(--text-primary);">';
        outlineHTML += `<h4 style="margin-bottom: 15px;">主要分类</h4>`;
        mainCategories.forEach(([category, count]) => {
            const percentage = Math.round((count / totalNews) * 100);
            outlineHTML += `<div style="margin: 8px 0; font-size: 14px;">${category}: ${percentage}%</div>`;
        });
        outlineHTML += `</div>`;
        
        legendContainer.innerHTML = outlineHTML;
        legendContainer.style.display = 'block';
    } else {
        outlineToggle.textContent = '大纲';
        legendContainer.style.display = 'block';
        updateChart(); // 重新渲染完整图例
    }
}

// 自动排版功能
function autoLayout() {
    const newsItems = document.querySelectorAll('.news-item');
    newsItems.forEach(item => {
        // 根据内容长度调整样式
        const title = item.querySelector('.news-title');
        if (title.textContent.length > 100) {
            title.style.fontSize = '1rem';
        }
    });
}

// 加载词云
function loadWordcloud() {
    const wordcloudImage = document.getElementById('wordcloudImage');
    wordcloudImage.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">正在加载词云...</p>';
    
    // 添加时间戳避免缓存
    const timestamp = new Date().getTime();
    const img = new Image();
    img.src = 'wordcloud.png?' + timestamp;
    img.alt = '新闻词云';
    img.style.maxWidth = '100%';
    img.style.height = 'auto';
    img.style.borderRadius = '8px';
    
    img.onload = function() {
        wordcloudImage.innerHTML = '';
        wordcloudImage.appendChild(img);
    };
    
    img.onerror = function() {
        wordcloudImage.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">词云图像加载失败</p>';
    };
}

// 刷新词云
function refreshWordcloud() {
    loadWordcloud();
}

// 加载历史数据索引
let currentChart; // 用于存储当前的Chart实例

// 加载历史数据索引并填充下拉菜单
async function loadHistoryIndex() {
    try {
        const response = await fetch('data/history_index.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const historyIndex = await response.json();
        const historySelect = document.getElementById('historySelect');
        historySelect.innerHTML = '<option value="">选择历史数据</option>'; // 清空并添加默认选项

        historyIndex.history_files.forEach(file => {
            const option = document.createElement('option');
            option.value = file.filename.replace(/\\/g, '/');
            option.textContent = file.display_time;
            historySelect.appendChild(option);
        });

        // 默认加载最新的数据
        if (historyIndex.history_files.length > 0) {
            const latestFile = historyIndex.history_files[0].filename.replace(/\\/g, '/');
            historySelect.value = latestFile;
            await loadNewsData(latestFile);
        } else {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('newsContent').innerHTML = '<p>没有可用的历史新闻数据。</p>';
        }

    } catch (error) {
        console.error('加载历史数据索引失败:', error);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('newsContent').innerHTML = '<p>加载历史数据失败，请检查控制台。</p>';
    }
}

// 根据选择加载新闻数据
async function loadNewsData(jsonPath) {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('newsContent').innerHTML = ''; // 清空旧内容
    document.getElementById('aiSummaryContent').innerHTML = '<p>正在加载AI总结...</p>';
    document.getElementById('totalNews').textContent = '0';
    document.getElementById('sourceCount').textContent = '0';
    document.getElementById('lastUpdate').textContent = '-';
    document.getElementById('wordcloudImage').innerHTML = '<p>词云正在生成中...</p>';


<<<<<<< Updated upstream
    try {
        console.log('正在加载的新闻数据路径:', jsonPath); // 新增日志查看路径
        const response = await fetch(jsonPath);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
=======
    let retries = 3;
    
    while (retries > 0) {
        try {
            console.log('正在加载的新闻数据路径:', jsonPath); // 新增日志查看路径
            const response = await fetch(jsonPath);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            renderDashboard(data);
            logError('新闻数据加载成功');
            break;
        } catch (error) {
            retries--;
            if (retries === 0) {
                logError(`加载新闻数据失败: ${error.message}`);
                document.getElementById('newsContent').innerHTML = `
                    <div style="text-align: center; padding: 40px; color: var(--text-secondary);">
                        <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 20px;"></i>
                        <p>加载新闻数据失败</p>
                        <p style="font-size: 0.9rem; margin-top: 10px;">${error.message}</p>
                        <button onclick="loadNewsData()" style="margin-top: 15px; padding: 8px 16px; background: var(--primary-color); color: white; border: none; border-radius: 4px; cursor: pointer;">重试</button>
                    </div>
                `;
            } else {
                logError(`加载新闻数据失败，剩余重试次数: ${retries}`);
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
>>>>>>> Stashed changes
        }
    }
    document.getElementById('loading').style.display = 'none';
}

// 渲染仪表板
function renderDashboard(data) {
    // 渲染AI总结
    document.getElementById('aiSummaryContent').innerHTML = `<p>${data.summary || '暂无AI总结。'}</p>`;

    // 渲染统计数据
    document.getElementById('totalNews').textContent = data.statistics.total_news;
    document.getElementById('sourceCount').textContent = data.statistics.sources_count;
    document.getElementById('lastUpdate').textContent = new Date(data.statistics.last_updated).toLocaleString();

    // 渲染新闻列表
    const newsContent = document.getElementById('newsContent');
    newsContent.innerHTML = ''; // 清空旧内容

    for (const category in data.categorized_news) {
        if (data.categorized_news.hasOwnProperty(category)) {
            const categorySection = document.createElement('div');
            categorySection.className = 'category-section';
            categorySection.innerHTML = `<h3>${category}</h3>`;

            data.categorized_news[category].forEach(article => {
                const articleElement = document.createElement('div');
                articleElement.className = 'news-article';
                articleElement.innerHTML = `
                    <h4><a href="${article.link}" target="_blank">${article.title}</a></h4>
                    <p class="news-meta">来源: ${article.source} | 发布时间: ${article.published ? new Date(article.published).toLocaleString() : '未知'}</p>
                    <p>${article.description || ''}</p>
                `;
                categorySection.appendChild(articleElement);
            });
            newsContent.appendChild(categorySection);
        }
    }

    // 渲染饼状图
    renderCategoryChart(data.statistics.categories_distribution);

    // 渲染词云图
    renderWordCloud(data.statistics.last_updated);
}

// 渲染新闻分类饼状图
function renderCategoryChart(categoriesDistribution) {
    try {
        const ctx = document.getElementById('categoryChart').getContext('2d');
        if (!ctx) {
            console.error('饼状图画布元素未找到');
            return;
        }

        // 验证数据格式
        if (!categoriesDistribution || typeof categoriesDistribution !== 'object' || Object.keys(categoriesDistribution).length === 0) {
            console.warn('饼状图数据为空或格式不正确');
            document.getElementById('categoryChart').innerHTML = '<p style="text-align: center; color: var(--text-secondary);">暂无分类数据</p>';
            return;
        }

        // 如果存在旧图表实例，则销毁它
        if (currentChart) {
            currentChart.destroy();
        }

        const labels = Object.keys(categoriesDistribution);
        const values = Object.values(categoriesDistribution);
        
        // 确保所有值都是数字
        const numericValues = values.map(val => Number(val) || 0);
        
        const backgroundColors = generateRandomColors(labels.length);

        currentChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: numericValues,
                    backgroundColor: backgroundColors,
                    borderColor: '#fff',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false // 隐藏默认图例
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed !== null) {
                                    label += context.parsed;
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });

        // 生成自定义图例
        generateCustomLegend(labels, numericValues, backgroundColors);
    } catch (error) {
        console.error('饼状图渲染失败:', error);
        document.getElementById('categoryChart').innerHTML = '<p style="text-align: center; color: var(--text-secondary);">图表加载失败</p>';
    }
}

// 生成自定义图例
function generateCustomLegend(labels, values, colors) {
    const legendContainer = document.getElementById('chartLegend');
    legendContainer.innerHTML = ''; // 清空旧图例

    labels.forEach((label, index) => {
        const legendItem = document.createElement('div');
        legendItem.className = 'chart-legend-item';
        legendItem.innerHTML = `
            <span class="legend-color" style="background-color: ${colors[index]}"></span>
            <span class="legend-label">${label} (${values[index]})</span>
        `;
        legendContainer.appendChild(legendItem);
    });
}

// 生成随机颜色
function generateRandomColors(num) {
    const colors = [];
    for (let i = 0; i < num; i++) {
        const hue = (i * 137.508) % 360; // 使用黄金比例共轭来生成颜色
        colors.push(`hsl(${hue}, 70%, 60%)`);
    }
    return colors;
}

// 渲染词云图
function renderWordCloud(timestamp) {
    try {
        const wordcloudImageDiv = document.getElementById('wordcloudImage');
        if (!wordcloudImageDiv) {
            console.error('词云图容器元素未找到');
            return;
        }

        // 验证时间戳格式
        if (!timestamp || typeof timestamp !== 'string') {
            console.warn('词云图时间戳格式不正确');
            timestamp = new Date().toISOString().replace(/[-T:]/g, '').split('.')[0];
        }

        // 假设词云图片命名规则为 wordcloud_YYYYMMDD_HHMMSS.png
        // 或者直接使用 news_crawler.py 生成的 wordcloud.png
        const wordcloudPath = `word_cloud/wordcloud_${timestamp.replace(/[-T:]/g, '')}.png`;
        
        // 显示加载状态
        wordcloudImageDiv.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">加载词云图...</p>';
        
        // 检查文件是否存在，如果不存在则使用默认的 wordcloud.png
        // 实际部署时，可能需要后端接口来确认文件是否存在
        const img = new Image();
        img.onload = () => {
            wordcloudImageDiv.innerHTML = `<img src="${wordcloudPath}" alt="新闻词云" style="max-width: 100%; height: auto;">`;
        };
        img.onerror = () => {
            // 如果带时间戳的词云不存在，尝试加载默认的 wordcloud.png
            const defaultPath = 'word_cloud/wordcloud.png';
            const fallbackImg = new Image();
            fallbackImg.onload = () => {
                wordcloudImageDiv.innerHTML = `<img src="${defaultPath}" alt="新闻词云" style="max-width: 100%; height: auto;">`;
            };
            fallbackImg.onerror = () => {
                wordcloudImageDiv.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">词云图加载失败</p>';
                console.error('词云图加载失败，路径：', wordcloudPath, '和', defaultPath);
            };
            fallbackImg.src = defaultPath;
        };
        img.src = wordcloudPath;
    } catch (error) {
        console.error('词云图渲染失败:', error);
        const wordcloudImageDiv = document.getElementById('wordcloudImage');
        if (wordcloudImageDiv) {
            wordcloudImageDiv.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">词云图加载失败</p>';
        }
    }
}

// 刷新新闻 (重新加载最新数据)
async function refreshNews() {
    document.getElementById('loading').style.display = 'block';
    // 重新加载历史索引，它会自动加载最新的数据
    await loadHistoryIndex();
    document.getElementById('loading').style.display = 'none';
}

// 切换主题
function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    const themeIcon = document.querySelector('.theme-toggle i');
    if (document.body.classList.contains('dark-mode')) {
        themeIcon.className = 'fas fa-sun'; // 切换到太阳图标
    } else {
        themeIcon.className = 'fas fa-moon'; // 切换到月亮图标
    }
}

// 保存为PDF (使用浏览器打印功能)
document.getElementById('savePdfBtn').addEventListener('click', () => {
    // 显示生成进度提示
    alert('正在生成PDF，请等待打印对话框打开...');
    // 使用浏览器打印功能生成PDF
    window.print();
});

// 历史数据选择器事件监听
document.getElementById('historySelect').addEventListener('change', async (event) => {
    const selectedFilePath = event.target.value;
    if (selectedFilePath) {
        await loadNewsData(selectedFilePath);
    }
});

// 初始加载
document.addEventListener('DOMContentLoaded', () => {
    loadHistoryIndex();
});