/**
 * 收藏同步功能
 */

// 同步收藏到云端
function syncFavoritesToCloud() {
    return new Promise((resolve) => {
        // 检查登录状态
        const isLoggedIn = getFromLocalStorage('is_logged_in', false);
        if (!isLoggedIn) {
            resolve(false);
            return;
        }

        // 加载本地收藏
        const localFavorites = loadFavorites();
        
        // 模拟网络延迟
        setTimeout(() => {
            // 模拟云端存储，使用 localStorage 的另一个字段
            saveToLocalStorage('cloud_favorites', localFavorites);
            // 记录同步时间
            saveToLocalStorage('last_sync_time', new Date().toISOString());
            resolve(true);
        }, 500);
    });
}

// 从云端拉取收藏
function fetchFavoritesFromCloud() {
    return new Promise((resolve) => {
        // 检查登录状态
        const isLoggedIn = getFromLocalStorage('is_logged_in', false);
        if (!isLoggedIn) {
            resolve([]);
            return;
        }

        // 模拟网络延迟
        setTimeout(() => {
            // 从模拟的云端存储中获取收藏
            const cloudFavorites = getFromLocalStorage('cloud_favorites', []);
            resolve(cloudFavorites);
        }, 500);
    });
}

// 合并本地和云端收藏
function mergeFavorites(localFavorites, cloudFavorites) {
    // 创建一个以竞赛 ID 为键的映射
    const mergedMap = new Map();
    
    // 先添加本地收藏
    localFavorites.forEach(fav => {
        mergedMap.set(fav.id, fav);
    });
    
    // 再添加云端收藏，覆盖本地收藏（云端优先）
    cloudFavorites.forEach(fav => {
        mergedMap.set(fav.id, fav);
    });
    
    // 转换回数组
    return Array.from(mergedMap.values());
}

// 同步收藏（双向）
async function syncFavorites() {
    // 检查登录状态
    const isLoggedIn = getFromLocalStorage('is_logged_in', false);
    if (!isLoggedIn) {
        return false;
    }

    try {
        // 从云端拉取收藏
        const cloudFavorites = await fetchFavoritesFromCloud();
        // 加载本地收藏
        const localFavorites = loadFavorites();
        // 合并收藏
        const mergedFavorites = mergeFavorites(localFavorites, cloudFavorites);
        // 保存合并后的收藏
        saveFavorites(mergedFavorites);
        // 同步回云端
        await syncFavoritesToCloud();
        return true;
    } catch (error) {
        console.error('同步收藏失败:', error);
        return false;
    }
}

// 初始化同步功能
function initSync() {
    // 检查登录状态
    const isLoggedIn = getFromLocalStorage('is_logged_in', false);
    if (isLoggedIn) {
        // 登录后自动同步
        syncFavorites().then(success => {
            if (success) {
                console.log('收藏同步成功');
            } else {
                console.log('收藏同步失败');
            }
        });
    }
}

// 添加同步按钮到收藏页面
function addSyncButton() {
    const container = document.querySelector('.filter-bar');
    if (container) {
        const syncButton = document.createElement('button');
        syncButton.id = 'sync-favorites';
        syncButton.style.marginLeft = '10px';
        syncButton.style.padding = '8px 12px';
        syncButton.style.backgroundColor = '#4CAF50';
        syncButton.style.color = 'white';
        syncButton.style.border = 'none';
        syncButton.style.borderRadius = '4px';
        syncButton.style.cursor = 'pointer';
        syncButton.style.display = 'flex';
        syncButton.style.alignItems = 'center';
        syncButton.innerHTML = '<i class="fas fa-sync"></i> 同步收藏';
        
        syncButton.addEventListener('click', async function() {
            const isLoggedIn = getFromLocalStorage('is_logged_in', false);
            if (!isLoggedIn) {
                alert('请先登录后再同步收藏');
                return;
            }
            
            // 显示加载状态
            const originalText = syncButton.innerHTML;
            syncButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 同步中...';
            syncButton.disabled = true;
            
            // 执行同步
            const success = await syncFavorites();
            
            // 恢复按钮状态
            syncButton.innerHTML = originalText;
            syncButton.disabled = false;
            
            // 显示结果
            if (success) {
                alert('收藏同步成功');
                // 重新渲染收藏列表
                if (typeof renderFavorites === 'function') {
                    renderFavorites();
                }
            } else {
                alert('收藏同步失败');
            }
        });
        
        container.appendChild(syncButton);
    }
}

// 监听登录状态变化
window.addEventListener('storage', function(e) {
    if (e.key === 'is_logged_in' || e.key === 'user_token') {
        initSync();
    }
});