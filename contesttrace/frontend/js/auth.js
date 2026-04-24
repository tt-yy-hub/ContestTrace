/**
 * 认证相关功能
 */

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    initAuthForm();
    initNavbarLoginStatus();
    initLoginModal();
});

// 初始化登录模态框
function initLoginModal() {
    // 切换到注册表单
    const switchToRegister = document.getElementById('switch-to-register-modal');
    if (switchToRegister) {
        switchToRegister.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('login-form-modal').style.display = 'none';
            document.getElementById('register-form-modal').style.display = 'block';
        });
    }

    // 切换到登录表单
    const switchToLogin = document.getElementById('switch-to-login-modal');
    if (switchToLogin) {
        switchToLogin.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('register-form-modal').style.display = 'none';
            document.getElementById('login-form-modal').style.display = 'block';
        });
    }

    // 登录按钮点击事件
    const loginButton = document.getElementById('login-button-modal');
    if (loginButton) {
        loginButton.addEventListener('click', function() {
            const username = document.getElementById('login-username-modal').value.trim();
            const password = document.getElementById('login-password-modal').value;
            const errorElement = document.getElementById('login-error-modal');

            if (!username || !password) {
                errorElement.textContent = '用户名和密码不能为空';
                return;
            }

            login(username, password).then(success => {
                if (success) {
                    closeLoginModal();
                    location.reload();
                } else {
                    errorElement.textContent = '用户名或密码错误';
                }
            });
        });
    }

    // 注册按钮点击事件
    const registerButton = document.getElementById('register-button-modal');
    if (registerButton) {
        registerButton.addEventListener('click', function() {
            const username = document.getElementById('register-username-modal').value.trim();
            const password = document.getElementById('register-password-modal').value;
            const confirmPassword = document.getElementById('register-confirm-password-modal').value;
            const errorElement = document.getElementById('register-error-modal');
            const successElement = document.getElementById('register-success-modal');

            if (!username || !password || !confirmPassword) {
                errorElement.textContent = '所有字段不能为空';
                successElement.textContent = '';
                return;
            }

            if (password !== confirmPassword) {
                errorElement.textContent = '两次输入的密码不一致';
                successElement.textContent = '';
                return;
            }

            register(username, password).then(success => {
                if (success) {
                    errorElement.textContent = '';
                    successElement.textContent = '注册成功，请登录';
                    setTimeout(() => {
                        document.getElementById('register-form-modal').style.display = 'none';
                        document.getElementById('login-form-modal').style.display = 'block';
                        successElement.textContent = '';
                    }, 2000);
                } else {
                    errorElement.textContent = '注册失败，用户名已存在';
                    successElement.textContent = '';
                }
            });
        });
    }

    // 关闭按钮点击事件
    const closeBtn = document.getElementById('close-login-modal');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeLoginModal);
    }

    // 点击模态框外部关闭
    const modal = document.getElementById('login-modal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeLoginModal();
            }
        });
    }
}

// 打开登录模态框
function openLoginModal() {
    const modal = document.getElementById('login-modal');
    if (modal) {
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        // 默认显示登录表单
        document.getElementById('login-form-modal').style.display = 'block';
        document.getElementById('register-form-modal').style.display = 'none';
        // 清除错误信息
        document.getElementById('login-error-modal').textContent = '';
        document.getElementById('register-error-modal').textContent = '';
        document.getElementById('register-success-modal').textContent = '';
    }
}

// 关闭登录模态框
function closeLoginModal() {
    const modal = document.getElementById('login-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// 初始化认证表单
function initAuthForm() {
    // 切换到注册表单
    const switchToRegister = document.getElementById('switch-to-register');
    if (switchToRegister) {
        switchToRegister.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('register-form').style.display = 'block';
        });
    }

    // 切换到登录表单
    const switchToLogin = document.getElementById('switch-to-login');
    if (switchToLogin) {
        switchToLogin.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('register-form').style.display = 'none';
            document.getElementById('login-form').style.display = 'block';
        });
    }

    // 登录按钮点击事件
    const loginButton = document.getElementById('login-button');
    if (loginButton) {
        loginButton.addEventListener('click', function() {
            const username = document.getElementById('login-username').value.trim();
            const password = document.getElementById('login-password').value;
            const errorElement = document.getElementById('login-error');

            if (!username || !password) {
                errorElement.textContent = '用户名和密码不能为空';
                return;
            }

            // 调用登录函数
            login(username, password).then(success => {
                if (success) {
                    // 登录成功，跳转到首页
                    window.location.href = 'index.html';
                } else {
                    errorElement.textContent = '用户名或密码错误';
                }
            });
        });
    }

    // 注册按钮点击事件
    const registerButton = document.getElementById('register-button');
    if (registerButton) {
        registerButton.addEventListener('click', function() {
            const username = document.getElementById('register-username').value.trim();
            const password = document.getElementById('register-password').value;
            const confirmPassword = document.getElementById('register-confirm-password').value;
            const errorElement = document.getElementById('register-error');
            const successElement = document.getElementById('register-success');

            if (!username || !password || !confirmPassword) {
                errorElement.textContent = '所有字段不能为空';
                successElement.textContent = '';
                return;
            }

            if (password !== confirmPassword) {
                errorElement.textContent = '两次输入的密码不一致';
                successElement.textContent = '';
                return;
            }

            // 调用注册函数
            register(username, password).then(success => {
                if (success) {
                    errorElement.textContent = '';
                    successElement.textContent = '注册成功，请登录';
                    // 3秒后切换到登录表单
                    setTimeout(() => {
                        document.getElementById('register-form').style.display = 'none';
                        document.getElementById('login-form').style.display = 'block';
                        successElement.textContent = '';
                    }, 3000);
                } else {
                    errorElement.textContent = '注册失败，用户名已存在';
                    successElement.textContent = '';
                }
            });
        });
    }
}

