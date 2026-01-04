"""
Tool Lồng Tiếng Tự Động
Chuyển đổi video tiếng Anh sang tiếng Việt

Author: Auto Dubbing Tool
Date: 2026-01-04
"""

import os
import sys
import json
from pathlib import Path

# Import config
import config

# Import các module
from extract_audio import extract_audio
from asr_whisper import transcribe
from voice_analysis import analyze_all_segments
from translate import translate_segments
from tts_advanced import tts_segments_advanced
from merge_audio_v3 import merge_segments_with_background
from merge_video import merge_video


def main():
    """Pipeline chính"""
    
    print("=" * 60)
    print("🎬 TOOL LỒNG TIẾNG TỰ ĐỘNG - VIETNAMESE DUBBING")
    print("=" * 60)
    
    # Đường dẫn
    base_dir = Path(__file__).parent.parent
    input_video = base_dir / "input" / "video.mp4"
    output_video = base_dir / "output" / "video_vi.mp4"
    
    audio_dir = base_dir / "audio"
    original_audio = audio_dir / "original.wav"
    vi_full_audio = audio_dir / "vi_full.wav"
    vi_segments_dir = audio_dir / "vi_segments"
    
    subtitles_dir = base_dir / "subtitles"
    en_json = subtitles_dir / "en.json"
    vi_json = subtitles_dir / "vi.json"
    
    # Kiểm tra file input
    if not input_video.exists():
        print(f"❌ Không tìm thấy video: {input_video}")
        print(f"📌 Vui lòng đặt video vào thư mục: {input_video.parent}")
        return False
    
    print(f"\n📹 Video input: {input_video.name}")
    print(f"📁 Kích thước: {input_video.stat().st_size / (1024*1024):.2f} MB")
    
    try:
        # Bước 1: Tách audio
        print("\n" + "="*60)
        print("BƯỚC 1/6: TÁCH AUDIO TỪ VIDEO")
        print("="*60)
        if not extract_audio(str(input_video), str(original_audio)):
            raise Exception("Lỗi tách audio")
        
        # Bước 2: Nhận dạng giọng nói (ASR)
        print("\n" + "="*60)
        print("BƯỚC 2/7: NHẬN DẠNG GIỌNG NÓI (WHISPER)")
        print("="*60)
        if not transcribe(str(original_audio), str(en_json), model_size="small"):
            raise Exception("Lỗi nhận dạng giọng nói")
        
        # Bước 3: Phân tích giọng nói (Gender & Emotion)
        print("\n" + "="*60)
        print("BƯỚC 3/7: PHÂN TÍCH GIỌNG NÓI (GENDER & EMOTION)")
        print("="*60)
        if not analyze_all_segments(str(original_audio), str(en_json)):
            print("⚠️ Lỗi phân tích giọng, tiếp tục với giọng mặc định")
        
        # Bước 4: Dịch sang tiếng Việt
        print("\n" + "="*60)
        print("BƯỚC 4/7: DỊCH SANG TIẾNG VIỆT")
        print("="*60)
        if not translate_segments(str(en_json), str(vi_json)):
            raise Exception("Lỗi dịch")
        
        # Bước 5: Text-to-Speech tiếng Việt (với auto voice selection & mixing)
        print("\n" + "="*60)
        print("BƯỚC 5/7: TỔNG HỢP GIỌNG NÓI TIẾNG VIỆT (ADVANCED TTS)")
        print("="*60)
        # enable_mixing=True để mix audio gốc (20% volume) với TTS, giữ cảm xúc tốt hơn
        # Set False nếu audio gốc có nhiều noise hoặc không muốn mix
        if not tts_segments_advanced(str(vi_json), str(original_audio), str(vi_segments_dir), 
                                     auto_voice=True, enable_mixing=True):
            raise Exception("Lỗi TTS")
        
        # Bước 6: Ghép audio segments với background liên tục
        print("\n" + "="*60)
        print("BƯỚC 6/7: GHÉP AUDIO SEGMENTS (VỚI BACKGROUND LIÊN TỤC)")
        print("="*60)
        # Sử dụng background_volume từ config (có thể điều chỉnh trong config.py)
        if not merge_segments_with_background(
            str(vi_json), 
            str(original_audio),  # Audio gốc làm background
            str(vi_full_audio),
            background_volume=config.BACKGROUND_VOLUME,
            normalize=True
        ):
            raise Exception("Lỗi ghép audio")
        
        # Bước 7: Ghép audio vào video
        print("\n" + "="*60)
        print("BƯỚC 7/7: GHÉP AUDIO VÀO VIDEO")
        print("="*60)
        if not merge_video(str(input_video), str(vi_full_audio), str(output_video)):
            raise Exception("Lỗi ghép video")
        
        # Hoàn thành
        print("\n" + "="*60)
        print("🎉 HOÀN THÀNH!")
        print("="*60)
        print(f"✅ Video đã lồng tiếng: {output_video}")
        print(f"📁 Kích thước: {output_video.stat().st_size / (1024*1024):.2f} MB")
        print(f"\n📊 Các file trung gian:")
        print(f"   - Transcript EN: {en_json}")
        print(f"   - Transcript VI: {vi_json}")
        print(f"   - Audio VI: {vi_full_audio}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
