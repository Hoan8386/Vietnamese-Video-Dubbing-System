"""
Các utility functions
"""

import os
import json
from pathlib import Path
from typing import Optional
import subprocess


def validate_video_file(video_path: str) -> bool:
    """
    Kiểm tra file video có hợp lệ không
    
    Args:
        video_path: Đường dẫn video
        
    Returns:
        True nếu hợp lệ, False nếu không
    """
    # Kiểm tra file tồn tại
    if not os.path.exists(video_path):
        print(f"❌ File không tồn tại: {video_path}")
        return False
    
    # Kiểm tra extension
    valid_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']
    ext = Path(video_path).suffix.lower()
    if ext not in valid_extensions:
        print(f"❌ Định dạng không hỗ trợ: {ext}")
        print(f"   Các định dạng hỗ trợ: {', '.join(valid_extensions)}")
        return False
    
    # Kiểm tra file size
    size_mb = os.path.getsize(video_path) / (1024 * 1024)
    if size_mb < 0.1:
        print(f"❌ File quá nhỏ: {size_mb:.2f} MB")
        return False
    
    # Kiểm tra video với ffprobe
    try:
        result = subprocess.run([
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_type",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ], capture_output=True, text=True, timeout=10)
        
        if result.stdout.strip() != "video":
            print(f"❌ File không chứa video stream")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⚠️ Không thể validate video (timeout)")
        return True  # Cho phép tiếp tục
    except FileNotFoundError:
        print(f"⚠️ Không tìm thấy ffprobe, bỏ qua validation")
        return True
    except Exception as e:
        print(f"⚠️ Lỗi validate: {e}")
        return True
    
    return True


def get_video_duration(video_path: str) -> Optional[float]:
    """
    Lấy độ dài video (giây)
    
    Args:
        video_path: Đường dẫn video
        
    Returns:
        Độ dài video hoặc None nếu lỗi
    """
    try:
        result = subprocess.run([
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ], capture_output=True, text=True, timeout=10)
        
        duration = float(result.stdout.strip())
        return duration
    except:
        return None


def format_time(seconds: float) -> str:
    """
    Format giây thành HH:MM:SS
    
    Args:
        seconds: Số giây
        
    Returns:
        String định dạng thời gian
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def save_checkpoint(checkpoint_file: str, step: str, data: dict = None):
    """
    Lưu checkpoint để resume
    
    Args:
        checkpoint_file: Đường dẫn file checkpoint
        step: Tên bước hiện tại
        data: Dữ liệu bổ sung
    """
    checkpoint = {
        "step": step,
        "data": data or {}
    }
    
    with open(checkpoint_file, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)


def load_checkpoint(checkpoint_file: str) -> Optional[dict]:
    """
    Load checkpoint
    
    Args:
        checkpoint_file: Đường dẫn file checkpoint
        
    Returns:
        Dữ liệu checkpoint hoặc None
    """
    if not os.path.exists(checkpoint_file):
        return None
    
    try:
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


def normalize_audio(audio_segment, target_dBFS=-20):
    """
    Chuẩn hóa âm lượng audio
    
    Args:
        audio_segment: pydub AudioSegment
        target_dBFS: Mức âm lượng mục tiêu
        
    Returns:
        AudioSegment đã chuẩn hóa
    """
    change_in_dBFS = target_dBFS - audio_segment.dBFS
    return audio_segment.apply_gain(change_in_dBFS)


def speed_change(audio_segment, speed=1.0):
    """
    Thay đổi tốc độ audio (time-stretching)
    
    Args:
        audio_segment: pydub AudioSegment
        speed: Tốc độ (1.0 = bình thường, 1.5 = nhanh hơn 50%)
        
    Returns:
        AudioSegment với tốc độ mới
    """
    # Thay đổi frame rate để tăng tốc
    sound_with_altered_frame_rate = audio_segment._spawn(
        audio_segment.raw_data,
        overrides={"frame_rate": int(audio_segment.frame_rate * speed)}
    )
    # Convert về sample rate gốc
    return sound_with_altered_frame_rate.set_frame_rate(audio_segment.frame_rate)
