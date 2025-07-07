# app_optimized.py - Optimized version with caching and cleanup (no real-time monitoring)
import gc
import hashlib
from functools import lru_cache
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from wtpsplit import SaT
import logging
from typing import List, Optional, Dict, Any
import time
import asyncio

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
sat_model = None

# Cache configuration
CACHE_SIZE = 100  # Số lượng kết quả cache tối đa

# Memory management configuration
GC_COLLECT_INTERVAL = 10  # Số requests để trigger gc.collect()

request_counter = 0
cache_stats = {"hits": 0, "misses": 0}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management cho FastAPI app"""
    # Startup
    await load_model()
    
    # Background task để cleanup memory định kỳ
    cleanup_task = asyncio.create_task(background_cleanup())
    
    yield
    
    # Shutdown
    cleanup_task.cancel()
    await cleanup_model()

# Khởi tạo FastAPI app với lifespan
app = FastAPI(
    title="Segment Any Text API - Optimized",
    description="Optimized API for text segmentation using SaT model with caching and cleanup",
    version="1.1.0",
    lifespan=lifespan
)

async def load_model():
    """Load model với optimization"""
    global sat_model
    logger.info("Loading SaT model...")
    start_time = time.time()
    
    try:
        sat_model = SaT("sat-3l-sm")
        
        # Set model to eval mode để tắt gradient computation
        if hasattr(sat_model, 'eval'):
            sat_model.eval()
            
        # Nếu có GPU, uncomment và optimize:
        # sat_model.half().to("cuda")
        # torch.cuda.empty_cache()
        
        load_time = time.time() - start_time
        logger.info(f"Model loaded successfully in {load_time:.2f}s!")
        
        # Initial memory cleanup
        gc.collect()
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise e

async def cleanup_model():
    """Cleanup model resources"""
    global sat_model
    if sat_model is not None:
        del sat_model
        sat_model = None
        gc.collect()
        logger.info("Model resources cleaned up")

def force_cleanup():
    """Force cleanup without monitoring"""
    try:
        # Python garbage collection
        collected = gc.collect()
        
        # Clear torch cache if available
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
        
        logger.info(f"Cleanup: collected {collected} objects")
        return collected
    except Exception as e:
        logger.warning(f"Cleanup error: {str(e)}")
        return 0

async def background_cleanup():
    """Background task cleanup định kỳ"""
    while True:
        try:
            await asyncio.sleep(60)  # Cleanup every 60 seconds
            force_cleanup()
            logger.info("Background cleanup executed")
                
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Background cleanup error: {str(e)}")

def create_text_hash(text: str, **kwargs) -> str:
    """Tạo hash unique cho text và parameters"""
    content = f"{text}_{kwargs}"
    return hashlib.md5(content.encode()).hexdigest()

@lru_cache(maxsize=CACHE_SIZE)
def cached_segment_single(text_hash: str, text: str, **kwargs) -> tuple:
    """Cached segmentation cho single text"""
    global sat_model, cache_stats
    
    if sat_model is None:
        raise ValueError("Model not loaded")
    
    cache_stats["misses"] += 1
    
    # Thực hiện segmentation
    sentences = sat_model.split(text, **kwargs)
    
    # Xử lý kết quả cho paragraph segmentation
    if kwargs.get('do_paragraph_segmentation', False):
        flat_sentences = []
        for paragraph in sentences:
            flat_sentences.extend(paragraph)
        sentences = flat_sentences
    
    # Làm sạch sentences
    clean_sentences = [s.strip() for s in sentences if s.strip()]
    
    return tuple(clean_sentences)  # Return tuple để có thể cache

def get_cached_result(text: str, **kwargs) -> List[str]:
    """Lấy kết quả từ cache hoặc tính toán mới"""
    global cache_stats
    
    text_hash = create_text_hash(text, **kwargs)
    
    try:
        # Try cache first
        result = cached_segment_single(text_hash, text, **kwargs)
        cache_stats["hits"] += 1
        return list(result)
    except:
        # Cache miss, tính toán trực tiếp
        cache_stats["misses"] += 1
        return list(cached_segment_single(text_hash, text, **kwargs))

async def cleanup_after_request():
    """Cleanup sau mỗi request"""
    global request_counter
    request_counter += 1
    
    # Garbage collection mỗi N requests
    if request_counter % GC_COLLECT_INTERVAL == 0:
        force_cleanup()

# Pydantic models
class TextInput(BaseModel):
    text: str
    do_paragraph_segmentation: Optional[bool] = False
    threshold: Optional[float] = None

class BatchTextInput(BaseModel):
    texts: List[str]
    do_paragraph_segmentation: Optional[bool] = False
    threshold: Optional[float] = None

class SegmentationResponse(BaseModel):
    sentences: List[str]
    sentence_count: int
    processing_time: Optional[float] = None
    cached: Optional[bool] = False

class BatchSegmentationResponse(BaseModel):
    results: List[SegmentationResponse]
    total_texts: int
    total_processing_time: float

# API endpoints
@app.get("/")
async def root():
    return {
        "message": "Segment Any Text API - Optimized", 
        "model": "sat-3l-sm",
        "version": "1.1.0",
        "features": ["caching", "auto_cleanup"]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "model_loaded": sat_model is not None,
        "request_count": request_counter
    }

@app.post("/cache/clear")
async def clear_cache():
    """Clear segmentation cache"""
    cached_segment_single.cache_clear()
    cache_stats["hits"] = 0
    cache_stats["misses"] = 0
    
    return {
        "message": "Cache cleared successfully",
        "cache_stats": cache_stats
    }

@app.get("/cache/stats")
async def cache_stats_endpoint():
    """Get cache statistics"""
    cache_info = cached_segment_single.cache_info()
    
    return {
        "cache_size": CACHE_SIZE,
        "cache_hits": cache_info.hits,
        "cache_misses": cache_info.misses,
        "cache_hit_rate": f"{(cache_info.hits / max(cache_info.hits + cache_info.misses, 1) * 100):.1f}%",
        "current_size": cache_info.currsize,
        "max_size": cache_info.maxsize
    }

@app.post("/segment", response_model=SegmentationResponse)
async def segment_text(input_data: TextInput, background_tasks: BackgroundTasks):
    """Chia tách một văn bản thành các câu - Optimized version"""
    start_time = time.time()
    
    try:
        if sat_model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Prepare kwargs
        kwargs = {}
        if input_data.threshold is not None:
            kwargs['threshold'] = input_data.threshold
        if input_data.do_paragraph_segmentation:
            kwargs['do_paragraph_segmentation'] = True
        
        # Check if result is cached
        cache_info = cached_segment_single.cache_info()
        initial_hits = cache_info.hits
        
        clean_sentences = get_cached_result(input_data.text, **kwargs)
        
        # Check if this was a cache hit
        cache_info_after = cached_segment_single.cache_info()
        was_cached = cache_info_after.hits > initial_hits
        
        processing_time = time.time() - start_time
        
        # Schedule cleanup
        background_tasks.add_task(cleanup_after_request)
        
        return SegmentationResponse(
            sentences=clean_sentences,
            sentence_count=len(clean_sentences),
            processing_time=processing_time,
            cached=was_cached
        )
        
    except Exception as e:
        logger.error(f"Error in segmentation: {str(e)}")
        # Cleanup on error
        background_tasks.add_task(cleanup_after_request)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/segment-batch", response_model=BatchSegmentationResponse)
async def segment_batch_texts(input_data: BatchTextInput, background_tasks: BackgroundTasks):
    """Chia tách nhiều văn bản cùng lúc - Optimized batch processing"""
    start_time = time.time()
    
    try:
        if sat_model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        kwargs = {}
        if input_data.threshold is not None:
            kwargs['threshold'] = input_data.threshold
        if input_data.do_paragraph_segmentation:
            kwargs['do_paragraph_segmentation'] = True
        
        results = []
        
        # Process each text
        for text in input_data.texts:
            text_start = time.time()
            
            # Check cache
            cache_info = cached_segment_single.cache_info()
            initial_hits = cache_info.hits
            
            clean_sentences = get_cached_result(text, **kwargs)
            
            cache_info_after = cached_segment_single.cache_info()
            was_cached = cache_info_after.hits > initial_hits
            
            text_time = time.time() - text_start
            
            results.append(SegmentationResponse(
                sentences=clean_sentences,
                sentence_count=len(clean_sentences),
                processing_time=text_time,
                cached=was_cached
            ))
        
        total_time = time.time() - start_time
        
        # Schedule cleanup
        background_tasks.add_task(cleanup_after_request)
        
        return BatchSegmentationResponse(
            results=results,
            total_texts=len(input_data.texts),
            total_processing_time=total_time
        )
        
    except Exception as e:
        logger.error(f"Error in batch segmentation: {str(e)}")
        background_tasks.add_task(cleanup_after_request)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model-info")
async def model_info():
    """Thông tin về model hiện tại"""
    if sat_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    cache_info = cached_segment_single.cache_info()
    
    return {
        "model_name": "sat-3l-sm",
        "description": "3-layer Segment Any Text model",
        "supported_languages": 85,
        "includes_vietnamese": True,
        "paper": "https://arxiv.org/abs/2406.16678",
        "optimization_features": {
            "caching": True,
            "background_cleanup": True,
            "cache_size": CACHE_SIZE,
            "cache_hits": cache_info.hits,
            "cache_misses": cache_info.misses,
            "cache_hit_rate": f"{(cache_info.hits / max(cache_info.hits + cache_info.misses, 1) * 100):.1f}%"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8087) 