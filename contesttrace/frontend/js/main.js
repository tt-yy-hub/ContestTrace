/**
 * 主逻辑
 */

let allContests = [];
let currentPage = 1;
const pageSize = 10;

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', async function() {
    // 加载竞赛数据
    allContests = await loadContests();
    
    // 初始化页面
    initNavigation();
    initSearch();
    initContestList();
    initRecommendations();
    initStatistics();
    initSettings();
    initModal();
    
    // 请求通知权限
    requestNotificationPermission();
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
    const searchBtn = document.getElementById('search-btn');
    const searchInput = document.getElementById('search-input');
    const filterCategory = document.getElementById('filter-category');
    
    searchBtn.addEventListener('click', function() {
        currentPage = 1;
        renderContestList();
    });
    
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            currentPage = 1;
            renderContestList();
        }
    });
    
    filterCategory.addEventListener('change', function() {
        currentPage = 1;
        renderContestList();
    });
}

// 初始化竞赛列表
function initContestList() {
    renderContestList();
}

// 渲染竞赛列表
function renderContestList() {
    const contestList = document.getElementById('contest-list');
    const pagination = document.getElementById('pagination');
    
    // 获取搜索和筛选条件
    const searchQuery = document.getElementById('search-input').value;
    const categoryFilter = document.getElementById('filter-category').value;
    
    // 筛选竞赛
    const filteredContests = searchContests(allContests, searchQuery, categoryFilter);
    
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
    renderPagination(pagination, totalPages);
}

// 创建竞赛卡片
function createContestCard(contest) {
    const card = document.createElement('div');
    card.className = 'contest-card';
    
    const daysLeft = calculateDaysLeft(contest.deadline);
    const daysLeftClass = getDaysLeftClass(daysLeft);
    const daysLeftText = getDaysLeftText(daysLeft);
    
    card.innerHTML = `
        <h3>${contest.title}</h3>
        <div class="meta">
            <span>${contest.source}</span> | 
            <span>${formatDate(contest.publish_time)}</span>
        </div>
        <p class="summary">${contest.summary}</p>
        <div class="tags">
            ${contest.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
        </div>
        <div class="deadline ${daysLeftClass}">
            ${daysLeftText}
        </div>
    `;
    
    // 点击卡片打开模态框
    card.addEventListener('click', function() {
        openContestModal(contest);
    });
    
    return card;
}

// 渲染分页控件
function renderPagination(pagination, totalPages) {
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
    document.getElementById('total-contests').textContent = stats.total;
    
    // 分类统计图表
    const categoryCtx = document.getElementById('category-chart').getContext('2d');
    new Chart(categoryCtx, {
        type: 'pie',
        data: {
            labels: Object.keys(stats.categoryStats),
            datasets: [{
                data: Object.values(stats.categoryStats),
                backgroundColor: [
                    '#3498db',
                    '#e74c3c',
                    '#f39c12',
                    '#27ae60',
                    '#9b59b6'
                ]
            }]
        },
        options: {
            responsive: true
        }
    });
    
    // 月份统计图表
    const monthCtx = document.getElementById('month-chart').getContext('2d');
    const monthLabels = Object.keys(stats.monthStats).sort();
    const monthData = monthLabels.map(month => stats.monthStats[month]);
    
    new Chart(monthCtx, {
        type: 'bar',
        data: {
            labels: monthLabels,
            datasets: [{
                label: '竞赛数量',
                data: monthData,
                backgroundColor: '#3498db'
            }]
        },
        options: {
            responsive: true,
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
    document.getElementById('favorite-btn').addEventListener('click', function() {
        const contestUrl = this.dataset.url;
        toggleFavorite(contestUrl);
        this.textContent = isFavorite(contestUrl) ? '取消收藏' : '收藏';
    });
    
    // 有用按钮
    document.getElementById('like-btn').addEventListener('click', function() {
        alert('感谢您的反馈！');
    });
    
    // 无用按钮
    document.getElementById('dislike-btn').addEventListener('click', function() {
        alert('感谢您的反馈，我们会不断改进！');
    });
}

// 打开竞赛详情模态框
function openContestModal(contest) {
    const modal = document.getElementById('contest-modal');
    
    // 填充模态框内容
    document.getElementById('modal-title').textContent = contest.title;
    document.getElementById('modal-source').textContent = contest.source;
    document.getElementById('modal-publish-time').textContent = formatDate(contest.publish_time);
    document.getElementById('modal-deadline').textContent = formatDate(contest.deadline);
    document.getElementById('modal-category').textContent = contest.category;
    document.getElementById('modal-organizer').textContent = contest.organizer || '未知';
    document.getElementById('modal-participants').textContent = contest.participants || '未知';
    document.getElementById('modal-prize').textContent = contest.prize || '未知';
    document.getElementById('modal-contact').textContent = contest.contact || '未知';
    document.getElementById('modal-summary').textContent = contest.summary;
    document.getElementById('modal-link').href = contest.url;
    
    // 剩余天数
    const daysLeft = calculateDaysLeft(contest.deadline);
    const daysLeftClass = getDaysLeftClass(daysLeft);
    const daysLeftText = getDaysLeftText(daysLeft);
    const daysLeftElement = document.getElementById('modal-days-left');
    daysLeftElement.textContent = daysLeftText;
    daysLeftElement.className = `days-left ${daysLeftClass}`;
    
    // 标签
    const tagsElement = document.getElementById('modal-tags');
    tagsElement.innerHTML = contest.tags.map(tag => `<span class="tag">${tag}</span>`).join('');
    
    // 设置收藏按钮状态
    const favoriteBtn = document.getElementById('favorite-btn');
    favoriteBtn.dataset.url = contest.url;
    favoriteBtn.textContent = isFavorite(contest.url) ? '取消收藏' : '收藏';
    
    // 显示模态框
    modal.style.display = 'block';
}
