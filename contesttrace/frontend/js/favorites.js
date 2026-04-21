/**
 * 收藏页面逻辑
 */

let currentView = 'card';

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    try {
        // 清理无效的收藏数据
        const favorites = loadFavorites();
        if (!Array.isArray(favorites) || favorites.some(fav => !fav || !fav.id || !fav.title)) {
            // 重置为有效数据
            saveFavorites(favorites.filter(fav => fav && fav.id && fav.title));
        }
        
        // 初始化页面
        renderFavorites();
        initEventListeners();
        initModal();
        
        // 监听 localStorage 变化
        window.addEventListener('storage', function(e) {
            if (e.key === 'contest_favorites') {
                renderFavorites();
            }
        });
    } catch (error) {
        console.error('初始化失败:', error);
    }
});

// 初始化事件监听器
function initEventListeners() {
    // 来源筛选
    const sourceFilter = document.getElementById('source-filter');
    if (sourceFilter) {
        sourceFilter.addEventListener('change', function() {
            renderFavorites();
        });
    }
    
    // 时间筛选
    const timeFilter = document.getElementById('time-filter');
    if (timeFilter) {
        timeFilter.addEventListener('change', function() {
            renderFavorites();
        });
    }
    
    // 月份筛选
    const monthFilter = document.getElementById('month-filter');
    if (monthFilter) {
        monthFilter.addEventListener('change', function() {
            renderFavorites();
        });
    }
    
    // 排序选择器
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            renderFavorites();
        });
    }
    
    // 开启通知提醒
    const enableNotificationsBtn = document.getElementById('enable-notifications');
    if (enableNotificationsBtn) {
        enableNotificationsBtn.addEventListener('click', async function() {
            if (!('Notification' in window)) {
                alert('您的浏览器不支持通知功能');
                return;
            }
            
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                saveToLocalStorage('notification_enabled', true);
                alert('通知提醒已开启');
            } else {
                alert('您已拒绝通知权限，如需开启请在浏览器设置中允许通知');
            }
        });
    }
    
    // 关闭通知提醒
    const disableNotificationsBtn = document.getElementById('disable-notifications');
    if (disableNotificationsBtn) {
        disableNotificationsBtn.addEventListener('click', function() {
            saveToLocalStorage('notification_enabled', false);
            alert('通知提醒已关闭');
        });
    }
    
    // 清空所有收藏
    const clearFavoritesBtn = document.getElementById('clear-favorites');
    if (clearFavoritesBtn) {
        clearFavoritesBtn.addEventListener('click', function() {
            if (confirm('确定要清空所有收藏吗？')) {
                saveFavorites([]);
                saveToLocalStorage('reminded_flags', {});
                renderFavorites();
                alert('所有收藏已清空');
            }
        });
    }
    
    // 导出 JSON
    const exportJsonBtn = document.getElementById('export-json-btn');
    if (exportJsonBtn) {
        exportJsonBtn.addEventListener('click', exportDataToJSON);
    }
    
    // 导出 CSV
    const exportCsvBtn = document.getElementById('export-csv-btn');
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', exportDataToCSV);
    }
    
    // 视图切换按钮
    const viewSwitchBtns = document.querySelectorAll('.view-switch-btn');
    viewSwitchBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const view = this.dataset.view;
            if (view && view !== currentView) {
                currentView = view;
                
                // 更新按钮状态
                viewSwitchBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                // 切换视图
                renderFavorites();
            }
        });
    });
}

// 从deadline字符串中提取日期
function extractDate(deadlineStr) {
    if (!deadlineStr) return null;
    // 匹配 YYYY-MM-DD 格式
    const match = deadlineStr.match(/\d{4}-\d{2}-\d{2}/);
    return match ? match[0] : null;
}

