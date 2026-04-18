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
}