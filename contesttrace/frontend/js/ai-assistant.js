(function() {
    const aiButton = document.getElementById('ai-float-button');
    const aiDialog = document.getElementById('ai-chat-dialog');
    const dialogHeader = document.getElementById('ai-dialog-header');
    const dialogClose = document.getElementById('ai-dialog-close');
    const aiInput = document.getElementById('ai-input');
    const aiSendBtn = document.getElementById('ai-send-btn');
    const dialogBody = document.getElementById('ai-dialog-body');

    let isDraggingButton = false;
    let isDraggingDialog = false;
    let dragOffsetX, dragOffsetY;
    let isDialogOpen = false;
    let hasMoved = false;
    let buttonDialogOffsetX = -50;
    let buttonDialogOffsetY = -50;

    function initButtonPosition() {
        aiButton.style.left = (window.innerWidth - 70) + 'px';
        aiButton.style.top = (window.innerHeight - 70) + 'px';
        aiButton.style.right = 'auto';
        aiButton.style.bottom = 'auto';
    }

    function initDialogPosition() {
        aiDialog.style.left = (window.innerWidth - 390) + 'px';
        aiDialog.style.top = (window.innerHeight - 550) + 'px';
        aiDialog.style.right = 'auto';
        aiDialog.style.bottom = 'auto';
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
    });

    aiButton.addEventListener('click', function() {
        if (!isDraggingButton && !hasMoved) {
            if (isDialogOpen) {
                closeDialog();
            } else {
                openDialog();
            }
        }
    });

    dialogClose.addEventListener('click', function() {
        closeDialog();
    });

    function openDialog() {
        aiDialog.classList.add('active');
        isDialogOpen = true;
        aiInput.focus();
        
        const buttonRect = aiButton.getBoundingClientRect();
        aiDialog.style.left = (buttonRect.left - buttonDialogOffsetX) + 'px';
        aiDialog.style.top = (buttonRect.top - buttonDialogOffsetY) + 'px';
        aiDialog.style.right = 'auto';
        aiDialog.style.bottom = 'auto';
    }

    function closeDialog() {
        aiDialog.classList.remove('active');
        isDialogOpen = false;
    }

    aiSendBtn.addEventListener('click', sendMessage);
    aiInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const message = aiInput.value.trim();
        if (!message) return;

        addMessage(message, 'user');
        aiInput.value = '';

        setTimeout(function() {
            const response = generateResponse(message);
            addMessage(response, 'assistant');
        }, 500);
    }

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

    function generateResponse(userMessage) {
        const lowerMessage = userMessage.toLowerCase();

        const contests = {
            '计算机': [
                { name: 'ACM-ICPC国际大学生程序设计竞赛', reason: '算法竞赛含金量高，全球认可度大' },
                { name: '全国大学生计算机设计大赛', reason: '计算机设计领域权威赛事' },
                { name: '蓝桥杯全国软件和信息技术专业人才大赛', reason: '适合编程爱好者，提升算法能力' }
            ],
            '程序': [
                { name: 'ACM-ICPC国际大学生程序设计竞赛', reason: '算法竞赛含金量高' },
                { name: 'Kaggle大数据竞赛', reason: '国际知名数据科学竞赛平台' },
                { name: 'Codeforces编程竞赛', reason: '全球程序设计爱好者广泛参与' }
            ],
            '数学': [
                { name: '全国大学生数学建模竞赛', reason: '培养数学应用和建模能力' },
                { name: '全国大学生数学竞赛', reason: '数学学科最高级别竞赛' },
                { name: '美国大学生数学建模竞赛(MCM/ICM)', reason: '国际认可度高的数学建模赛事' }
            ],
            '英语': [
                { name: '全国大学生英语竞赛', reason: '全面考查英语综合应用能力' },
                { name: '"外研社杯"全国英语演讲大赛', reason: '提升英语表达和思辨能力' },
                { name: '全国大学生翻译大赛', reason: '展示翻译能力和语言功底' }
            ],
            '商': [
                { name: '"挑战杯"中国大学生创业计划竞赛', reason: '创业类权威竞赛，认可度高' },
                { name: '全国大学生电子商务创新创意及创业挑战赛', reason: '电商领域创新创业实践平台' },
                { name: '全国商院精英挑战赛', reason: '商业案例分析和管理能力提升' }
            ],
            '创新': [
                { name: '"挑战杯"全国大学生课外学术科技作品竞赛', reason: '认可度高，综合性强' },
                { name: '中国"互联网+"大学生创新创业大赛', reason: '国家顶级创新创业赛事' },
                { name: '全国大学生创新创业训练计划', reason: '培养创新思维和科研能力' }
            ],
            '艺术': [
                { name: '全国大学生广告艺术大赛', reason: '广告创意和设计能力展示平台' },
                { name: '中国大学生美术作品年鉴', reason: '艺术设计作品收录和展示' },
                { name: '全国高校数字艺术设计大赛', reason: '数字媒体和艺术设计结合' }
            ],
            '机械': [
                { name: '全国大学生机械创新设计大赛', reason: '机械设计和创新能力培养' },
                { name: '工程训练综合能力竞赛', reason: '工程实践和动手能力提升' },
                { name: 'RoboMaster机甲大师赛', reason: '机器人技术和团队协作' }
            ],
            '电子': [
                { name: '全国大学生电子设计竞赛', reason: '电子设计能力和创新实践' },
                { name: '"挑战杯"课外学术科技作品竞赛', reason: '科技创新成果展示平台' },
                { name: '全国大学生智能汽车竞赛', reason: '汽车智能化技术应用' }
            ],
            '经济': [
                { name: '全国大学生金融精英挑战赛', reason: '金融知识和实务能力' },
                { name: '全国大学生商务谈判大赛', reason: '商务谈判和沟通技巧' },
                { name: '全国大学生统计建模大赛', reason: '统计分析和数据挖掘能力' }
            ]
        };

        let matchedContests = [];
        let found = false;

        for (const [keyword, contestList] of Object.entries(contests)) {
            if (lowerMessage.includes(keyword)) {
                matchedContests = contestList;
                found = true;
                break;
            }
        }

        if (!found) {
            matchedContests = [
                { name: '"挑战杯"全国大学生课外学术科技作品竞赛', reason: '认可度高，综合性强，适合各专业' },
                { name: '中国"互联网+"大学生创新创业大赛', reason: '国家顶级赛事，创新创业首选' },
                { name: '全国大学生数学建模竞赛', reason: '培养问题分析和解决能力' }
            ];
        }

        let response = '<p>根据您的需求，为您推荐以下竞赛：</p>';
        matchedContests.forEach(function(contest) {
            response += '<div class="contest-item">';
            response += '<div class="contest-name">' + contest.name + '</div>';
            response += '<div class="contest-reason">推荐理由：' + contest.reason + '</div>';
            response += '</div>';
        });

        response += '<p style="margin-top:10px;font-size:12px;color:#999;">点击竞赛卡片可查看详情</p>';

        return response;
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initButtonPosition);
    } else {
        initButtonPosition();
    }

    window.addEventListener('resize', function() {
        if (!isDraggingButton) {
            initButtonPosition();
        }
    });
})();