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

// 竞赛进度相关函数
// 旧进度值映射到新进度值
const progressMigration = {
    '初赛通过': '校赛通过',
    '决赛入围': '省赛通过',
    '已获奖': '国赛获奖'
};

function getProgress(contestId) {
    try {
        const progressData = getFromLocalStorage('contest_progress', {});
        let progress = progressData[contestId] || '未开始';
        
        // 如果是旧进度值，进行迁移
        if (progressMigration[progress]) {
            const newProgress = progressMigration[progress];
            progressData[contestId] = newProgress;
            saveToLocalStorage('contest_progress', progressData);
            console.log(`进度数据已迁移: ${contestId}: ${progress} -> ${newProgress}`);
            progress = newProgress;
        }
        
        return progress;
    } catch (e) {
        console.error('获取进度失败:', e);
        return '未开始';
    }
}

function setProgress(contestId, status) {
    try {
        const progressData = getFromLocalStorage('contest_progress', {});
        progressData[contestId] = status;
        saveToLocalStorage('contest_progress', progressData);
        return true;
    } catch (e) {
        console.error('保存进度失败:', e);
        return false;
    }
}

// 竞赛笔记相关函数
function getNote(contestId) {
    try {
        const notesData = getFromLocalStorage('contest_notes', {});
        return notesData[contestId] || '';
    } catch (e) {
        console.error('获取笔记失败:', e);
        return '';
    }
}

function setNote(contestId, text) {
    try {
        const notesData = getFromLocalStorage('contest_notes', {});
        notesData[contestId] = text;
        saveToLocalStorage('contest_notes', notesData);
        return true;
    } catch (e) {
        console.error('保存笔记失败:', e);
        return false;
    }
}

// 打开笔记编辑模态框
function openNoteModal(contestId, currentNote, onSave) {
    try {
        const modal = document.getElementById('note-modal');
        const textarea = modal.querySelector('textarea');
        const saveBtn = modal.querySelector('.save-btn');
        const cancelBtn = modal.querySelector('.cancel-btn');
        
        if (!modal || !textarea || !saveBtn || !cancelBtn) {
            console.error('笔记模态框元素缺失');
            return;
        }
        
        // 填充现有内容
        textarea.value = currentNote || '';
        
        // 保存按钮点击事件
        const handleSave = () => {
            const newNote = textarea.value;
            if (onSave) {
                onSave(newNote);
            }
            modal.style.display = 'none';
        };
        
        // 取消按钮点击事件
        const handleCancel = () => {
            modal.style.display = 'none';
        };
        
        // 移除旧的事件监听器
        saveBtn.removeEventListener('click', handleSave);
        cancelBtn.removeEventListener('click', handleCancel);
        
        // 添加新的事件监听器
        saveBtn.addEventListener('click', handleSave);
        cancelBtn.addEventListener('click', handleCancel);
        
        // 显示模态框
        modal.style.display = 'flex';
        
        // 聚焦到文本框
        textarea.focus();
    } catch (e) {
        console.error('打开笔记模态框失败:', e);
    }
}

// 获取竞赛自定义数据
function getCustomization(contestId) {
    try {
        const customData = getFromLocalStorage('contest_customizations', {});
        return customData[contestId] || null;
    } catch (e) {
        console.error('获取自定义数据失败:', e);
        return null;
    }
}

// 保存竞赛自定义数据
function setCustomization(contestId, fields) {
    try {
        const customData = getFromLocalStorage('contest_customizations', {});
        if (!customData[contestId]) {
            customData[contestId] = {};
        }
        Object.assign(customData[contestId], fields);
        customData[contestId].reset = false;
        saveToLocalStorage('contest_customizations', customData);
        return true;
    } catch (e) {
        console.error('保存自定义数据失败:', e);
        return false;
    }
}

