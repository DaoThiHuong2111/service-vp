# 🤖 AI Services Multi-Deployment

Tự động hóa deployment cho 2 AI services trên VPS Ubuntu:
- **Chunk Text API**: Segment Any Text API (Port 8087)
- **Embedding API**: Sentence Transformers Model (Port 8088)

## 🚀 Quick Start

### 1. Cài đặt Prerequisites
```bash
# Docker (Ubuntu)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

### 2. Deploy All Services
```bash
# Cấp quyền execute cho scripts
chmod +x *.sh

# Deploy tất cả services
./deploy.sh
```

### 3. Kiểm tra Status
```bash
./status.sh
```

## 📋 Available Scripts

| Script | Mô tả | Sử dụng |
|--------|-------|---------|
| `deploy.sh` | Deploy tất cả services | `./deploy.sh` |
| `status.sh` | Kiểm tra trạng thái services | `./status.sh` |
| `cleanup.sh` | Dọn dẹp containers/images | `./cleanup.sh [--all] [--volumes]` |

## 🛠️ Manual Commands

### Docker Compose Commands
```bash
# Start services
docker-compose up -d

# Stop services  
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart chunk-text-api
docker-compose restart embedding-api

# Rebuild specific service
docker-compose up -d --build chunk-text-api
```

### Health Checks
```bash
# Chunk Text API
curl http://localhost:8087/health

# Embedding API
curl http://localhost:8088/health
```

## 🔧 Services Configuration

### Chunk Text API (Port 8087)
- **Model**: segment-any-text/sat-3l-sm
- **Framework**: FastAPI + wtpsplit
- **Health Check**: `/health`
- **Documentation**: `/docs`

### Embedding API (Port 8088)  
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Framework**: Infinity Server
- **Health Check**: `/health`
- **Models Info**: `/models`

## 📂 Project Structure
```
vps/
├── chunk_text/          # Chunk Text API source
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── embeding/            # Embedding service config
│   └── flow.md
├── docker-compose.yml   # Services orchestration
├── deploy.sh           # Main deployment script
├── status.sh           # Status checking script
├── cleanup.sh          # Cleanup script
└── README.md           # This file
```

## 🔍 Troubleshooting

### Services không start
```bash
# Kiểm tra logs
docker-compose logs chunk-text-api
docker-compose logs embedding-api

# Kiểm tra ports có bị conflict không
netstat -tulpn | grep :808
```

### Memory issues
```bash
# Kiểm tra resource usage
docker stats

# Restart với memory limit
docker-compose down
docker-compose up -d
```

### Model download issues
```bash
# Clear cache và restart
./cleanup.sh --volumes
./deploy.sh
```

## 🌐 API Usage Examples

### Chunk Text API
```bash
# Test API
curl -X POST "http://localhost:8087/segment" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here"}'
```

### Embedding API
```bash
# Get embeddings
curl -X POST "http://localhost:8088/embeddings" \
  -H "Content-Type: application/json" \
  -d '{"input": ["text to embed"]}'
```

## 📊 Monitoring

### Real-time logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f chunk-text-api
```

### Resource monitoring
```bash
./status.sh
```

## 🔄 Updates

### Update services
```bash
# Pull latest images và rebuild
docker-compose pull
docker-compose up -d --build
```

### Clean deployment  
```bash
./cleanup.sh --all
./deploy.sh
```

## 💡 Tips

1. **First deployment** có thể mất vài phút do download models
2. **Memory**: Embedding service cần ít nhất 2GB RAM
3. **Storage**: Models cache sẽ được lưu trong Docker volumes
4. **Networking**: Services có thể communicate với nhau qua network `ai-services`

## 📞 Support

- Kiểm tra logs: `docker-compose logs -f`
- Status dashboard: `./status.sh`
- Full cleanup: `./cleanup.sh --all --volumes` 