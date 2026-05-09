/**
 * 主逻辑
 */

let allContests = [];
let currentPage = 1;
const pageSize = 10;

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', async function() {
    try {
        // 加载竞赛数据
        allContests = await loadContests();
        console.log('数据加载成功，共', allContests.length, '条竞赛');
        // 存储到localStorage，供其他模块使用
        saveToLocalStorage('all_contests', allContests);
        
        // 检查是否有 URL 参数指定竞赛ID
        const urlParams = new URLSearchParams(window.location.search);
        const contestId = urlParams.get('contestId');
        if (contestId) {
            const contest = allContests.find(c => c.id == contestId);
            if (contest) {
                openContestModal(contest);
                // 清除 URL 参数，避免刷新后重复打开
                history.replaceState({}, document.title, window.location.pathname);
            }
        }
        
        // 初始化页面
        initSearch();
        initContestList();
        initModal();
        initAiRecommendations();
        
        // 检查是否有词云搜索关键词
        const cloudKeyword = sessionStorage.getItem('cloud_search_keyword');
        if (cloudKeyword) {
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                searchInput.value = cloudKeyword;
                searchInput.focus();
                // 触发搜索
                renderContestList();
                // 清除 sessionStorage
                sessionStorage.removeItem('cloud_search_keyword');
            }
        }
        
        // 请求通知权限
        requestNotificationPermission();
    } catch (error) {
        console.error('初始化失败:', error);
    }
});

function initAiRecommendations() {
    const btn = document.getElementById('recommend-button');
    const resetBtn = document.getElementById('reset-profile-button');
    if (btn) {
        btn.addEventListener('click', fetchAiRecommendations);
    }
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            resetBehaviorProfile();
            saveRecommendHistory([]);
            renderRecommendHistory();
            const statusEl = document.getElementById('recommend-status');
            if (statusEl) {
                statusEl.textContent = '用户画像已重置。';
            }
        });
    }
    renderRecommendHistory();
}

async function fetchAiRecommendations() {
    const select = document.getElementById('interest-select');
    const statusEl = document.getElementById('recommend-status');
    const resultsEl = document.getElementById('recommend-results');
    if (!select || !statusEl || !resultsEl) return;

    const interests = Array.from(select.selectedOptions).map((o) => o.value);
    if (!interests.length) {
        statusEl.textContent = '请至少选择一个兴趣方向。';
        return;
    }

    const profile = getBehaviorProfile();
    profile.last_interests = interests;
    saveBehaviorProfile(profile);

    statusEl.textContent = '正在调用大模型推荐，请稍候...';
    resultsEl.innerHTML = '';

    try {
        const resp = await fetch('http://127.0.0.1:8001/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ interests, user_profile: profile })
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.error || '推荐接口调用失败');

        const recommended = Array.isArray(data.recommended) ? data.recommended : [];
        statusEl.textContent = `推荐完成（模型：${data.model || '未知'}，召回候选：${data.recall_size || 0}）。${data.reason || ''}`;

        if (!recommended.length) {
            resultsEl.innerHTML = '<p class="loading">暂无推荐结果，请换一组兴趣再试。</p>';
            return;
        }

        const normalized = recommended.map(normalizeContest);
        normalized.forEach((contest) => {
            const card = createContestCard(contest);
            injectRecommendReason(card, contest, interests);
            resultsEl.appendChild(card);
        });
        appendRecommendHistory(interests, normalized, data.reason || '');
    } catch (error) {
        statusEl.textContent = `推荐失败：${error.message}。请确认 Ollama 与推荐服务都已启动`;
    }
}

