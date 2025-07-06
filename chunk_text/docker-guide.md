# Docker Guide - Segment Any Text API

## Cách build và chạy Docker container

### 1. Build Docker image
```bash
# Di chuyển vào thư mục chứa Dockerfile
cd chunk_text

# Build Docker image
docker build -t sat-api:latest .
```

### 2. Chạy Docker container
```bash
# Chạy container
docker run -d -p 8087:8087 --name sat-api-container sat-api:latest

# Hoặc chạy với logs
docker run -p 8087:8087 --name sat-api-container sat-api:latest
```

### 3. Kiểm tra container
```bash
# Kiểm tra container đang chạy
docker ps

# Kiểm tra logs
docker logs sat-api-container

# Kiểm tra health
curl http://0.0.0.0:8087/health
```

### 4. Test API
```bash
# Test endpoint root
curl http://l0.0.0.0:8087/

# Test segmentation
curl -X POST "http://0.0.0.0:8087/segment" \
     -H "Content-Type: application/json" \
     -d '{"text": "Đây là câu đầu tiên. Đây là câu thứ hai."}'
```

### 5. Dừng và xóa container
```bash
# Dừng container
docker stop sat-api-container

# Xóa container
docker rm sat-api-container

# Xóa image (nếu cần)
docker rmi sat-api:latest
```

## Thông tin về Docker image
- **Base image**: python:3.11-slim
- **Port**: 8087
- **Health check**: Có sẵn tại `/health`
- **Security**: Chạy với non-root user
- **Optimization**: Multi-layer caching, .dockerignore

## Lưu ý
- Lần đầu chạy sẽ mất thời gian để download model `sat-3l-sm`
- Container sẽ tự động restart nếu app bị crash
- Có thể mount volume để persist data nếu cần 