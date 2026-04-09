// 初始化数据到 localStorage
if (!localStorage.getItem('contest_data')) {
    // 从 contests.json 加载数据
    fetch('data/contests.json')
        .then(response => response.json())
        .then(data => {
            localStorage.setItem('contest_data', JSON.stringify(data));
            console.log('数据已初始化到 localStorage');
        })
        .catch(error => {
            console.error('加载数据失败:', error);
        });
}