function injectRecommendReason(card, contest, interests) {
    const categories = Array.isArray(contest.ai_match_categories) ? contest.ai_match_categories : [];
    const keywords = Array.isArray(contest.ai_match_keywords) ? contest.ai_match_keywords : [];
    const hitCategory = categories.length ? `类别：${categories.join(' / ')}` : '语义相关推荐';
    const hitKeyword = keywords.length ? `；关键词：${keywords.slice(0, 3).join('、')}` : '';
    const hint = `${hitCategory}${hitKeyword}`;
    const chip = document.createElement('div');
    chip.className = 'ai-reason-chip';
    chip.textContent = hint;
    const meta = card.querySelector('.meta');
    if (meta) {
        meta.appendChild(chip);
    } else {
        card.prepend(chip);
    }
}

function appendRecommendHistory(interests, contests, reason) {
    const history = loadRecommendHistory();
    history.unshift({
        at: new Date().toISOString(),
        interests,
        reason,
        titles: contests.slice(0, 3).map((c) => c.title)
    });
    saveRecommendHistory(history.slice(0, 20));
    renderRecommendHistory();
}

function renderRecommendHistory() {
    const listEl = document.getElementById('recommend-history-list');
    if (!listEl) return;
    const history = loadRecommendHistory();
    if (!history.length) {
        listEl.innerHTML = '<div class="history-item">暂无推荐历史</div>';
        return;
    }
    listEl.innerHTML = '';
    history.forEach((item) => {
        const div = document.createElement('div');
        div.className = 'history-item';
        const time = (item.at || '').replace('T', ' ').slice(0, 16);
        div.textContent = `[${time}] 兴趣：${(item.interests || []).join('、')}；推荐：${(item.titles || []).join(' / ')}`;
        listEl.appendChild(div);
    });
}

function normalizeContest(item) {
    return {
        id: item.id || item.raw_notice_id || Math.floor(Math.random() * 1000000),
        title: item.title || '无标题',
        url: item.url || item.notice_url || '',
        source: item.source || item.publisher || '未知来源',
        publish_time: item.publish_time || '',
        deadline: item.deadline || '',
        category: item.category || '其他竞赛',
        organizer: item.organizer || item.source || '未知',
        participants: item.participants || '全体学生',
        prize: item.prize || '未知',
        requirement: item.requirement || '',
        contact: item.contact || '',
        content: item.content || '',
        summary: item.summary || (item.content ? item.content.substring(0, 100) + '...' : '无摘要'),
        keywords: item.keywords || [],
        tags: item.tags || '',
        spider_name: item.spider_name || item.source || '未知',
        ai_match_categories: item.ai_match_categories || [],
        ai_match_keywords: item.ai_match_keywords || []
    };
}

// 初始化导航
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // 移除所有活动状态
            navLinks.forEach(l => l.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            
            // 添加当前活动状态
            this.classList.add('active');
            const sectionId = this.dataset.section + '-section';
            document.getElementById(sectionId).classList.add('active');
            
            // 重新初始化对应模块
            if (sectionId === 'list-section') {
                renderContestList();
            } else if (sectionId === 'recommend-section') {
                renderRecommendations();
            } else if (sectionId === 'stats-section') {
                renderStatistics();
            } else if (sectionId === 'settings-section') {
                renderSettings();
            }
        });
    });
}

// 初始化搜索
function initSearch() {
    const searchBtn = document.getElementById('search-button');
    const searchInput = document.getElementById('search-input');
    const filterSource = document.getElementById('source-filter');
    const filterTime = document.getElementById('time-filter');
    const filterMonth = document.getElementById('month-filter');
    
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            currentPage = 1;
            renderContestList();
        });
    }
    
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                currentPage = 1;
                renderContestList();
            }
        });
    }
    
    if (filterSource) {
        filterSource.addEventListener('change', function() {
            currentPage = 1;
            renderContestList();
        });
    }
    
    if (filterTime) {
        filterTime.addEventListener('change', function() {
            currentPage = 1;
            renderContestList();
        });
    }
    
    if (filterMonth) {
        filterMonth.addEventListener('change', function() {
            currentPage = 1;
            renderContestList();
        });
    }
    
    // 排序选择器
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            currentPage = 1;
            renderContestList();
        });
    }
}

// 初始化竞赛列表
function initContestList() {
    renderContestList();
}

