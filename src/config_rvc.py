"""
Configuration cho RVC Voice Cloning
Tối ưu cho RTX 3050 4GB

Author: Tool Lồng Tiếng
Date: 2026-01-05
"""

import torch

# ============================================================================
# RVC SETTINGS
# ============================================================================

# RVC Model paths
RVC_MODEL_PATH = None  # Set to your trained model path: "Retrieval-based-Voice-Conversion-WebUI/logs/model_name/added_*.pth"
RVC_INDEX_PATH = None  # Set to your index path: "Retrieval-based-Voice-Conversion-WebUI/logs/model_name/added_*.index"

# RVC Inference settings
RVC_F0_METHOD = "rmvpe"  # F0 extraction: "rmvpe", "harvest", "crepe", "pm"
RVC_INDEX_RATE = 0.75    # Index search rate (0.0-1.0) - higher = more similar to voice
RVC_FILTER_RADIUS = 3    # Median filter radius for F0
RVC_RMS_MIX_RATE = 0.25  # RMS mix rate (0.0-1.0) - 0.25 = 75% new voice
RVC_PROTECT = 0.33       # Protect voiceless consonants (0.0-0.5)

# RVC Training settings (for WebUI)
RVC_BATCH_SIZE = 4       # Batch size for training (4-6 for RTX 3050)
RVC_EPOCHS = 500         # Training epochs (500-1000)
RVC_SAVE_FREQUENCY = 50  # Save checkpoint every N epochs

# ============================================================================
# WHISPER SETTINGS
# ============================================================================

WHISPER_MODEL_SIZE = "small"  # tiny, base, small, medium, large
WHISPER_LANGUAGE = "en"       # auto-detect nếu để None
WHISPER_DEVICE = "auto"       # "cuda", "cpu", hoặc "auto"

# ============================================================================
# TRANSLATION SETTINGS
# ============================================================================

TRANSLATION_MODEL = "Helsinki-NLP/opus-mt-en-vi"
MAX_TRANSLATION_LENGTH = 512
TRANSLATION_BATCH_SIZE = 8

# ============================================================================
# TTS SETTINGS
# ============================================================================

TTS_MODEL = "tts_models/vi/vivos/vits"
TTS_SPEED = 1.0  # Tốc độ nói (0.5-2.0)
TTS_DEVICE = "auto"

# ============================================================================
# AUDIO SETTINGS
# ============================================================================

AUDIO_SAMPLE_RATE = 16000
AUDIO_NORMALIZE = True
AUDIO_NOISE_REDUCTION = False

# Background audio settings
BACKGROUND_VOLUME = 0.20  # Volume audio gốc (0.0-1.0)
# 0.15-0.20: Background nhẹ (nhạc background ít)
# 0.25-0.30: Background vừa phải
# 0.35-0.40: Background rõ hơn

# ============================================================================
# VIDEO SETTINGS
# ============================================================================

VIDEO_CODEC = "copy"      # copy hoặc libx264
AUDIO_CODEC = "aac"
AUDIO_BITRATE = "192k"

# ============================================================================
# GPU OPTIMIZATION SETTINGS (RTX 3050 4GB)
# ============================================================================

# Memory management
GPU_MEMORY_FRACTION = 0.85  # Use 85% of GPU memory
ENABLE_FP16 = True          # Use FP16 (half precision) - saves 50% VRAM
ENABLE_CUDNN_BENCHMARK = True
ENABLE_TF32 = True

# VRAM optimization
CLEAR_CACHE_FREQUENCY = 10  # Clear CUDA cache every N operations
BATCH_PROCESSING = True     # Process in batches to save memory

# ============================================================================
# PROCESSING SETTINGS
# ============================================================================

BATCH_SIZE = 10  # Số câu xử lý cùng lúc
KEEP_INTERMEDIATE_FILES = True
ENABLE_PROGRESS_BAR = True
NUM_WORKERS = 4  # Số CPU threads

# ============================================================================
# PATHS (relative to project root)
# ============================================================================

INPUT_DIR = "input"
OUTPUT_DIR = "output"
AUDIO_DIR = "audio"
SUBTITLES_DIR = "subtitles"

# RVC specific paths
RVC_BASE_DIR = "Retrieval-based-Voice-Conversion-WebUI"
RVC_LOGS_DIR = f"{RVC_BASE_DIR}/logs"
RVC_WEIGHTS_DIR = f"{RVC_BASE_DIR}/weights"

