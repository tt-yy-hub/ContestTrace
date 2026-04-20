/**
 * 提醒历史UI模块
 */

let currentPage = 1;
const pageSize = 10;

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    console.log('[Reminder-UI] DOMContentLoaded 事件触发');
    // 初始化铃铛图标（带重试机制）
    initReminderBellWithRetry(3);

    // 初始化弹窗
    initReminderPanel();

    // 更新未读数量
    updateUnreadCount();
});

// 初始化铃铛图标（带重试机制）
function initReminderBellWithRetry(retryCount) {
    console.log('[Reminder-UI] 开始初始化铃铛...');
    const bell = document.getElementById('reminder-bell');
    console.log('[Reminder-UI] 铃铛元素:', bell);
    console.log('[Reminder-UI] 重试次数:', retryCount);

    if (!bell) {
        if (retryCount > 0) {
            console.log(`[Reminder-UI] 铃铛元素未找到，${retryCount}秒后重试...`);
            setTimeout(() => {
                initReminderBellWithRetry(retryCount - 1);
            }, 1000);
        } else {
            console.warn('[Reminder-UI] 铃铛元素未找到，初始化失败');
            // 尝试手动创建铃铛元素
            createReminderBell();
        }
        return;
    }

    console.log('[Reminder-UI] 铃铛初始化成功');
    initReminderBell();
}

// 手动创建铃铛元素（备用方案）
function createReminderBell() {
    console.log('[Reminder-UI] 尝试手动创建铃铛元素...');
    
    // 找到导航栏的 ul 元素
    const navUl = document.querySelector('.nav ul');
    if (!navUl) {
        console.error('[Reminder-UI] 导航栏 ul 元素未找到');
        return;
    }
    
    // 检查是否已经有铃铛容器
    if (document.querySelector('.reminder-bell-container')) {
        console.log('[Reminder-UI] 铃铛容器已存在');
        return;
    }
    
    // 创建铃铛容器
    const bellContainer = document.createElement('li');
    bellContainer.className = 'reminder-bell-container';
    
    // 创建铃铛图标
    const bellIcon = document.createElement('i');
    bellIcon.className = 'fas fa-bell';
    bellIcon.id = 'reminder-bell';
    
    // 添加到容器
    bellContainer.appendChild(bellIcon);
    // 添加到导航栏
    navUl.appendChild(bellContainer);
    
    console.log('[Reminder-UI] 铃铛元素创建成功');
    
    // 初始化新创建的铃铛
    setTimeout(() => {
        initReminderBell();
    }, 100);
}

// 初始化铃铛图标
function initReminderBell() {
    const bell = document.getElementById('reminder-bell');
    if (!bell) return;

    // 点击铃铛切换弹窗显示/隐藏
    bell.addEventListener('click', function(e) {
        e.stopPropagation();
        console.log('[Reminder-UI] 铃铛被点击');
        toggleReminderPanel();
    });
    
    // 点击页面其他区域关闭弹窗
    document.addEventListener('click', function(e) {
        const panel = document.getElementById('reminder-panel');
        if (panel && panel.style.display !== 'none' && !panel.contains(e.target) && e.target !== bell) {
            hideReminderPanel();
        }
    });
    
    // 按ESC键关闭弹窗
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            hideReminderPanel();
        }
    });
}

// 初始化弹窗
function initReminderPanel() {
    const panel = document.getElementById('reminder-panel');
    if (!panel) return;
    
    // 初始隐藏
    panel.style.display = 'none';
    
    // 绑定分页控件
    const prevBtn = panel.querySelector('#reminder-prev');
    const nextBtn = panel.querySelector('#reminder-next');
    
    if (prevBtn) {
        prevBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            if (currentPage > 1) {
                currentPage--;
                loadReminderHistory(currentPage);
            }
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            currentPage++;
            loadReminderHistory(currentPage);
        });
    }
}

// 切换弹窗显示/隐藏
function toggleReminderPanel() {
    const panel = document.getElementById('reminder-panel');
    console.log('[Reminder-UI] toggleReminderPanel 面板元素:', panel);
    if (!panel) return;

    if (panel.style.display === 'none' || panel.style.display === '') {
        console.log('[Reminder-UI] 显示面板');
        showReminderPanel();
    } else {
        console.log('[Reminder-UI] 隐藏面板');
        hideReminderPanel();
    }
}

// 显示弹窗
function showReminderPanel() {
    const panel = document.getElementById('reminder-panel');
    console.log('[Reminder-UI] showReminderPanel 面板元素:', panel);
    if (!panel) return;

    panel.style.display = 'block';
    console.log('[Reminder-UI] 面板已设置为 block');

    // 加载历史记录
    currentPage = 1;
    loadReminderHistory(currentPage);
}

// 隐藏弹窗
function hideReminderPanel() {
    const panel = document.getElementById('reminder-panel');
    if (!panel) return;
    
    panel.style.display = 'none';
}

