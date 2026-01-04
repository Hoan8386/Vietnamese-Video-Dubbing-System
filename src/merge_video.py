import subprocess
import os


def merge_video(video_path, audio_path, out_video):
    """
    Ghép audio tiếng Việt vào video gốc (THAY THẾ audio gốc)
    
    Args:
        video_path: Đường dẫn video gốc
        audio_path: Đường dẫn audio tiếng Việt
        out_video: Đường dẫn video output
    """
    print(f"🎬 Đang ghép audio tiếng Việt vào video...")
    print(f"   📹 Video: {os.path.basename(video_path)}")
    print(f"   🎵 Audio: {os.path.basename(audio_path)}")
    
    # Tạo thư mục output nếu chưa có
    os.makedirs(os.path.dirname(out_video), exist_ok=True)
    
    try:
        # Lệnh FFmpeg: THAY THẾ audio gốc bằng audio VI
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,      # Input video (có audio gốc)
            "-i", audio_path,      # Input audio tiếng Việt
            "-map", "0:v:0",       # Chọn video stream từ input 0
            "-map", "1:a:0",       # Chọn audio stream từ input 1 (THAY THẾ audio gốc)
            "-c:v", "copy",        # Copy video codec (không encode lại)
            "-c:a", "aac",         # Encode audio sang AAC
            "-b:a", "192k",        # Audio bitrate
            "-shortest",           # Cắt theo input ngắn nhất
            out_video
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print(f"✅ Ghép video thành công: {out_video}")
        print(f"📁 Kích thước: {os.path.getsize(out_video) / (1024*1024):.2f} MB")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi ghép video:")
        print(f"   Return code: {e.returncode}")
        if e.stderr:
            print(f"   FFmpeg error: {e.stderr[-500:]}")  # In 500 ký tự cuối
        return False
    except FileNotFoundError:
        print("❌ Không tìm thấy ffmpeg. Vui lòng cài đặt ffmpeg.")
        print("   Download: https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
        return False


if __name__ == "__main__":
    # Test
    merge_video("../input/video.mp4", "../audio/vi_full.wav", "../output/video_vi.mp4")
