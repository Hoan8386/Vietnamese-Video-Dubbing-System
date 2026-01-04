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
        result = subprocess.run([
            "ffmpeg", "-y",
            "-i", video_path,
            "-vn",  # Không video
            "-acodec", "pcm_s16le",  # PCM 16-bit
            "-ar", "16000",  # Sample rate 16kHz (tốt cho Whisper)
            "-ac", "1",  # Mono channel
            out_audio
        ], check=True, capture_output=True, text=True)
        
        # Kiểm tra file output có tồn tại và có kích thước > 0
        if os.path.exists(out_audio) and os.path.getsize(out_audio) > 0:
            print(f"✅ Tách audio thành công: {out_audio}")
            print(f"📁 Kích thước: {os.path.getsize(out_audio) / (1024*1024):.2f} MB")
            return True
        else:
            print(f"❌ File audio không được tạo hoặc rỗng")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi tách audio:")
        print(f"   Error code: {e.returncode}")
        if e.stderr:
            print(f"   FFmpeg error: {e.stderr[-500:]}")  # In 500 ký tự cuối
        return False
    except FileNotFoundError:
        print("❌ Không tìm thấy ffmpeg. Vui lòng cài đặt ffmpeg.")
        print("   Tải tại: https://ffmpeg.org/download.html")
        return False


if __name__ == "__main__":
    # Test
    extract_audio("../input/video.mp4", "../audio/original.wav")