// 渲染竞赛列表
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

// 从deadline字符串中提取日期
function extractDate(deadlineStr) {
    if (!deadlineStr) return null;
    // 匹配 YYYY-MM-DD 格式
    const match = deadlineStr.match(/\d{4}-\d{2}-\d{2}/);
    return match ? match[0] : null;
}

function renderContestList() {
    const contestList = document.getElementById('contest-container');
    const pagination = document.getElementById('pagination');
    
    if (!contestList) {
        console.error('contest-container元素不存在');
        return;
    }
    
    // 获取搜索和筛选条件
    let searchQuery = '';
    let sourceFilter = 'all';
    let timeFilter = 'all';
    let monthFilter = 'all';
    
    const searchInput = document.getElementById('search-input');
    const sourceFilterEl = document.getElementById('source-filter');
    const timeFilterEl = document.getElementById('time-filter');
    const monthFilterEl = document.getElementById('month-filter');
    
    if (searchInput) searchQuery = searchInput.value;
    if (sourceFilterEl) sourceFilter = sourceFilterEl.value;
    if (timeFilterEl) timeFilter = timeFilterEl.value;
    if (monthFilterEl) monthFilter = monthFilterEl.value;
    
    // 筛选竞赛
    let filteredContests = allContests;
    
    // 按关键词搜索
    if (searchQuery) {
        filteredContests = filteredContests.filter(contest => 
            contest.title.includes(searchQuery) || 
            contest.summary.includes(searchQuery) || 
            (contest.keywords && contest.keywords.some(keyword => keyword.includes(searchQuery)))
        );
    }
    
    // 按来源筛选
    if (sourceFilter !== 'all') {
        filteredContests = filteredContests.filter(contest => 
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
        
        filteredContests = filteredContests.filter(contest => 
            new Date(contest.publish_time) >= cutoffDate
        );
    }
    
    // 按月份筛选
    if (monthFilter !== 'all') {
        filteredContests = filteredContests.filter(contest => {
            // 使用字符串前缀匹配，避免时区问题
            const publishMonth = contest.publish_time.substring(0, 7); // YYYY-MM
            return publishMonth === monthFilter;
        });
    }
    
    // 排序
    const sortSelect = document.getElementById('sort-select');
    const sortType = sortSelect ? sortSelect.value : 'default';
    filteredContests = sortContests(filteredContests, sortType);
    
    // 分页
    const paginatedContests = paginate(filteredContests, currentPage, pageSize);
    const totalPages = Math.ceil(filteredContests.length / pageSize);
    
    // 渲染竞赛卡片
    contestList.innerHTML = '';
    if (paginatedContests.length === 0) {
        contestList.innerHTML = '<p class="loading">没有找到符合条件的竞赛</p>';
    } else {
        paginatedContests.forEach(contest => {
            // 应用自定义数据
            const custom = getCustomization(contest.id);
            const displayContest = applyCustomization(contest, custom);
            const card = createContestCard(displayContest);
            contestList.appendChild(card);
        });
    }
    
    // 渲染分页控件
    if (pagination) {
        renderPagination(pagination, totalPages);
    }
}

// 创建竞赛卡片
function createContestCard(contest) {
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
        <div class="card-actions">
            <button class="favorite-btn" data-id="${contest.id}" data-url="${contest.url}">
                ${isFavorite(contest.id) ? '<i class="fas fa-star"></i> 已收藏' : '<i class="far fa-star"></i> 收藏'}
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
    
    // 收藏按钮事件
    const favoriteBtn = card.querySelector('.favorite-btn');
    if (favoriteBtn) {
        favoriteBtn.addEventListener('click', function(e) {
            e.stopPropagation(); // 阻止事件冒泡，避免触发卡片点击事件
            const contestId = contest.id;
            const wasFav = isFavorite(contestId);
            toggleFavorite(contestId, contest);
            // 重新获取收藏状态并更新按钮
            const isFav = isFavorite(contestId);
            if (!wasFav && isFav) {
                recordPersonalizedFeedback(contest, 'favorite');
            }
            this.innerHTML = isFav ? '<i class="fas fa-star"></i> 已收藏' : '<i class="far fa-star"></i> 收藏';
        });
    }
    
    // 有用按钮事件
    const usefulBtn = card.querySelector('.useful-btn');
    if (usefulBtn) {
        usefulBtn.addEventListener('click', function(e) {
            e.stopPropagation(); // 阻止事件冒泡，避免触发卡片点击事件
            recordPersonalizedFeedback(contest, 'useful');
            alert('感谢您的反馈！');
        });
    }
    
    // 无用按钮事件
    const uselessBtn = card.querySelector('.useless-btn');
    if (uselessBtn) {
        uselessBtn.addEventListener('click', function(e) {
            e.stopPropagation(); // 阻止事件冒泡，避免触发卡片点击事件
            recordPersonalizedFeedback(contest, 'dislike');
            alert('感谢您的反馈，我们会不断改进！');
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
                // 更新卡片上的信息
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
            // 更新卡片上的信息
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
        // 记录查看行为
        recordContestAction(contest.id, 'view');
        openContestModal(contest);
    });
    
    return card;
}

// 渲染分页控件
function renderPagination(pagination, totalPages) {
    if (!pagination) {
        console.error('pagination元素不存在');
        return;
    }
    
    pagination.innerHTML = '';
    
    if (totalPages <= 1) return;
    
    // 上一页
    const prevBtn = document.createElement('button');
    prevBtn.textContent = '上一页';
    prevBtn.disabled = currentPage === 1;
    prevBtn.addEventListener('click', function() {
        if (currentPage > 1) {
            currentPage--;
            renderContestList();
        }
    });
    pagination.appendChild(prevBtn);
    
    // 页码
    for (let i = 1; i <= totalPages; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.className = currentPage === i ? 'active' : '';
        pageBtn.addEventListener('click', function() {
            currentPage = i;
            renderContestList();
        });
        pagination.appendChild(pageBtn);
    }
    
    // 下一页
    const nextBtn = document.createElement('button');
    nextBtn.textContent = '下一页';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.addEventListener('click', function() {
        if (currentPage < totalPages) {
            currentPage++;
            renderContestList();
        }
    });
    pagination.appendChild(nextBtn);
}

// 初始化推荐
function initRecommendations() {
    renderRecommendations();
}

// 渲染推荐
function renderRecommendations() {
    const recommendList = document.getElementById('recommend-list');
    
    // 简单的推荐逻辑：按发布时间排序
    const recommendedContests = [...allContests]
        .sort((a, b) => new Date(b.publish_time) - new Date(a.publish_time))
        .slice(0, 6);
    
    recommendList.innerHTML = '';
    recommendedContests.forEach(contest => {
        const card = createContestCard(contest);
        recommendList.appendChild(card);
    });
}



// 初始化设置
function initSettings() {
    renderSettings();
    
    // 保存设置
    document.getElementById('save-settings').addEventListener('click', function() {
        const notifications = document.getElementById('notification-toggle').checked;
        const keywords = document.getElementById('keywords-input').value
            .split(',').map(k => k.trim()).filter(k => k);
        
        const settings = {
            notifications,
            keywords
        };
        
        saveSettings(settings);
        alert('设置保存成功');
    });
    
    // 导出CSV
    document.getElementById('export-csv').addEventListener('click', function() {
        exportToCSV(allContests);
    });
}

// 渲染设置
function renderSettings() {
    const settings = loadSettings();
    
    document.getElementById('notification-toggle').checked = settings.notifications;
    document.getElementById('keywords-input').value = settings.keywords.join(', ');
}

// 初始化模态框
function initModal() {
    // 为所有模态框绑定关闭按钮事件
    document.querySelectorAll('.modal').forEach(modal => {
        const closeBtn = modal.querySelector('.close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                modal.style.display = 'none';
            });
        }
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    // 收藏按钮
    const favoriteBtn = document.getElementById('favorite-btn');
    if (favoriteBtn) {
        favoriteBtn.addEventListener('click', function() {
            const contestUrl = this.dataset.url;
            const wasFavorite = isFavorite(contestUrl);
            toggleFavorite(contestUrl);
            const isNowFavorite = isFavorite(contestUrl);
            
            // 记录收藏行为
            if (!wasFavorite && isNowFavorite) {
                // 查找竞赛对象
                const allContests = loadAllContests();
                const contest = allContests.find(c => c.url === contestUrl);
                if (contest) {
                    recordContestAction(contest.id, 'favorite');
                    recordPersonalizedFeedback(contest, 'favorite');
                }
            }
            
            this.textContent = isNowFavorite ? '取消收藏' : '收藏';
        });
    }
    
    // 有用按钮
    const likeBtn = document.getElementById('like-btn');
    if (likeBtn) {
        likeBtn.addEventListener('click', function() {
            // 记录有用行为
            const modalTitle = document.getElementById('modal-title');
            const contestTitle = modalTitle ? modalTitle.textContent : '';
            const allContests = loadAllContests();
            const contest = allContests.find(c => c.title === contestTitle);
            if (contest) {
                recordContestAction(contest.id, 'useful');
                recordPersonalizedFeedback(contest, 'useful');
            }
            alert('感谢您的反馈！');
        });
    }
    
    // 无用按钮
    const dislikeBtn = document.getElementById('dislike-btn');
    if (dislikeBtn) {
        dislikeBtn.addEventListener('click', function() {
            const modalTitle = document.getElementById('modal-title');
            const title = modalTitle ? modalTitle.textContent : '';
            const contest = loadAllContests().find(c => c.title === title);
            if (contest) {
                recordPersonalizedFeedback(contest, 'dislike');
            }
            alert('感谢您的反馈，我们会不断改进！');
        });
    }
}

// 打开竞赛详情模态框
window.openContestModal = function(contest) {
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
    if (modalContactEl) modalContactEl.textContent = contest.contact || '未知';
    
    const modalContentEl = document.getElementById('modal-content');
    if (modalContentEl) modalContentEl.textContent = contest.content || '无详细内容';
    
    const modalUrlEl = document.getElementById('modal-url');
    if (modalUrlEl) modalUrlEl.href = contest.url;
    
    // 设置模态框内收藏按钮的状态
    const modalFavoriteBtn = document.getElementById('favorite-btn');
    if (modalFavoriteBtn) {
        // 存储当前竞赛信息
        modalFavoriteBtn.dataset.contestId = contest.id;
        
        // 设置初始状态
        const isFav = isFavorite(contest.id);
        modalFavoriteBtn.innerHTML = isFav ? '<i class="fas fa-star"></i> 已收藏' : '<i class="far fa-star"></i> 收藏';
        
        // 移除可能存在的旧事件监听器
        modalFavoriteBtn.onclick = null;
        
        // 添加新的点击事件
        modalFavoriteBtn.addEventListener('click', function() {
            const contestId = this.dataset.contestId;
            // 切换收藏状态
            toggleFavorite(contestId, contest);
            
            // 获取新的收藏状态
            const isFavNew = isFavorite(contestId);
            
            // 更新模态框内按钮
            this.innerHTML = isFavNew ? '<i class="fas fa-star"></i> 已收藏' : '<i class="far fa-star"></i> 收藏';
            
            // 更新卡片上的收藏按钮
            const cardFavoriteBtn = document.querySelector(`.favorite-btn[data-id="${contestId}"]`);
            if (cardFavoriteBtn) {
                cardFavoriteBtn.innerHTML = isFavNew ? '<i class="fas fa-star"></i> 已收藏' : '<i class="far fa-star"></i> 收藏';
            }
        });
    }
    
    // 显示模态框
    modal.style.display = 'block';
}