// 加载并渲染历史记录
function loadReminderHistory(page = 1) {
    try {
        // 获取历史记录
        let history = getFromLocalStorage('reminder_history', []);
        
        // 按提醒日期降序排序
        history.sort((a, b) => new Date(b.remindDate) - new Date(a.remindDate));
        
        // 计算分页
        const startIndex = (page - 1) * pageSize;
        const endIndex = startIndex + pageSize;
        const paginatedHistory = history.slice(startIndex, endIndex);
        
        // 渲染记录
        const listContainer = document.getElementById('reminder-list');
        if (!listContainer) return;
        
        if (paginatedHistory.length === 0) {
            listContainer.innerHTML = '<div class="no-reminders">暂无提醒记录</div>';
        } else {
            listContainer.innerHTML = '';
            
            paginatedHistory.forEach(record => {
                const item = document.createElement('div');
                item.className = `reminder-item ${record.read ? '' : 'unread'}`;
                item.dataset.id = record.id;
                item.dataset.contestId = record.contestId;
                
                // 计算提醒时间
                const remindDate = new Date(record.remindDate);
                const now = new Date();
                const diffTime = now - remindDate;
                const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
                
                let timeText = '';
                if (diffDays === 0) {
                    timeText = '今天提醒';
                } else if (diffDays === 1) {
                    timeText = '1天前提醒';
                } else {
                    timeText = `${diffDays}天前提醒`;
                }
                
                item.innerHTML = `
                    <div class="reminder-title">${record.contestTitle}</div>
                    <div class="reminder-meta">
                        <span class="reminder-date">${record.remindDate}</span>
                        <span class="reminder-days">剩余${record.daysLeft}天</span>
                        <span class="reminder-time">${timeText}</span>
                    </div>
                `;
                
                // 点击标记为已读并跳转到竞赛详情
                item.addEventListener('click', function(e) {
                    e.stopPropagation();
                    markAsRead(record.id);
                    openContestModalById(record.contestId);
                });
                
                listContainer.appendChild(item);
            });
        }
        
        // 更新分页信息
        updatePagination(page, history.length);
        
    } catch (error) {
        console.error('加载提醒历史失败:', error);
    }
}

// 标记为已读
function markAsRead(reminderId) {
    try {
        let history = getFromLocalStorage('reminder_history', []);
        
        // 找到并更新记录
        const recordIndex = history.findIndex(record => record.id === reminderId);
        if (recordIndex !== -1) {
            history[recordIndex].read = true;
            saveToLocalStorage('reminder_history', history);
            
            // 更新未读数量
            updateUnreadCount();
            
            // 重新渲染当前页
            loadReminderHistory(currentPage);
        }
    } catch (error) {
        console.error('标记已读失败:', error);
    }
}

// 更新分页信息
function updatePagination(currentPage, totalRecords) {
    const pagination = document.getElementById('reminder-pagination');
    if (!pagination) return;
    
    const totalPages = Math.ceil(totalRecords / pageSize);
    
    const prevBtn = document.getElementById('reminder-prev');
    const nextBtn = document.getElementById('reminder-next');
    const pageInfo = document.getElementById('reminder-page-info');
    
    if (prevBtn) {
        prevBtn.disabled = currentPage === 1;
    }
    
    if (nextBtn) {
        nextBtn.disabled = currentPage === totalPages || totalPages === 0;
    }
    
    if (pageInfo) {
        pageInfo.textContent = `第 ${currentPage} 页，共 ${totalPages} 页`;
    }
}

// 更新未读数量
function updateUnreadCount() {
    try {
        const history = getFromLocalStorage('reminder_history', []);
        const unreadCount = history.filter(record => !record.read).length;
        
        const bell = document.getElementById('reminder-bell');
        if (!bell) return;
        
        // 移除旧的小红点
        let badge = bell.nextElementSibling;
        if (badge && badge.classList.contains('unread-badge')) {
            badge.remove();
        }
        
        // 添加新的小红点
        if (unreadCount > 0) {
            badge = document.createElement('span');
            badge.className = 'unread-badge';
            badge.textContent = unreadCount;
            bell.parentNode.insertBefore(badge, bell.nextSibling);
        }
    } catch (error) {
        console.error('更新未读数量失败:', error);
    }
}

// 根据竞赛ID打开详情模态框
function openContestModalById(contestId) {
    try {
        // 尝试获取竞赛数据
        let contests = [];
        
        // 首先尝试从全局变量获取
        if (typeof allContests !== 'undefined' && allContests.length > 0) {
            contests = allContests;
        } else {
            // 从localStorage获取
            contests = getFromLocalStorage('all_contests', []);
        }
        
        // 找到对应竞赛
        const contest = contests.find(c => c.id.toString() === contestId);
        if (contest) {
            // 调用打开模态框的函数
            if (typeof openContestModal === 'function') {
                openContestModal(contest);
            } else {
                // 如果openContestModal不存在，跳转到首页并传递参数
                window.location.href = `index.html?contestId=${contestId}`;
            }
        }
    } catch (error) {
        console.error('打开竞赛详情失败:', error);
    }
}

// 从localStorage获取数据
function getFromLocalStorage(key, defaultValue = null) {
    try {
        const value = localStorage.getItem(key);
        return value ? JSON.parse(value) : defaultValue;
    } catch (error) {
        console.error('从localStorage获取数据失败:', error);
        return defaultValue;
    }
}

// 保存数据到localStorage
function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error('保存数据到localStorage失败:', error);
    }
}