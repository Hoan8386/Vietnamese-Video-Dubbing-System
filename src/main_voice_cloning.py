"""
Tool Lồng Tiếng Tự Động với Voice Cloning
Chuyển đổi video tiếng Anh sang tiếng Việt, giữ nguyên giọng gốc

Author: Auto Dubbing Tool
Date: 2026-01-04
"""

import os
import sys
import json
from pathlib import Path

# Import các module
from extract_audio import extract_audio
from asr_whisper import transcribe
from translate import translate_segments
from voice_cloning import tts_with_voice_cloning
from merge_audio import merge_segments
from merge_video import merge_video


def main():
    """Pipeline với Voice Cloning"""
    
    print("=" * 60)
    print("🎬 TOOL LỒNG TIẾNG - VOICE CLONING MODE")
    print("=" * 60)
    
    # Đường dẫn
    base_dir = Path(__file__).parent.parent
    input_video = base_dir / "input" / "video.mp4"
    output_video = base_dir / "output" / "video_vi_cloned.mp4"
    
    audio_dir = base_dir / "audio"
    original_audio = audio_dir / "original.wav"
    vi_full_audio = audio_dir / "vi_full_cloned.wav"
    vi_segments_dir = audio_dir / "vi_segments_cloned"
    
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
        print("BƯỚC 2/6: NHẬN DẠNG GIỌNG NÓI (WHISPER)")
        print("="*60)
        if not transcribe(str(original_audio), str(en_json), model_size="small"):
            raise Exception("Lỗi nhận dạng giọng nói")
        
        # Bước 3: Dịch sang tiếng Việt
        print("\n" + "="*60)
        print("BƯỚC 3/6: DỊCH SANG TIẾNG VIỆT")
        print("="*60)
        if not translate_segments(str(en_json), str(vi_json)):
            raise Exception("Lỗi dịch")
        
        # Bước 4: Voice Cloning TTS
        print("\n" + "="*60)
        print("BƯỚC 4/6: VOICE CLONING TTS")
        print("="*60)
        if not tts_with_voice_cloning(str(vi_json), str(original_audio), str(vi_segments_dir)):
            print("\n⚠️ Voice cloning failed. Quay về Edge TTS...")
            # Fallback to Edge TTS
            from tts_vi import tts_segments
            if not tts_segments(str(vi_json), str(vi_segments_dir), auto_voice=True):
                raise Exception("Lỗi TTS")
        
        # Bước 5: Ghép audio segments
        print("\n" + "="*60)
        print("BƯỚC 5/6: GHÉP AUDIO SEGMENTS")
        print("="*60)
        if not merge_segments(str(vi_json), str(vi_full_audio)):
            raise Exception("Lỗi ghép audio")
        
        # Bước 6: Ghép audio vào video
        print("\n" + "="*60)
        print("BƯỚC 6/6: GHÉP AUDIO VÀO VIDEO")
        print("="*60)
        if not merge_video(str(input_video), str(vi_full_audio), str(output_video)):
            raise Exception("Lỗi ghép video")
        
        # Hoàn thành
        print("\n" + "="*60)
        print("🎉 HOÀN THÀNH!")
        print("="*60)
        print(f"✅ Video đã lồng tiếng (Voice Cloned): {output_video}")
        print(f"📁 Kích thước: {output_video.stat().st_size / (1024*1024):.2f} MB")
        print(f"\n💡 Lưu ý: Giọng nói đã được clone từ video gốc")
        print(f"📊 Các file trung gian:")
        print(f"   - Transcript EN: {en_json}")
        print(f"   - Transcript VI: {vi_json}")
        print(f"   - Audio VI: {vi_full_audio}")
        print(f"   - Speaker Embedding: {vi_segments_dir}/speaker_embedding.pth")
        
        return True
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
