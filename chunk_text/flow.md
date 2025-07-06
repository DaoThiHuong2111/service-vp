# Hướng dẫn triển khai huggingface model segment-any-text/sat-3l-sm

- Môi trường: python
- tạo venv: python -m venv sat-env
- run terminal: source sat-env/bin/activate
- run terminal: pip install wtpsplit
- run terminal: pip install fastapi uvicorn
- tạo file: app.py
<!-- port mặc định của app.py là 8087 -->
- run file app.py on background terminal: nohup python app.py > output.log 2>&1 &