/**
 * 截止日期提醒模块
 */

let reminderInterval = null;

// 计算剩余天数
function calculateDaysLeft(deadline) {
    if (!deadline) return null;
    
    // 移除截止日期前缀
    const cleanDeadline = deadline.replace('截止日期：', '').replace('活动日期：', '');
    
    // 解析日期并设置为当天的00:00:00
    const deadlineDate = new Date(cleanDeadline);
    deadlineDate.setHours(0, 0, 0, 0);
    
    // 获取今天的00:00:00
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    // 计算时间差（毫秒）
    const timeDiff = deadlineDate - today;
    
    // 转换为天数
    const daysLeft = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));
    
    return daysLeft;
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    // 启动提醒检查
    startReminderCheck();
    
    // 页面关闭时清除定时器
    window.addEventListener('beforeunload', function() {
        stopReminderCheck();
    });
});

// 启动提醒检查
function startReminderCheck() {
    // 检查间隔（30分钟）
    const checkInterval = 30 * 60 * 1000;
    
    // 立即执行一次检查
    checkDeadlines();
    
    // 设置定时器
    reminderInterval = setInterval(checkDeadlines, checkInterval);
}

// 停止提醒检查
function stopReminderCheck() {
    if (reminderInterval) {
        clearInterval(reminderInterval);
        reminderInterval = null;
    }
}

// 检查截止日期和活动日期
function checkDeadlines() {
    // 检查通知权限
    if (!('Notification' in window) || Notification.permission !== 'granted') {
        return;
    }
    
    // 检查应用层通知是否已启用
    const notificationEnabled = getFromLocalStorage('notification_enabled', false);
    if (!notificationEnabled) {
        return;
    }
    
    // 加载收藏的竞赛
    const favorites = loadFavorites();
    if (favorites.length === 0) {
        return;
    }
    
    // 加载已提醒的标记
    const remindedFlags = getFromLocalStorage('reminded_flags', {});
    
    // 检查每个收藏的竞赛
    favorites.forEach(contest => {
        // 应用自定义数据
        const custom = getCustomization(contest.id);
        const displayContest = applyCustomization(contest, custom);
        
        if (!displayContest.deadline) return;
        
        const daysLeft = calculateDaysLeft(displayContest.deadline);
        
        // 只提醒剩余3天、1天、0天的竞赛
        const reminderDays = [3, 1, 0];
        
        if (reminderDays.includes(daysLeft)) {
            // 检查是否已经提醒过
            const contestId = contest.id.toString();
            if (!remindedFlags[contestId]) {
                remindedFlags[contestId] = {};
            }
            
            if (!remindedFlags[contestId][daysLeft.toString()]) {
                // 发送通知
                sendDeadlineNotification(displayContest, daysLeft);
                
                // 标记为已提醒
                remindedFlags[contestId][daysLeft.toString()] = true;
                saveToLocalStorage('reminded_flags', remindedFlags);
            }
        }
    });
}

// 发送日期通知
function sendDeadlineNotification(contest, daysLeft) {
    if (!('Notification' in window) || Notification.permission !== 'granted') {
        return;
    }
    
    let message = '';
    let notificationTitle = '';
    
    // 检查是活动日期还是截止日期
    const isActivityDate = contest.deadline && contest.deadline.includes('活动日期');
    
    if (daysLeft === 0) {
        if (isActivityDate) {
            message = `今天开始，点击查看详情`;
            notificationTitle = `竞赛活动提醒：${contest.title}`;
        } else {
            message = `今天截止，点击查看详情`;
            notificationTitle = `竞赛截止提醒：${contest.title}`;
        }
    } else if (daysLeft === 1) {
        if (isActivityDate) {
            message = `距离 ${contest.deadline} 仅剩 1 天，点击查看详情`;
            notificationTitle = `竞赛活动提醒：${contest.title}`;
        } else {
            message = `距离 ${contest.deadline} 仅剩 1 天，点击查看详情`;
            notificationTitle = `竞赛截止提醒：${contest.title}`;
        }
    } else {
        if (isActivityDate) {
            message = `距离 ${contest.deadline} 仅剩 ${daysLeft} 天，点击查看详情`;
            notificationTitle = `竞赛活动提醒：${contest.title}`;
        } else {
            message = `距离 ${contest.deadline} 仅剩 ${daysLeft} 天，点击查看详情`;
            notificationTitle = `竞赛截止提醒：${contest.title}`;
        }
    }
    
    const notification = new Notification(notificationTitle, {
        body: message,
        icon: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=academic%20competition%20notification%20icon&image_size=square',
        data: {
            contestId: contest.id,
            contestUrl: contest.url
        }
    });
    
    // 点击通知跳转到首页
    notification.onclick = function() {
        window.open('index.html', '_self');
    };
    
    // 保存提醒历史
    saveReminderHistory(contest, daysLeft);
}

// 保存提醒历史
function saveReminderHistory(contest, daysLeft) {
    try {
        // 获取现有历史记录
        let history = getFromLocalStorage('reminder_history', []);
        
        // 创建新记录
        const now = new Date();
        const newRecord = {
            id: `${now.getTime()}_${contest.id}`,
            contestId: contest.id.toString(),
            contestTitle: contest.title,
            remindDate: now.toLocaleString('zh-CN'),
            daysLeft: daysLeft,
            read: false
        };
        
        // 添加到历史记录
        history.unshift(newRecord);
        
        // 清理30天前的记录
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        
        history = history.filter(record => {
            const recordDate = new Date(record.remindDate);
            return recordDate >= thirtyDaysAgo;
        });
        
        // 限制最多100条记录
        if (history.length > 100) {
            history = history.slice(0, 100);
        }
        
        // 保存回localStorage
        saveToLocalStorage('reminder_history', history);
        
        // 尝试更新未读数量（如果UI已加载）
        if (typeof updateUnreadCount === 'function') {
            updateUnreadCount();
        }
    } catch (error) {
        console.error('保存提醒历史失败:', error);
    }
}

// 监听 localStorage 变化，更新提醒状态
window.addEventListener('storage', function(e) {
    if (e.key === 'contest_favorites') {
        // 收藏列表变化，重新检查
        checkDeadlines();
    }
});