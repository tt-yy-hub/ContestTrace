/**
 * 统计页面逻辑
 */

let allContests = [];

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', async function() {
    try {
        // 加载竞赛数据
        allContests = await loadContests();
        console.log('数据加载成功，共', allContests.length, '条竞赛');
        
        // 渲染统计信息
        renderStatistics();
    } catch (error) {
        console.error('初始化失败:', error);
    }
});

// 渲染统计信息
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
    
    // 收藏总数
    const totalFavoritesEl = document.getElementById('total-favorites');
    if (totalFavoritesEl) {
        const favorites = loadFavorites();
        totalFavoritesEl.textContent = favorites.length;
    }
    
    // 即将截止的收藏数
    const upcomingDeadlinesEl = document.getElementById('upcoming-deadlines');
    if (upcomingDeadlinesEl) {
        const favorites = loadFavorites();
        const upcomingCount = favorites.filter(contest => {
            const daysLeft = calculateDaysLeft(contest.deadline);
            return daysLeft >= 0 && daysLeft <= 3;
        }).length;
        upcomingDeadlinesEl.textContent = upcomingCount;
    }
    
    // 绘制图表（按月份统计）
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
                    label: '公告数量',
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
                        text: '竞赛公告月份统计'
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
    
    // 渲染热门竞赛榜单
    renderHotContests();
}

// 渲染热门竞赛榜单
function renderHotContests() {
    const container = document.getElementById('hot-contests-container');
    if (!container) return;
    
    // 获取热门竞赛
    const hotContests = getHotContests(10);
    
    if (hotContests.length === 0) {
        container.innerHTML = '<p class="no-data">暂无热门竞赛数据</p>';
        return;
    }
    
    // 渲染热门竞赛列表
    container.innerHTML = '';
    hotContests.forEach((contest, index) => {
        const card = document.createElement('div');
        card.className = 'hot-contest-card';
        card.innerHTML = `
            <div class="rank">${index + 1}</div>
            <div class="hot-contest-content">
                <h4><a href="#" class="contest-title">${contest.title}</a></h4>
                <p class="contest-source">${contest.source}</p>
                <p class="contest-deadline">${contest.deadline || '无截止日期'}</p>
                <div class="hotness">热度: ${contest.hotness}</div>
            </div>
        `;
        
        // 添加点击事件
        const titleLink = card.querySelector('.contest-title');
        titleLink.addEventListener('click', function(e) {
            e.preventDefault();
            openContestModal(contest);
        });
        
        container.appendChild(card);
    });
}

// 打开竞赛详情模态框
function openContestModal(contest) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'contest-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close">&times;</span>
            <h2 id="modal-title">${contest.title}</h2>
            <div class="modal-body">
                <div class="info-item">
                    <span class="label">来源：</span>
                    <span id="modal-source">${contest.source}</span>
                </div>
                <div class="info-item">
                    <span class="label">发布时间：</span>
                    <span id="modal-publish-time">${formatDate(contest.publish_time)}</span>
                </div>
                <div class="info-item">
                    <span class="label">截止时间：</span>
                    <span id="modal-deadline">${contest.deadline || '无'}</span>
                </div>
                <div class="info-item">
                    <span class="label">组织者：</span>
                    <span id="modal-organizer">${contest.organizer || '未知'}</span>
                </div>
                <div class="info-item">
                    <span class="label">参赛对象：</span>
                    <span id="modal-participants">${contest.participants || '未知'}</span>
                </div>
                <div class="info-item">
                    <span class="label">奖项设置：</span>
                    <span id="modal-prize">${contest.prize || '未知'}</span>
                </div>
                <div class="info-item">
                    <span class="label">联系方式：</span>
                    <span id="modal-contact">${contest.contact || '未知'}</span>
                </div>
                <div class="info-item">
                    <span class="label">原文链接：</span>
                    <div class="url-note-container">
                        <a id="modal-url" href="${contest.url}" target="_blank" class="url-btn-small">
                            <i class="fas fa-external-link-alt"></i> 查看原文
                        </a>
                        <p class="note">以上内容仅供参考，详情请查看原文</p>
                    </div>
                </div>
                <div class="info-item">
                    <span class="label">详细内容：</span>
                    <p id="modal-content">${contest.content || '无详细内容'}</p>
                </div>
                <div class="modal-actions">
                    <button id="favorite-btn" data-url="${contest.url}">
                        ${isFavorite(contest.url) ? '<i class="fas fa-star"></i> 取消收藏' : '<i class="far fa-star"></i> 收藏'}
                    </button>
                    <button id="like-btn">
                        <i class="far fa-thumbs-up"></i> 有用
                    </button>
                    <button id="dislike-btn">
                        <i class="far fa-thumbs-down"></i> 无用
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // 显示模态框
    modal.style.display = 'block';
    
    // 关闭按钮
    const closeBtn = modal.querySelector('.close');
    closeBtn.addEventListener('click', function() {
        modal.style.display = 'none';
        setTimeout(() => {
            document.body.removeChild(modal);
        }, 300);
    });
    
    // 点击模态框外部关闭
    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
            setTimeout(() => {
                document.body.removeChild(modal);
            }, 300);
        }
    });
    
    // 收藏按钮
    const favoriteBtn = modal.querySelector('#favorite-btn');
    favoriteBtn.addEventListener('click', function() {
        const contestUrl = this.dataset.url;
        toggleFavorite(contestUrl);
        this.innerHTML = isFavorite(contestUrl) ? '<i class="fas fa-star"></i> 取消收藏' : '<i class="far fa-star"></i> 收藏';
    });
    
    // 有用按钮
    const likeBtn = modal.querySelector('#like-btn');
    likeBtn.addEventListener('click', function() {
        alert('感谢您的反馈！');
    });
    
    // 无用按钮
    const dislikeBtn = modal.querySelector('#dislike-btn');
    dislikeBtn.addEventListener('click', function() {
        alert('感谢您的反馈，我们会不断改进！');
    });
}