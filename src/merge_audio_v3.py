"""
Version v3: Giữ audio gốc làm background xuyên suốt video
- Audio gốc giảm volume (20-30%) làm nền liên tục
- TTS overlay lên trên chỉ ở các đoạn có lời thoại
"""

from pydub import AudioSegment
import json
import os


def merge_segments_with_background(segments_json, original_audio_path, out_wav, 
                                   background_volume=0.25, normalize=True):
    """
    Ghép các audio segments lên trên audio gốc (dùng làm background)
    
    Args:
        segments_json: JSON chứa segments với timing và audio paths
        original_audio_path: Đường dẫn audio gốc (dùng làm background liên tục)
        out_wav: Đường dẫn file audio output
        background_volume: Volume của audio gốc (0.0-1.0), mặc định 0.25 = 25%
        normalize: Chuẩn hóa âm lượng các đoạn TTS
    """
    print("🎵 Đang ghép audio với background liên tục...")
    
    try:
        # Load segments
        with open(segments_json, encoding="utf-8") as f:
            segments = json.load(f)
        
        # Load audio gốc làm background
        print(f"📂 Loading audio gốc: {original_audio_path}")
        background_audio = AudioSegment.from_file(original_audio_path)
        
        # Giảm volume audio gốc để làm nền
        volume_reduction_db = int((1.0 - background_volume) * 60)  # 0.25 -> ~45dB giảm
        background_audio = background_audio - volume_reduction_db
        
        print(f"🔉 Background volume: {background_volume*100:.0f}% (giảm {volume_reduction_db}dB)")
        print(f"⏱️  Background duration: {len(background_audio)/1000:.2f}s")
        print(f"📊 Số segments: {len(segments)}")
        
        # Tạo một bản copy để overlay các đoạn TTS lên
        final_audio = background_audio
        
        # Overlay từng segment TTS lên trên background
        overlay_count = 0
        for i, seg in enumerate(segments):
            if seg.get("vi_audio_path") and os.path.exists(seg["vi_audio_path"]):
                try:
                    # Load audio segment
                    audio_path = seg["vi_audio_path"]
                    
                    # Tự động detect format
                    if audio_path.lower().endswith('.mp3'):
                        audio_seg = AudioSegment.from_mp3(audio_path)
                    elif audio_path.lower().endswith('.wav'):
                        audio_seg = AudioSegment.from_wav(audio_path)
                    else:
                        audio_seg = AudioSegment.from_file(audio_path)
                    
                    # Normalize volume TTS nếu cần
                    if normalize:
                        # Tăng volume TTS để nổi bật hơn background
                        target_dBFS = -16.0
                        change_in_dBFS = target_dBFS - audio_seg.dBFS
                        audio_seg = audio_seg + change_in_dBFS
                    
                    # Vị trí bắt đầu (ms)
                    start_ms = int(seg["start"] * 1000)
                    
                    # Overlay audio TTS lên background
                    final_audio = final_audio.overlay(audio_seg, position=start_ms)
                    overlay_count += 1
                    
                    print(f"  [{i+1}/{len(segments)}] ✅ {seg['start']:.1f}s - {seg['end']:.1f}s")
                    
                except Exception as e:
                    print(f"  ⚠️ Lỗi overlay segment {i+1}: {e}")
        
        print(f"\n📈 Đã overlay {overlay_count}/{len(segments)} segments")
        
        # Xuất file
        out_dir = os.path.dirname(out_wav)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        
        print(f"💾 Đang xuất file audio: {out_wav}")
        final_audio.export(out_wav, format="wav", bitrate="192k")
        
        # Kiểm tra file đã tạo
        if os.path.exists(out_wav):
            file_size = os.path.getsize(out_wav) / (1024*1024)
            print(f"✅ Ghép audio hoàn tất: {out_wav}")
            print(f"📁 Kích thước: {file_size:.2f} MB")
            print(f"⏱️  Thời lượng: {len(final_audio)/1000:.2f}s")
        else:
            print(f"❌ File không được tạo: {out_wav}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi ghép audio: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test
    merge_segments_with_background(
        "../subtitles/vi.json", 
        "../audio/original.wav",
        "../audio/vi_full_with_bg.wav",
        background_volume=0.25
    )
