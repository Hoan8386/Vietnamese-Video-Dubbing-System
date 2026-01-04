from pydub import AudioSegment
import json
import os


def merge_segments(segments_json, out_wav):
    """
    Ghép các audio segments thành một file audio hoàn chỉnh
    Giữ nguyên timing theo timestamp gốc
    
    Args:
        segments_json: JSON chứa segments với timing và audio paths
        out_wav: Đường dẫn file audio output
    """
    print("🎵 Đang ghép audio segments...")
    
    try:
        # Load segments
        with open(segments_json, encoding="utf-8") as f:
            segments = json.load(f)
        
        # Tính tổng thời lượng
        max_end_time = max(seg["end"] for seg in segments)
        total_duration_ms = int(max_end_time * 1000)
        
        # Tạo audio trống với độ dài tổng
        final_audio = AudioSegment.silent(duration=total_duration_ms)
        
        print(f"📊 Tổng thời lượng: {max_end_time:.2f}s")
        
        # Ghép từng segment vào đúng vị trí
        for i, seg in enumerate(segments):
            if seg.get("vi_audio_path") and os.path.exists(seg["vi_audio_path"]):
                try:
                    # Load audio segment (hỗ trợ cả MP3 và WAV)
                    audio_path = seg["vi_audio_path"]
                    
                    # Tự động detect format từ extension
                    if audio_path.lower().endswith('.mp3'):
                        audio_seg = AudioSegment.from_mp3(audio_path)
                    elif audio_path.lower().endswith('.wav'):
                        audio_seg = AudioSegment.from_wav(audio_path)
                    else:
                        # Fallback: để pydub tự detect
                        audio_seg = AudioSegment.from_file(audio_path)
                    
                    # Vị trí bắt đầu (ms)
                    start_ms = int(seg["start"] * 1000)
                    
                    # Overlay audio vào đúng vị trí
                    final_audio = final_audio.overlay(audio_seg, position=start_ms)
                    
                    print(f"  [{i+1}/{len(segments)}] ✅ {seg['start']:.1f}s - {seg['end']:.1f}s")
                    
                except Exception as e:
                    print(f"  ⚠️ Lỗi ghép segment {i+1}: {e}")
                    # Bỏ qua segment lỗi, tiếp tục các segment khác
        
        # Xuất file
        os.makedirs(os.path.dirname(out_wav), exist_ok=True)
        final_audio.export(out_wav, format="wav")
        
        print(f"✅ Ghép audio hoàn tất: {out_wav}")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi ghép audio: {e}")
        return False


if __name__ == "__main__":
    # Test
    merge_segments("../subtitles/vi.json", "../audio/vi_full.wav")
