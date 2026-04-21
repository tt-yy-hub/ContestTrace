/**
 * 统计页面逻辑
 */

let allContests = [];

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', async function() {
    try {
        // 加载竞赛数据
        allContests = await loadContests();
        console.log('数据加载成功，共', allContests.length, '条竞赛');
        
        // 渲染统计信息
        renderStatistics();
    } catch (error) {
        console.error('初始化失败:', error);
    }
});

// 渲染统计信息
function renderStatistics() {
    const stats = loadStatistics(allContests);
    
    // 总竞赛数
    const totalContestsEl = document.getElementById('total-contests');
    if (totalContestsEl) {
        totalContestsEl.textContent = stats.total;
    }
    
    // 本月新增
    const monthlyContestsEl = document.getElementById('monthly-contests');
    if (monthlyContestsEl) {
        const now = new Date();
        const currentMonth = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0');
        monthlyContestsEl.textContent = stats.monthStats[currentMonth] || 0;
    }
    
    // 收藏总数
    const totalFavoritesEl = document.getElementById('total-favorites');
    if (totalFavoritesEl) {
        const favorites = loadFavorites();
        totalFavoritesEl.textContent = favorites.length;
    }
    
    // 即将截止的收藏数
    const upcomingDeadlinesEl = document.getElementById('upcoming-deadlines');
    if (upcomingDeadlinesEl) {
        const favorites = loadFavorites();
        const upcomingCount = favorites.filter(contest => {
            const daysLeft = calculateDaysLeft(contest.deadline);
            return daysLeft >= 0 && daysLeft <= 3;
        }).length;
        upcomingDeadlinesEl.textContent = upcomingCount;
    }
    
    // 绘制图表（按月份统计）
    const contestChartEl = document.getElementById('contest-chart');
    if (contestChartEl) {
        const ctx = contestChartEl.getContext('2d');
        
        // 准备图表数据（按月份）
        const monthLabels = Object.keys(stats.monthStats).sort();
        const monthData = monthLabels.map(month => stats.monthStats[month]);
        
        // 销毁之前的图表（如果存在）
        if (window.contestChart) {
            window.contestChart.destroy();
        }
        
        // 创建新图表
        window.contestChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: monthLabels.length > 0 ? monthLabels : ['无数据'],
                datasets: [{
                    label: '公告数量',
                    data: monthData.length > 0 ? monthData : [0],
                    backgroundColor: '#667eea',
                    borderColor: '#764ba2',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: '竞赛公告月份统计'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
    
    // 渲染热门竞赛榜单
    renderHotContests();
    
    // 生成词云
    generateKeywordCloud();
}

// 渲染热门竞赛榜单
function renderHotContests() {
    const container = document.getElementById('hot-contests-container');
    if (!container) return;
    
    // 获取热门竞赛
    const hotContests = getHotContests(10);
    
    if (hotContests.length === 0) {
        container.innerHTML = '<p class="no-data">暂无热门竞赛数据</p>';
        return;
    }
    
    // 渲染热门竞赛列表
    container.innerHTML = '';
    hotContests.forEach((contest, index) => {
        const card = document.createElement('div');
        card.className = 'hot-contest-card';
        card.innerHTML = `
            <div class="rank">${index + 1}</div>
            <div class="hot-contest-content">
                <h4><a href="#" class="contest-title">${contest.title}</a></h4>
                <p class="contest-source">${contest.source}</p>
                <p class="contest-deadline">${contest.deadline || '无截止日期'}</p>
                <div class="hotness">热度: ${contest.hotness}</div>
            </div>
        `;
        
        // 添加点击事件
        const titleLink = card.querySelector('.contest-title');
        titleLink.addEventListener('click', function(e) {
            e.preventDefault();
            openContestModal(contest);
        });
        
        container.appendChild(card);
    });
}

// 打开竞赛详情模态框
function openContestModal(contest) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'contest-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close">&times;</span>
            <h2 id="modal-title">${contest.title}</h2>
            <div class="modal-body">
                <div class="info-item">
                    <span class="label">来源：</span>
                    <span id="modal-source">${contest.source}</span>
                </div>
                <div class="info-item">
                    <span class="label">发布时间：</span>
                    <span id="modal-publish-time">${formatDate(contest.publish_time)}</span>
                </div>
                <div class="info-item">
                    <span class="label">截止时间：</span>
                    <span id="modal-deadline">${contest.deadline || '无'}</span>
                </div>
                <div class="info-item">
                    <span class="label">组织者：</span>
                    <span id="modal-organizer">${contest.organizer || '未知'}</span>
                </div>
                <div class="info-item">
                    <span class="label">参赛对象：</span>
                    <span id="modal-participants">${contest.participants || '未知'}</span>
                </div>
                <div class="info-item">
                    <span class="label">奖项设置：</span>
                    <span id="modal-prize">${contest.prize || '未知'}</span>
                </div>
                <div class="info-item">
                    <span class="label">联系方式：</span>
                    <span id="modal-contact">${contest.contact || '未知'}</span>
                </div>
                <div class="info-item">
                    <span class="label">原文链接：</span>
                    <div class="url-note-container">
                        <a id="modal-url" href="${contest.url}" target="_blank" class="url-btn-small">
                            <i class="fas fa-external-link-alt"></i> 查看原文
                        </a>
                        <p class="note">以上内容仅供参考，详情请查看原文</p>
                    </div>
                </div>
                <div class="info-item">
                    <span class="label">详细内容：</span>
                    <p id="modal-content">${contest.content || '无详细内容'}</p>
                </div>
                <div class="modal-actions">
                    <button id="favorite-btn" data-url="${contest.url}">
                        ${isFavorite(contest.url) ? '<i class="fas fa-star"></i> 取消收藏' : '<i class="far fa-star"></i> 收藏'}
                    </button>
                    <button id="like-btn">
                        <i class="far fa-thumbs-up"></i> 有用
                    </button>
                    <button id="dislike-btn">
                        <i class="far fa-thumbs-down"></i> 无用
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // 显示模态框
    modal.style.display = 'block';
    
    // 关闭按钮
    const closeBtn = modal.querySelector('.close');
    closeBtn.addEventListener('click', function() {
        modal.style.display = 'none';
        setTimeout(() => {
            document.body.removeChild(modal);
        }, 300);
    });
    
    // 点击模态框外部关闭
    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
            setTimeout(() => {
                document.body.removeChild(modal);
            }, 300);
        }
    });
    
    // 收藏按钮
    const favoriteBtn = modal.querySelector('#favorite-btn');
    favoriteBtn.addEventListener('click', function() {
        const contestUrl = this.dataset.url;
        toggleFavorite(contestUrl);
        this.innerHTML = isFavorite(contestUrl) ? '<i class="fas fa-star"></i> 取消收藏' : '<i class="far fa-star"></i> 收藏';
    });
    
    // 有用按钮
    const likeBtn = modal.querySelector('#like-btn');
    likeBtn.addEventListener('click', function() {
        alert('感谢您的反馈！');
    });
    
    // 无用按钮
    const dislikeBtn = modal.querySelector('#dislike-btn');
    dislikeBtn.addEventListener('click', function() {
        alert('感谢您的反馈，我们会不断改进！');
    });
}

