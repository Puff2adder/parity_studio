@echo off
pushd "%~dp0"
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8512 --browser.gatherUsageStats false
popd