// 排序函数
function sortContests(contests, sortType) {
    const contestsCopy = [...contests];
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    switch (sortType) {
        case 'default':
            // 默认按发布时间降序（最新发布在前）
            return contestsCopy.sort((a, b) => new Date(b.publish_time) - new Date(a.publish_time));
        
        case 'deadline_nearest':
            // 按剩余天数升序（最近截止在前），已过期和无效日期放最后
            return contestsCopy.sort((a, b) => {
                const deadlineA = a.deadline ? extractDate(a.deadline) : null;
                const deadlineB = b.deadline ? extractDate(b.deadline) : null;
                
                const getDaysLeft = (deadlineStr) => {
                    if (!deadlineStr) return 9999;
                    const date = new Date(deadlineStr);
                    if (isNaN(date.getTime())) return 9999;
                    const timeDiff = date - today;
                    const daysLeft = Math.ceil(timeDiff / (1000 * 3600 * 24));
                    return daysLeft < 0 ? 9999 : daysLeft;
                };
                
                const daysLeftA = getDaysLeft(deadlineA);
                const daysLeftB = getDaysLeft(deadlineB);
                
                if (daysLeftA !== daysLeftB) {
                    return daysLeftA - daysLeftB;
                }
                // 剩余天数相同，按发布时间降序
                return new Date(b.publish_time) - new Date(a.publish_time);
            });
        
        case 'deadline_earliest':
            // 按绝对日期升序（最早的截止日期在前），无效日期放最后
            return contestsCopy.sort((a, b) => {
                const deadlineA = a.deadline ? extractDate(a.deadline) : null;
                const deadlineB = b.deadline ? extractDate(b.deadline) : null;
                if (!deadlineA && !deadlineB) return 0;
                if (!deadlineA) return 1;
                if (!deadlineB) return -1;
                return new Date(deadlineA) - new Date(deadlineB);
            });
        
        case 'deadline_latest':
            // 按绝对日期降序（最晚的截止日期在前），无效日期放最后
            return contestsCopy.sort((a, b) => {
                const deadlineA = a.deadline ? extractDate(a.deadline) : null;
                const deadlineB = b.deadline ? extractDate(b.deadline) : null;
                if (!deadlineA && !deadlineB) return 0;
                if (!deadlineA) return 1;
                if (!deadlineB) return -1;
                return new Date(deadlineB) - new Date(deadlineA);
            });
        
        case 'publish_asc':
            // 按发布时间升序（最早发布在前）
            return contestsCopy.sort((a, b) => new Date(a.publish_time) - new Date(b.publish_time));
        
        case 'publish_desc':
            // 按发布时间降序（最新发布在前）
            return contestsCopy.sort((a, b) => new Date(b.publish_time) - new Date(a.publish_time));
        
        case 'title_asc':
            // 按标题字母顺序
            return contestsCopy.sort((a, b) => a.title.localeCompare(b.title, 'zh-CN'));
        
        default:
            return contestsCopy;
    }
}

// 渲染收藏列表
function renderFavorites() {
    const favoriteContainer = document.getElementById('favorite-container');
    const timelineView = document.getElementById('timeline-view');
    const emptyFavorites = document.getElementById('empty-favorites');
    
    if (!favoriteContainer || !timelineView) {
        console.error('favorite-container或timeline-view元素不存在');
        return;
    }
    
    // 加载收藏的竞赛
    let favorites = loadFavorites();
    
    // 确保是数组
    if (!Array.isArray(favorites)) {
        favorites = [];
    }
    
    // 获取筛选条件
    let sourceFilter = 'all';
    let timeFilter = 'all';
    let monthFilter = 'all';
    
    const sourceFilterEl = document.getElementById('source-filter');
    const timeFilterEl = document.getElementById('time-filter');
    const monthFilterEl = document.getElementById('month-filter');
    
    if (sourceFilterEl) sourceFilter = sourceFilterEl.value;
    if (timeFilterEl) timeFilter = timeFilterEl.value;
    if (monthFilterEl) monthFilter = monthFilterEl.value;
    
    // 筛选竞赛
    let filteredFavorites = favorites;
    
    // 按来源筛选
    if (sourceFilter !== 'all') {
        filteredFavorites = filteredFavorites.filter(contest => 
            contest.source === sourceFilter
        );
    }
    
    // 按时间筛选
    if (timeFilter !== 'all') {
        const now = new Date();
        let cutoffDate;
        
        switch (timeFilter) {
            case 'week':
                cutoffDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                break;
            case 'month':
                cutoffDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
                break;
            case 'quarter':
                cutoffDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
                break;
            default:
                cutoffDate = new Date(0);
        }
        
        filteredFavorites = filteredFavorites.filter(contest => 
            new Date(contest.publish_time) >= cutoffDate
        );
    }
    
    // 按月份筛选
    if (monthFilter !== 'all') {
        filteredFavorites = filteredFavorites.filter(contest => {
            // 使用字符串前缀匹配，避免时区问题
            const publishMonth = contest.publish_time.substring(0, 7); // YYYY-MM
            return publishMonth === monthFilter;
        });
    }
    
    // 根据当前视图渲染
    if (currentView === 'card') {
        // 卡片视图
        favoriteContainer.style.display = 'grid';
        timelineView.style.display = 'none';
        
        // 排序
        const sortSelect = document.getElementById('sort-select');
        const sortType = sortSelect ? sortSelect.value : 'default';
        filteredFavorites = sortContests(filteredFavorites, sortType);
        
        // 渲染收藏的竞赛卡片
        favoriteContainer.innerHTML = '';
        
        if (filteredFavorites.length === 0) {
            if (emptyFavorites) {
                emptyFavorites.style.display = 'block';
            }
        } else {
            if (emptyFavorites) {
                emptyFavorites.style.display = 'none';
            }
            
            filteredFavorites.forEach(contest => {
                // 应用自定义数据
                const custom = getCustomization(contest.id);
                const displayContest = applyCustomization(contest, custom);
                const card = createFavoriteCard(displayContest);
                favoriteContainer.appendChild(card);
            });
        }
    } else {
        // 时间轴视图
        favoriteContainer.style.display = 'none';
        timelineView.style.display = 'block';
        renderTimelineView(filteredFavorites);
    }
}