// 重置竞赛自定义数据
function resetCustomization(contestId) {
    try {
        const customData = getFromLocalStorage('contest_customizations', {});
        delete customData[contestId];
        saveToLocalStorage('contest_customizations', customData);
        return true;
    } catch (e) {
        console.error('重置自定义数据失败:', e);
        return false;
    }
}

// 应用自定义数据到竞赛对象
function applyCustomization(contest, custom) {
    if (!custom) return contest;
    const result = { ...contest };
    if (custom.title !== undefined) result.title = custom.title;
    if (custom.deadline !== undefined) result.deadline = custom.deadline;
    if (custom.summary !== undefined) result.summary = custom.summary;
    if (custom.organizer !== undefined) result.organizer = custom.organizer;
    if (custom.participants !== undefined) result.participants = custom.participants;
    if (custom.prize !== undefined) result.prize = custom.prize;
    return result;
}

// 打开编辑竞赛模态框
function openEditModal(contest, onSave) {
    try {
        const modal = document.getElementById('edit-contest-modal');
        if (!modal) {
            console.error('编辑模态框元素缺失');
            return;
        }
        
        const custom = getCustomization(contest.id);
        const titleInput = modal.querySelector('#edit-title');
        const deadlineInput = modal.querySelector('#edit-deadline');
        const summaryInput = modal.querySelector('#edit-summary');
        const organizerInput = modal.querySelector('#edit-organizer');
        const participantsInput = modal.querySelector('#edit-participants');
        const prizeInput = modal.querySelector('#edit-prize');
        const saveBtn = modal.querySelector('.save-btn');
        const cancelBtn = modal.querySelector('.cancel-btn');
        const resetBtn = modal.querySelector('.reset-btn');
        
        if (titleInput) titleInput.value = custom?.title || contest.title || '';
        if (deadlineInput) deadlineInput.value = custom?.deadline || contest.deadline || '';
        if (summaryInput) summaryInput.value = custom?.summary || contest.summary || '';
        if (organizerInput) organizerInput.value = custom?.organizer || contest.organizer || '';
        if (participantsInput) participantsInput.value = custom?.participants || contest.participants || '';
        if (prizeInput) prizeInput.value = custom?.prize || contest.prize || '';
        
        // 保存当前竞赛ID到局部变量，避免闭包陷阱
        const currentContestId = contest.id;
        
        const handleSave = () => {
            const fields = {};
            if (titleInput && titleInput.value !== contest.title) fields.title = titleInput.value;
            if (deadlineInput && deadlineInput.value !== contest.deadline) fields.deadline = deadlineInput.value;
            if (summaryInput && summaryInput.value !== contest.summary) fields.summary = summaryInput.value;
            if (organizerInput && organizerInput.value !== contest.organizer) fields.organizer = organizerInput.value;
            if (participantsInput && participantsInput.value !== contest.participants) fields.participants = participantsInput.value;
            if (prizeInput && prizeInput.value !== contest.prize) fields.prize = prizeInput.value;
            
            if (Object.keys(fields).length > 0) {
                setCustomization(currentContestId, fields);
                // 更新卡片上的截止日期显示
                if (fields.deadline) {
                    updateCardDeadline(currentContestId);
                }
            }
            if (onSave) onSave();
            modal.style.display = 'none';
        };
        
        const handleCancel = () => {
            modal.style.display = 'none';
        };
        
        const handleReset = () => {
            resetCustomization(currentContestId);
            // 更新卡片上的截止日期显示
            updateCardDeadline(currentContestId);
            if (onSave) onSave();
            modal.style.display = 'none';
        };
        
        saveBtn.removeEventListener('click', handleSave);
        cancelBtn.removeEventListener('click', handleCancel);
        resetBtn.removeEventListener('click', handleReset);
        
        saveBtn.addEventListener('click', handleSave);
        cancelBtn.addEventListener('click', handleCancel);
        resetBtn.addEventListener('click', handleReset);
        
        modal.style.display = 'flex';
        if (titleInput) titleInput.focus();
    } catch (e) {
        console.error('打开编辑模态框失败:', e);
    }
}

