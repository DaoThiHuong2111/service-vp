# Hướng dẫn triển khai huggingface model sentence-transformers/all-MiniLM-L6-v2

docker run -d -p 8088:8088 -m 2g --cpus="1.5" --restart unless-stopped -v ~/infinity_cache:/app/.cache michaelf34/infinity:latest v2 --model-id sentence-transformers/all-MiniLM-L6-v2 --port 8088 --engine torch --device cpu