/**
 * 用户认证和权限控制模块
 * 支持多用户群：访客、护士、医生、药师、管理员
 */

// 用户权限配置
const PERMISSIONS = {
    visitor: {
        name: '访客',
        level: 1,
        canView: ['basic_info'],
        canAccess: ['home', 'drug_search'],
        hiddenSections: ['dosage', 'contraindications', 'adverse_reactions', 'interactions', 'precautions', 'pharmacokinetics', 'solvent', 'workflow', 'guide']
    },
    nurse: {
        name: '护士',
        level: 2,
        // 护士只能看到：基础信息 + 用法用量 + 溶媒
        canView: ['basic_info', 'dosage_info'],
        canAccess: ['home', 'drug_search', 'favorites', 'history'],
        hiddenSections: ['contraindications', 'adverse_reactions', 'interactions', 'pharmacokinetics', 'workflow', 'guide']
    },
    doctor: {
        name: '医生',
        level: 3,
        // 医生可以看到：基础信息 + 用法用量 + 完整手册（除岗位手册外）
        canView: ['basic_info', 'dosage_info', 'full_manual'],
        canAccess: ['home', 'drug_search', 'favorites', 'history'],
        hiddenSections: ['workflow', 'guide']
    },
    pharmacist: {
        name: '药师',
        level: 4,
        canView: ['all'],
        canAccess: ['home', 'drug_search', 'favorites', 'history', 'workflow', 'guide'],
        hiddenSections: []
    },
    admin: {
        name: '管理员',
        level: 5,
        canView: ['all'],
        canAccess: ['all'],
        hiddenSections: []
    }
};

