(function() {
    const aiButton = document.getElementById('ai-float-button');
    const aiDialog = document.getElementById('ai-chat-dialog');
    const dialogHeader = document.getElementById('ai-dialog-header');
    const dialogClose = document.getElementById('ai-dialog-close');
    const aiInput = document.getElementById('ai-input');
    const aiSendBtn = document.getElementById('ai-send-btn');
    const dialogBody = document.getElementById('ai-dialog-body');
    const dialogFooter = document.querySelector('.ai-dialog-footer');

    if (!aiButton || !aiDialog || !dialogHeader || !dialogClose || !aiInput || !aiSendBtn || !dialogBody || !dialogFooter) {
        return;
    }

    const PROFILE_KEY = 'ai_assistant_profile_v2';
    const DIALOG_SIZE_KEY = 'ai_assistant_dialog_size_v1';
    const CHAT_HISTORY_KEY = 'ai_assistant_chat_history_v1';
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
        { label: 'A/A+目录', value: 'A/A+官方权威学科竞赛目录' }
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
        { name: '2026年“经•舞”校园舞蹈视频大赛', category: '文体体育类赛事活动', tags: ['文体体育', '艺术设计'], level: '校级', time: '2026年', year: 2026 },
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
        { name: '大学生数据要素素质大赛', category: '数学建模、统计调研类专业竞赛', tags: ['数学统计', '经管商科'], level: '校级/省级', time: '2025年', year: 2025 },
        { name: '湖北省/全国企业竞争模拟大赛校赛', category: '经管商科、企业运营模拟类竞赛', tags: ['经管商科', '创新创业'], level: '省级/国家级', time: '2025年', year: 2025 },
        { name: '中国大学生工程实践与创新能力大赛虚拟仿真赛道企业运营仿真赛项校赛', category: '经管商科、企业运营模拟类竞赛', tags: ['经管商科'], level: '国家级 A类', time: '2025年', year: 2025 },
        { name: '“新青年吴兴杯”全国大学生物流设计大赛校内选拔赛', category: '经管商科、企业运营模拟类竞赛', tags: ['经管商科'], level: '国家级', time: '2025年', year: 2025 },
        { name: '工商管理学院2025年度竞赛备赛预通知', category: '经管商科、企业运营模拟类竞赛', tags: ['经管商科'], level: '院级通知', time: '2025年', year: 2025 },
        { name: '2026年（19届）中国大学生计算机设计大赛校赛', category: '计算机、软件、数字设计艺术类竞赛', tags: ['计算机设计', '艺术设计', '心理健康', '思政德育'], level: 'A类', time: '2026年3-5月', year: 2026 },
        { name: '蓝桥杯全国大学生软件和信息技术专业人才大赛', category: '计算机、软件、数字设计艺术类竞赛', tags: ['计算机设计', '艺术设计'], level: 'A类', time: '2025年', year: 2025 },
        { name: '米兰设计周-中国高校设计学科师生优秀作品展', category: '计算机、软件、数字设计艺术类竞赛', tags: ['艺术设计'], level: 'A类', time: '2025年', year: 2025 },
        { name: '两岸新锐设计竞赛·华灿奖', category: '计算机、软件、数字设计艺术类竞赛', tags: ['艺术设计'], level: 'A类', time: '2025年', year: 2025 },
        { name: '中国好创意暨全国数字艺术设计大赛', category: '计算机、软件、数字设计艺术类竞赛', tags: ['艺术设计'], level: 'A类', time: '2025年', year: 2025 },
        { name: '全国大学生数字媒体科技作品及创意竞赛', category: '计算机、软件、数字设计艺术类竞赛', tags: ['计算机设计', '数字媒体', 'A目录'], level: 'A类', time: '2025年', year: 2025 },
        { name: '全国三维数字化创新设计大赛', category: '计算机、软件、数字设计艺术类竞赛', tags: ['计算机设计', '三维数字化', 'A目录'], level: 'A类', time: '2025年', year: 2025 },
        { name: '全国大学生广告艺术大赛', category: '计算机、软件、数字设计艺术类竞赛', tags: ['艺术设计', 'A目录'], level: 'A类', time: '2025年', year: 2025 },
        { name: '未来设计师·全国高校数字艺术设计大赛（NCDA）', category: '计算机、软件、数字设计艺术类竞赛', tags: ['艺术设计', 'NCDA', 'A目录'], level: 'A类', time: '2025年', year: 2025 },
        { name: '2026年“挑战杯”大学生创业计划竞赛校级选拔赛', category: '创新创业高水平A+/A类竞赛', tags: ['创新创业', 'A+目录'], level: 'A+', time: '2026年', year: 2026 },
        { name: '第十五届“挑战杯”湖北省大学生课外学术科技作品竞赛', category: '创新创业高水平A+/A类竞赛', tags: ['创新创业', '思政德育', 'A+目录'], level: 'A+', time: '2025年', year: 2025 },
        { name: '中国国际大学生创新大赛（2026）', category: '创新创业高水平A+/A类竞赛', tags: ['创新创业', 'A+目录'], level: 'A+', time: '2026年', year: 2026 },
        { name: '全国大学生电子商务“三创赛”', category: '创新创业高水平A+/A类竞赛', tags: ['创新创业', 'A目录', '电子商务'], level: 'A类', time: '2025年', year: 2025 },
        { name: '大学生数据要素素质大赛、大学生职业规划大赛', category: '教务管理、竞赛统筹、学业相关通知', tags: ['教务学业'], level: '校级通知', time: '2025年', year: 2025 },
        { name: '各类竞赛指南、奖励申报、免考通知等', category: '教务管理、竞赛统筹、学业相关通知', tags: ['教务学业'], level: '教务通知', time: '2025年', year: 2025 }
    ];
    const TAG_TAXONOMY = {
        '文体体育类赛事活动': {
            aliases: ['文体体育', '文体', '体育', '舞蹈', '摄影', '导游风采', '烹饪'],
            contests: ['会计学院2025年羽毛球赛', '各学院第二十二届田径运动会预选赛及全校体育运动会', '2025年“青春歌行”五四歌咏比赛', '“匠影定格：最美劳动瞬间”校园摄影大赛', '旅游与酒店管理学院第二届导游风采大赛', '旅游与酒店管理学院2025年烹饪大赛', '2026年“经•舞”校园舞蹈视频大赛']
        },
        '心理健康&思政德育类活动': {
            aliases: ['心理思政', '心理', '思政', '德育', '红色', '团课', '清廉'],
            contests: ['第二十三届“藏龙杯”健康之星心理知识大赛', '第九届“十佳心委”评选大赛', '会计学院第一届心理健康教育微课大赛', '“传承红色基因，续写青春华章”主题微团课大赛', '会计学院红色文化科普讲解案例大赛', '第二届/第三届“浩然杯”读书演讲大赛', '2025年清廉教育主题系列活动']
        },
        '英语外语学科竞赛': {
            aliases: ['英语外语', '英语', '外语', '口译', '笔译', 'neccs', '21世纪杯', '外研社', '国才杯'],
            contests: ['全国大学生英语竞赛（NECCS）', '第30-31届中国日报社“21世纪杯”全国英语演讲比赛校园选拔赛', '2025“外研社•国才杯”“理解当代中国”全国大学生外语能力大赛校赛']
        },
        '数学建模、统计调研类专业竞赛': {
            aliases: ['数学统计', '数学', '统计', '建模', '正大杯', '数据要素'],
            contests: ['全国大学生统计建模大赛', '湖北经济学院2025年大学生数学建模校内赛', '全国大学生数学竞赛选拔测试', '“正大杯”全国大学生市场调查与分析大赛', '大学生数据要素素质大赛']
        },
        '经管商科、企业运营模拟类竞赛': {
            aliases: ['经管商科', '经管', '商科', '企业运营', '竞争模拟', '物流设计'],
            contests: ['湖北省/全国企业竞争模拟大赛校赛', '中国大学生工程实践与创新能力大赛虚拟仿真赛道企业运营仿真赛项校赛', '“新青年吴兴杯”全国大学生物流设计大赛校内选拔赛']
        },
        '计算机、软件、数字设计艺术类竞赛': {
            aliases: ['计算机设计', '计算机', '软件', '数字艺术', 'ncda', '蓝桥杯', '华灿奖', '米兰设计周'],
            contests: ['2026年（19届）中国大学生计算机设计大赛校赛', '蓝桥杯全国大学生软件和信息技术专业人才大赛', '米兰设计周-中国高校设计学科师生优秀作品展', '两岸新锐设计竞赛·华灿奖', '中国好创意暨全国数字艺术设计大赛', '全国大学生数字媒体科技作品及创意竞赛', '全国三维数字化创新设计大赛', '全国大学生广告艺术大赛', '未来设计师·全国高校数字艺术设计大赛（NCDA）']
        },
        '创新创业高水平A+/A类竞赛': {
            aliases: ['创新创业', '挑战杯', 'a+', 'a类', '创业计划'],
            contests: ['2026年“挑战杯”大学生创业计划竞赛校级选拔赛', '第十五届“挑战杯”湖北省大学生课外学术科技作品竞赛', '中国国际大学生创新大赛（2026）', '全国大学生电子商务“三创赛”']
        },
        'A/A+官方权威学科竞赛目录': {
            aliases: ['a/a+', 'a+目录', 'a类目录', '官方目录'],
            contests: ['中国国际大学生创新大赛（2026）', '2026年“挑战杯”大学生创业计划竞赛校级选拔赛', '全国大学生数字媒体科技作品及创意竞赛', '全国三维数字化创新设计大赛', '全国大学生广告艺术大赛', '两岸新锐设计竞赛·华灿奖', '2026年（19届）中国大学生计算机设计大赛校赛', '中国好创意暨全国数字艺术设计大赛', '未来设计师·全国高校数字艺术设计大赛（NCDA）', '米兰设计周-中国高校设计学科师生优秀作品展', '蓝桥杯全国大学生软件和信息技术专业人才大赛', '全国大学生电子商务“三创赛”']
        }
    };
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
    let isFullscreen = false;
    let fullscreenBtn = null;
    let dialogSnapshot = null;
    let resizeHandleEl = null;
    let isResizingDialog = false;
    let resizeStartX = 0;
    let resizeStartY = 0;
    let resizeStartW = 0;
    let resizeStartH = 0;
    let bodyOverflowBeforeDialog = '';
    const contestDetailMap = {};
    const contestRefMap = {};
    let currentAssistantContestRefs = [];

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

    function ensureFloatButtonVisible() {
        const rect = aiButton.getBoundingClientRect();
        const margin = 10;
        const maxX = window.innerWidth - rect.width - margin;
        const maxY = window.innerHeight - rect.height - margin;
        let x = rect.left;
        let y = rect.top;
        if (!Number.isFinite(x) || !Number.isFinite(y)) {
            x = window.innerWidth - rect.width - 20;
            y = window.innerHeight - rect.height - 20;
        }
        x = Math.max(margin, Math.min(x, maxX));
        y = Math.max(margin, Math.min(y, maxY));
        aiButton.style.left = x + 'px';
        aiButton.style.top = y + 'px';
        aiButton.style.right = 'auto';
        aiButton.style.bottom = 'auto';
        aiButton.style.display = 'flex';
        aiButton.style.visibility = 'visible';
        aiButton.style.opacity = '1';
        aiButton.style.zIndex = '10002';
    }

    function getDialogSizeBounds() {
        return {
            minW: 280,
            minH: 400,
            maxW: Math.max(280, window.innerWidth - 20),
            maxH: Math.max(400, window.innerHeight - 20)
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

    function iconSvg(kind) {
        if (kind === 'minimize') {
            return '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="4 14 10 14 10 20"></polyline><polyline points="20 10 14 10 14 4"></polyline><line x1="14" y1="10" x2="21" y2="3"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>';
        }
        return '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline><line x1="21" y1="3" x2="14" y2="10"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>';
    }

    function updateFullscreenButton() {
        if (!fullscreenBtn) return;
        const label = isFullscreen ? '收起' : '全屏';
        fullscreenBtn.innerHTML = iconSvg(isFullscreen ? 'minimize' : 'maximize') + '<span>' + label + '</span>';
        fullscreenBtn.setAttribute('aria-label', label);
        fullscreenBtn.title = label;
    }

    function toggleFullscreen() {
        if (!isDialogOpen) return;
        if (!isFullscreen) {
            const rect = aiDialog.getBoundingClientRect();
            dialogSnapshot = {
                left: rect.left,
                top: rect.top,
                width: aiDialog.offsetWidth,
                height: aiDialog.offsetHeight
            };
            aiDialog.classList.add('ai-chat-dialog-fullscreen');
            aiDialog.style.left = '0px';
            aiDialog.style.top = '0px';
            aiDialog.style.width = '100vw';
            aiDialog.style.height = '100vh';
            aiDialog.style.right = 'auto';
            aiDialog.style.bottom = 'auto';
            isFullscreen = true;
        } else {
            aiDialog.classList.remove('ai-chat-dialog-fullscreen');
            const snap = dialogSnapshot || {};
            const width = Number(snap.width) || 350;
            const height = Number(snap.height) || 450;
            aiDialog.style.width = width + 'px';
            aiDialog.style.height = height + 'px';
            aiDialog.style.left = (Number(snap.left) || 20) + 'px';
            aiDialog.style.top = (Number(snap.top) || 20) + 'px';
            clampDialogPosition();
            isFullscreen = false;
            saveDialogSize();
        }
        updateFullscreenButton();
    }

    function setupResizeControls() {
        if (dialogHeader.querySelector('.ai-resize-tools')) return;

        const tools = document.createElement('div');
        tools.className = 'ai-resize-tools';

        fullscreenBtn = document.createElement('button');
        fullscreenBtn.type = 'button';
        fullscreenBtn.className = 'ai-resize-btn ai-fullscreen-btn';
        fullscreenBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleFullscreen();
        });
        tools.appendChild(fullscreenBtn);
        dialogHeader.insertBefore(tools, dialogClose);
        updateFullscreenButton();

        if (!resizeHandleEl) {
            resizeHandleEl = document.createElement('div');
            resizeHandleEl.className = 'ai-resize-handle';
            resizeHandleEl.title = '拖拽调整大小';
            aiDialog.appendChild(resizeHandleEl);
            resizeHandleEl.addEventListener('mousedown', function(e) {
                if (e.button !== 0) return;
                if (isFullscreen) return;
                isResizingDialog = true;
                resizeStartX = e.clientX;
                resizeStartY = e.clientY;
                resizeStartW = aiDialog.offsetWidth;
                resizeStartH = aiDialog.offsetHeight;
                e.preventDefault();
                e.stopPropagation();
            });
        }
    }

    function getChatHistory() {
        return getFromLocalStorageSafe(CHAT_HISTORY_KEY, []);
    }

    function saveChatHistory(history) {
        localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify((history || []).slice(-100)));
    }

    function appendChatHistory(role, content, contestRefs) {
        const history = getChatHistory();
        const payload = {
            role: role,
            content: content,
            timestamp: new Date().toISOString()
        };
        if (Array.isArray(contestRefs) && contestRefs.length > 0) {
            payload.contestRefs = contestRefs;
        }
        history.push(payload);
        saveChatHistory(history);
    }

    function registerContestRefs(refs) {
        if (!Array.isArray(refs)) return;
        refs.forEach(function(ref) {
            if (!ref || !ref.refId) return;
            contestRefMap[String(ref.refId)] = ref;
        });
    }

    function renderChatHistory() {
        const history = getChatHistory();
        if (!Array.isArray(history) || history.length === 0) return;
        dialogBody.querySelectorAll('.ai-message').forEach(function(node) {
            node.remove();
        });
        history.forEach(function(item) {
            if (!item || !item.role) return;
            addMessage(String(item.content || ''), item.role, false, item.contestRefs);
        });
    }

    function loadProfile() {
        const base = {
            major: '',
            college: '',
            experience: '',
            academicYear: '',
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
            const normalizedText = normalizeText(text);

            let staticScore = 0;
            queryTokens.forEach(function(token) {
                if (token && text.includes(token)) {
                    staticScore += 7;
                }
            });
            if (profile.college && text.includes(profile.college.toLowerCase())) staticScore += 8;
            if (profile.major && text.includes(profile.major.toLowerCase())) staticScore += 8;
            if (profile.staticInterests.some(function(interest) { return text.includes(String(interest).toLowerCase()); })) staticScore += 10;
            const taxonomy = TAG_TAXONOMY[contest.categoryName] || null;
            if (taxonomy) {
                const aliasBoost = (taxonomy.aliases || []).filter(function(alias) {
                    const n = normalizeText(alias);
                    return n && normalizedText.includes(n);
                }).length;
                const contestBoost = (taxonomy.contests || []).some(function(name) {
                    const n = normalizeText(name);
                    return n && (normalizedText.includes(n) || normalizeText(contest.title).includes(n));
                }) ? 1 : 0;
                staticScore += aliasBoost * 2 + contestBoost * 8;
            }

            // 画像打分：专业/学院/经验/目标奖项（四要素全部参与）
            if (profile.college) {
                if (text.includes(String(profile.college).toLowerCase())) staticScore += 10;
                else staticScore -= 2;
            }
            if (profile.major) {
                if (text.includes(String(profile.major).toLowerCase())) staticScore += 10;
                else staticScore -= 2;
            }
            const levelText = String(contest.level || contest.competition_level || '').toLowerCase();
            if (profile.experience) {
                const exp = String(profile.experience);
                if (/无参赛经验|无经验|没经验|新手|入门/.test(exp)) {
                    if (/a\+|国家级/.test(levelText)) staticScore -= 12;
                    if (/院级|校级|普通/.test(levelText)) staticScore += 8;
                } else if (/有参赛经验|有经验|熟练|经验丰富/.test(exp)) {
                    if (/a\+|a类|国家级/.test(levelText)) staticScore += 10;
                    if (/院级/.test(levelText)) staticScore -= 4;
                }
            }
            if (profile.targetAward) {
                const target = String(profile.targetAward).toLowerCase();
                if (/国家级|a\+|冲奖/.test(target)) {
                    if (/a\+|a类|国家级/.test(levelText)) staticScore += 14;
                    else staticScore -= 5;
                } else if (/省级|a类/.test(target)) {
                    if (/a类|省级|国家级/.test(levelText)) staticScore += 8;
                } else if (/校级|保底/.test(target)) {
                    if (/校级|院级|普通/.test(levelText)) staticScore += 9;
                    if (/a\+|国家级/.test(levelText)) staticScore -= 6;
                }
            }

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
            const isLocalHost =
                location.hostname === 'localhost' ||
                location.hostname === '127.0.0.1' ||
                location.hostname === '::1';
            const configuredApi = (window.AI_RERANK_API && String(window.AI_RERANK_API).trim()) || '';
            const localStorageApi = localStorage.getItem('ai_rerank_api') || '';
            const rerankApi = configuredApi || localStorageApi || (isLocalHost ? 'http://127.0.0.1:8001/api/ai/rerank' : '');
            if (!rerankApi) {
                return top;
            }
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
            const detailId = 'ranked-' + String(contest.id) + '-' + idx + '-' + Date.now();
            const refId = 'ref-ranked-' + String(contest.id) + '-' + idx + '-' + Date.now() + '-' + Math.random().toString(16).slice(2, 6);
            contestDetailMap[detailId] = {
                name: contest.title || '未命名竞赛',
                level: contest.level || contest.competition_level || '普通',
                time: contest.deadline || contest.publish_time || '以官方通知为准',
                intro: contest.summary || contest.content || '暂无详细介绍',
                prepAdvice: '先确认报名条件与时间节点，再按“选题/组队/材料准备/提交复核”四步推进。',
                source: contest.source || '以官方通知为准',
                publishTime: contest.publish_time || '-',
                deadline: contest.deadline || '-',
                organizer: contest.source || '待补充',
                participants: '以官方通知中的参赛对象要求为准',
                prize: contest.level || '待补充',
                contact: contest.source ? ('可联系：' + contest.source) : '见原文通知',
                url: contest.url || '#',
                content: contest.content || contest.summary || '暂无正文内容',
                modalContest: {
                    id: contest.id || detailId,
                    title: contest.title || '未命名竞赛',
                    source: contest.source || '以官方通知为准',
                    publish_time: contest.publish_time || '',
                    deadline: contest.deadline || '',
                    organizer: contest.organizer || contest.source || '未知',
                    participants: contest.participants || '以官方通知中的参赛对象要求为准',
                    prize: contest.prize || contest.level || '未知',
                    contact: contest.contact || contest.source || '未知',
                    content: contest.content || contest.summary || '无详细内容',
                    url: contest.url || '#'
                }
            };
            const refPayload = {
                refId: refId,
                detailId: detailId,
                modalContest: contestDetailMap[detailId].modalContest,
                name: contestDetailMap[detailId].name
            };
            contestRefMap[refId] = refPayload;
            currentAssistantContestRefs.push(refPayload);
            const reasons = [];
            reasons.push('类别：' + contest.categoryName);
            reasons.push('等级：' + contest.level);
            if (item.staticScore >= 10) reasons.push('与你输入条件强相关');
            if (item.dynamicScore >= 8) reasons.push('结合你近期行为偏好');
            if (item.qualityScore >= 4) reasons.push('时效/质量较高');

            html += '<div class="contest-item ai-contest-clickable" data-detail-id="' + escapeHtml(detailId) + '" data-contest-ref-id="' + escapeHtml(refId) + '">';
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
        const taxonomyCategory = Object.keys(TAG_TAXONOMY).find(function(name) {
            const entry = TAG_TAXONOMY[name] || {};
            const aliases = Array.isArray(entry.aliases) ? entry.aliases : [];
            const contests = Array.isArray(entry.contests) ? entry.contests : [];
            const aliasHit = aliases.some(function(alias) {
                const n = normalizeText(alias);
                return n && (normalized.includes(n) || n.includes(normalized));
            });
            if (aliasHit) return true;
            return contests.some(function(contestName) {
                const n = normalizeText(contestName);
                return n && (normalized.includes(n) || n.includes(normalized));
            });
        });
        if (taxonomyCategory) return taxonomyCategory;
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

    function renderFooterInterestChips() {
        if (dialogFooter.querySelector('.ai-footer-interest-bar')) return;
        const bar = document.createElement('div');
        bar.className = 'ai-footer-interest-bar';
        DIALOG_INTEREST_CHIPS.forEach(function(chip) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'ai-interest-chip ai-footer-interest-chip';
            btn.textContent = chip.label;
            btn.setAttribute('data-interest', chip.value);
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                triggerInterestRecommendation(chip.value);
            });
            bar.appendChild(btn);
        });
        dialogFooter.insertBefore(bar, dialogFooter.firstChild);
    }

    function setupDialogScrollProxy() {
        // 让用户在对话框空白区域滚轮时，也能驱动消息区滚动
        aiDialog.addEventListener('wheel', function(e) {
            if (!isDialogOpen) return;
            if (e.target && e.target.closest && e.target.closest('.ai-dialog-footer')) return;
            if (e.target === dialogBody || (e.target.closest && e.target.closest('#ai-dialog-body'))) return;
            dialogBody.scrollTop += e.deltaY;
            e.preventDefault();
        }, { passive: false });
    }

    function updateProfileFromMessage(profile, message) {
        const majorMatch = message.match(/(会计|统计|数学|外语|英语|计算机|软件|金融|工商管理|旅游|酒店|艺术|设计|信息工程|信息管理|经济学|经济|经贸)[学院系专业]?/);
        if (majorMatch) profile.major = majorMatch[1];

        const collegeMatch = message.match(/(会计学院|统计与数学学院|外国语学院|信息工程学院|信息管理学院|工商管理学院|旅游与酒店管理学院|艺术学院|金融学院|经济与贸易学院)/);
        if (collegeMatch) profile.college = collegeMatch[1];

        const expMatch = message.match(/(无参赛经验|无经验|没经验|有参赛经验|有经验|新手|入门|熟练|经验丰富)/);
        if (expMatch) profile.experience = expMatch[1];

        const yearMatch = message.match(/(大一|大二|大三|大四|研一|研二|研三)/);
        if (yearMatch) profile.academicYear = yearMatch[1];

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

    function extractSaiXingQuerySignals(message) {
        const text = String(message || '');
        const lower = text.toLowerCase();
        const categories = [];
        const yearMatch = text.match(/20\d{2}/g) || [];
        const levelHints = [];

        const categoryRules = [
            { reg: /文体|体育|运动会|羽毛球|田径|摄影|歌咏/, name: '文体体育类赛事活动' },
            { reg: /心理|思政|德育|红色|团课/, name: '心理健康&思政德育类活动' },
            { reg: /英语|外语|演讲|翻译|听力/, name: '英语外语学科竞赛' },
            { reg: /数学|统计|建模|调研|正大杯/, name: '数学建模、统计调研类专业竞赛' },
            { reg: /经管|商科|会计|金融|运营|物流/, name: '经管商科、企业运营模拟类竞赛' },
            { reg: /计算机|软件|蓝桥杯|设计|数字艺术|信息工程/, name: '计算机、软件、数字设计艺术类竞赛' },
            { reg: /创新创业|挑战杯|创新大赛|a\+|a类/, name: '创新创业高水平A+/A类竞赛' }
        ];
        categoryRules.forEach(function(rule) {
            if (rule.reg.test(text) && !categories.includes(rule.name)) {
                categories.push(rule.name);
            }
        });

        if (/a\+|国家级|国奖|冲国赛/i.test(text)) levelHints.push('high');
        if (/a类|省级/i.test(text)) levelHints.push('mid');
        if (/校级|院级|新手|入门/i.test(text)) levelHints.push('low');

        return {
            categories: categories,
            years: yearMatch,
            levelHints: levelHints,
            preferRecent: /近期|最近|本学期|尽快|马上/.test(text),
            tokens: lower.split(/[\s,，。；;、]+/).map(function(x) { return x.trim(); }).filter(function(x) { return x.length >= 2; })
        };
    }

    function runSaiXingEngine(message, profile, intent) {
        const querySignals = extractSaiXingQuerySignals(message);
        const selectedCategory = getSelectedCategory(intent, message) || (querySignals.categories[0] || '');
        const hasProfileSignal = !!(
            selectedCategory ||
            profile.major ||
            profile.college ||
            profile.experience ||
            profile.academicYear ||
            profile.targetAward
        );
        if (!hasProfileSignal) {
            return null;
        }

        const clickedInterests = profile.staticInterests || [];
        const userSnapshot = [];
        if (profile.college) userSnapshot.push(profile.college);
        if (profile.major) userSnapshot.push(profile.major);
        if (profile.academicYear) userSnapshot.push(profile.academicYear);
        if (profile.experience) userSnapshot.push(profile.experience);
        if (profile.targetAward) userSnapshot.push('目标' + profile.targetAward);
        if (profile.weeklyHours) userSnapshot.push('每周' + profile.weeklyHours + '小时');
        if (clickedInterests.length > 0) userSnapshot.push('近期兴趣:' + clickedInterests.slice(-2).join('/'));
        const snapshotText = userSnapshot.length ? userSnapshot.join('，') : '新用户默认';

        const relatedCategoryMap = {
            '文体体育类赛事活动': ['心理健康&思政德育类活动'],
            '心理健康&思政德育类活动': ['文体体育类赛事活动', '英语外语学科竞赛'],
            '英语外语学科竞赛': ['心理健康&思政德育类活动'],
            '数学建模、统计调研类专业竞赛': ['经管商科、企业运营模拟类竞赛'],
            '经管商科、企业运营模拟类竞赛': ['数学建模、统计调研类专业竞赛', '创新创业高水平A+/A类竞赛'],
            '计算机、软件、数字设计艺术类竞赛': ['创新创业高水平A+/A类竞赛'],
            '创新创业高水平A+/A类竞赛': ['经管商科、企业运营模拟类竞赛', '计算机、软件、数字设计艺术类竞赛']
        };

        let pool = SAIXING_KB.map(function(item) {
            let score = 40;
            const sameCategory = selectedCategory && item.category === selectedCategory;
            if (sameCategory) score += 45;
            const taxonomy = TAG_TAXONOMY[item.category] || null;
            if (taxonomy) {
                const isTaxonomyContest = (taxonomy.contests || []).some(function(name) {
                    const n = normalizeText(name);
                    const iname = normalizeText(item.name);
                    return n && (iname === n || iname.includes(n) || n.includes(iname));
                });
                if (isTaxonomyContest) score += 12;
                if (selectedCategory && selectedCategory === item.category) score += 6;
            }
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
            // 经验分层：拉开“有经验 vs 无经验”的结果差异
            if (profile.experience && /无参赛经验|无经验|没经验|新手|入门/.test(profile.experience) && /国家级|A\+/.test(item.level)) score -= 35;
            if (profile.experience && /无参赛经验|无经验|没经验|新手|入门/.test(profile.experience) && /院级|校级/.test(item.level)) score += 18;
            if (profile.experience && /有参赛经验|有经验|熟练|经验丰富/.test(profile.experience) && /国家级|A\+|A类/.test(item.level)) score += 15;
            if (profile.experience && /有参赛经验|有经验|熟练|经验丰富/.test(profile.experience) && /院级/.test(item.level)) score -= 8;

            // 目标奖项纳入打分：保证“目标导向”真实生效
            if (profile.targetAward) {
                const target = String(profile.targetAward).toLowerCase();
                if (/国家级|a\+|冲奖/.test(target)) {
                    if (/A\+|A类|国家级/.test(item.level)) score += 18;
                    else score -= 10;
                } else if (/省级|a类/.test(target)) {
                    if (/A类|省级|国家级/.test(item.level)) score += 10;
                } else if (/校级|保底/.test(target)) {
                    if (/校级|院级/.test(item.level)) score += 14;
                    if (/A\+|国家级/.test(item.level)) score -= 8;
                }
            }

            // 年级分层：拉开“大一 vs 大二”的结果差异
            if (profile.academicYear === '大一') {
                if (/国家级|A\+/.test(item.level)) score -= 26;
                if (/院级|校级/.test(item.level)) score += 22;
                if (/文体体育类赛事活动|心理健康&思政德育类活动/.test(item.category)) score += 8;
            }
            if (profile.academicYear === '大二') {
                if (/校级|省级|A类/.test(item.level)) score += 14;
                if (/A\+/.test(item.level)) score -= 6;
                if (/数学建模、统计调研类专业竞赛|经管商科、企业运营模拟类竞赛|计算机、软件、数字设计艺术类竞赛/.test(item.category)) score += 8;
            }
            if (profile.academicYear === '大三') {
                if (/国家级|A\+|A类/.test(item.level)) score += 16;
            }
            if (profile.weeklyHours && profile.weeklyHours < 3 && /A\+/.test(item.level) && item.year >= 2026) score -= 15;
            // 降低年份惩罚，避免不同兴趣都收敛到同一批A+赛事
            score += isCurrentWindow(item) ? 35 : -15;
            score += hotnessBonus(item);

            // 当次输入语义强化：避免不同话术打到同一组结果
            const itemText = (item.name + ' ' + item.category + ' ' + (item.tags || []).join(' ') + ' ' + item.level).toLowerCase();
            querySignals.tokens.forEach(function(tk) {
                if (itemText.includes(tk)) score += 8;
            });
            if (querySignals.categories.length > 0) {
                if (querySignals.categories.includes(item.category)) score += 26;
                else score -= 12;
            }
            if (querySignals.preferRecent) {
                score += isCurrentWindow(item) ? 10 : -8;
            }
            if (querySignals.years.length > 0) {
                const y = String(item.year || '');
                if (querySignals.years.includes(y)) score += 12;
                else score -= 5;
            }
            if (querySignals.levelHints.includes('high') && /A\+|A类|国家级/.test(item.level)) score += 12;
            if (querySignals.levelHints.includes('low') && /院级|校级/.test(item.level)) score += 10;
            if (querySignals.levelHints.includes('low') && /A\+/.test(item.level)) score -= 10;

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

        // 兴趣优先：点击兴趣后，至少保留2个同类别结果（不足再补）
        if (selectedCategory) {
            const sameCategoryCandidates = pool.filter(function(x) {
                return x.item.category === selectedCategory;
            });
            const pickedSame = selected.filter(function(x) {
                return x.item.category === selectedCategory;
            });
            if (pickedSame.length < 2 && sameCategoryCandidates.length > pickedSame.length) {
                const existingNames = new Set(selected.map(function(x) { return x.item.name; }));
                sameCategoryCandidates.forEach(function(x) {
                    if (pickedSame.length >= 2) return;
                    if (!existingNames.has(x.item.name)) {
                        selected.push(x);
                        existingNames.add(x.item.name);
                        pickedSame.push(x);
                    }
                });
                selected.sort(function(a, b) { return b.score - a.score; });
                selected = selected.slice(0, 3);
            }
        }

        if (selected.length < 3) {
            // 新兜底：必须同时满足“标签相关 + 专业相关”
            const rule = getMajorRule(profile);
            const majorAllowed = rule
                ? new Set([].concat(rule.high || [], rule.mid || []))
                : null;
            const preferredCats = selectedCategory
                ? [selectedCategory].concat(relatedCategoryMap[selectedCategory] || [])
                : [];
            const tagRelated = selectedCategory
                ? SAIXING_KB.filter(function(item) {
                    return preferredCats.includes(item.category);
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

        // 终极兜底：确保兴趣模块永远走统一“赛行推荐”样式，不回退到通用格式
        if (selected.length === 0 && selectedCategory) {
            const categoryFallback = SAIXING_KB
                .filter(function(item) { return item.category === selectedCategory; })
                .map(function(item) {
                    return {
                        item: item,
                        score: 62 + (isCurrentWindow(item) ? 8 : 0) + hotnessBonus(item),
                        cross: false,
                        fallback: true,
                        majorMatchLevel: 'unknown'
                    };
                })
                .sort(function(a, b) { return b.score - a.score; })
                .slice(0, 3);
            selected = categoryFallback;
        }

        if (selected.length < 3 && selectedCategory) {
            const existing = new Set(selected.map(function(x) { return x.item.name; }));
            const extraSameCategory = SAIXING_KB
                .filter(function(item) { return item.category === selectedCategory && !existing.has(item.name); })
                .map(function(item) {
                    return {
                        item: item,
                        score: 56 + (isCurrentWindow(item) ? 6 : 0) + hotnessBonus(item),
                        cross: false,
                        fallback: true,
                        majorMatchLevel: 'unknown'
                    };
                })
                .sort(function(a, b) { return b.score - a.score; });
            extraSameCategory.forEach(function(x) {
                if (selected.length >= 3) return;
                selected.push(x);
            });
            selected = selected.slice(0, 3);
        }

        selected = applyAcademicYearSelectionPolicy(selected, pool, profile);

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

    function isBeginnerFriendlyLevel(levelText) {
        const lv = String(levelText || '');
        return /院级|校级|普通/.test(lv);
    }

    function isIntermediateFriendlyLevel(levelText) {
        const lv = String(levelText || '');
        return /省级|A类|国家级/.test(lv) || (/校级/.test(lv) && !/院级/.test(lv));
    }

    function getYearProfileBonus(row, profile) {
        const year = String((profile && profile.academicYear) || '');
        const level = String(row.item.level || '');
        const category = String(row.item.category || '');
        const majorLv = getMajorMatchLevel(profile || {}, category);
        const majorBonus = majorLv === 'high' ? 10 : (majorLv === 'mid' ? 4 : -12);
        const exp = String((profile && profile.experience) || '');
        const target = String((profile && profile.targetAward) || '').toLowerCase();
        const college = String((profile && profile.college) || '');
        const title = String(row.item.name || '');
        const tagsText = (row.item.tags || []).join(' ');
        let bonus = majorBonus;

        if (college && (title.includes(college) || tagsText.includes(college))) bonus += 8;

        if (year === '大一') {
            bonus += isBeginnerFriendlyLevel(level) ? 12 : -14;
            if (/无参赛经验|新手|入门|没经验/.test(exp) && /国家级|A\+/.test(level)) bonus -= 18;
            if (/国家级|a\+|冲奖/.test(target) && /A\+|国家级/.test(level)) bonus += 6;
            if (/校级|保底/.test(target) && isBeginnerFriendlyLevel(level)) bonus += 10;
            if (category === '文体体育类赛事活动' || category === '心理健康&思政德育类活动') bonus += 6;
        } else if (year === '大二') {
            bonus += isIntermediateFriendlyLevel(level) ? 14 : -10;
            if (/无参赛经验|新手|入门|没经验/.test(exp) && /A\+|国家级/.test(level)) bonus -= 8;
            if (/有参赛经验|熟练|经验丰富/.test(exp) && /省级|A类|国家级/.test(level)) bonus += 8;
            if (/国家级|a\+|冲奖/.test(target) && /A\+|国家级|A类/.test(level)) bonus += 12;
            if (/校级|保底/.test(target) && /院级/.test(level)) bonus -= 8;
            if (category === '数学建模、统计调研类专业竞赛' || category === '经管商科、企业运营模拟类竞赛' || category === '计算机、软件、数字设计艺术类竞赛') bonus += 6;
        }
        return bonus;
    }

    // 年级差异化选拔层：联动专业/学院/经验/目标奖项，避免不同画像结果同质化
    function applyAcademicYearSelectionPolicy(selected, pool, profile) {
        const year = String((profile && profile.academicYear) || '');
        if (year !== '大一' && year !== '大二') return selected;

        const uniq = function(list) {
            const seen = {};
            return (list || []).filter(function(row) {
                if (!row || !row.item || !row.item.name) return false;
                if (seen[row.item.name]) return false;
                seen[row.item.name] = true;
                return true;
            });
        };

        const base = uniq(pool).map(function(row) {
            return Object.assign({}, row, {
                yearProfileScore: Number(row.score || 0) + getYearProfileBonus(row, profile || {})
            });
        });

        const filtered = base.filter(function(row) {
            return year === '大一' ? isBeginnerFriendlyLevel(row.item.level) : isIntermediateFriendlyLevel(row.item.level);
        });
        const effective = filtered.length >= 3 ? filtered : base;
        effective.sort(function(a, b) {
            return b.yearProfileScore - a.yearProfileScore;
        });

        const selectedSafe = uniq(selected).map(function(row) {
            return Object.assign({}, row, {
                yearProfileScore: Number(row.score || 0) + getYearProfileBonus(row, profile || {})
            });
        });
        selectedSafe.sort(function(a, b) {
            return b.yearProfileScore - a.yearProfileScore;
        });

        return mergeByName(effective.slice(0, 3), selectedSafe).slice(0, 3);
    }

    function getRawContestSnapshot() {
        if (typeof loadAllContests !== 'function') return [];
        const all = loadAllContests();
        return Array.isArray(all) ? all : [];
    }

    function getCategoryHintWords(categoryName) {
        const map = {
            '英语外语学科竞赛': ['英语', '外语', '演讲', '翻译', '口译', '笔译', '听力', '外研社', '国才杯', '21世纪杯', 'neccs'],
            '数学建模、统计调研类专业竞赛': ['数学', '建模', '统计', '调研', '正大杯'],
            '经管商科、企业运营模拟类竞赛': ['经管', '商科', '企业', '运营', '物流', '模拟'],
            '计算机、软件、数字设计艺术类竞赛': ['计算机', '软件', '信息技术', '蓝桥杯', '设计', '数字艺术'],
            '创新创业高水平A+/A类竞赛': ['创新', '创业', '挑战杯', '创新大赛'],
            '心理健康&思政德育类活动': ['心理', '思政', '德育', '团课', '红色'],
            '文体体育类赛事活动': ['文体', '体育', '运动会', '羽毛球', '田径', '歌咏', '摄影']
        };
        return map[categoryName] || [];
    }

    function resolveRawContestForSaiXing(item) {
        if (!item || !item.name) return null;
        const all = getRawContestSnapshot();
        if (!all.length) return null;
        const targetName = String(item.name || '').trim();
        if (!targetName) return null;

        const exact = all.find(function(c) {
            return String(c.title || '').trim() === targetName;
        });
        if (exact) return exact;

        const nameTokens = targetName
            .split(/[“”"'‘’【】\[\]（）()、，,。.!！?？\s\-_:：]+/)
            .map(function(x) { return x.trim(); })
            .filter(function(x) { return x.length >= 2; });
        const hintWords = getCategoryHintWords(item.category);
        const ranked = all.map(function(c) {
            const title = String(c.title || '');
            const content = String(c.content || '');
            const compName = String(c.competition_name || '');
            const joined = (title + ' ' + content + ' ' + compName).toLowerCase();
            let bonus = 0;
            nameTokens.forEach(function(tk) {
                if (tk && title.includes(tk)) bonus += 5;
            });
            hintWords.forEach(function(w) {
                if (joined.includes(String(w).toLowerCase())) bonus += 3;
            });
            return {
                contest: c,
                score: calcTitleSimilarity(targetName, title) + bonus
            };
        }).sort(function(a, b) { return b.score - a.score; });
        if (ranked[0] && ranked[0].score >= 30) {
            return ranked[0].contest;
        }
        return null;
    }

    function buildSaiXingHtml(result, profile) {
        if (!result || !result.items || result.items.length === 0) return '';
        let html = '';
        html += '<h4>🎯 基于 ' + escapeHtml(result.selectedCategory) + ' 的智能推荐</h4>';
        const reasonList = result.items.map(function(row, idx) {
            return makeSaiXingReason(row.item, profile, idx, row.majorMatchLevel || 'unknown');
        });
        const diversifiedReasons = diversifyReasons(reasonList);
        let renderedCount = 0;
        result.items.forEach(function(row, idx) {
            const item = row.item;
            const rawContest = resolveRawContestForSaiXing(item);
            if (!rawContest) return;
            const detailId = 'saixing-' + idx + '-' + Date.now() + '-' + Math.random().toString(16).slice(2, 6);
            const refId = 'ref-saixing-' + idx + '-' + Date.now() + '-' + Math.random().toString(16).slice(2, 6);
            const displayTitle = rawContest.title || item.name || '未命名竞赛';
            const displayLevel = rawContest.competition_level || item.level || '普通';
            const displayTime = rawContest.deadline || item.time || rawContest.publish_time || '以官方通知为准';
            const displaySource = rawContest.source || '以官方通知为准';
            contestDetailMap[detailId] = {
                name: displayTitle,
                level: displayLevel,
                time: displayTime,
                intro: rawContest.summary || rawContest.content || getContestFeature(item),
                prepAdvice: getValueHint(item, profile),
                source: displaySource,
                publishTime: rawContest.publish_time || '-',
                deadline: rawContest.deadline || displayTime || '-',
                organizer: rawContest.organizer || displaySource || '未知',
                participants: rawContest.participants || '以官方通知中的参赛对象要求为准',
                prize: rawContest.prize || displayLevel || '待补充',
                contact: rawContest.contact || displaySource || '见原文通知',
                url: rawContest.url || '#',
                content: rawContest.content || rawContest.summary || (getContestFeature(item) + '。' + getValueHint(item, profile)),
                modalContest: {
                    id: rawContest.id || detailId,
                    title: displayTitle,
                    source: displaySource,
                    publish_time: rawContest.publish_time || '',
                    deadline: rawContest.deadline || '',
                    organizer: rawContest.organizer || displaySource || '未知',
                    participants: rawContest.participants || '以官方通知中的参赛对象要求为准',
                    prize: rawContest.prize || displayLevel || '未知',
                    contact: rawContest.contact || displaySource || '未知',
                    content: rawContest.content || rawContest.summary || '无详细内容',
                    url: rawContest.url || '#'
                }
            };
            const refPayload = {
                refId: refId,
                detailId: detailId,
                modalContest: contestDetailMap[detailId].modalContest,
                name: contestDetailMap[detailId].name
            };
            contestRefMap[refId] = refPayload;
            currentAssistantContestRefs.push(refPayload);
            renderedCount += 1;
            html += '<div class="contest-item ai-contest-clickable" data-detail-id="' + escapeHtml(detailId) + '" data-contest-ref-id="' + escapeHtml(refId) + '">';
            html += '<div class="contest-name"><strong>' + (renderedCount) + '. ' + escapeHtml(displayTitle) + '</strong> [' + escapeHtml(displayLevel) + '] [' + escapeHtml(displayTime) + ']</div>';
            html += '<div class="contest-reason"><strong>匹配度</strong>：' + buildMatchStars(row.score) + '</div>';
            html += '<div class="contest-reason"><strong>为什么推荐</strong>：' + escapeHtml(diversifiedReasons[idx]) + '</div>';
            html += '<div class="contest-reason"><strong>关键提醒</strong>：以学校官方通知为准，建议提前确认报名时间与材料要求。</div>';
            html += '</div>';
        });
        if (renderedCount === 0) {
            return '<p>当前兴趣推荐暂未匹配到站内原始竞赛数据，请换一个关键词（如赛事名/学院名）后重试。</p>';
        }
        if (profile.major || profile.college || profile.weeklyHours || profile.experience) {
            html += '<p><strong>📌 个性化备赛建议</strong><br/>针对你当前画像，优先从前两项中选择 1 项集中准备，先做校内选拔材料，再逐步冲击更高等级赛事。</p>';
        }
        if (result.items.some(function(x) { return x.cross || x.fallback; })) {
            html += '<p><strong>💡 跨类别补充推荐</strong><br/>另外补充了可融入相同主题或门槛较低的备选赛事，方便你在本学期快速落地参赛。</p>';
        }
        return html;
    }

    async function generateResponse(userMessage) {
        currentAssistantContestRefs = [];
        const profile = loadProfile();
        updateProfileFromMessage(profile, userMessage);
        const intent = extractUserIntent(userMessage);
        const saixing = runSaiXingEngine(userMessage, profile, intent);
        if (saixing && Array.isArray(saixing.items) && saixing.items.length > 0) {
            const html = buildSaiXingHtml(saixing, profile);
            if (String(html || '').trim()) {
                return html;
            }
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
        const finalHtml = buildRecommendResponse(reranked.length ? reranked : scored, intent, profile);
        if (!String(finalHtml || '').trim()) {
            return '<p>已收到你的兴趣模块请求，但当前可用候选较少。建议补充“专业/学院/目标奖项/每周时间”，我会立即重算推荐。</p>';
        }
        return finalHtml;
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
        if (e.target.closest('.ai-fullscreen-btn')) return;
        if (isFullscreen) return;
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
        if (isResizingDialog) {
            const dx = e.clientX - resizeStartX;
            const dy = e.clientY - resizeStartY;
            setDialogSize(resizeStartW + dx, resizeStartH + dy, false);
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

    function addMessage(content, type, persist, contestRefs) {
        const shouldPersist = persist !== false;
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
        if (type === 'assistant' && Array.isArray(contestRefs) && contestRefs.length > 0) {
            registerContestRefs(contestRefs);
        }
        dialogBody.scrollTop = dialogBody.scrollHeight;
        if (shouldPersist) {
            appendChatHistory(type, content, contestRefs);
        }
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
            const refs = Array.isArray(currentAssistantContestRefs) ? currentAssistantContestRefs.slice() : [];
            addMessage(response, 'assistant', true, refs);
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
        bodyOverflowBeforeDialog = document.body.style.overflow || '';
        document.body.style.overflow = 'hidden';
        aiDialog.classList.add('active');
        isDialogOpen = true;
        if (isFullscreen) {
            aiDialog.classList.add('ai-chat-dialog-fullscreen');
            aiDialog.style.left = '0px';
            aiDialog.style.top = '0px';
            aiDialog.style.width = '100vw';
            aiDialog.style.height = '100vh';
        } else {
            aiDialog.classList.remove('ai-chat-dialog-fullscreen');
            const buttonRect = aiButton.getBoundingClientRect();
            aiDialog.style.left = (buttonRect.left - buttonDialogOffsetX) + 'px';
            aiDialog.style.top = (buttonRect.top - buttonDialogOffsetY) + 'px';
            aiDialog.style.right = 'auto';
            aiDialog.style.bottom = 'auto';
            clampDialogPosition();
        }
        aiInput.focus();
    }

    function closeDialog() {
        document.body.style.overflow = bodyOverflowBeforeDialog;
        if (isFullscreen) {
            isFullscreen = false;
            aiDialog.classList.remove('ai-chat-dialog-fullscreen');
            updateFullscreenButton();
        }
        aiDialog.classList.remove('active');
        isDialogOpen = false;
        ensureFloatButtonVisible();
    }

    function safeText(text) {
        const raw = String(text == null ? '' : text).trim();
        if (!raw || raw.toLowerCase() === 'null' || raw.toLowerCase() === 'undefined') return '';
        return raw;
    }

    function normalizeLooseText(text) {
        return String(text || '')
            .toLowerCase()
            .replace(/\s+/g, '')
            .replace(/[“”"'‘’【】\[\]（）()、，,。.!！?？\-_:：]/g, '');
    }

    function getYearTokens(text) {
        const matches = String(text || '').match(/20\d{2}/g);
        return matches || [];
    }

    function calcTitleSimilarity(a, b) {
        const na = normalizeLooseText(a);
        const nb = normalizeLooseText(b);
        if (!na || !nb) return 0;
        if (na === nb) return 100;
        if (na.includes(nb) || nb.includes(na)) return 92;

        let score = 0;
        const yearsA = getYearTokens(a);
        const yearsB = getYearTokens(b);
        if (yearsA.length && yearsB.length && yearsA.some(function(y) { return yearsB.includes(y); })) {
            score += 15;
        }

        const keyTokens = String(a || '')
            .split(/[“”"'‘’【】\[\]（）()、，,。.!！?？\s\-_:：]+/)
            .map(function(x) { return x.trim(); })
            .filter(function(x) { return x.length >= 2; });
        keyTokens.forEach(function(token) {
            const nt = normalizeLooseText(token);
            if (!nt) return;
            if (nb.includes(nt)) score += 6;
        });
        if (/挑战杯/.test(a) && /挑战杯/.test(b)) score += 20;
        if (/创新大赛|创新创业/.test(a) && /创新大赛|创新创业/.test(b)) score += 10;
        return score;
    }

    function toModalContest(detail) {
        if (!detail) return null;
        if (typeof loadAllContests !== 'function') return null;
        const all = loadAllContests() || [];
        if (!all.length) return null;

        const directId = detail.modalContest && detail.modalContest.id ? String(detail.modalContest.id) : '';
        const name = String(detail.name || '').trim();
        const modalTitle = detail.modalContest ? String(detail.modalContest.title || '').trim() : '';
        const exact = all.find(function(c) {
            if (directId && String(c.id) === directId) return true;
            const title = String(c.title || '').trim();
            if (name && title === name) return true;
            if (modalTitle && title === modalTitle) return true;
            return false;
        });
        if (exact) return exact;

        const targetName = name || modalTitle;
        if (!targetName) return null;
        const ranked = all.map(function(c) {
            return {
                contest: c,
                score: calcTitleSimilarity(targetName, c.title || '')
            };
        }).sort(function(a, b) { return b.score - a.score; });
        if (ranked[0] && ranked[0].score >= 45) {
            return ranked[0].contest;
        }
        return null;
    }

    function extractContestNameFromCard(card) {
        if (!card) return '';
        const titleEl = card.querySelector('.contest-name');
        const raw = String((titleEl && titleEl.textContent) || card.textContent || '').trim();
        if (!raw) return '';
        // 去掉序号前缀和尾部标签，如“1. xxx [A+] [2026年]”
        const noIndex = raw.replace(/^\s*\d+\.\s*/, '');
        const noTags = noIndex.replace(/\s*\[[^\]]+\]\s*/g, ' ').replace(/\s+/g, ' ').trim();
        return noTags;
    }

    function buildDetailFromCardFallback(card) {
        const name = extractContestNameFromCard(card);
        if (!name) return null;
        return {
            id: '',
            name: name,
            level: '普通',
            source: '以官方通知为准',
            publishTime: '',
            deadline: '',
            organizer: '未知',
            participants: '以官方通知中的参赛对象要求为准',
            prize: '未知',
            contact: '见原文通知',
            content: name + '，请查看竞赛详情了解报名与赛程要求。',
            url: '#'
        };
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

    dialogBody.addEventListener('click', function(e) {
        const card = e.target && e.target.closest ? e.target.closest('.ai-contest-clickable') : null;
        if (!card) return;
        const refId = card.getAttribute('data-contest-ref-id');
        const detailId = card.getAttribute('data-detail-id');
        let detail = null;
        if (refId && contestRefMap[refId]) {
            const ref = contestRefMap[refId];
            if (ref.modalContest) {
                detail = {
                    name: ref.name || '',
                    modalContest: ref.modalContest
                };
            } else if (ref.detailId && contestDetailMap[ref.detailId]) {
                detail = contestDetailMap[ref.detailId];
            }
        }
        if (detailId) {
            detail = detail || contestDetailMap[detailId] || null;
        }
        // 历史记录中的卡片 data-detail-id 可能存在，但内存映射已丢失，这里做兜底还原
        if (!detail) {
            detail = buildDetailFromCardFallback(card);
        }
        if (!detail) return;
        const modalContest = toModalContest(detail);
        if (typeof window.openContestModal === 'function' && modalContest) {
            window.openContestModal(modalContest);
        } else if (typeof window.openContestModalById === 'function' && modalContest && modalContest.id) {
            window.openContestModalById(modalContest.id);
        } else {
            addMessage('<p>该推荐项暂未匹配到站内原始竞赛数据，已跳过打开详情。请换一个关键词重试，或点击列表中的同名竞赛卡片查看完整信息。</p>', 'assistant');
            return;
        }
        const modalEl = document.getElementById('contest-modal');
        if (modalEl) {
            modalEl.style.zIndex = '10050';
        }
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
            renderFooterInterestChips();
            renderChatHistory();
        });
    } else {
        initButtonPosition();
        renderDialogInterestChips();
        renderFooterInterestChips();
        renderChatHistory();
    }
    window.addEventListener('resize', function() {
        if (!isDraggingButton) initButtonPosition();
        if (isDialogOpen && !isFullscreen) {
            clampDialogPosition();
            setDialogSize(aiDialog.offsetWidth, aiDialog.offsetHeight, false);
        }
        if (isDialogOpen && isFullscreen) {
            aiDialog.style.left = '0px';
            aiDialog.style.top = '0px';
            aiDialog.style.width = '100vw';
            aiDialog.style.height = '100vh';
        }
    });

    setupResizeControls();
    setupDialogScrollProxy();
    restoreDialogSize();
})();