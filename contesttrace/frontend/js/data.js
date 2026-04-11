/**
 * 数据处理
 */

// 模拟数据
const mockContests = [
    {
        "title": "2024年全国大学生数学建模竞赛",
        "url": "http://example.com/contest1",
        "source": "湖北经济学院团委",
        "publish_time": "2024-03-01",
        "deadline": "2024-05-15",
        "category": "学科竞赛",
        "organizer": "全国大学生数学建模竞赛组委会",
        "participants": "全国高校本科生",
        "prize": "一等奖5000元，二等奖3000元，三等奖1000元",
        "requirement": "3人一组，提交论文",
        "contact": "mathmodel@example.com",
        "content": "2024年全国大学生数学建模竞赛开始报名，欢迎广大学生积极参与。",
        "summary": "2024年全国大学生数学建模竞赛开始报名，欢迎广大学生积极参与。",
        "keywords": ["数学", "建模", "竞赛", "全国"],
        "tags": ["学科竞赛", "国家级", "团队赛"],
        "spider_name": "湖北经济学院团委"
    },
    {
        "title": "2024年互联网+大学生创新创业大赛",
        "url": "http://example.com/contest2",
        "source": "湖北经济学院团委",
        "publish_time": "2024-03-10",
        "deadline": "2024-06-30",
        "category": "创业竞赛",
        "organizer": "教育部",
        "participants": "全国高校学生",
        "prize": "金奖10万元，银奖5万元，铜奖3万元",
        "requirement": "团队参赛，提交商业计划书",
        "contact": "internetplus@example.com",
        "content": "2024年互联网+大学生创新创业大赛启动，鼓励学生创新创业。",
        "summary": "2024年互联网+大学生创新创业大赛启动，鼓励学生创新创业。",
        "keywords": ["互联网+", "创业", "创新", "大赛"],
        "tags": ["创业竞赛", "国家级", "团队赛"],
        "spider_name": "湖北经济学院团委"
    },
    {
        "title": "2024年全国大学生英语竞赛",
        "url": "http://example.com/contest3",
        "source": "湖北经济学院团委",
        "publish_time": "2024-02-20",
        "deadline": "2024-04-10",
        "category": "学科竞赛",
        "organizer": "全国大学生英语竞赛组委会",
        "participants": "全国高校学生",
        "prize": "一等奖证书，二等奖证书，三等奖证书",
        "requirement": "个人参赛，笔试",
        "contact": "english@example.com",
        "content": "2024年全国大学生英语竞赛开始报名，测试学生英语水平。",
        "summary": "2024年全国大学生英语竞赛开始报名，测试学生英语水平。",
        "keywords": ["英语", "竞赛", "全国"],
        "tags": ["学科竞赛", "国家级", "个人赛"],
        "spider_name": "湖北经济学院团委"
    }
];

// 加载竞赛数据
async function loadContests() {
    try {
        console.log('开始加载数据...');
        
        // 尝试从data/contests.json加载数据
        try {
            const response = await fetch('data/contests.json');
            if (response.ok) {
                const data = await response.json();
                console.log('从data/contests.json加载数据成功，共', data.length, '条竞赛');
                
                // 处理数据格式，确保字段名与前端代码匹配
                const processedData = data.map(item => ({
                    id: item.id || item.raw_notice_id || Math.floor(Math.random() * 10000),
                    title: item.title || '无标题',
                    url: item.url || item.notice_url || '',
                    source: item.source || item.source_department || '未知来源',
                    publish_time: item.publish_time || '2025-01-01',
                    deadline: item.deadline || item.sign_up_deadline || '',
                    category: item.category || '其他竞赛',
                    organizer: item.organizer || item.source_department || '未知',
                    participants: item.participants || '全体学生',
                    prize: item.prize || '未知',
                    requirement: item.requirement || '',
                    contact: item.contact || '',
                    content: item.content || '无详细内容',
                    summary: item.summary || (item.content ? item.content.substring(0, 100) + '...' : '无摘要'),
                    keywords: item.keywords || (item.tags ? item.tags.split(',') : []),
                    tags: item.tags || (item.keywords ? item.keywords.join(',') : ''),
                    spider_name: item.spider_name || item.source_department || '未知'
                }));
                
                return processedData;
            } else {
                console.log('从data/contests.json加载数据失败，状态:', response.status);
            }
        } catch (fetchError) {
            console.log('网络加载失败，使用模拟数据:', fetchError);
        }
        
        // 使用模拟数据
        console.log('使用模拟数据，共', mockContests.length, '条竞赛');
        return mockContests;
    } catch (e) {
        console.error('加载数据失败:', e);
        return mockContests;
    }
}

// 加载统计数据
function loadStatistics(contests) {
    const total = contests.length;
    
    // 按分类统计
    const categoryStats = {};
    contests.forEach(contest => {
        const category = contest.category || '其他竞赛';
        categoryStats[category] = (categoryStats[category] || 0) + 1;
    });
    
    // 按月份统计
    const monthStats = {};
    contests.forEach(contest => {
        if (contest.publish_time) {
            const month = contest.publish_time.substring(0, 7); // YYYY-MM
            monthStats[month] = (monthStats[month] || 0) + 1;
        }
    });
    
    return {
        total,
        categoryStats,
        monthStats
    };
}

// 保存用户设置
function saveSettings(settings) {
    saveToLocalStorage('contest_settings', settings);
}

// 加载用户设置
function loadSettings() {
    return getFromLocalStorage('contest_settings', {
        notifications: false,
        keywords: []
    });
}

// 保存收藏的竞赛
function saveFavorites(favorites) {
    saveToLocalStorage('contest_favorites', favorites);
}

// 加载收藏的竞赛
function loadFavorites() {
    return getFromLocalStorage('contest_favorites', []);
}

// 检查竞赛是否已收藏
function isFavorite(contestUrl) {
    const favorites = loadFavorites();
    return favorites.includes(contestUrl);
}

// 切换收藏状态
function toggleFavorite(contestUrl) {
    let favorites = loadFavorites();
    const index = favorites.indexOf(contestUrl);
    if (index > -1) {
        favorites.splice(index, 1);
    } else {
        favorites.push(contestUrl);
    }
    saveFavorites(favorites);
    return favorites;
}
