/**
 * 竞赛日历功能
 */

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', async function() {
    console.log('日历页面 DOM 加载完成');
    try {
        await initCalendar();
        console.log('日历初始化成功');
    } catch (error) {
        console.error('日历初始化失败:', error);
        showCalendarError('日历加载失败，请刷新重试');
    }
    initCalendarEventListeners();
});

// 初始化日历
async function initCalendar() {
    // 确保 calendar 容器存在
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) {
        console.error('日历容器 #calendar 不存在');
        return;
    }
    
    // 加载所有竞赛数据
    const allContests = await loadContests();
    console.log('加载竞赛数据成功，共', allContests.length, '条');
    
    // 转换为日历事件
    const events = convertContestsToEvents(allContests);
    console.log('生成日历事件', events.length, '个');
    
    // 初始化 FullCalendar
    if (typeof FullCalendar === 'undefined') {
        console.error('FullCalendar 库未加载');
        showCalendarError('日历组件加载失败，请刷新页面');
        return;
    }
    
    const calendar = new FullCalendar.Calendar(calendarEl, {
        locale: 'zh-cn',
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: events,
        eventClick: function(info) {
            info.jsEvent.preventDefault();
            openContestModal(info.event.extendedProps.contest);
        },
        eventBackgroundColor: function(info) {
            const daysLeft = info.event.extendedProps.daysLeft;
            if (daysLeft < 0) {
                return '#f44336';
            } else if (daysLeft <= 3) {
                return '#ff9800';
            } else {
                return '#667eea';
            }
        }
    });
    
    calendar.render();
    window.calendar = calendar;
    console.log('日历渲染完成');
}

// 将竞赛数据转换为日历事件
function convertContestsToEvents(contests) {
    const events = [];
    
    contests.forEach(contest => {
        if (contest.deadline) {
            // 提取日期部分
            const dateMatch = contest.deadline.match(/(\d{4}-\d{2}-\d{2}|\d{4}年\d{1,2}月\d{1,2}日)/);
            if (dateMatch) {
                const dateStr = dateMatch[0];
                // 转换为标准日期格式
                const normalizedDate = dateStr.replace(/年|月/g, '-').replace(/日/g, '');
                const eventDate = new Date(normalizedDate);
                
                if (!isNaN(eventDate.getTime())) {
                    // 计算剩余天数
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);
                    const timeDiff = eventDate - today;
                    const daysLeft = Math.ceil(timeDiff / (1000 * 3600 * 24));
                    
                    // 确定事件标题（只显示前12个字符）
                    let eventTitle = contest.title;
                    if (eventTitle.length > 12) {
                        eventTitle = eventTitle.substring(0, 12) + '...';
                    }
                    
                    // 确定事件类型
                    const isActivityDate = contest.deadline.includes('活动日期');
                    const eventType = isActivityDate ? '活动' : '截止';
                    
                    // 确定 CSS 类名
                    let eventClassName = 'ec-event-normal';
                    if (daysLeft < 0) {
                        eventClassName = 'ec-event-expired';
                    } else if (daysLeft <= 3) {
                        eventClassName = 'ec-event-urgent';
                    }
                    
                    events.push({
                        title: `${eventType}: ${eventTitle}`,
                        start: eventDate,
                        allDay: true,
                        classNames: [eventClassName],
                        extendedProps: {
                            contest: contest,
                            daysLeft: daysLeft,
                            isActivityDate: isActivityDate
                        }
                    });
                }
            }
        }
    });
    
    return events;
}

// 初始化日历事件监听器
function initCalendarEventListeners() {
    // 来源筛选
    const sourceFilter = document.getElementById('calendar-source-filter');
    if (sourceFilter) {
        sourceFilter.addEventListener('change', async function() {
            await updateCalendarEvents();
        });
    }
    
    // 初始化模态框
    initModal();
}

// 更新日历事件
async function updateCalendarEvents() {
    // 加载所有竞赛数据
    let allContests = await loadContests();
    
    // 应用筛选
    const sourceFilter = document.getElementById('calendar-source-filter');
    if (sourceFilter && sourceFilter.value !== 'all') {
        allContests = allContests.filter(contest => contest.source === sourceFilter.value);
    }
    
    // 转换为日历事件
    const events = convertContestsToEvents(allContests);
    
    // 更新日历
    if (window.calendar) {
        window.calendar.removeAllEvents();
        window.calendar.addEventSource(events);
    }
}

// 显示日历错误信息
function showCalendarError(message) {
    const calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        calendarEl.innerHTML = `<div class="calendar-error"><i class="fas fa-exclamation-circle" style="font-size: 24px; margin-right: 10px;"></i>${message}</div>`;
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
    
    // 处理截止时间，为空时不显示
    const modalDeadlineEl = document.getElementById('modal-deadline');
    const deadlineInfoItem = modalDeadlineEl ? modalDeadlineEl.closest('.info-item') : null;
    if (deadlineInfoItem) {
        if (contest.deadline) {
            // 提取deadline中的标签和日期
            if (contest.deadline.includes('活动日期')) {
                // 找到标签元素并修改
                const labelEl = deadlineInfoItem.querySelector('.label');
                if (labelEl) labelEl.textContent = '活动日期：';
                // 只显示日期部分
                modalDeadlineEl.textContent = contest.deadline.replace('活动日期：', '');
            } else if (contest.deadline.includes('截止日期')) {
                // 找到标签元素并修改
                const labelEl = deadlineInfoItem.querySelector('.label');
                if (labelEl) labelEl.textContent = '截止日期：';
                // 只显示日期部分
                modalDeadlineEl.textContent = contest.deadline.replace('截止日期：', '');
            } else {
                // 默认标签
                const labelEl = deadlineInfoItem.querySelector('.label');
                if (labelEl) labelEl.textContent = '截止时间：';
                modalDeadlineEl.textContent = contest.deadline;
            }
            deadlineInfoItem.style.display = 'block';
        } else {
            deadlineInfoItem.style.display = 'none';
        }
    }
    
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

// 初始化模态框
function initModal() {
    const modal = document.getElementById('contest-modal');
    const closeBtn = document.querySelector('.modal .close');
    
    if (!modal || !closeBtn) {
        console.error('modal或closeBtn元素不存在');
        return;
    }
    
    // 关闭按钮点击事件
    closeBtn.onclick = function() {
        modal.style.display = 'none';
    };
    
    // 点击模态框外部关闭
    modal.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };
    
    // 收藏按钮
    const favoriteBtn = document.getElementById('favorite-btn');
    if (favoriteBtn) {
        favoriteBtn.onclick = async function() {
            const modalTitle = document.getElementById('modal-title');
            const contestTitle = modalTitle ? modalTitle.textContent : '';
            const allContests = await loadContests();
            const contest = allContests.find(c => c.title === contestTitle);
            if (contest) {
                toggleFavorite(contest.id, contest);
                this.innerHTML = isFavorite(contest.id) ? '<i class="fas fa-star"></i> 已收藏' : '<i class="far fa-star"></i> 收藏';
            }
        };
    }
    
    // 有用按钮
    const likeBtn = document.getElementById('like-btn');
    if (likeBtn) {
        likeBtn.onclick = function() {
            alert('感谢您的反馈！');
        };
    }
    
    // 无用按钮
    const dislikeBtn = document.getElementById('dislike-btn');
    if (dislikeBtn) {
        dislikeBtn.onclick = function() {
            alert('感谢您的反馈，我们会不断改进！');
        };
    }
}