// 创建收藏的竞赛卡片
function createFavoriteCard(contest) {
    const card = document.createElement('div');
    card.className = 'contest-card';
    card.dataset.id = contest.id;
    
    const daysLeft = calculateDaysLeft(contest.deadline);
    const daysLeftClass = getDaysLeftClass(daysLeft);
    const isActivityDate = contest.deadline && contest.deadline.includes('活动日期');
    const daysLeftText = getDaysLeftText(daysLeft, isActivityDate);
    
    // 根据前缀设置样式类
    let deadlineClass = daysLeftClass;
    if (contest.deadline && contest.deadline.startsWith('截止日期：')) {
        deadlineClass += ' deadline-urgent';
    } else if (contest.deadline && contest.deadline.startsWith('活动日期：')) {
        deadlineClass += ' deadline-active';
    }
    
    // 处理tags，确保它是一个数组
    const tags = Array.isArray(contest.tags) ? contest.tags : (contest.tags ? contest.tags.split(',') : []);
    
    // 生成deadline部分的HTML
    let deadlineHtml = '';
    if (contest.deadline) {
        deadlineHtml = `
        <div class="deadline ${deadlineClass}">
            <span class="deadline-value">${contest.deadline}</span>
            <span class="deadline-status">(${daysLeftText})</span>
        </div>
        `;
    }
    
    // 生成meta部分的HTML
    let metaHtml = `
        <span class="source">${contest.source || '未知来源'}</span>
    `;
    
    if (contest.publish_time) {
        metaHtml += ` | <span class="publish-time">${formatDate(contest.publish_time)}</span>`;
    }
    
    if (contest.competition_level && contest.competition_level !== '未知等级' && contest.competition_level !== '') {
        metaHtml += ` | <span class="competition-level">${contest.competition_level}</span>`;
    }
    
    // 检查是否有笔记
    const hasNote = getNote(contest.id) !== '';
    // 获取进度
    const progress = getProgress(contest.id);
    // 检查并应用自定义数据
    const custom = getCustomization(contest.id);
    const displayContest = applyCustomization(contest, custom);
    
    card.innerHTML = `
        <div class="card-title-area">
            <h3>${displayContest.title || '无标题'}${custom ? '<span class="customized-badge">已编辑</span>' : ''}</h3>
            <div class="card-actions-area">
                <i class="fas fa-edit edit-icon" data-id="${contest.id}" title="编辑竞赛信息"></i>
                <i class="fas fa-undo reset-icon ${custom ? '' : 'hidden'}" data-id="${contest.id}" title="恢复原始信息"></i>
                <i class="fas fa-sticky-note note-icon ${hasNote ? 'has-note' : ''}" data-id="${contest.id}" title="${hasNote ? '编辑笔记' : '添加笔记'}"></i>
            </div>
        </div>
        <div class="meta">
            ${metaHtml}
        </div>
        <p class="summary">${displayContest.summary || (displayContest.content ? displayContest.content.substring(0, 100) + '...' : '无摘要')}</p>
        ${deadlineHtml}
        <div class="progress-section">
            <select class="progress-select" data-id="${contest.id}">
                <option value="未开始" ${progress === '未开始' ? 'selected' : ''}>未开始</option>
                <option value="已报名" ${progress === '已报名' ? 'selected' : ''}>已报名</option>
                <option value="校赛通过" ${progress === '校赛通过' ? 'selected' : ''}>校赛通过</option>
                <option value="省赛通过" ${progress === '省赛通过' ? 'selected' : ''}>省赛通过</option>
                <option value="国赛入围" ${progress === '国赛入围' ? 'selected' : ''}>国赛入围</option>
                <option value="国赛获奖" ${progress === '国赛获奖' ? 'selected' : ''}>国赛获奖</option>
            </select>
        </div>
        <div class="card-actions">
            <button class="remove-favorite-btn" data-id="${contest.id}">
                <i class="fas fa-trash"></i> 取消收藏
            </button>
            <button class="action-btn useful-btn" data-id="${contest.id}">
                <i class="far fa-thumbs-up"></i> 有用
            </button>
            <button class="action-btn useless-btn" data-id="${contest.id}">
                <i class="far fa-thumbs-down"></i> 无用
            </button>
            <button class="action-btn poster-btn" data-id="${contest.id}">
                <i class="fas fa-camera"></i> 海报
            </button>
        </div>
    `;
    
    // 取消收藏按钮事件
    const removeFavoriteBtn = card.querySelector('.remove-favorite-btn');
    if (removeFavoriteBtn) {
        removeFavoriteBtn.addEventListener('click', function(e) {
            e.stopPropagation(); // 阻止事件冒泡，避免触发卡片点击事件
            const contestId = this.dataset.id;
            removeFavorite(contestId);
            renderFavorites();
        });
    }
    
    // 有用按钮事件
    const usefulBtn = card.querySelector('.useful-btn');
    if (usefulBtn) {
        usefulBtn.addEventListener('click', function(e) {
            e.stopPropagation(); // 阻止事件冒泡，避免触发卡片点击事件
            alert('感谢您的反馈！');
        });
    }
    
    // 无用按钮事件
    const uselessBtn = card.querySelector('.useless-btn');
    if (uselessBtn) {
        uselessBtn.addEventListener('click', function(e) {
            e.stopPropagation(); // 阻止事件冒泡，避免触发卡片点击事件
            alert('感谢您的反馈，我们会不断改进！');
        });
    }
    
    // 进度下拉框事件
    const progressSelect = card.querySelector('.progress-select');
    if (progressSelect) {
        progressSelect.addEventListener('click', function(e) {
            e.stopPropagation(); // 阻止点击事件冒泡
        });
        progressSelect.addEventListener('change', function(e) {
            e.stopPropagation(); // 阻止change事件冒泡
            const contestId = this.dataset.id;
            const newStatus = this.value;
            setProgress(contestId, newStatus);
        });
    }
    
    // 笔记图标点击事件
    const noteIcon = card.querySelector('.note-icon');
    if (noteIcon) {
        noteIcon.addEventListener('click', function(e) {
            e.stopPropagation(); // 阻止事件冒泡，避免触发卡片点击事件
            const contestId = contest.id;
            const currentNote = getNote(contestId);
            openNoteModal(contestId, currentNote, function(newNote) {
                setNote(contestId, newNote);
                // 更新图标状态
                if (newNote !== '') {
                    noteIcon.classList.add('has-note');
                } else {
                    noteIcon.classList.remove('has-note');
                }
            });
        });
    }
    
    // 编辑图标点击事件
    const editIcon = card.querySelector('.edit-icon');
    if (editIcon) {
        editIcon.addEventListener('click', function(e) {
            e.stopPropagation();
            openEditModal(contest, function() {
                // 不再重新渲染整个列表，而是更新单个卡片
                updateCard(contest.id);
            });
        });
    }
    
    // 重置图标点击事件
    const resetIcon = card.querySelector('.reset-icon');
    if (resetIcon) {
        resetIcon.addEventListener('click', function(e) {
            e.stopPropagation();
            resetCustomization(contest.id);
            // 不再重新渲染整个列表，而是更新单个卡片
            updateCard(contest.id);
        });
    }
    
    // 海报按钮点击事件
    const posterBtn = card.querySelector('.poster-btn');
    if (posterBtn) {
        posterBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            generatePoster(contest.id, card);
        });
    }
    
    // 点击卡片打开模态框
    card.addEventListener('click', function() {
        openContestModal(contest);
    });
    
    return card;
}