// 登录
function login(username, password) {
    return new Promise((resolve) => {
        // 模拟网络延迟
        setTimeout(() => {
            // 从 localStorage 读取用户列表
            const users = getFromLocalStorage('users', []);
            
            // 检查用户名和密码
            const user = users.find(u => u.username === username && u.password === password);
            
            if (user) {
                // 生成假 token
                const token = 'mock_token_' + Date.now();
                // 存储 token 和用户信息
                saveToLocalStorage('user_token', token);
                saveToLocalStorage('user_info', { username: user.username, id: user.id });
                saveToLocalStorage('is_logged_in', true);
                resolve(true);
            } else {
                resolve(false);
            }
        }, 500);
    });
}

// 注册
function register(username, password) {
    return new Promise((resolve) => {
        // 模拟网络延迟
        setTimeout(() => {
            // 从 localStorage 读取用户列表
            const users = getFromLocalStorage('users', []);
            
            // 检查用户名是否已存在
            if (users.some(u => u.username === username)) {
                resolve(false);
            } else {
                // 创建新用户
                const newUser = {
                    id: Date.now(),
                    username: username,
                    password: password,
                    createdAt: new Date().toISOString()
                };
                
                // 添加到用户列表
                users.push(newUser);
                // 保存回 localStorage
                saveToLocalStorage('users', users);
                
                // 生成假 token
                const token = 'mock_token_' + Date.now();
                // 存储 token 和用户信息
                saveToLocalStorage('user_token', token);
                saveToLocalStorage('user_info', { username: newUser.username, id: newUser.id });
                saveToLocalStorage('is_logged_in', true);
                resolve(true);
            }
        }, 500);
    });
}

// 登出
function logout() {
    // 清除 token 和用户信息
    localStorage.removeItem('user_token');
    localStorage.removeItem('user_info');
    localStorage.removeItem('is_logged_in');
    // 跳转到首页
    window.location.href = 'index.html';
}

// 检查登录状态
function checkLoginStatus() {
    return getFromLocalStorage('is_logged_in', false);
}

// 获取当前用户信息
function getCurrentUser() {
    return getFromLocalStorage('user_info', null);
}

// 获取 token
function getToken() {
    return getFromLocalStorage('user_token', null);
}

// 初始化导航栏登录状态
function initNavbarLoginStatus() {
    const isLoggedIn = checkLoginStatus();
    const userInfo = getCurrentUser();
    const nav = document.querySelector('.nav');
    
    if (nav) {
        // 移除现有的登录/注册按钮或用户信息
        const existingAuthElement = document.getElementById('auth-container');
        if (existingAuthElement) {
            existingAuthElement.remove();
        }
        
        // 创建新的认证容器
        const authContainer = document.createElement('div');
        authContainer.id = 'auth-container';

        if (isLoggedIn && userInfo) {
            // 已登录状态
            authContainer.innerHTML = `
                <span class="user-name">欢迎，${userInfo.username}</span>
                <button id="logout-button" class="logout-btn">
                    <i class="fas fa-sign-out-alt"></i> 退出
                </button>
            `;

            // 添加登出事件
            setTimeout(() => {
                const logoutButton = document.getElementById('logout-button');
                if (logoutButton) {
                    logoutButton.addEventListener('click', logout);
                }
            }, 0);
        } else {
            // 未登录状态
            authContainer.innerHTML = `
                <button class="login-btn" id="login-btn-nav">
                    <i class="fas fa-sign-in-alt"></i> 登录/注册
                </button>
            `;

            // 添加登录按钮事件
            setTimeout(() => {
                const loginBtnNav = document.getElementById('login-btn-nav');
                if (loginBtnNav) {
                    loginBtnNav.addEventListener('click', openLoginModal);
                }
            }, 0);
        }

        // 插入到铃铛容器右侧（在同一 flex 行上）
        const bellContainer = nav.querySelector('.reminder-bell-container');
        if (bellContainer) {
            bellContainer.insertAdjacentElement('afterend', authContainer);
        } else {
            nav.appendChild(authContainer);
        }
    }
}