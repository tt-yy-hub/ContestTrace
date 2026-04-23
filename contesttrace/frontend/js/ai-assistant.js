(function() {
    const aiButton = document.getElementById('ai-float-button');
    const aiDialog = document.getElementById('ai-chat-dialog');
    const dialogHeader = document.getElementById('ai-dialog-header');
    const dialogClose = document.getElementById('ai-dialog-close');
    const aiInput = document.getElementById('ai-input');
    const aiSendBtn = document.getElementById('ai-send-btn');
    const dialogBody = document.getElementById('ai-dialog-body');

    if (!aiButton || !aiDialog || !dialogHeader || !dialogClose || !aiInput || !aiSendBtn || !dialogBody) {
        return;
    }

    const PROFILE_KEY = 'ai_assistant_profile_v2';
    const DIALOG_SIZE_KEY = 'ai_assistant_dialog_size_v1';
    const CLASSIFY_CACHE_KEY = 'ai_contest_classify_cache_v1';
    const RECENT_ACTION_KEY = 'contest_action_log';
    const HOTNESS_KEY = 'contest_hotness';
    const MAX_RECOMMEND = 6;
    const INTEREST_CLICK_THROTTLE_MS = 800;
    const DIALOG_INTEREST_CHIPS = [
        { label: '文体体育', value: '文体体育类赛事活动' },
        { label: '心理思政', value: '心理健康&思政德育类活动' },
        { label: '英语外语', value: '英语外语学科竞赛' },
        { label: '数学统计', value: '数学建模、统计调研类专业竞赛' },
        { label: '经管商科', value: '经管商科、企业运营模拟类竞赛' },
        { label: '计算机设计', value: '计算机、软件、数字设计艺术类竞赛' },
        { label: '创新创业A类', value: '创新创业高水平A+/A类竞赛' },
        { label: 'A/A+目录', value: 'A/A+官方权威学科竞赛目录' },
        { label: '教务学业', value: '教务管理、竞赛统筹、学业相关通知' }
    ];
    const REFERENCE_YEAR = 2026;
    const REFERENCE_MONTH = 4;
    const SAIXING_KB = [
        { name: '会计学院2025年羽毛球赛', category: '文体体育类赛事活动', tags: ['文体体育', '会计学院'], level: '院级', time: '2025年', year: 2025 },
        { name: '各学院第二十二届田径运动会预选赛及全校体育运动会', category: '文体体育类赛事活动', tags: ['文体体育'], level: '校级', time: '2025年', year: 2025 },
        { name: '2025年“青春歌行”五四歌咏比赛', category: '文体体育类赛事活动', tags: ['文体体育', '思政德育'], level: '校级', time: '2025年5月', year: 2025 },
        { name: '“匠影定格：最美劳动瞬间”校园摄影大赛', category: '文体体育类赛事活动', tags: ['文体体育', '艺术设计'], level: '校级', time: '2025年', year: 2025 },
        { name: '旅游与酒店管理学院第二届导游风采大赛', category: '文体体育类赛事活动', tags: ['文体体育', '经管商科'], level: '院级', time: '2025年', year: 2025 },
        { name: '旅游与酒店管理学院2025年烹饪大赛', category: '文体体育类赛事活动', tags: ['文体体育'], level: '院级', time: '2025年', year: 2025 },
        { name: '第二十三届“藏龙杯”健康之星心理知识大赛', category: '心理健康&思政德育类活动', tags: ['心理健康', '思政德育'], level: '校级', time: '2025年', year: 2025 },
        { name: '第九届“十佳心委”评选大赛', category: '心理健康&思政德育类活动', tags: ['心理健康'], level: '校级', time: '2025年', year: 2025 },
        { name: '会计学院第一届心理健康教育微课大赛作品征集', category: '心理健康&思政德育类活动', tags: ['心理健康', '思政德育', '会计学院'], level: '院级', time: '2025年', year: 2025 },
        { name: '“传承红色基因，续写青春华章”主题微团课大赛', category: '心理健康&思政德育类活动', tags: ['思政德育', '会计学院'], level: '院级/校级', time: '2025年', year: 2025 },
        { name: '会计学院2025年红色文化科普讲解案例大赛', category: '心理健康&思政德育类活动', tags: ['思政德育', '会计学院'], level: '院级', time: '2025年', year: 2025 },
        { name: '2025年清廉教育主题系列活动', category: '心理健康&思政德育类活动', tags: ['思政德育'], level: '校级', time: '2025年', year: 2025 },
        { name: '第二届/第三届“浩然杯”读书演讲大赛', category: '心理健康&思政德育类活动', tags: ['思政德育', '演讲'], level: '校级', time: '2025年', year: 2025 },
        { name: '全国大学生英语竞赛（NECCS）', category: '英语外语学科竞赛', tags: ['英语外语'], level: '国家级 B类', time: '2025年4月初赛', year: 2025 },
        { name: '第30-31届中国日报社“21世纪杯”全国英语演讲比赛校园选拔赛', category: '英语外语学科竞赛', tags: ['英语外语', '演讲'], level: '国家级', time: '2025年', year: 2025 },
        { name: '2025“外研社•国才杯”“理解当代中国”全国大学生外语能力大赛校赛', category: '英语外语学科竞赛', tags: ['英语外语', '思政德育'], level: 'A类', time: '2025年5-10月', year: 2025 },
        { name: '全国大学生统计建模大赛', category: '数学建模、统计调研类专业竞赛', tags: ['数学统计', '经管商科'], level: '国家级', time: '2025年', year: 2025 },
        { name: '湖北经济学院2025年大学生数学建模校内赛', category: '数学建模、统计调研类专业竞赛', tags: ['数学统计'], level: '校级', time: '2025年', year: 2025 },
        { name: '全国大学生数学竞赛选拔测试', category: '数学建模、统计调研类专业竞赛', tags: ['数学统计'], level: '省级/国家级', time: '2025年', year: 2025 },
        { name: '“正大杯”全国大学生市场调查与分析大赛', category: '数学建模、统计调研类专业竞赛', tags: ['数学统计', '经管商科'], level: '国家级 B类', time: '2025年', year: 2025 },
        { name: '湖北省/全国企业竞争模拟大赛校赛', category: '经管商科、企业运营模拟类竞赛', tags: ['经管商科', '创新创业'], level: '省级/国家级', time: '2025年', year: 2025 },
        { name: '中国大学生工程实践与创新能力大赛虚拟仿真赛道企业运营仿真赛项校赛', category: '经管商科、企业运营模拟类竞赛', tags: ['经管商科'], level: '国家级 A类', time: '2025年', year: 2025 },
        { name: '“新青年吴兴杯”全国大学生物流设计大赛校内选拔赛', category: '经管商科、企业运营模拟类竞赛', tags: ['经管商科'], level: '国家级', time: '2025年', year: 2025 },
        { name: '工商管理学院2025年度竞赛备赛预通知', category: '经管商科、企业运营模拟类竞赛', tags: ['经管商科'], level: '院级通知', time: '2025年', year: 2025 },
        { name: '2026年（19届）中国大学生计算机设计大赛校赛', category: '计算机、软件、数字设计艺术类竞赛', tags: ['计算机设计', '艺术设计', '心理健康', '思政德育'], level: 'A类', time: '2026年3-5月', year: 2026 },
        { name: '蓝桥杯全国大学生软件和信息技术专业人才大赛', category: '计算机、软件、数字设计艺术类竞赛', tags: ['计算机设计', '艺术设计'], level: 'A类', time: '2025年', year: 2025 },
        { name: '米兰设计周-中国高校设计学科师生优秀作品展', category: '计算机、软件、数字设计艺术类竞赛', tags: ['艺术设计'], level: 'A类', time: '2025年', year: 2025 },
        { name: '两岸新锐设计竞赛·华灿奖', category: '计算机、软件、数字设计艺术类竞赛', tags: ['艺术设计'], level: 'A类', time: '2025年', year: 2025 },
        { name: '中国好创意暨全国数字艺术设计大赛', category: '计算机、软件、数字设计艺术类竞赛', tags: ['艺术设计'], level: 'A类', time: '2025年', year: 2025 },
        { name: '2026年“挑战杯”大学生创业计划竞赛校级选拔赛', category: '创新创业高水平A+/A类竞赛', tags: ['创新创业', 'A+目录'], level: 'A+', time: '2026年', year: 2026 },
        { name: '第十五届“挑战杯”湖北省大学生课外学术科技作品竞赛', category: '创新创业高水平A+/A类竞赛', tags: ['创新创业', '思政德育', 'A+目录'], level: 'A+', time: '2025年', year: 2025 },
        { name: '中国国际大学生创新大赛（2026）', category: '创新创业高水平A+/A类竞赛', tags: ['创新创业', 'A+目录'], level: 'A+', time: '2026年', year: 2026 },
        { name: '大学生数据要素素质大赛、大学生职业规划大赛', category: '教务管理、竞赛统筹、学业相关通知', tags: ['教务学业'], level: '校级通知', time: '2025年', year: 2025 },
        { name: '各类竞赛指南、奖励申报、免考通知等', category: '教务管理、竞赛统筹、学业相关通知', tags: ['教务学业'], level: '教务通知', time: '2025年', year: 2025 }
    ];
    const REASON_BANNED_PATTERNS = [
        /和你最近点击的兴趣方向比较一致/g,
        /和你最近点击的兴趣方向比较匹配/g,
        /和你最近的兴趣方向一致/g,
        /上手快，适合本学期尽快出成果/g,
        /含金量高，但要预留更完整的备赛周期/g,
        /规则清晰，准备路径相对明确/g,
        /偏向.{0,8}(表现|能力|表达)/g
    ];
    const MAJOR_CATEGORY_MAP = [
        {
            majorPattern: /金融|会计|经济|经贸|工商管理/,
            high: ['经管商科、企业运营模拟类竞赛', '创新创业高水平A+/A类竞赛', '数学建模、统计调研类专业竞赛'],
            mid: ['英语外语学科竞赛', '心理健康&思政德育类活动'],
            low: ['计算机、软件、数字设计艺术类竞赛', '文体体育类赛事活动']
        },
        {
            majorPattern: /计算机|软件|信息工程|信息管理/,
            high: ['计算机、软件、数字设计艺术类竞赛', '数学建模、统计调研类专业竞赛'],
            mid: ['创新创业高水平A+/A类竞赛', '经管商科、企业运营模拟类竞赛'],
            low: ['文体体育类赛事活动']
        },
        {
            majorPattern: /艺术|设计/,
            high: ['计算机、软件、数字设计艺术类竞赛'],
            mid: ['创新创业高水平A+/A类竞赛', '文体体育类赛事活动'],
            low: ['数学建模、统计调研类专业竞赛']
        }
    ];

    const CATEGORY_RULES = [
        { id: 'sports_art', name: '文体体育类赛事活动', keywords: ['羽毛球', '田径', '运动会', '歌咏', '摄影', '导游风采', '烹饪', '文体', '体育', '艺术活动'] },
        { id: 'mental_ideology', name: '心理健康&思政德育类活动', keywords: ['心理', '藏龙杯', '十佳心委', '微课', '红色', '团课', '清廉', '思政', '德育', '读书演讲', '浩然杯'] },
        { id: 'english_foreign', name: '英语外语学科竞赛', keywords: ['英语', '外语', '21世纪杯', '外研社', '国才杯', '演讲', '翻译', '听力'] },
        { id: 'math_stats', name: '数学建模、统计调研类专业竞赛', keywords: ['数学建模', '数学竞赛', '统计建模', '调查与分析', '正大杯', '统计', '建模'] },
        { id: 'business_sim', name: '经管商科、企业运营模拟类竞赛', keywords: ['企业竞争模拟', '企业运营仿真', '物流设计', '工商管理', '商科', '运营模拟', '工程实践'] },
        { id: 'cs_design', name: '计算机、软件、数字设计艺术类竞赛', keywords: ['计算机设计', '蓝桥杯', '信息技术', '米兰设计周', '华灿奖', '数字艺术', '视觉艺术', '设计竞赛'] },
        { id: 'innovation_a', name: '创新创业高水平A+/A类竞赛', keywords: ['挑战杯', '中国国际大学生创新大赛', '创新创业', '学术科技作品'] },
        { id: 'official_catalog', name: 'A/A+官方权威学科竞赛目录', keywords: ['A+', 'A类', '官方目录', 'NCDA', '广告艺术', '三维数字化', '数字媒体科技作品', '电子商务'] },
        { id: 'academic_admin', name: '教务管理、竞赛统筹、学业相关通知', keywords: ['教务', '指南编制', '教师教学竞赛', '工作量填报', '免考', '奖励申报', '职业规划', '数据要素'] }
    ];

    const LEVEL_RULES = [
        { level: 'A+', keywords: ['挑战杯', '中国国际大学生创新大赛'] },
        { level: 'A', keywords: ['蓝桥杯', '计算机设计大赛', '华灿奖', '米兰设计周', 'NCDA', '广告艺术', '三维数字化', '电子商务'] }
    ];

    let isDraggingButton = false;
    let isDraggingDialog = false;
    let dragOffsetX = 0;
    let dragOffsetY = 0;
    let isDialogOpen = false;
    let hasMoved = false;
    let buttonDialogOffsetX = -50;
    let buttonDialogOffsetY = -50;
    let contestPoolPromise = null;
    let lastInterestClickTs = 0;
    let isResizingDialog = false;
    let resizeStartX = 0;
    let resizeStartY = 0;
    let resizeStartW = 0;
    let resizeStartH = 0;
    let resizeHandleEl = null;

    function initButtonPosition() {
        aiButton.style.left = (window.innerWidth - 70) + 'px';
        aiButton.style.top = (window.innerHeight - 70) + 'px';
        aiButton.style.right = 'auto';
        aiButton.style.bottom = 'auto';
    }

    function clampDialogPosition() {
        const rect = aiDialog.getBoundingClientRect();
        const maxX = Math.max(0, window.innerWidth - rect.width);
        const maxY = Math.max(0, window.innerHeight - rect.height);
        const x = Math.max(0, Math.min(rect.left, maxX));
        const y = Math.max(0, Math.min(rect.top, maxY));
        aiDialog.style.left = x + 'px';
        aiDialog.style.top = y + 'px';
    }

    function getDialogSizeBounds() {
        return {
            minW: 320,
            minH: 360,
            maxW: Math.max(320, window.innerWidth - 20),
            maxH: Math.max(360, window.innerHeight - 20)
        };
    }

    function saveDialogSize() {
        const payload = {
            width: aiDialog.offsetWidth,
            height: aiDialog.offsetHeight
        };
        localStorage.setItem(DIALOG_SIZE_KEY, JSON.stringify(payload));
    }

    function setDialogSize(width, height, persist) {
        const b = getDialogSizeBounds();
        const w = Math.max(b.minW, Math.min(width, b.maxW));
        const h = Math.max(b.minH, Math.min(height, b.maxH));
        aiDialog.style.width = w + 'px';
        aiDialog.style.height = h + 'px';
        clampDialogPosition();
        if (persist) saveDialogSize();
    }

    function restoreDialogSize() {
        const raw = localStorage.getItem(DIALOG_SIZE_KEY);
        if (!raw) return;
        try {
            const size = JSON.parse(raw);
            if (!size || !size.width || !size.height) return;
            setDialogSize(Number(size.width), Number(size.height), false);
        } catch (e) {
            // ignore broken storage
        }
    }

    function setupResizeControls() {
        if (dialogHeader.querySelector('.ai-resize-tools')) return;

        const tools = document.createElement('div');
        tools.className = 'ai-resize-tools';

        const zoomOutBtn = document.createElement('button');
        zoomOutBtn.type = 'button';
        zoomOutBtn.className = 'ai-resize-btn';
        zoomOutBtn.textContent = '缩小';
        zoomOutBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            setDialogSize(aiDialog.offsetWidth - 36, aiDialog.offsetHeight - 48, true);
        });

        const zoomInBtn = document.createElement('button');
        zoomInBtn.type = 'button';
        zoomInBtn.className = 'ai-resize-btn';
        zoomInBtn.textContent = '放大';
        zoomInBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            setDialogSize(aiDialog.offsetWidth + 36, aiDialog.offsetHeight + 48, true);
        });

        tools.appendChild(zoomOutBtn);
        tools.appendChild(zoomInBtn);
        dialogHeader.insertBefore(tools, dialogClose);

        resizeHandleEl = document.createElement('div');
        resizeHandleEl.className = 'ai-resize-handle';
        resizeHandleEl.title = '拖拽调整大小';
        aiDialog.appendChild(resizeHandleEl);

        resizeHandleEl.addEventListener('mousedown', function(e) {
            if (e.button !== 0) return;
            isResizingDialog = true;
            resizeStartX = e.clientX;
            resizeStartY = e.clientY;
            resizeStartW = aiDialog.offsetWidth;
            resizeStartH = aiDialog.offsetHeight;
            e.preventDefault();
            e.stopPropagation();
        });
    }

    function loadProfile() {
        const base = {
            major: '',
            college: '',
            experience: '',
            targetAward: '',
            weeklyHours: null,
            staticInterests: [],
            dynamicWeights: {},
            lastUpdated: new Date().toISOString()
        };
        try {
            const raw = localStorage.getItem(PROFILE_KEY);
            if (!raw) return base;
            return Object.assign(base, JSON.parse(raw));
        } catch (e) {
            return base;
        }
    }

    function saveProfile(profile) {
        profile.lastUpdated = new Date().toISOString();
        localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
    }

    async function getContestPool() {
        if (contestPoolPromise) {
            return contestPoolPromise;
        }
        contestPoolPromise = (async function() {
            let contests = [];
            if (typeof loadAllContests === 'function') {
                const localContests = loadAllContests();
                if (Array.isArray(localContests) && localContests.length > 0) {
                    contests = localContests;
                }
            }
            if (contests.length === 0) {
                const response = await fetch('data/contests.json');
                if (response.ok) {
                    contests = await response.json();
                }
            }
            return (contests || []).map(normalizeContest);
        })();
        return contestPoolPromise;
    }

    function normalizeContest(contest) {
        const tags = Array.isArray(contest.tags)
            ? contest.tags
            : (contest.tags ? String(contest.tags).split(',').map(function(t) { return t.trim(); }).filter(Boolean) : []);
        const keywords = Array.isArray(contest.keywords)
            ? contest.keywords
            : (contest.keywords ? String(contest.keywords).split(',').map(function(t) { return t.trim(); }).filter(Boolean) : []);
        return {
            id: String(contest.id || contest.raw_notice_id || contest.notice_url || Math.random()),
            title: contest.title || '',
            content: contest.content || '',
            summary: contest.summary || '',
            source: contest.source || contest.source_department || '',
            publish_time: contest.publish_time || '',
            deadline: contest.deadline || contest.sign_up_deadline || '',
            competition_level: contest.competition_level || '',
            url: contest.url || contest.notice_url || '#',
            tags: tags,
            keywords: keywords
        };
    }

    function classifyContest(contest) {
        const cached = getCacheById(contest.id);
        if (cached) {
            return Object.assign({}, contest, cached);
        }

        const text = [contest.title, contest.content, contest.summary, contest.tags.join(' '), contest.keywords.join(' ')].join(' ').toLowerCase();
        let category = { id: 'academic_admin', name: '教务管理、竞赛统筹、学业相关通知' };
        let maxHit = -1;
        CATEGORY_RULES.forEach(function(rule) {
            let hit = 0;
            rule.keywords.forEach(function(kw) {
                if (text.includes(kw.toLowerCase())) {
                    hit += 1;
                }
            });
            if (hit > maxHit) {
                maxHit = hit;
                category = { id: rule.id, name: rule.name };
            }
        });

        let level = contest.competition_level || '普通';
        if (!level || level === '未知等级') {
            for (let i = 0; i < LEVEL_RULES.length; i += 1) {
                const rule = LEVEL_RULES[i];
                const matched = rule.keywords.some(function(kw) {
                    return text.includes(kw.toLowerCase());
                });
                if (matched) {
                    level = rule.level;
                    break;
                }
            }
        }
        if (!level || level === '未知等级') {
            level = '普通';
        }

        const result = { categoryId: category.id, categoryName: category.name, level: level };
        saveCacheById(contest.id, result);
        return Object.assign({}, contest, result);
    }

    function getCacheById(id) {
        const cache = getFromLocalStorageSafe(CLASSIFY_CACHE_KEY, {});
        return cache[id] || null;
    }

    function saveCacheById(id, payload) {
        const cache = getFromLocalStorageSafe(CLASSIFY_CACHE_KEY, {});
        cache[id] = payload;
        localStorage.setItem(CLASSIFY_CACHE_KEY, JSON.stringify(cache));
    }

    function getFromLocalStorageSafe(key, fallback) {
        try {
            const raw = localStorage.getItem(key);
            return raw ? JSON.parse(raw) : fallback;
        } catch (e) {
            return fallback;
        }
    }

    function extractUserIntent(message) {
        const lower = message.toLowerCase();
        const wantProfile = /专业|学院|经验|奖项|每周|小时/.test(message);
        const wantExplain = /拆解|解读|解析|介绍|怎么报名|如何申报|是什么/.test(message);
        const wantPlan = /备赛|计划|提醒|时间节点|时间安排/.test(message);
        const wantList = /清单|筛选|下半年|a类|a\+|优先级/.test(lower);
        const wantFaq = /适合|能不能|是否|怎么|疑问|问答/.test(message);
        const interestMatch = message.match(/兴趣模块[：:]\s*([^。！!\n]+)/);
        const clickedInterest = interestMatch ? String(interestMatch[1]).trim() : '';
        const forcedCategory = clickedInterest ? extractInterestFromText(clickedInterest) : '';
        const forcedRule = forcedCategory
            ? CATEGORY_RULES.find(function(rule) { return rule.name === forcedCategory; })
            : null;

        let module = 'recommend';
        if (wantExplain) module = 'explain';
        else if (wantPlan) module = 'plan';
        else if (wantList) module = 'list';
        else if (wantFaq) module = 'faq';
        else if (wantProfile) module = 'recommend';

        return {
            module: module,
            text: message,
            forcedCategoryName: forcedRule ? forcedRule.name : '',
            forcedCategoryId: forcedRule ? forcedRule.id : ''
        };
    }

    function scoreContests(contests, profile, query, options) {
        const opts = options || {};
        const now = Date.now();
        const actionLog = getFromLocalStorageSafe(RECENT_ACTION_KEY, []);
        const hotness = getFromLocalStorageSafe(HOTNESS_KEY, {});
        const interestWeights = buildDynamicWeights(profile, actionLog, contests);
        const queryTokens = tokenize(query);

        return contests.map(function(rawContest) {
            const contest = classifyContest(rawContest);
            const text = [contest.title, contest.summary, contest.content, contest.tags.join(' '), contest.keywords.join(' ')].join(' ').toLowerCase();

            let staticScore = 0;
            queryTokens.forEach(function(token) {
                if (token && text.includes(token)) {
                    staticScore += 7;
                }
            });
            if (profile.college && text.includes(profile.college.toLowerCase())) staticScore += 8;
            if (profile.major && text.includes(profile.major.toLowerCase())) staticScore += 8;
            if (profile.staticInterests.some(function(interest) { return text.includes(String(interest).toLowerCase()); })) staticScore += 10;

            let dynamicScore = 0;
            dynamicScore += (interestWeights.category[contest.categoryId] || 0) * 1.8;
            dynamicScore += (interestWeights.level[contest.level] || 0) * 1.2;
            dynamicScore += normalizedHotness(hotness[String(contest.id)]) * 10;
            dynamicScore += recencyScore(contest.publish_time, now) * 8;

            let qualityScore = 0;
            if (contest.level === 'A+') qualityScore += 6;
            if (contest.level === 'A') qualityScore += 4;
            qualityScore += deadlineScore(contest.deadline);

            if (opts.forcedCategoryId) {
                if (contest.categoryId === opts.forcedCategoryId) {
                    staticScore += 30;
                    dynamicScore += 10;
                } else {
                    staticScore -= 20;
                }
            }

            if (opts.forcedCategoryId && opts.forcedCategoryId !== 'academic_admin' && isAdministrativeNotice(contest)) {
                staticScore -= 18;
            }

            const totalScore = staticScore * 0.55 + dynamicScore * 0.35 + qualityScore * 0.10;
            return {
                contest: contest,
                staticScore: staticScore,
                dynamicScore: dynamicScore,
                qualityScore: qualityScore,
                totalScore: totalScore
            };
        }).sort(function(a, b) {
            return b.totalScore - a.totalScore;
        });
    }

    function getCategoryRuleById(categoryId) {
        return CATEGORY_RULES.find(function(rule) {
            return rule.id === categoryId;
        }) || null;
    }

    function keywordMatchCount(contest, rule) {
        if (!contest || !rule) return 0;
        const text = normalizeText([
            contest.title,
            contest.summary,
            contest.content,
            (contest.tags || []).join(' '),
            (contest.keywords || []).join(' ')
        ].join(' '));
        let hit = 0;
        rule.keywords.forEach(function(kw) {
            const n = normalizeText(kw);
            if (n && text.includes(n)) hit += 1;
        });
        return hit;
    }

    function isAdministrativeNotice(contest) {
        const adminWords = ['指南', '编制', '工作量', '填报', '奖励申报', '免考', '通知', '征集', '管理'];
        const text = [contest.title, contest.summary, contest.content].join(' ');
        return adminWords.some(function(word) { return text.includes(word); });
    }

    function deadlineDays(deadline) {
        if (!deadline) return null;
        const match = String(deadline).match(/\d{4}-\d{1,2}-\d{1,2}|\d{4}年\d{1,2}月\d{1,2}日/);
        if (!match) return null;
        const normalized = match[0].replace(/年|月/g, '-').replace(/日/g, '');
        const t = new Date(normalized).getTime();
        if (!Number.isFinite(t)) return null;
        return Math.ceil((t - Date.now()) / (1000 * 3600 * 24));
    }

    function applyRecencyFilter(contests, query) {
        if (!/近期|最近|尽快|本月/.test(query || '')) {
            return contests;
        }
        const filtered = contests.filter(function(contest) {
            const days = deadlineDays(contest.deadline);
            if (days === null) return true;
            return days >= 0;
        });
        return filtered.length >= 3 ? filtered : contests;
    }

    function buildDynamicWeights(profile, actionLog, contests) {
        const byId = {};
        contests.forEach(function(c) {
            byId[String(c.id)] = classifyContest(c);
        });
        const category = Object.assign({}, profile.dynamicWeights.category || {});
        const level = Object.assign({}, profile.dynamicWeights.level || {});
        const now = Date.now();

        actionLog.slice(-300).forEach(function(action) {
            const contest = byId[String(action.contestId)];
            if (!contest) return;
            const actionTime = new Date(action.timestamp).getTime();
            const days = Number.isFinite(actionTime) ? Math.max(1, (now - actionTime) / (1000 * 3600 * 24)) : 30;
            const decay = Math.exp(-days / 30);
            let delta = 0.5;
            if (action.actionType === 'favorite') delta = 2.2;
            if (action.actionType === 'useful') delta = 1.6;
            if (action.actionType === 'view') delta = 0.8;

            category[contest.categoryId] = (category[contest.categoryId] || 0) + delta * decay;
            level[contest.level] = (level[contest.level] || 0) + delta * 0.5 * decay;
        });

        profile.dynamicWeights = { category: category, level: level };
        saveProfile(profile);
        return { category: category, level: level };
    }

    function normalizedHotness(hotObj) {
        if (!hotObj) return 0;
        const total = Number(hotObj.total || 0);
        return Math.max(0, Math.min(1, total / 20));
    }

    function recencyScore(publishTime, now) {
        if (!publishTime) return 0.2;
        const t = new Date(publishTime).getTime();
        if (!Number.isFinite(t)) return 0.2;
        const days = Math.max(0, (now - t) / (1000 * 3600 * 24));
        if (days <= 7) return 1;
        if (days <= 30) return 0.7;
        if (days <= 90) return 0.4;
        return 0.1;
    }

    function deadlineScore(deadline) {
        if (!deadline) return 0.5;
        const match = String(deadline).match(/\d{4}-\d{1,2}-\d{1,2}|\d{4}年\d{1,2}月\d{1,2}日/);
        if (!match) return 0.6;
        const normalized = match[0].replace(/年|月/g, '-').replace(/日/g, '');
        const t = new Date(normalized).getTime();
        if (!Number.isFinite(t)) return 0.6;
        const days = (t - Date.now()) / (1000 * 3600 * 24);
        if (days < 0) return 0;
        if (days <= 7) return 1.2;
        if (days <= 30) return 1;
        return 0.5;
    }

    function tokenize(query) {
        return String(query || '')
            .toLowerCase()
            .split(/[\s,，。；;、]+/)
            .map(function(t) { return t.trim(); })
            .filter(function(t) { return t.length >= 2; });
    }

    async function llmRerankOrFallback(intent, rankedItems) {
        const top = rankedItems.slice(0, 12);
        try {
            const rerankApi =
                (window.AI_RERANK_API && String(window.AI_RERANK_API).trim()) ||
                localStorage.getItem('ai_rerank_api') ||
                'http://127.0.0.1:8001/api/ai/rerank';
            const controller = new AbortController();
            const timeout = setTimeout(function() { controller.abort(); }, 2500);
            const response = await fetch(rerankApi, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: intent.text,
                    candidates: top.map(function(item) {
                        return {
                            id: item.contest.id,
                            title: item.contest.title,
                            category: item.contest.categoryName,
                            level: item.contest.level,
                            summary: item.contest.summary,
                            score: item.totalScore
                        };
                    })
                }),
                signal: controller.signal
            });
            clearTimeout(timeout);
            if (!response.ok) {
                return top;
            }
            const data = await response.json();
            if (!Array.isArray(data) || data.length === 0) {
                return top;
            }
            const map = {};
            top.forEach(function(item) { map[item.contest.id] = item; });
            const reranked = [];
            data.forEach(function(id) {
                if (map[id]) reranked.push(map[id]);
            });
            top.forEach(function(item) {
                if (!reranked.includes(item)) reranked.push(item);
            });
            return reranked;
        } catch (e) {
            return top;
        }
    }

    function buildRecommendResponse(items, intent, profile) {
        if (items.length === 0) {
            return '<p>暂时没有匹配结果，请补充“专业/学院/目标奖项/每周可投入时间”。</p>';
        }
        const picked = items.slice(0, MAX_RECOMMEND);
        let html = '<p>已基于“静态标签 + 动态偏好 + 热度时效 + 语义重排(失败自动规则兜底)”完成推荐：</p>';
        picked.forEach(function(item, idx) {
            const contest = item.contest;
            const reasons = [];
            reasons.push('类别：' + contest.categoryName);
            reasons.push('等级：' + contest.level);
            if (item.staticScore >= 10) reasons.push('与你输入条件强相关');
            if (item.dynamicScore >= 8) reasons.push('结合你近期行为偏好');
            if (item.qualityScore >= 4) reasons.push('时效/质量较高');

            html += '<div class="contest-item">';
            html += '<div class="contest-name">' + (idx + 1) + '. ' + escapeHtml(contest.title) + '</div>';
            html += '<div class="contest-reason">推荐理由：' + escapeHtml(reasons.join('；')) + '</div>';
            html += '</div>';
        });
        html += '<p style="margin-top:8px;font-size:12px;color:#777;">可继续输入：例如“会计学院、无经验、校级奖项、每周3小时”做更精准匹配。</p>';
        html += '<p style="margin-top:6px;font-size:12px;color:#999;">说明：赛事时间与申报要求请以学校官方通知为准。</p>';
        if (!profile.major && !profile.college) {
            html += '<p style="margin-top:6px;font-size:12px;color:#999;">提示：补充专业和学院后，推荐效果会显著提升。</p>';
        }
        return html;
    }

    function buildExplainResponse(item) {
        const c = item.contest;
        const summary = c.summary || c.content || '暂无详细描述';
        return [
            '<p><strong>赛事信息拆解</strong></p>',
            '<div class="contest-item">',
            '<div class="contest-name">' + escapeHtml(c.title) + '</div>',
            '<div class="contest-reason">类别：' + escapeHtml(c.categoryName) + ' | 含金量：' + escapeHtml(c.level) + '</div>',
            '<div class="contest-reason">备赛重点：先读官方通知、确认参赛对象、根据时间节点倒排任务。</div>',
            '<div class="contest-reason">关联说明：可关注同类别竞赛进行梯度备赛（校赛→省赛→国赛）。</div>',
            '<div class="contest-reason">内容摘要：' + escapeHtml(summary.slice(0, 120)) + '...</div>',
            '</div>',
            '<p style="font-size:12px;color:#999;">申报时间与要求请以官方通知为准。</p>'
        ].join('');
    }

    function buildPlanResponse(item) {
        const c = item.contest;
        return [
            '<p><strong>简易备赛计划（4周模板）</strong></p>',
            '<div class="contest-item">',
            '<div class="contest-name">' + escapeHtml(c.title) + '</div>',
            '<div class="contest-reason">第1周：读规则、确定分工、整理往届优秀案例。</div>',
            '<div class="contest-reason">第2周：完成核心方案初稿并内部评审。</div>',
            '<div class="contest-reason">第3周：补证据材料/代码/展示稿，模拟答辩。</div>',
            '<div class="contest-reason">第4周：按申报清单复核，提交并留出修订缓冲。</div>',
            '</div>',
            '<p style="font-size:12px;color:#999;">你也可以补充“每周可投入时间”，我会自动压缩或展开计划强度。</p>'
        ].join('');
    }

    function buildFaqResponse(intent, scored) {
        const top = scored[0];
        if (!top) {
            return '<p>当前数据中未找到明确答案，建议提供具体赛事名，我可以按清单逐项解释。</p>';
        }
        return '<p>基于当前清单，' + escapeHtml(top.contest.title) + '与您的问题最相关。一般建议：先看参赛对象与赛道要求，再评估准备周期与团队能力，优先选择“难度匹配+时间可控”的赛事路径。</p>';
    }

    function escapeHtml(text) {
        return String(text || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function normalizeText(text) {
        return String(text || '')
            .replace(/\s+/g, '')
            .replace(/[：:，,。.!！?？()（）【】\[\]\-]/g, '')
            .toLowerCase();
    }

    function extractInterestFromText(rawText) {
        const text = String(rawText || '').trim();
        if (!text) return '';
        const normalized = normalizeText(text);
        const candidate = CATEGORY_RULES.find(function(rule) {
            const ruleName = normalizeText(rule.name);
            if (normalized === ruleName || normalized.includes(ruleName) || ruleName.includes(normalized)) {
                return true;
            }
            return rule.keywords.some(function(kw) {
                const n = normalizeText(kw);
                return normalized === n || normalized.includes(n);
            });
        });
        return candidate ? candidate.name : '';
    }

    function shouldHandleInterestClick(targetEl) {
        if (!targetEl) return false;
        if (targetEl.closest('#ai-chat-dialog')) return false;
        const interestRoots = [
            '.interest-tags',
            '.interest-container',
            '.interest-selector',
            '.recommend-interest',
            '.recommend-section',
            '.personalized-recommend',
            '.recommend-header'
        ];
        return interestRoots.some(function(selector) {
            return !!targetEl.closest(selector);
        });
    }

    function renderDialogInterestChips() {
        const welcome = dialogBody.querySelector('.ai-welcome-message');
        if (!welcome) return;
        if (welcome.querySelector('.ai-interest-section')) return;

        const section = document.createElement('div');
        section.className = 'ai-interest-section';
        section.innerHTML = '<div class="ai-interest-title">快速选择兴趣：</div>';

        const chipsWrap = document.createElement('div');
        chipsWrap.className = 'ai-interest-chips';
        DIALOG_INTEREST_CHIPS.forEach(function(chip) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'ai-interest-chip';
            btn.textContent = chip.label;
            btn.setAttribute('data-interest', chip.value);
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                triggerInterestRecommendation(chip.value);
            });
            chipsWrap.appendChild(btn);
        });
        section.appendChild(chipsWrap);
        welcome.appendChild(section);
    }

    function updateProfileFromMessage(profile, message) {
        const majorMatch = message.match(/(会计|统计|数学|外语|英语|计算机|软件|金融|工商管理|旅游|酒店|艺术|设计|信息工程|信息管理|经济学|经济|经贸)[学院系专业]?/);
        if (majorMatch) profile.major = majorMatch[1];

        const collegeMatch = message.match(/(会计学院|统计与数学学院|外国语学院|信息工程学院|信息管理学院|工商管理学院|旅游与酒店管理学院|艺术学院|金融学院|经济与贸易学院)/);
        if (collegeMatch) profile.college = collegeMatch[1];

        const expMatch = message.match(/(无参赛经验|有参赛经验|新手|入门|熟练|经验丰富)/);
        if (expMatch) profile.experience = expMatch[1];

        const targetMatch = message.match(/(校级|省级|国家级|a\+|a类|冲奖|保底)/i);
        if (targetMatch) profile.targetAward = targetMatch[1];

        const hoursMatch = message.match(/每周.{0,3}(\d+)\s*小时/);
        if (hoursMatch) profile.weeklyHours = Number(hoursMatch[1]);

        const interestHits = CATEGORY_RULES.filter(function(rule) {
            return rule.keywords.some(function(kw) { return message.includes(kw); });
        }).map(function(rule) { return rule.name; });
        if (interestHits.length > 0) {
            profile.staticInterests = Array.from(new Set(profile.staticInterests.concat(interestHits))).slice(-8);
        }
        saveProfile(profile);
    }

    function getPreferredCategoriesByProfile(profile) {
        const result = [];
        const college = profile.college || '';
        const major = profile.major || '';

        if (/经济与贸易学院|经贸/.test(college) || /经济学|经济|经贸/.test(major)) {
            result.push('经管商科、企业运营模拟类竞赛', '数学建模、统计调研类专业竞赛', '创新创业高水平A+/A类竞赛');
        }
        if (/会计学院|会计/.test(college + major)) {
            result.push('经管商科、企业运营模拟类竞赛', '数学建模、统计调研类专业竞赛', '创新创业高水平A+/A类竞赛');
        }
        if (/信息工程学院|信息管理学院|计算机|软件|信息工程|信息管理/.test(college + major)) {
            result.push('计算机、软件、数字设计艺术类竞赛');
        }
        if (/外国语学院|英语|外语/.test(college + major)) {
            result.push('英语外语学科竞赛');
        }
        if (/统计与数学学院|统计|数学/.test(college + major)) {
            result.push('数学建模、统计调研类专业竞赛');
        }
        return Array.from(new Set(result));
    }

    function getMajorRule(profile) {
        const key = (profile.major || '') + ' ' + (profile.college || '');
        return MAJOR_CATEGORY_MAP.find(function(rule) {
            return rule.majorPattern.test(key);
        }) || null;
    }

    function getMajorMatchLevel(profile, category) {
        const rule = getMajorRule(profile);
        if (!rule) return 'unknown';
        if (rule.high.includes(category)) return 'high';
        if (rule.mid.includes(category)) return 'mid';
        if (rule.low.includes(category)) return 'low';
        return 'mid';
    }

    // 专业匹配度校验层：位于静态筛选后、动态加权前
    function applyMajorValidationLayer(pool, profile) {
        const hasMajor = !!(profile.major || profile.college);
        if (!hasMajor) {
            return pool.map(function(x) {
                return Object.assign({}, x, { majorMatchLevel: 'unknown' });
            });
        }
        const validated = pool.map(function(x) {
            const lv = getMajorMatchLevel(profile, x.item.category);
            return Object.assign({}, x, { majorMatchLevel: lv });
        }).filter(function(x) {
            // 低匹配直接过滤，禁止进入 Top 推荐
            return x.majorMatchLevel !== 'low';
        });
        return validated;
    }

    function getSelectedCategory(intent, message) {
        if (intent.forcedCategoryName) return intent.forcedCategoryName;
        const fromText = extractInterestFromText(message);
        if (fromText) return fromText;
        const lower = String(message || '');
        const map = [
            ['文体', '文体体育类赛事活动'],
            ['心理', '心理健康&思政德育类活动'],
            ['思政', '心理健康&思政德育类活动'],
            ['英语', '英语外语学科竞赛'],
            ['外语', '英语外语学科竞赛'],
            ['数学', '数学建模、统计调研类专业竞赛'],
            ['统计', '数学建模、统计调研类专业竞赛'],
            ['经管', '经管商科、企业运营模拟类竞赛'],
            ['商科', '经管商科、企业运营模拟类竞赛'],
            ['计算机', '计算机、软件、数字设计艺术类竞赛'],
            ['软件', '计算机、软件、数字设计艺术类竞赛'],
            ['设计', '计算机、软件、数字设计艺术类竞赛'],
            ['创新创业', '创新创业高水平A+/A类竞赛'],
            ['a+', '创新创业高水平A+/A类竞赛'],
            ['教务', '教务管理、竞赛统筹、学业相关通知']
        ];
        const hit = map.find(function(pair) { return lower.toLowerCase().includes(pair[0]); });
        return hit ? hit[1] : '';
    }

    function isCurrentWindow(item) {
        if (item.year >= REFERENCE_YEAR) return true;
        return false;
    }

    function hotnessBonus(item) {
        const lv = item.level || '';
        if (lv.includes('A+')) return 20;
        if (lv.includes('A类') || lv.includes('国家级 A类')) return 10;
        if (lv.includes('院级')) return 0;
        return 5;
    }

    function getContestFeature(item) {
        const name = item.name || '';
        if (/全国大学生统计建模大赛/.test(name)) return '需要组队完成数据分析并提交论文，核心是统计建模和报告写作';
        if (/大学生数学建模校内赛/.test(name)) return '属于国赛前热身，通常按队伍解题并输出模型与论文';
        if (/全国大学生数学竞赛选拔测试/.test(name)) return '以纯笔试为主，重点考高数与解题速度，不需要组队';
        if (/田径|运动会/.test(name)) return '需要现场参赛，重点看体能与临场发挥';
        if (/羽毛球/.test(name)) return '以单打/双打实战为主，节奏快、对抗强';
        if (/歌咏|演讲/.test(name)) return '以舞台展示为核心，考验节奏感和表达力';
        if (/摄影/.test(name)) return '以作品提交为主，手机也能参与，核心是选题和构图';
        if (/导游风采/.test(name)) return '通常含现场讲解环节，口才和控场能力很关键';
        if (/烹饪/.test(name)) return '更看重实操与呈现，作品完成度决定上限';
        if (/挑战杯/.test(name)) return '核心是创业计划书和路演答辩，竞争强度较高';
        if (/创新大赛|创新创业/.test(name)) return '更看重项目落地与商业可行性';
        if (/统计建模|数学建模/.test(name)) return '要完成建模分析和报告写作，对逻辑要求高';
        if (/英语|外语|21世纪杯|外研社/.test(name)) return '常见笔试/演讲环节，语言输出能力是关键';
        if (/计算机设计|蓝桥杯/.test(name)) return '以代码与作品为主，评审看实现质量和展示';
        if (/设计周|华灿奖|好创意/.test(name)) return '作品导向明显，创意和视觉表达决定竞争力';
        return '赛制相对清晰，准备时先把报名材料和展示内容做扎实';
    }

    function getProfileFit(item, profile, majorMatchLevel) {
        if (profile.college && (item.name.includes(profile.college) || (item.tags || []).includes(profile.college))) {
            return '你在' + profile.college + '，院内信息获取和组队都会更顺';
        }
        if (profile.major) {
            if (/会计/.test(profile.major) && /挑战杯|创新|经管|统计|建模/.test(item.name)) {
                return '会计背景在财务预测和数据分析部分有天然优势';
            }
            if (/英语|外语/.test(profile.major) && /英语|外语|演讲/.test(item.name)) {
                return '你的专业训练能直接转化为比赛中的语言表现';
            }
            if (/计算机|软件|信息工程|信息管理/.test(profile.major) && /计算机|蓝桥杯|设计/.test(item.name)) {
                return '你的技术基础能直接支撑作品实现和现场答辩';
            }
        }
        if (profile.experience && /无参赛经验|新手|入门/.test(profile.experience)) {
            if (/院级|校级/.test(item.level)) return '这类赛道对新手更友好，适合先建立参赛节奏';
            if (/国家级|A\+|A类/.test(item.level)) return '含金量高但压力更大，建议先小范围打样再冲奖';
        }
        if (majorMatchLevel === 'mid') {
            return '和你专业不是一一对应，但在数据分析/表达/项目管理上有可迁移能力';
        }
        return '和你的关注方向存在直接关联，进入状态会更快';
    }

    function getValueHint(item, profile) {
        const name = item.name || '';
        if (/全国大学生统计建模大赛/.test(name)) return '准备周期通常2-3个月，获奖论文有机会继续打磨成成果';
        if (/大学生数学建模校内赛/.test(name)) return '校赛是国赛练兵场，题目梯度友好，能先把完整流程跑通';
        if (/全国大学生数学竞赛选拔测试/.test(name)) return '刷题效率决定上限，适合用短周期冲一次笔试成绩';
        if (/院级/.test(item.level)) return '院级通常先选拔再推荐，试错成本低';
        if (/校级/.test(item.level)) return '校级参与面广，拿到名次对后续评优也有帮助';
        if (/A\+/.test(item.level)) return 'A+赛事含金量高，建议至少预留6-8周准备周期';
        if (/A类|国家级/.test(item.level)) return '竞争强度中高，提前组队和分工会更稳';
        if (/挑战杯|创新大赛/.test(name)) return '同一项目后续可继续打磨，复用到更高层级赛事';
        if (profile.weeklyHours && profile.weeklyHours < 3) return '你每周时间偏紧，建议优先做可快速提交的版本';
        return '建议先做时间倒排，把报名、作品、答辩三个节点提前锁定';
    }

    function normalizeReasonLength(text) {
        const clean = String(text || '').replace(/\s+/g, '');
        if (clean.length > 60) {
            return clean.slice(0, 59) + '。';
        }
        if (clean.length < 30) {
            return clean + '准备时先看官方通知里的报名和提交要求。';
        }
        return clean;
    }

    function hasBannedReasonPattern(text) {
        const raw = String(text || '');
        return REASON_BANNED_PATTERNS.some(function(reg) {
            reg.lastIndex = 0;
            return reg.test(raw);
        });
    }

    function buildSafeFallbackReason(item, profile, index, majorMatchLevel) {
        const starts = ['这场比赛的关键在于', '从备赛投入看', '如果你想稳一点推进'];
        const start = starts[index % starts.length];
        const a = getContestFeature(item);
        const b = getProfileFit(item, profile, majorMatchLevel);
        const c = getValueHint(item, profile);
        return normalizeReasonLength(start + a + '；' + b + '；' + c + '。');
    }

    function makeSaiXingReason(item, profile, index, majorMatchLevel) {
        const openers = ['这项比赛', '换个角度看', '如果你准备本学期参赛'];
        const opener = openers[index % openers.length];
        const part1 = getContestFeature(item);
        const part2 = getProfileFit(item, profile, majorMatchLevel);
        const part3 = getValueHint(item, profile);
        const draft = normalizeReasonLength(opener + '，' + part1 + '；' + part2 + '；' + part3);
        if (hasBannedReasonPattern(draft)) {
            return buildSafeFallbackReason(item, profile, index, majorMatchLevel);
        }
        return draft;
    }

    function diversifyReasons(lines) {
        const synonymMap = {
            '适合': ['更对口', '更契合', '更匹配'],
            '建议': ['推荐', '可以优先', '更稳妥的做法是'],
            '提升': ['增强', '打磨', '强化'],
            '准备': ['筹备', '推进', '安排'],
            '组队': ['找搭档', '拉队伍', '完成分工']
        };
        const seen = {};
        return lines.map(function(line, idx) {
            let out = String(line || '');
            Object.keys(synonymMap).forEach(function(word) {
                const count = (out.match(new RegExp(word, 'g')) || []).length;
                const total = seen[word] || 0;
                if (idx > 0 && (count > 0 && total > 0)) {
                    const replacement = synonymMap[word][Math.min(idx - 1, synonymMap[word].length - 1)];
                    out = out.replace(word, replacement);
                }
                seen[word] = total + count;
            });
            if (hasBannedReasonPattern(out)) {
                out = out
                    .replace(/和你最近点击的兴趣方向比较一致|和你最近点击的兴趣方向比较匹配|和你最近的兴趣方向一致/g, '和你的报名意向更对口')
                    .replace(/上手快，适合本学期尽快出成果/g, '准备节奏友好，本学期可完成一轮完整参赛')
                    .replace(/含金量高，但要预留更完整的备赛周期/g, '赛事认可度高，需要提前排好备赛进度')
                    .replace(/规则清晰，准备路径相对明确/g, '流程清楚，建议按时间节点逐项推进')
                    .replace(/偏向.{0,8}(表现|能力|表达)/g, '更看重对应赛项的专项要求');
            }
            return normalizeReasonLength(out);
        });
    }

    function buildMatchStars(score) {
        if (score >= 90) return '⭐⭐⭐⭐⭐';
        if (score >= 75) return '⭐⭐⭐⭐';
        return '⭐⭐⭐';
    }

    function runSaiXingEngine(message, profile, intent) {
        const selectedCategory = getSelectedCategory(intent, message);
        if (!selectedCategory && !profile.major && !profile.college) {
            return null;
        }

        const clickedInterests = profile.staticInterests || [];
        const userSnapshot = [];
        if (profile.college) userSnapshot.push(profile.college);
        if (profile.major) userSnapshot.push(profile.major);
        if (profile.experience) userSnapshot.push(profile.experience);
        if (profile.targetAward) userSnapshot.push('目标' + profile.targetAward);
        if (profile.weeklyHours) userSnapshot.push('每周' + profile.weeklyHours + '小时');
        if (clickedInterests.length > 0) userSnapshot.push('近期兴趣:' + clickedInterests.slice(-2).join('/'));
        const snapshotText = userSnapshot.length ? userSnapshot.join('，') : '新用户默认';

        let pool = SAIXING_KB.map(function(item) {
            let score = 40;
            const sameCategory = selectedCategory && item.category === selectedCategory;
            if (sameCategory) score += 45;
            if (profile.college && (item.tags.includes(profile.college) || item.name.includes(profile.college))) score += 20;
            if (profile.major && (item.name.includes(profile.major) || item.tags.join(' ').includes(profile.major))) score += 10;
            const preferredCategories = getPreferredCategoriesByProfile(profile);
            if (!selectedCategory && preferredCategories.length > 0) {
                if (preferredCategories.includes(item.category)) {
                    score += 22;
                } else {
                    score -= 16;
                }
            }
            if ((profile.dynamicWeights && profile.dynamicWeights.category) && sameCategory) score += 10;
            if (profile.experience && /无参赛经验|新手|入门/.test(profile.experience) && /国家级|A\+/.test(item.level)) score -= 20;
            if (profile.experience && /无参赛经验|新手|入门/.test(profile.experience) && /院级|校级/.test(item.level)) score += 10;
            if (profile.weeklyHours && profile.weeklyHours < 3 && /A\+/.test(item.level) && item.year >= 2026) score -= 15;
            score += isCurrentWindow(item) ? 40 : -50;
            score += hotnessBonus(item);
            return { item: item, score: score, cross: false };
        });

        if (selectedCategory) {
            const strict = pool.filter(function(x) { return x.item.category === selectedCategory; });
            if (strict.length >= 3) {
                pool = strict;
            }
        }

        // Layer 1.5: 专业匹配度校验层
        pool = applyMajorValidationLayer(pool, profile);

        if (selectedCategory === '心理健康&思政德育类活动') {
            const cross = SAIXING_KB.filter(function(item) {
                return item.tags.includes('心理健康') || item.tags.includes('思政德育');
            }).map(function(item) {
                return { item: item, score: 65 + hotnessBonus(item), cross: item.category !== selectedCategory };
            });
            pool = mergeByName(pool, cross);
        }
        if (selectedCategory === '英语外语学科竞赛') {
            const cross2 = SAIXING_KB.filter(function(item) {
                return item.tags.includes('思政德育') && item.tags.includes('英语外语');
            }).map(function(item) {
                return { item: item, score: 70 + hotnessBonus(item), cross: true };
            });
            pool = mergeByName(pool, cross2);
        }

        pool.sort(function(a, b) { return b.score - a.score; });
        let selected = pool.slice(0, 3);

        if (selected.length < 3) {
            // 新兜底：必须同时满足“标签相关 + 专业相关”
            const rule = getMajorRule(profile);
            const majorAllowed = rule
                ? new Set([].concat(rule.high || [], rule.mid || []))
                : null;
            const tagRelated = selectedCategory
                ? SAIXING_KB.filter(function(item) {
                    return item.category === selectedCategory || (item.tags || []).some(function(t) { return selectedCategory.includes(t) || t.includes('创新创业'); });
                })
                : SAIXING_KB;
            const fallback = tagRelated.filter(function(item) {
                if (!majorAllowed) return true;
                return majorAllowed.has(item.category);
            }).map(function(item) {
                const lv = getMajorMatchLevel(profile, item.category);
                if (lv === 'low') return null;
                return { item: item, score: 58, cross: true, fallback: true, majorMatchLevel: lv };
            }).filter(Boolean);

            // 金融/会计/经济画像：优先经管或数学统计补位，避免补到计算机设计
            const financeBias = /金融|会计|经济|经贸/.test((profile.major || '') + (profile.college || ''));
            const sortedFallback = fallback.sort(function(a, b) {
                const aBiz = /经管商科、企业运营模拟类竞赛|数学建模、统计调研类专业竞赛/.test(a.item.category) ? 1 : 0;
                const bBiz = /经管商科、企业运营模拟类竞赛|数学建模、统计调研类专业竞赛/.test(b.item.category) ? 1 : 0;
                if (financeBias && aBiz !== bBiz) return bBiz - aBiz;
                return b.score - a.score;
            });
            selected = mergeByName(selected, sortedFallback).slice(0, 3);
        }

        return {
            selectedCategory: selectedCategory || '你当前输入条件',
            profileSnapshot: snapshotText,
            items: selected
        };
    }

    function mergeByName(base, extra) {
        const map = {};
        base.concat(extra).forEach(function(x) {
            const key = x.item.name;
            if (!map[key] || x.score > map[key].score) {
                map[key] = x;
            }
        });
        return Object.keys(map).map(function(k) { return map[k]; });
    }

    function buildSaiXingHtml(result, profile) {
        if (!result || !result.items || result.items.length === 0) return '';
        let html = '';
        html += '<h4>🎯 基于 ' + escapeHtml(result.selectedCategory) + ' 的智能推荐</h4>';
        const reasonList = result.items.map(function(row, idx) {
            return makeSaiXingReason(row.item, profile, idx, row.majorMatchLevel || 'unknown');
        });
        const diversifiedReasons = diversifyReasons(reasonList);
        result.items.forEach(function(row, idx) {
            const item = row.item;
            html += '<div class="contest-item">';
            html += '<div class="contest-name"><strong>' + (idx + 1) + '. ' + escapeHtml(item.name) + '</strong> [' + escapeHtml(item.level) + '] [' + escapeHtml(item.time) + ']</div>';
            html += '<div class="contest-reason"><strong>匹配度</strong>：' + buildMatchStars(row.score) + '</div>';
            html += '<div class="contest-reason"><strong>为什么推荐</strong>：' + escapeHtml(diversifiedReasons[idx]) + '</div>';
            html += '<div class="contest-reason"><strong>关键提醒</strong>：以学校官方通知为准，建议提前确认报名时间与材料要求。</div>';
            html += '</div>';
        });
        if (profile.major || profile.college || profile.weeklyHours || profile.experience) {
            html += '<p><strong>📌 个性化备赛建议</strong><br/>针对你当前画像，优先从前两项中选择 1 项集中准备，先做校内选拔材料，再逐步冲击更高等级赛事。</p>';
        }
        if (result.items.some(function(x) { return x.cross || x.fallback; })) {
            html += '<p><strong>💡 跨类别补充推荐</strong><br/>另外补充了可融入相同主题或门槛较低的备选赛事，方便你在本学期快速落地参赛。</p>';
        }
        return html;
    }

    async function generateResponse(userMessage) {
        const profile = loadProfile();
        updateProfileFromMessage(profile, userMessage);
        const intent = extractUserIntent(userMessage);
        const saixing = runSaiXingEngine(userMessage, profile, intent);
        if (saixing) {
            return buildSaiXingHtml(saixing, profile);
        }
        const contests = await getContestPool();
        let candidateContests = contests;
        if (intent.forcedCategoryId) {
            const forcedRule = getCategoryRuleById(intent.forcedCategoryId);
            let strict = contests.filter(function(contest) {
                return classifyContest(contest).categoryId === intent.forcedCategoryId;
            });
            if (forcedRule) {
                strict = strict.filter(function(contest) {
                    return keywordMatchCount(contest, forcedRule) >= 1;
                });
            }
            if (intent.forcedCategoryId !== 'academic_admin') {
                const strictNonAdmin = strict.filter(function(contest) {
                    return !isAdministrativeNotice(contest);
                });
                if (strictNonAdmin.length >= 3) {
                    strict = strictNonAdmin;
                }
            }
            strict = applyRecencyFilter(strict, intent.text);
            if (strict.length >= 3) {
                candidateContests = strict;
            } else {
                // 如果严格集合太少，放宽到“关键词命中 + 近期可参与”
                let relaxed = contests;
                if (forcedRule) {
                    relaxed = relaxed.filter(function(contest) {
                        return keywordMatchCount(contest, forcedRule) >= 1;
                    });
                }
                relaxed = applyRecencyFilter(relaxed, intent.text);
                if (relaxed.length >= 3) {
                    candidateContests = relaxed;
                }
            }
        }
        const scored = scoreContests(candidateContests, profile, intent.text, {
            forcedCategoryId: intent.forcedCategoryId
        });
        const reranked = await llmRerankOrFallback(intent, scored);

        if (intent.module === 'explain') {
            return buildExplainResponse(reranked[0] || scored[0]);
        }
        if (intent.module === 'plan') {
            return buildPlanResponse(reranked[0] || scored[0]);
        }
        if (intent.module === 'faq') {
            return buildFaqResponse(intent, reranked.length ? reranked : scored);
        }
        return buildRecommendResponse(reranked.length ? reranked : scored, intent, profile);
    }

    aiButton.addEventListener('mousedown', function(e) {
        if (e.button !== 0) return;
        isDraggingButton = true;
        hasMoved = false;
        const rect = aiButton.getBoundingClientRect();
        dragOffsetX = e.clientX - rect.left;
        dragOffsetY = e.clientY - rect.top;
        aiButton.style.cursor = 'grabbing';
        e.preventDefault();
    });

    dialogHeader.addEventListener('mousedown', function(e) {
        if (e.button !== 0) return;
        if (e.target.closest('.ai-dialog-close')) return;
        isDraggingDialog = true;
        const rect = aiDialog.getBoundingClientRect();
        dragOffsetX = e.clientX - rect.left;
        dragOffsetY = e.clientY - rect.top;
        dialogHeader.style.cursor = 'grabbing';
        e.preventDefault();
    });

    document.addEventListener('mousemove', function(e) {
        if (isDraggingButton) {
            let newX = e.clientX - dragOffsetX;
            let newY = e.clientY - dragOffsetY;
            const maxX = window.innerWidth - 50;
            const maxY = window.innerHeight - 50;
            newX = Math.max(0, Math.min(newX, maxX));
            newY = Math.max(0, Math.min(newY, maxY));
            aiButton.style.left = newX + 'px';
            aiButton.style.top = newY + 'px';
            aiButton.style.right = 'auto';
            aiButton.style.bottom = 'auto';
            hasMoved = true;

            if (isDialogOpen) {
                aiDialog.style.left = (newX - buttonDialogOffsetX) + 'px';
                aiDialog.style.top = (newY - buttonDialogOffsetY) + 'px';
                aiDialog.style.right = 'auto';
                aiDialog.style.bottom = 'auto';
                clampDialogPosition();
            }
        }
        if (isDraggingDialog) {
            let newX = e.clientX - dragOffsetX;
            let newY = e.clientY - dragOffsetY;
            const maxX = window.innerWidth - 350;
            const maxY = window.innerHeight - 450;
            newX = Math.max(0, Math.min(newX, maxX));
            newY = Math.max(0, Math.min(newY, maxY));
            aiDialog.style.left = newX + 'px';
            aiDialog.style.top = newY + 'px';
            aiDialog.style.right = 'auto';
            aiDialog.style.bottom = 'auto';

            aiButton.style.left = (newX + buttonDialogOffsetX) + 'px';
            aiButton.style.top = (newY + buttonDialogOffsetY) + 'px';
            aiButton.style.right = 'auto';
            aiButton.style.bottom = 'auto';
        }
    });

    document.addEventListener('mouseup', function() {
        if (isDraggingButton) {
            isDraggingButton = false;
            aiButton.style.cursor = 'pointer';
        }
        if (isDraggingDialog) {
            isDraggingDialog = false;
            dialogHeader.style.cursor = 'move';
        }
        if (isResizingDialog) {
            isResizingDialog = false;
            saveDialogSize();
        }
    });

    function addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'ai-message ' + type;
        const contentDiv = document.createElement('div');
        contentDiv.className = 'ai-message-content';
        if (type === 'assistant') {
            contentDiv.innerHTML = content;
        } else {
            contentDiv.textContent = content;
        }
        messageDiv.appendChild(contentDiv);
        dialogBody.appendChild(messageDiv);
        dialogBody.scrollTop = dialogBody.scrollHeight;
    }

    async function sendMessage() {
        const message = aiInput.value.trim();
        if (!message) return;
        return sendMessageWithText(message);
    }

    async function sendMessageWithText(message) {
        if (!message) return;
        addMessage(message, 'user');
        aiInput.value = '';
        aiSendBtn.disabled = true;
        try {
            const response = await generateResponse(message);
            addMessage(response, 'assistant');
        } catch (e) {
            addMessage('<p>推荐服务暂时不可用，已启用规则兜底。请稍后重试或补充更具体的条件。</p>', 'assistant');
        } finally {
            aiSendBtn.disabled = false;
        }
    }

    function triggerInterestRecommendation(interestText) {
        const interest = extractInterestFromText(interestText) || String(interestText || '').trim();
        if (!interest) return;
        const now = Date.now();
        if (now - lastInterestClickTs < INTEREST_CLICK_THROTTLE_MS) return;
        lastInterestClickTs = now;

        if (!isDialogOpen) openDialog();
        const ask = '我刚点击了兴趣模块：' + interest + '。请推荐对应竞赛，优先考虑近期可参与且与我偏好匹配的项目。';
        sendMessageWithText(ask);
    }

    function openDialog() {
        aiDialog.classList.add('active');
        isDialogOpen = true;
        aiInput.focus();
        const buttonRect = aiButton.getBoundingClientRect();
        aiDialog.style.left = (buttonRect.left - buttonDialogOffsetX) + 'px';
        aiDialog.style.top = (buttonRect.top - buttonDialogOffsetY) + 'px';
        aiDialog.style.right = 'auto';
        aiDialog.style.bottom = 'auto';
        clampDialogPosition();
    }

    function closeDialog() {
        aiDialog.classList.remove('active');
        isDialogOpen = false;
    }

    aiButton.addEventListener('click', function() {
        if (!isDraggingButton && !hasMoved) {
            if (isDialogOpen) closeDialog();
            else openDialog();
        }
    });

    dialogClose.addEventListener('click', closeDialog);
    aiSendBtn.addEventListener('click', sendMessage);
    aiInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });

    // 点击“个性化兴趣模块”后，自动唤起 AI 助手并给出对应推荐
    document.addEventListener('click', function(e) {
        const target = e.target;
        if (!target) return;
        const now = Date.now();
        if (now - lastInterestClickTs < INTEREST_CLICK_THROTTLE_MS) return;

        const clickable = target.closest('button,div,span,a');
        if (!clickable) return;

        let interest = '';
        const dataInterest = clickable.getAttribute('data-interest');
        if (dataInterest) {
            interest = extractInterestFromText(dataInterest);
        }
        if (!interest) {
            const text = (clickable.textContent || '').trim().slice(0, 40);
            interest = extractInterestFromText(text);
        }
        if (!interest) return;

        // 避免页面其他无关文本误触发：要求在推荐/兴趣区域内，或显式 data-interest
        if (!dataInterest && !shouldHandleInterestClick(clickable)) {
            return;
        }

        lastInterestClickTs = now;
        triggerInterestRecommendation(interest);
    });

    // 对外开放，便于其他页面模块主动调用 AI 助手
    window.AIAssistant = Object.assign({}, window.AIAssistant, {
        open: openDialog,
        close: closeDialog,
        send: sendMessageWithText,
        triggerInterestRecommendation: function(interestText) {
            triggerInterestRecommendation(interestText);
        }
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initButtonPosition();
            renderDialogInterestChips();
        });
    } else {
        initButtonPosition();
        renderDialogInterestChips();
    }
    window.addEventListener('resize', function() {
        if (!isDraggingButton) initButtonPosition();
        if (isDialogOpen) clampDialogPosition();
        setDialogSize(aiDialog.offsetWidth, aiDialog.offsetHeight, false);
    });

    document.addEventListener('mousemove', function(e) {
        if (!isResizingDialog) return;
        const dx = e.clientX - resizeStartX;
        const dy = e.clientY - resizeStartY;
        setDialogSize(resizeStartW + dx, resizeStartH + dy, false);
    });

    setupResizeControls();
    restoreDialogSize();
})();