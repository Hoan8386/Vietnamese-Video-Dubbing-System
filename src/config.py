"""
File cấu hình cho tool
"""

# Whisper settings
WHISPER_MODEL_SIZE = "small"  # tiny, base, small, medium, large
WHISPER_LANGUAGE = "en"  # auto-detect nếu để None

# Translation settings
TRANSLATION_MODEL = "Helsinki-NLP/opus-mt-en-vi"
MAX_TRANSLATION_LENGTH = 512

# TTS settings
TTS_MODEL = "tts_models/vi/vivos/vits"
TTS_SPEED = 1.0  # Tốc độ nói (0.5-2.0)

# Audio settings
AUDIO_SAMPLE_RATE = 16000
AUDIO_NORMALIZE = True  # Chuẩn hóa âm lượng
AUDIO_NOISE_REDUCTION = False  # Giảm noise (experimental)

# Video settings
VIDEO_CODEC = "copy"  # copy hoặc libx264
AUDIO_CODEC = "aac"
AUDIO_BITRATE = "192k"

# Processing settings
BATCH_SIZE = 10  # Số câu xử lý cùng lúc cho TTS
KEEP_INTERMEDIATE_FILES = True  # Giữ file trung gian
ENABLE_PROGRESS_BAR = True  # Hiển thị thanh tiến trình

# Paths (relative to project root)
INPUT_DIR = "input"
OUTPUT_DIR = "output"
AUDIO_DIR = "audio"
SUBTITLES_DIR = "subtitles"
