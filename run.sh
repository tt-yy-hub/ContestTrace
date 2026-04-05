#!/bin/bash
echo "正在启动ContestTrace..."
echo "1. 安装依赖..."
pip3 install --no-cache-dir --timeout 60 -r requirements.txt
echo "2. 运行爬虫..."
python3 run.py --crawl
echo "3. 启动前端服务器..."
python3 -m http.server 8000 --directory contesttrace/frontend
echo "启动完成！请在浏览器中访问 http://localhost:8000"
echo "按Ctrl+C退出..."
