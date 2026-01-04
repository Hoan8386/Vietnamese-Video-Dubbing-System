import subprocess
import os


def merge_video(video_path, audio_path, out_video):
    """
    Ghép audio tiếng Việt vào video gốc
    
    Args:
        video_path: Đường dẫn video gốc
        audio_path: Đường dẫn audio tiếng Việt
        out_video: Đường dẫn video output
    """
    print(f"🎬 Đang ghép audio vào video...")
    
    # Tạo thư mục output nếu chưa có
    os.makedirs(os.path.dirname(out_video), exist_ok=True)
    
    try:
        subprocess.run([
            "ffmpeg", "-y",
            "-i", video_path,  # Input video
            "-i", audio_path,  # Input audio
            "-map", "0:v",     # Lấy video từ input 0
            "-map", "1:a",     # Lấy audio từ input 1
            "-c:v", "copy",    # Copy video codec (không encode lại)
            "-c:a", "aac",     # Encode audio sang AAC
            "-shortest",       # Cắt theo input ngắn nhất
            out_video
        ], check=True, capture_output=True)
        
        print(f"✅ Ghép video thành công: {out_video}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi ghép video: {e}")
        return False
    except FileNotFoundError:
        print("❌ Không tìm thấy ffmpeg. Vui lòng cài đặt ffmpeg.")
        return False


if __name__ == "__main__":
    # Test
    merge_video("../input/video.mp4", "../audio/vi_full.wav", "../output/video_vi.mp4")
