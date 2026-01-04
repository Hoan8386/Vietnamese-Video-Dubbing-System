"""
Version cải tiến của merge_audio.py
Xử lý tốc độ nói và timing tốt hơn
"""

from pydub import AudioSegment
import json
import os
from utils import normalize_audio, speed_change


def merge_segments_v2(segments_json, out_wav, normalize=True):
    """
    Ghép các audio segments thành một file audio hoàn chỉnh
    Tự động điều chỉnh tốc độ nói để khớp với timing gốc
    
    Args:
        segments_json: JSON chứa segments với timing và audio paths
        out_wav: Đường dẫn file audio output
        normalize: Chuẩn hóa âm lượng
    """
    print("🎵 Đang ghép audio segments (v2 - auto speed adjustment)...")
    
    try:
        # Load segments
        with open(segments_json, encoding="utf-8") as f:
            segments = json.load(f)
        
        # Tính tổng thời lượng
        max_end_time = max(seg["end"] for seg in segments)
        total_duration_ms = int(max_end_time * 1000)
        
        # Tạo audio trống
        final_audio = AudioSegment.silent(duration=total_duration_ms)
        
        print(f"📊 Tổng thời lượng: {max_end_time:.2f}s")
        print(f"📊 Số segments: {len(segments)}")
        
        # Ghép từng segment với speed adjustment
        for i, seg in enumerate(segments):
            if seg.get("vi_audio_path") and os.path.exists(seg["vi_audio_path"]):
                try:
                    # Load audio segment
                    audio_seg = AudioSegment.from_wav(seg["vi_audio_path"])
                    
                    # Normalize volume nếu cần
                    if normalize:
                        audio_seg = normalize_audio(audio_seg)
                    
                    # Tính timing
                    start_ms = int(seg["start"] * 1000)
                    end_ms = int(seg["end"] * 1000)
                    target_duration_ms = end_ms - start_ms
                    actual_duration_ms = len(audio_seg)
                    
                    # Điều chỉnh tốc độ nếu chênh lệch > 10%
                    duration_ratio = actual_duration_ms / target_duration_ms
                    
                    if duration_ratio > 1.1 or duration_ratio < 0.9:
                        # Cần điều chỉnh tốc độ
                        speed_factor = duration_ratio
                        audio_seg = speed_change(audio_seg, speed=speed_factor)
                        
                        print(f"  [{i+1}/{len(segments)}] ⚡ Speed: {speed_factor:.2f}x | {seg['start']:.1f}s-{seg['end']:.1f}s")
                    else:
                        print(f"  [{i+1}/{len(segments)}] ✅ {seg['start']:.1f}s-{seg['end']:.1f}s")
                    
                    # Overlay audio vào đúng vị trí
                    final_audio = final_audio.overlay(audio_seg, position=start_ms)
                    
                except Exception as e:
                    print(f"  ⚠️ Lỗi ghép segment {i+1}: {e}")
        
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
    merge_segments_v2("../subtitles/vi.json", "../audio/vi_full.wav")