// 认证管理器
const AuthManager = {
    // 检查是否已登录
    isLoggedIn() {
        const userInfo = localStorage.getItem('userInfo');
        return !!userInfo;
    },

    // 获取当前用户信息
    getCurrentUser() {
        const userInfo = localStorage.getItem('userInfo');
        return userInfo ? JSON.parse(userInfo) : null;
    },

    // 获取当前用户权限
    getCurrentPermissions() {
        const user = this.getCurrentUser();
        if (!user) return PERMISSIONS.visitor;
        return PERMISSIONS[user.type] || PERMISSIONS.visitor;
    },

    // 检查是否有权限查看某部分
    canView(section) {
        const permissions = this.getCurrentPermissions();
        if (permissions.canView.includes('all')) return true;
        return permissions.canView.includes(section);
    },

    // 检查是否可以访问某页面/功能
    canAccess(feature) {
        const permissions = this.getCurrentPermissions();
        if (permissions.canAccess.includes('all')) return true;
        return permissions.canAccess.includes(feature);
    },

    // 检查某部分是否应该隐藏
    isHidden(section) {
        const permissions = this.getCurrentPermissions();
        return permissions.hiddenSections.includes(section);
    },

    // 登出
    logout() {
        localStorage.removeItem('userInfo');
        window.location.href = 'index.html';
    },

    // 初始化检查（在页面加载时调用）
    init() {
        // 检查是否在登录页面
        if (window.location.pathname.includes('index.html')) {
            return;
        }

        // 检查是否已登录
        if (!this.isLoggedIn()) {
            // 未登录，重定向到登录页
            window.location.href = 'index.html';
            return;
        }

        // 已登录，应用权限控制
        this.applyPermissions();
    },

    // 应用权限控制到页面
    applyPermissions() {
        const user = this.getCurrentUser();
        const permissions = this.getCurrentPermissions();

        // 显示用户信息
        this.showUserInfo(user, permissions);

        // 根据权限隐藏/显示内容
        this.filterContentByPermission(permissions);

        // 控制导航菜单
        this.filterNavigation(permissions);
    },

    // 显示用户信息
    showUserInfo(user, permissions) {
        console.log('[AuthManager] showUserInfo called for user:', user?.username);
        
        // 使用更严格的选择器删除所有已存在的用户信息栏
        const selectors = ['#userInfoBar', '.user-bar', '[id*="user"][id*="bar"]', '[class*="user"][class*="bar"]'];
        let removedCount = 0;
        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(bar => {
                console.log('[AuthManager] Removing existing bar:', bar.id || bar.className);
                bar.remove();
                removedCount++;
            });
        });
        console.log('[AuthManager] Total bars removed:', removedCount);

        // 再次检查确保没有残留
        const remaining = document.querySelectorAll('#userInfoBar, .user-bar');
        if (remaining.length > 0) {
            console.log('[AuthManager] Warning: Still found', remaining.length, 'bars, force removing...');
            remaining.forEach(bar => bar.remove());
        }

        // 创建用户信息栏
        const userBar = document.createElement('div');
        userBar.id = 'userInfoBar';
        userBar.className = 'user-bar';
        userBar.style.cssText = 'position:fixed;top:0;right:0;background:rgba(14,116,144,0.95);color:white;padding:8px 16px;border-radius:0 0 0 12px;font-size:13px;z-index:1000;display:flex;align-items:center;gap:12px;box-shadow:0 2px 8px rgba(0,0,0,0.2);';
        userBar.innerHTML = '<span>👤 ' + user.username + ' (' + permissions.name + ')</span><button onclick="AuthManager.logout()" style="background:rgba(255,255,255,0.2);border:none;color:white;padding:4px 12px;border-radius:4px;cursor:pointer;font-size:12px;">退出</button>';
        document.body.appendChild(userBar);
        console.log('[AuthManager] New user bar created');

        // 调整header的padding-top，为用户信息栏留出空间
        const header = document.querySelector('.header');
        if (header) {
            header.style.paddingTop = '50px';
        }
    },

    // 根据权限过滤内容
    filterContentByPermission(permissions) {
        // 在药品详情中，根据权限隐藏某些章节
        const originalRenderDrugDetail = window.renderDrugDetail;
        if (originalRenderDrugDetail) {
            window.renderDrugDetail = function(drug) {
                // 先调用原函数
                const html = originalRenderDrugDetail(drug);

                // 如果用户有全部权限，直接返回
                if (permissions.canView.includes('all')) {
                    return html;
                }

                // 否则，在显示前过滤内容
                return html;
            };
        }
    },

    // 过滤导航菜单
    filterNavigation(permissions) {
        // 获取底部导航
        const bottomNav = document.querySelector('.bottom-nav');
        if (!bottomNav) return;

        const navItems = bottomNav.querySelectorAll('.nav-item');

        navItems.forEach(item => {
            const tab = item.dataset.tab;

            // 检查是否有权限访问该tab
            if (!permissions.canAccess.includes(tab) && !permissions.canAccess.includes('all')) {
                item.style.display = 'none';
            }
        });
    },

    // 获取权限提示信息
    getPermissionMessage() {
        const permissions = this.getCurrentPermissions();
        const messages = {
            visitor: '您当前以访客身份登录，仅可查看基础药品信息。如需更多功能，请联系管理员。',
            nurse: '您当前以护士身份登录，可查看药品基础信息和用法用量。',
            doctor: '您当前以医生身份登录，可查看完整药品手册。',
            pharmacist: '您当前以药师身份登录，可查看所有内容包括岗位手册。',
            admin: '您当前以管理员身份登录，拥有所有权限。'
        };
        return messages[this.getCurrentUser()?.type] || messages.visitor;
    }
};

// 页面加载时初始化认证 - 使用标志防止重复初始化
(function() {
    if (window.authManagerInitialized) {
        console.log('[AuthManager] Already initialized, skipping...');
        return;
    }
    
    document.addEventListener('DOMContentLoaded', function() {
        if (window.authManagerInitialized) {
            console.log('[AuthManager] Already initialized in DOMContentLoaded, skipping...');
            return;
        }
        window.authManagerInitialized = true;
        console.log('[AuthManager] Initializing...');
        AuthManager.init();
        console.log('[AuthManager] Initialization complete');
    });
})();

// 导出供其他模块使用
window.AuthManager = AuthManager;
window.PERMISSIONS = PERMISSIONS;