// 词云相关功能

// 自定义词典
const customDictionary = [
    "市场调查与分析", "大学生创新创业", "计算机设计", "全国大学生", "湖北经济学院", "深入贯彻", "年度全国", "挑战杯", "互联网+", "蓝桥杯", "数学建模", "正大杯", "藏龙杯", "华章杯",
    "创新大赛", "计算机设计大赛", "统计建模大赛", "米兰设计周", "浩然杯", "世纪杯", "健康之星心理", "传承红色基因", "续写青春华章", "企业决策赛道", "企业运营赛道"
];

// 超级停用词表
const stopWords = {
    school: ["湖北", "经济", "学院", "大学", "我校", "本校", "各学院", "教务处", "学生处", "团委", "学生会"],
    official: ["关于", "通知", "决定", "要求", "现将", "如下", "特此", "为深入", "贯彻", "落实", "开展", "举办", "举行", "组织", "参加"],
    general: ["简介", "说明", "办法", "规定", "流程", "时间", "地点", "对象", "要求", "报名", "参赛", "提交", "作品"],
    person: ["学生", "教师", "老师", "同学", "本科生", "研究生", "专科生", "负责人", "联系人"],
    meaningless: ["的", "了", "在", "是", "有", "和", "与", "或", "但", "而", "也", "都", "就", "被", "把", "我", "不", "这", "那", "它", "她", "他", "我们", "你们", "他们", "它们", "这个", "那个", "这些", "那些", "一些", "每个", "一个", "没有", "可以", "需要", "已经", "将会", "并且", "或者", "如果", "因为", "所以", "但是", "虽然", "然而", "而且", "还有", "另外", "总之", "也就是说", "事实上", "基本上", "大约", "左右", "上下", "以内", "以外", "之间", "之中", "之后", "之前", "之上", "之下", "之内", "之外"],
    award: ["一等奖", "二等奖", "三等奖", "优秀奖", "国家级", "省级"],
    structure: ["附件", "序号", "图片", "姓名", "分钟"],
    news: ["本网讯", "通讯员"]
};