// 移除收藏
function removeFavorite(contestId) {
    let favorites = loadFavorites();
    const contestIdStr = String(contestId);
    favorites = favorites.filter(fav => String(fav.id) !== contestIdStr);
    saveFavorites(favorites);
    
    // 清理提醒记录
    const remindedFlags = getFromLocalStorage('reminded_flags', {});
    delete remindedFlags[contestIdStr];
    saveToLocalStorage('reminded_flags', remindedFlags);
}

// 渲染时间轴视图
function renderTimelineView(favorites) {
    const timelineView = document.getElementById('timeline-view');
    if (!timelineView) return;
    
    timelineView.innerHTML = '';
    
    if (favorites.length === 0) {
        timelineView.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-calendar-alt"></i>
                <h3>暂无收藏竞赛</h3>
                <p>去首页添加一些竞赛吧！</p>
                <a href="index.html" class="btn">去首页</a>
            </div>
        `;
        return;
    }
    
    // 应用自定义数据
    const displayFavorites = favorites.map(contest => {
        const custom = getCustomization(contest.id);
        return applyCustomization(contest, custom);
    });
    
    // 按截止日期排序（升序）
    displayFavorites.sort((a, b) => {
        const dateA = a.deadline ? extractDate(a.deadline) : null;
        const dateB = b.deadline ? extractDate(b.deadline) : null;
        
        if (!dateA && !dateB) return 0;
        if (!dateA) return 1;
        if (!dateB) return -1;
        
        return new Date(dateA) - new Date(dateB);
    });
    
    // 生成时间轴条目
    displayFavorites.forEach(contest => {
        const daysLeft = calculateDaysLeft(contest.deadline);
        const isExpired = daysLeft < 0;
        const isUrgent = daysLeft >= 0 && daysLeft <= 3;
        
        let statusClass = 'normal';
        if (isExpired) statusClass = 'expired';
        else if (isUrgent) statusClass = 'urgent';
        
        const dateObj = contest.deadline ? extractDate(contest.deadline) : null;
        const dateText = dateObj ? formatDate(dateObj).substring(5) : '无日期';
        
        let daysText = '';
        let daysIcon = '';
        if (isExpired) {
            daysText = '已过期';
            daysIcon = '<i class="fas fa-hourglass-end"></i>';
        } else if (daysLeft === 0) {
            daysText = '今天截止';
            daysIcon = '<i class="fas fa-clock"></i>';
        } else {
            daysText = `${daysLeft}天后截止`;
            daysIcon = '<i class="fas fa-hourglass-half"></i>';
        }
        
        const item = document.createElement('div');
        item.className = `timeline-item ${statusClass}`;
        item.dataset.id = contest.id;
        
        item.innerHTML = `
            <div class="timeline-date">
                <i class="fas fa-circle"></i>
                ${dateText}
            </div>
            <div class="timeline-title" title="${contest.title}">${contest.title}</div>
            <div class="timeline-days">
                ${daysIcon}
                ${daysText}
            </div>
        `;
        
        // 点击打开详情模态框
        item.addEventListener('click', function() {
            openContestModal(contest);
        });
        
        timelineView.appendChild(item);
    });
}

// 打开竞赛详情模态框
function openContestModal(contest) {
    const modal = document.getElementById('contest-modal');
    
    if (!modal) {
        console.error('contest-modal元素不存在');
        return;
    }
    
    // 应用自定义数据
    const custom = getCustomization(contest.id);
    const displayContest = applyCustomization(contest, custom);
    
    // 填充模态框内容
    const modalTitleEl = document.getElementById('modal-title');
    if (modalTitleEl) modalTitleEl.textContent = displayContest.title;
    
    const modalSourceEl = document.getElementById('modal-source');
    if (modalSourceEl) modalSourceEl.textContent = displayContest.source;
    
    const modalPublishTimeEl = document.getElementById('modal-publish-time');
    if (modalPublishTimeEl) modalPublishTimeEl.textContent = formatDate(displayContest.publish_time);
    
    // 处理截止时间，为空时不显示
    const modalDeadlineEl = document.getElementById('modal-deadline');
    const deadlineInfoItem = modalDeadlineEl ? modalDeadlineEl.closest('.info-item') : null;
    if (deadlineInfoItem) {
        if (displayContest.deadline) {
            // 提取deadline中的标签和日期
            if (displayContest.deadline.includes('活动日期')) {
                // 找到标签元素并修改
                const labelEl = deadlineInfoItem.querySelector('.label');
                if (labelEl) labelEl.textContent = '活动日期：';
                // 只显示日期部分
                modalDeadlineEl.textContent = displayContest.deadline.replace('活动日期：', '');
            } else if (displayContest.deadline.includes('截止日期')) {
                // 找到标签元素并修改
                const labelEl = deadlineInfoItem.querySelector('.label');
                if (labelEl) labelEl.textContent = '截止日期：';
                // 只显示日期部分
                modalDeadlineEl.textContent = displayContest.deadline.replace('截止日期：', '');
            } else {
                // 默认标签
                const labelEl = deadlineInfoItem.querySelector('.label');
                if (labelEl) labelEl.textContent = '截止时间：';
                modalDeadlineEl.textContent = displayContest.deadline;
            }
            deadlineInfoItem.style.display = 'block';
        } else {
            deadlineInfoItem.style.display = 'none';
        }
    }
    
    const modalOrganizerEl = document.getElementById('modal-organizer');
    if (modalOrganizerEl) modalOrganizerEl.textContent = displayContest.organizer || '未知';
    
    const modalParticipantsEl = document.getElementById('modal-participants');
    if (modalParticipantsEl) modalParticipantsEl.textContent = displayContest.participants || '未知';
    
    const modalPrizeEl = document.getElementById('modal-prize');
    if (modalPrizeEl) modalPrizeEl.textContent = displayContest.prize || '未知';
    
    const modalContactEl = document.getElementById('modal-contact');
    if (modalContactEl) modalContactEl.textContent = displayContest.contact || '未知';
    
    const modalContentEl = document.getElementById('modal-content');
    if (modalContentEl) modalContentEl.textContent = displayContest.content || '无详细内容';
    
    const modalUrlEl = document.getElementById('modal-url');
    if (modalUrlEl) modalUrlEl.href = displayContest.url;
    
    // 显示模态框
    modal.style.display = 'block';
    
    // 设置收藏按钮状态
    const favoriteBtn = document.getElementById('favorite-btn');
    if (favoriteBtn) {
        const isFav = isFavorite(contest.id);
        favoriteBtn.innerHTML = isFav ? '<i class="fas fa-star"></i> 已收藏' : '<i class="far fa-star"></i> 收藏';
    }
}

// 初始化模态框
function initModal() {
    // 为所有模态框绑定关闭按钮事件
    document.querySelectorAll('.modal').forEach(modal => {
        const closeBtn = modal.querySelector('.close');
        if (closeBtn) {
            closeBtn.onclick = function(e) {
                e.stopPropagation();
                modal.style.display = 'none';
            };
        }
        modal.onclick = function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        };
    });
    
    // 收藏按钮
    const favoriteBtn = document.getElementById('favorite-btn');
    if (favoriteBtn) {
        favoriteBtn.onclick = function() {
            const modalTitle = document.getElementById('modal-title');
            const contestTitle = modalTitle ? modalTitle.textContent : '';
            const favorites = loadFavorites();
            const contest = favorites.find(fav => fav.title === contestTitle);
            if (contest) {
                toggleFavorite(contest.id, contest);
                this.innerHTML = isFavorite(contest.id) ? '<i class="fas fa-star"></i> 已收藏' : '<i class="far fa-star"></i> 收藏';
                
                // 更新卡片上的取消收藏按钮状态
                const card = document.querySelector(`.contest-card[data-id="${contest.id}"]`);
                if (card) {
                    const unfavoriteBtn = card.querySelector('.unfavorite-btn');
                    if (unfavoriteBtn) {
                        if (isFavorite(contest.id)) {
                            unfavoriteBtn.textContent = '取消收藏';
                        } else {
                            unfavoriteBtn.textContent = '收藏';
                        }
                    }
                }
            }
        };
    }
    
    // 有用按钮
    const likeBtn = document.getElementById('like-btn');
    if (likeBtn) {
        likeBtn.onclick = function() {
            alert('感谢您的反馈！');
        };
    }
    
    // 无用按钮
    const dislikeBtn = document.getElementById('dislike-btn');
    if (dislikeBtn) {
        dislikeBtn.onclick = function() {
            alert('感谢您的反馈，我们会不断改进！');
        };
    }
}