# ============================================================================
# DEVICE CONFIGURATION
# ============================================================================

def get_device():
    """Get optimal device for processing"""
    if torch.cuda.is_available():
        device = torch.device("cuda")
        
        # Apply optimizations for RTX 3050
        torch.cuda.set_per_process_memory_fraction(GPU_MEMORY_FRACTION, 0)
        
        if ENABLE_CUDNN_BENCHMARK:
            torch.backends.cudnn.benchmark = True
        
        if ENABLE_TF32:
            torch.backends.cuda.matmul.allow_tf32 = True
        
        return device
    else:
        return torch.device("cpu")


# ============================================================================
# PRESET CONFIGURATIONS
# ============================================================================

# Preset cho RTX 3050 4GB
PRESET_RTX3050 = {
    'whisper_model': 'small',
    'rvc_batch_size': 4,
    'rvc_f0_method': 'rmvpe',
    'enable_fp16': True,
    'gpu_memory_fraction': 0.85,
    'background_volume': 0.20,
    'rvc_index_rate': 0.75,
}

# Preset cho RTX 3060 6GB
PRESET_RTX3060 = {
    'whisper_model': 'medium',
    'rvc_batch_size': 8,
    'rvc_f0_method': 'rmvpe',
    'enable_fp16': True,
    'gpu_memory_fraction': 0.90,
    'background_volume': 0.20,
    'rvc_index_rate': 0.80,
}

# Preset cho RTX 3080+ 10GB
PRESET_RTX3080 = {
    'whisper_model': 'large',
    'rvc_batch_size': 16,
    'rvc_f0_method': 'crepe',
    'enable_fp16': False,
    'gpu_memory_fraction': 0.95,
    'background_volume': 0.20,
    'rvc_index_rate': 0.85,
}

# Preset cho CPU
PRESET_CPU = {
    'whisper_model': 'base',
    'rvc_batch_size': 2,
    'rvc_f0_method': 'harvest',
    'enable_fp16': False,
    'background_volume': 0.20,
    'rvc_index_rate': 0.70,
}


def apply_preset(preset_name):
    """Apply preset configuration"""
    presets = {
        'rtx3050': PRESET_RTX3050,
        'rtx3060': PRESET_RTX3060,
        'rtx3080': PRESET_RTX3080,
        'cpu': PRESET_CPU,
    }
    
    if preset_name.lower() in presets:
        preset = presets[preset_name.lower()]
        
        # Apply settings
        global WHISPER_MODEL_SIZE, RVC_BATCH_SIZE, RVC_F0_METHOD
        global ENABLE_FP16, GPU_MEMORY_FRACTION, BACKGROUND_VOLUME, RVC_INDEX_RATE
        
        WHISPER_MODEL_SIZE = preset.get('whisper_model', WHISPER_MODEL_SIZE)
        RVC_BATCH_SIZE = preset.get('rvc_batch_size', RVC_BATCH_SIZE)
        RVC_F0_METHOD = preset.get('rvc_f0_method', RVC_F0_METHOD)
        ENABLE_FP16 = preset.get('enable_fp16', ENABLE_FP16)
        GPU_MEMORY_FRACTION = preset.get('gpu_memory_fraction', GPU_MEMORY_FRACTION)
        BACKGROUND_VOLUME = preset.get('background_volume', BACKGROUND_VOLUME)
        RVC_INDEX_RATE = preset.get('rvc_index_rate', RVC_INDEX_RATE)
        
        print(f"✅ Applied preset: {preset_name.upper()}")
    else:
        print(f"⚠️ Unknown preset: {preset_name}")


def auto_detect_preset():
    """Auto detect and apply optimal preset"""
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0).upper()
        vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        
        print(f"🔍 Detected: {gpu_name} ({vram:.1f} GB VRAM)")
        
        if "3050" in gpu_name or vram <= 4.5:
            apply_preset('rtx3050')
        elif "3060" in gpu_name or (4.5 < vram <= 6.5):
            apply_preset('rtx3060')
        elif vram > 6.5:
            apply_preset('rtx3080')
        else:
            print("⚠️ Unknown GPU, using RTX 3050 preset as safe default")
            apply_preset('rtx3050')
    else:
        print("🔍 No GPU detected, using CPU preset")
        apply_preset('cpu')


# Auto-detect on import
if __name__ != "__main__":
    auto_detect_preset()