// 合并所有停用词
const allStopWords = [].concat(
    stopWords.school,
    stopWords.official,
    stopWords.general,
    stopWords.person,
    stopWords.meaningless,
    stopWords.award,
    stopWords.structure,
    stopWords.news
);

// 竞赛特定词（额外权重）
const contestSpecificWords = ["挑战杯", "互联网+", "蓝桥杯", "数学建模", "正大杯", "藏龙杯"];

// 通用词（降低权重）
const commonWords = ["大赛", "竞赛", "比赛"];

// 智能分词函数
function smartTokenize(text) {
    let words = [];
    
    try {
        // 首先检查自定义词典中的专有名词
        customDictionary.forEach(term => {
            if (text.includes(term)) {
                words.push(term);
            }
        });
        
        // 使用 cnchar 进行分词
        if (window.cnchar && window.cnchar.segment) {
            const cncharWords = window.cnchar.segment(text, {
                type: 'all',
                combine: true
            });
            
            // 合并词典词和分词结果，去重
            words = [...new Set([...words, ...cncharWords])];
        } else {
            // 降级为正则提取
            const regexWords = text.match(/[\u4e00-\u9fa5]{2,6}/g) || [];
            words = [...new Set([...words, ...regexWords])];
        }
    } catch (error) {
        console.error('分词失败，使用正则提取:', error);
        // 降级为正则提取
        const regexWords = text.match(/[\u4e00-\u9fa5]{2,6}/g) || [];
        words = [...new Set([...words, ...regexWords])];
    }
    
    // 过滤
    return words.filter(word => {
        // 过滤长度<2或>8的词
        if (word.length < 2 || word.length > 8) return false;
        
        // 过滤包含停用词的词
        if (allStopWords.some(stopWord => word.includes(stopWord))) return false;
        
        // 过滤纯数字和包含数字的词
        if (/\d/.test(word)) return false;
        
        return true;
    });
}

// 词频统计和权重计算
function calculateWordWeights(contests) {
    const wordWeights = {};
    
    console.log('开始计算词频，竞赛数量:', contests.length);
    
    contests.forEach((contest, index) => {
        // 提取标题和内容
        const title = contest.title || '';
        const content = contest.content || '';
        
        // 标题分词（权重×5）- 提高标题权重
        const titleWords = smartTokenize(title);
        titleWords.forEach(word => {
            wordWeights[word] = (wordWeights[word] || 0) + 5;
        });
        
        // 内容分词（权重×0.5）- 降低内容权重
        const contentWords = smartTokenize(content);
        contentWords.forEach(word => {
            wordWeights[word] = (wordWeights[word] || 0) + 0.5;
        });
        
        // 每100个竞赛输出一次进度
        if ((index + 1) % 100 === 0) {
            console.log(`已处理 ${index + 1}/${contests.length} 个竞赛`);
        }
    });
    
    console.log('分词完成，唯一词数量:', Object.keys(wordWeights).length);
    
    // 应用额外权重
    Object.keys(wordWeights).forEach(word => {
        if (contestSpecificWords.includes(word)) {
            wordWeights[word] *= 2;
        } else if (commonWords.includes(word)) {
            wordWeights[word] *= 0.5;
        }
    });
    
    // 过滤出现次数≥2的词（降低门槛）
    const filteredWeights = Object.entries(wordWeights)
        .filter(([_, weight]) => weight >= 2)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 30);
    
    console.log('过滤后的关键词数量:', filteredWeights.length);
    console.log('前10个关键词:', filteredWeights.slice(0, 10));
    
    return filteredWeights.map(([word, weight]) => ({ text: word, weight }));
}

