# Workflow: Multi Service Deployment

## Current tasks from user prompt:
- Tự động hóa deployment cho 2 services:
  - chunk_text: Segment Any Text API (port 8087)
  - embeding: sentence-transformers model (port 8088)
- Tạo docker-compose hoặc shell script để deploy cùng lúc
- Trên VPS Ubuntu

## Plan (simple):
Tạo docker-compose.yml để orchestrate cả 2 services:
- Service 1: chunk_text (custom Dockerfile có sẵn)
- Service 2: embeding (sử dụng image michaelf34/infinity:latest)
- Cấu hình networking, ports, volumes
- Tạo thêm shell scripts tiện lợi

## Steps:
1. Tạo docker-compose.yml với 2 services
2. Tạo shell script build-and-run.sh để tiện lợi
3. Tạo shell script cleanup.sh để dọn dẹp
4. Tạo README.md hướng dẫn sử dụng
5. Test deployment trên VPS

## Things done:
- ✓ Đọc và phân tích cấu trúc 2 services
- ✓ Hiểu requirements và ports của từng service
- ✓ Tạo docker-compose.yml với 2 services orchestration
- ✓ Tạo deploy.sh script với health checks và colored output
- ✓ Tạo cleanup.sh script với options --all và --volumes
- ✓ Tạo status.sh script với comprehensive dashboard
- ✓ Tạo README.md với hướng dẫn đầy đủ
- ✓ Cấp quyền execute cho tất cả scripts

## Things aren't done yet:
- Test deployment trên VPS để đảm bảo hoạt động chính xác 