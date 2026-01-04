import subprocess
import os


def extract_audio(video_path, out_audio):
    """
    Tách audio từ video bằng ffmpeg
    
    Args:
        video_path: Đường dẫn video input
        out_audio: Đường dẫn audio output (.wav)
    """
    print(f"🎵 Đang tách audio từ video: {video_path}")
    
    # Tạo thư mục nếu chưa tồn tại
    os.makedirs(os.path.dirname(out_audio), exist_ok=True)
    
    try:
        subprocess.run([
            "ffmpeg", "-y",
            "-i", video_path,
            "-vn",  # Không video
            "-acodec", "pcm_s16le",  # PCM 16-bit
            "-ar", "16000",  # Sample rate 16kHz (tốt cho Whisper)
            out_audio
        ], check=True, capture_output=True)
        
        print(f"✅ Tách audio thành công: {out_audio}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi tách audio: {e}")
        return False
    except FileNotFoundError:
        print("❌ Không tìm thấy ffmpeg. Vui lòng cài đặt ffmpeg.")
        return False


if __name__ == "__main__":
    # Test
    extract_audio("../input/video.mp4", "../audio/original.wav")
