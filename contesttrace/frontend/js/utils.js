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
    const today = new Date();
    const deadlineDate = new Date(deadline);
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
function getDaysLeftText(daysLeft) {
    if (daysLeft < 0) return '已过期';
    if (daysLeft === 0) return '今天截止';
    if (daysLeft === 1) return '明天截止';
    return `${daysLeft}天后截止`;
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
