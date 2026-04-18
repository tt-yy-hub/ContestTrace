/**
 * 工具函数
 */

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return '未知时间';
    return dateString;
}

// 计算剩余天数
function calculateDaysLeft(deadline) {
    if (!deadline) return -1;
    // 提取日期部分
    const dateMatch = deadline.match(/(\d{4}-\d{2}-\d{2}|\d{4}年\d{1,2}月\d{1,2}日)/);
    if (!dateMatch) return -1;
    const dateStr = dateMatch[0];
    // 转换为标准日期格式
    const normalizedDate = dateStr.replace(/年|月/g, '-').replace(/日/g, '');
    const today = new Date();
    const deadlineDate = new Date(normalizedDate);
    if (isNaN(deadlineDate.getTime())) return -1;
    const timeDiff = deadlineDate - today;
    return Math.ceil(timeDiff / (1000 * 3600 * 24));
}

// 获取剩余天数的样式类
function getDaysLeftClass(daysLeft) {
    if (daysLeft < 0) return 'urgent';
    if (daysLeft <= 7) return 'urgent';
    if (daysLeft <= 14) return 'warning';
    return 'normal';
}

// 生成剩余天数文本
function getDaysLeftText(daysLeft, isActivityDate = false) {
    if (daysLeft < 0) return isActivityDate ? '已结束' : '已过期';
    if (daysLeft === 0) return isActivityDate ? '今天开始' : '今天截止';
    if (daysLeft === 1) return isActivityDate ? '明天开始' : '明天截止';
    return isActivityDate ? `${daysLeft}天后开始` : `${daysLeft}天后截止`;
}

// 本地存储操作
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
        return true;
    } catch (e) {
        console.error('保存到本地存储失败:', e);
        return false;
    }
}

function getFromLocalStorage(key, defaultValue = null) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : defaultValue;
    } catch (e) {
        console.error('从本地存储读取失败:', e);
        return defaultValue;
    }
}

// 导出CSV
function exportToCSV(data, filename = 'contests.csv') {
    if (!data || data.length === 0) {
        alert('没有数据可导出');
        return;
    }

    // CSV表头
    const headers = [
        '标题', '来源', '发布时间', '截止时间', '分类',
        '组织者', '参赛对象', '奖项设置', '联系方式', '摘要', '链接'
    ];

    // 转换数据
    const csvContent = [
        headers.join(','),
        ...data.map(contest => [
            `"${contest.title || ''}"`,
            `"${contest.source || ''}"`,
            contest.publish_time || '',
            contest.deadline || '',
            contest.category || '',
            `"${contest.organizer || ''}"`,
            `"${contest.participants || ''}"`,
            `"${contest.prize || ''}"`,
            `"${contest.contact || ''}"`,
            `"${contest.summary || ''}"`,
            `"${contest.url || ''}"`
        ].join(','))
    ].join('\n');

    // 创建下载链接
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// 浏览器通知
function requestNotificationPermission() {
    if ('Notification' in window) {
        Notification.requestPermission();
    }
}

function sendNotification(title, options = {}) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, options);
    }
}

// 搜索和筛选
function searchContests(contests, query, category) {
    return contests.filter(contest => {
        // 分类筛选
        if (category && contest.category !== category) {
            return false;
        }
        
        // 关键词搜索
        if (!query) {
            return true;
        }
        
        const searchText = (
            (contest.title || '') + ' ' +
            (contest.content || '') + ' ' +
            (contest.keywords || []).join(' ') + ' ' +
            (contest.tags || []).join(' ')
        ).toLowerCase();
        
        return searchText.includes(query.toLowerCase());
    });
}

// 分页
function paginate(data, page, pageSize) {
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return data.slice(startIndex, endIndex);
}

// 生成随机ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// 记录竞赛行为
function recordContestAction(contestId, actionType) {
    // 加载现有的热度数据
    const contestHotness = getFromLocalStorage('contest_hotness', {});
    
    // 初始化该竞赛的热度数据
    if (!contestHotness[contestId]) {
        contestHotness[contestId] = {
            views: 0,
            favorites: 0,
            useful: 0,
            total: 0
        };
    }
    
    // 根据行为类型增加相应的热度值
    switch (actionType) {
        case 'view':
            contestHotness[contestId].views += 1;
            contestHotness[contestId].total += 1;
            break;
        case 'favorite':
            contestHotness[contestId].favorites += 3;
            contestHotness[contestId].total += 3;
            break;
        case 'useful':
            contestHotness[contestId].useful += 2;
            contestHotness[contestId].total += 2;
            break;
    }
    
    // 保存热度数据
    saveToLocalStorage('contest_hotness', contestHotness);
}

// 获取热门竞赛
function getHotContests(limit = 10) {
    // 加载所有竞赛
    const allContests = loadAllContests();
    // 加载热度数据
    const contestHotness = getFromLocalStorage('contest_hotness', {});
    
    // 计算每个竞赛的热度
    const contestsWithHotness = allContests.map(contest => {
        const hotness = contestHotness[contest.id] || { total: 0 };
        return {
            ...contest,
            hotness: hotness.total
        };
    });
    
    // 按热度排序
    contestsWithHotness.sort((a, b) => b.hotness - a.hotness);
    
    // 返回前 limit 个
    return contestsWithHotness.slice(0, limit);
}
