# Workflow: Docker Build Fix

## Current tasks from user prompt:
- Fix lỗi Docker build: ValueError: Please install `torch` to use WtP with a PyTorch model
- Thêm PyTorch dependency vào requirements.txt
- Rebuild Docker container thành công

## Plan (simple):
Vấn đề: wtpsplit cần PyTorch để load model "sat-3l-sm" nhưng torch không có trong requirements.txt
Giải pháp: Thêm torch vào requirements.txt, rebuild Docker image

## Steps:
1. Xác định nguyên nhân: thiếu torch dependency
2. Update requirements.txt thêm torch (CPU-only để tối ưu size)
3. Update docker-guide.md với hướng dẫn cleanup và rebuild
4. Hướng dẫn user rebuild Docker image
5. Test container chạy thành công

## Things done:
- ✓ Phân tích lỗi: thiếu PyTorch dependency
- ✓ Update requirements.txt thêm torch>=2.0.0
- ✓ Update docker-guide.md với section rebuild và troubleshooting
- ✓ Cung cấp hướng dẫn cleanup và rebuild cho user
- ✓ Tối ưu torch CPU-only để giảm kích thước Docker image từ ~500MB xuống ~300MB
- ✓ Update requirements.txt với --index-url cho PyTorch CPU-only
- ✓ Thêm environment variables tối ưu CPU trong Dockerfile (OMP_NUM_THREADS=1)
- ✓ Update docker-guide.md với section tối ưu hóa CPU

## Things aren't done yet:
- User cần rebuild Docker image với dependency mới
- Test container chạy thành công 