// 更新卡片上的所有自定义信息
function updateCard(contestId) {
    try {
        // 查找所有包含该竞赛ID的卡片（首页和收藏页可能都有）
        const cards = document.querySelectorAll(`.contest-card[data-id="${contestId}"]`);
        
        if (cards.length === 0) {
            console.warn(`未找到竞赛ID为 ${contestId} 的卡片，尝试重新渲染列表`);
            // 尝试重新渲染首页或收藏页
            const path = window.location.pathname;
            if (path.includes('favorites')) {
                if (typeof renderFavorites === 'function') {
                    renderFavorites();
                }
            } else if (path.includes('index') || path === '/' || path.endsWith('.html')) {
                if (typeof renderContestList === 'function') {
                    renderContestList();
                }
            }
            return;
        }
        
        cards.forEach(card => {
            // 找到竞赛对象（从DOM或缓存中获取）
            const contests = loadAllContests() || [];
            const contest = contests.find(c => c.id == contestId);
            if (contest) {
                // 应用自定义数据
                const custom = getCustomization(contestId);
                const displayContest = applyCustomization(contest, custom);
                
                // 更新标题
                const titleElement = card.querySelector('.card-title h3');
                if (titleElement) {
                    titleElement.textContent = displayContest.title;
                }
                
                // 重新计算剩余天数
                const daysLeft = calculateDaysLeft(displayContest.deadline);
                const daysLeftClass = getDaysLeftClass(daysLeft);
                const isActivityDate = displayContest.deadline && displayContest.deadline.includes('活动日期');
                const daysLeftText = getDaysLeftText(daysLeft, isActivityDate);
                
                // 根据前缀设置样式类
                let deadlineClass = daysLeftClass;
                if (displayContest.deadline && displayContest.deadline.startsWith('截止日期：')) {
                    deadlineClass += ' deadline-urgent';
                } else if (displayContest.deadline && displayContest.deadline.startsWith('活动日期：')) {
                    deadlineClass += ' deadline-active';
                }
                
                // 生成新的deadline HTML
                const deadlineHtml = `
                    <div class="deadline ${deadlineClass}">
                        <span class="deadline-value">${displayContest.deadline}</span>
                        <span class="deadline-status">(${daysLeftText})</span>
                    </div>
                `;
                
                // 替换现有的deadline元素
                const existingDeadline = card.querySelector('.deadline');
                if (existingDeadline) {
                    existingDeadline.outerHTML = deadlineHtml;
                }
                
                // 更新已编辑标记
                const badgeElement = card.querySelector('.customized-badge');
                if (custom && Object.keys(custom).length > 0) {
                    if (!badgeElement) {
                        const badge = document.createElement('div');
                        badge.className = 'customized-badge';
                        badge.textContent = '已编辑';
                        const titleArea = card.querySelector('.card-title');
                        if (titleArea) {
                            titleArea.appendChild(badge);
                        }
                    }
                } else if (badgeElement) {
                    badgeElement.remove();
                }
            }
        });
    } catch (e) {
        console.error('更新卡片信息失败:', e);
        // 失败时尝试重新渲染列表
        if (window.location.pathname.includes('favorites')) {
            if (typeof renderFavorites === 'function') {
                renderFavorites();
            }
        } else if (window.location.pathname.includes('index') || window.location.pathname === '/') {
            if (typeof renderContests === 'function') {
                renderContests();
            }
        }
    }
}

// 兼容旧的函数名
function updateCardDeadline(contestId) {
    updateCard(contestId);
}

// 从所有竞赛中加载竞赛对象（需要根据实际情况实现）
function loadAllContests() {
    try {
        // 尝试从localStorage中获取
        const contests = getFromLocalStorage('all_contests', null);
        if (contests) return contests;
        
        // 如果没有，返回空数组
        return [];
    } catch (e) {
        console.error('加载竞赛数据失败:', e);
        return [];
    }
}
