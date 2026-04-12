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
        
        // 初始化页面
        initSearch();
        initContestList();
        initStatistics();
        initModal();
        
        // 请求通知权限
        requestNotificationPermission();
    } catch (error) {
        console.error('初始化失败:', error);
    }
});

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
}

// 初始化竞赛列表
function initContestList() {
    renderContestList();
}

// 渲染竞赛列表
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
    
    // 分页
    const paginatedContests = paginate(filteredContests, currentPage, pageSize);
    const totalPages = Math.ceil(filteredContests.length / pageSize);
    
    // 渲染竞赛卡片
    contestList.innerHTML = '';
    if (paginatedContests.length === 0) {
        contestList.innerHTML = '<p class="loading">没有找到符合条件的竞赛</p>';
    } else {
        paginatedContests.forEach(contest => {
            const card = createContestCard(contest);
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
    
    const daysLeft = calculateDaysLeft(contest.deadline);
    const daysLeftClass = getDaysLeftClass(daysLeft);
    const daysLeftText = getDaysLeftText(daysLeft);
    
    // 处理tags，确保它是一个数组
    const tags = Array.isArray(contest.tags) ? contest.tags : (contest.tags ? contest.tags.split(',') : []);
    
    card.innerHTML = `
        <h3>${contest.title || '无标题'}</h3>
        <div class="meta">
            <span class="source">${contest.source || '未知来源'}</span> | 
            <span class="publish-time">${formatDate(contest.publish_time) || '未知时间'}</span> | 
            <span class="competition-level">${contest.competition_level || '未知等级'}</span>
        </div>
        <p class="summary">${contest.summary || (contest.content ? contest.content.substring(0, 100) + '...' : '无摘要')}</p>
        <div class="deadline ${daysLeftClass}">
            <span class="deadline-label">截止时间：</span>
            <span class="deadline-value">${contest.deadline || '未知'}</span>
            <span class="deadline-status">(${daysLeftText})</span>
        </div>
        <div class="expandable-info" style="display: none;">
            <div class="info-row">
                <div class="info-item">
                    <span class="info-label">参赛对象：</span>
                    <span class="info-value">${contest.participants || '全体学生'}</span>
                </div>
            </div>
            <div class="info-row">
                <div class="info-item">
                    <span class="info-label">奖项设置：</span>
                    <span class="info-value">${contest.prize || '未知'}</span>
                </div>
            </div>
            <div class="tags">
                ${tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
            </div>
        </div>
        <button class="expand-btn">展开</button>
    `;
    
    // 展开/折叠功能
    const expandBtn = card.querySelector('.expand-btn');
    const expandableInfo = card.querySelector('.expandable-info');
    
    expandBtn.addEventListener('click', function(e) {
        e.stopPropagation(); // 阻止事件冒泡，避免触发卡片点击事件
        if (expandableInfo.style.display === 'none') {
            expandableInfo.style.display = 'block';
            expandBtn.textContent = '收起';
        } else {
            expandableInfo.style.display = 'none';
            expandBtn.textContent = '展开';
        }
    });
    
    // 点击卡片打开模态框
    card.addEventListener('click', function() {
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

// 初始化统计
function initStatistics() {
    renderStatistics();
}

// 渲染统计
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
    
    // 绘制图表（修改为按月份统计）
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
                    label: '竞赛数量',
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
                        text: '竞赛月份统计'
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
    const modal = document.getElementById('contest-modal');
    const closeBtn = document.getElementsByClassName('close')[0];
    
    if (!modal || !closeBtn) {
        console.error('modal或closeBtn元素不存在');
        return;
    }
    
    // 关闭模态框
    closeBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    // 点击模态框外部关闭
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // 收藏按钮
    const favoriteBtn = document.getElementById('favorite-btn');
    if (favoriteBtn) {
        favoriteBtn.addEventListener('click', function() {
            const contestUrl = this.dataset.url;
            toggleFavorite(contestUrl);
            this.textContent = isFavorite(contestUrl) ? '取消收藏' : '收藏';
        });
    }
    
    // 有用按钮
    const likeBtn = document.getElementById('like-btn');
    if (likeBtn) {
        likeBtn.addEventListener('click', function() {
            alert('感谢您的反馈！');
        });
    }
    
    // 无用按钮
    const dislikeBtn = document.getElementById('dislike-btn');
    if (dislikeBtn) {
        dislikeBtn.addEventListener('click', function() {
            alert('感谢您的反馈，我们会不断改进！');
        });
    }
}

// 打开竞赛详情模态框
function openContestModal(contest) {
    const modal = document.getElementById('contest-modal');
    
    if (!modal) {
        console.error('contest-modal元素不存在');
        return;
    }
    
    // 填充模态框内容
    const modalTitleEl = document.getElementById('modal-title');
    if (modalTitleEl) modalTitleEl.textContent = contest.title;
    
    const modalSourceEl = document.getElementById('modal-source');
    if (modalSourceEl) modalSourceEl.textContent = contest.source;
    
    const modalPublishTimeEl = document.getElementById('modal-publish-time');
    if (modalPublishTimeEl) modalPublishTimeEl.textContent = formatDate(contest.publish_time);
    
    const modalDeadlineEl = document.getElementById('modal-deadline');
    if (modalDeadlineEl) modalDeadlineEl.textContent = formatDate(contest.deadline) || '未知';
    
    const modalOrganizerEl = document.getElementById('modal-organizer');
    if (modalOrganizerEl) modalOrganizerEl.textContent = contest.organizer || '未知';
    
    const modalParticipantsEl = document.getElementById('modal-participants');
    if (modalParticipantsEl) modalParticipantsEl.textContent = contest.participants || '未知';
    
    const modalPrizeEl = document.getElementById('modal-prize');
    if (modalPrizeEl) modalPrizeEl.textContent = contest.prize || '未知';
    
    const modalContactEl = document.getElementById('modal-contact');
    if (modalContactEl) modalContactEl.textContent = contest.contact || '未知';
    
    const modalContentEl = document.getElementById('modal-content');
    if (modalContentEl) modalContentEl.textContent = contest.content || '无详细内容';
    
    const modalUrlEl = document.getElementById('modal-url');
    if (modalUrlEl) modalUrlEl.href = contest.url;
    

    
    // 显示模态框
    modal.style.display = 'block';
}
