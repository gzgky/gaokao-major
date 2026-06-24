@echo off
cd /d "D:\VS软件存放处\蓝色vscode\Deep_learning\Deep_learning_260403\高考志愿"
start http://localhost:8503
streamlit run app.py --server.port 8503
pause