// 词云生成函数
function generateWordCloud(words) {
    const container = document.getElementById('keyword-cloud');
    if (!container) {
        console.error('词云容器未找到');
        return;
    }
    
    // 清空容器
    container.innerHTML = '';
    
    // 检查 WordCloud 库是否加载
    if (typeof WordCloud === 'undefined') {
        console.error('WordCloud 库未加载，使用备用方案');
        generateCSSWordCloud(words);
        return;
    }
    
    // 检查是否有数据
    if (!words || words.length === 0) {
        console.warn('词云数据为空');
        container.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">暂无关键词数据</p>';
        return;
    }
    
    console.log('开始生成词云，关键词数量:', words.length);
    
    // 颜色方案 - 柔和的莫兰迪色系
    const colors = ['#4a7c80', '#6b9e9f', '#7fb0b1', '#98c1c2', '#b0d4d5', '#3a6b6e', '#5a8f91', '#2c5a5c'];
    
    // 转换数据格式为 WordCloud 需要的格式
    const wordList = words.map(word => [word.text, word.weight]);
    
    try {
        // 生成词云
        WordCloud(container, {
            list: wordList,
            gridSize: 12,
            weightFactor: function(size) {
                return Math.min(Math.max(Math.floor(size * 0.6) + 14, 14), 42);
            },
            fontFamily: 'Segoe UI, Microsoft YaHei, sans-serif',
            color: function() {
                return colors[Math.floor(Math.random() * colors.length)];
            },
            rotateRatio: 0,
            rotationSteps: 2,
            backgroundColor: '#ffffff',
            shape: 'circle',
            ellipticity: 0.7,
            shrinkToFit: true,
            drawOutOfBound: false,
            hover: function(item, dimension, event) {
                container.style.cursor = 'pointer';
            },
            click: function(item, dimension, event) {
                // 点击词云里的词搜索对应竞赛
                const keyword = item[0];
                sessionStorage.setItem('cloud_search_keyword', keyword);
                window.location.href = 'index.html';
            }
        });
    } catch (error) {
        console.error('WordCloud 生成失败，使用备用方案:', error);
        generateCSSWordCloud(words);
    }
}

// 备用方案：CSS 标签云
function generateCSSWordCloud(words) {
    const container = document.getElementById('keyword-cloud');
    if (!container) return;
    
    // 清空容器
    container.innerHTML = '';
    
    // 检查是否有数据
    if (!words || words.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">暂无关键词数据</p>';
        return;
    }
    
    // 颜色方案 - 明亮但专业的色系
    const colors = ['#2193b0', '#4a90e2', '#5dade2', '#6ab0de', '#8e44ad', '#d35400', '#e67e22', '#2ecc71'];
    
    // 计算最大权重和最小权重
    const maxWeight = Math.max(...words.map(w => w.weight));
    const minWeight = Math.min(...words.map(w => w.weight));
    
    // 创建标签云容器
    const cloudContainer = document.createElement('div');
    cloudContainer.style.cssText = 'display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 10px; padding: 20px;';
    
    // 创建每个关键词标签
    words.forEach(word => {
        const span = document.createElement('span');
        span.className = 'cloud-word';
        span.textContent = word.text;
        span.dataset.keyword = word.text;
        
        // 随机选择颜色
        const color = colors[Math.floor(Math.random() * colors.length)];
        
        // 计算字体大小（14px - 48px）
        const fontSize = 14 + ((word.weight - minWeight) / (maxWeight - minWeight || 1)) * 34;
        
        span.style.cssText = `
            font-size: ${fontSize}px;
            font-weight: bold;
            color: ${color};
            background: transparent;
            padding: 6px 12px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-block;
            margin: 5px;
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
        `;
        
        // 添加悬停效果
        span.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
            this.style.textShadow = '0 2px 8px rgba(0,0,0,0.2)';
        });
        
        span.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.textShadow = 'none';
        });
        
        // 添加点击事件
        span.addEventListener('click', function() {
            const keyword = this.dataset.keyword;
            sessionStorage.setItem('cloud_search_keyword', keyword);
            window.location.href = 'index.html';
        });
        
        cloudContainer.appendChild(span);
    });
    
    container.appendChild(cloudContainer);
}

// 生成词云
async function generateKeywordCloud() {
    try {
        console.log('开始生成关键词云');
        
        // 清除旧缓存
        const cacheKey = 'wordcloud_cache';
        localStorage.removeItem(cacheKey);
        
        // 检查是否有竞赛数据
        if (!allContests || allContests.length === 0) {
            console.warn('没有竞赛数据，无法生成词云');
            const container = document.getElementById('keyword-cloud');
            if (container) {
                container.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">暂无竞赛数据</p>';
            }
            return;
        }
        
        // 计算词频和权重
        const words = calculateWordWeights(allContests);
        
        // 生成词云
        generateWordCloud(words);
        
    } catch (error) {
        console.error('生成词云失败:', error);
        const container = document.getElementById('keyword-cloud');
        if (container) {
            container.innerHTML = '<p style="text-align: center; color: #f56c6c; padding: 20px;">词云生成失败，请刷新页面重试</p>';
        }
    }
}

// 当竞赛数据更新时重新生成词云
function updateWordCloud() {
    generateKeywordCloud();
}