"""
Advanced TTS with Audio Mixing
Mix original audio with Vietnamese TTS to preserve emotion
"""
import os
import json
from pydub import AudioSegment
from pydub.effects import normalize
import edge_tts
import asyncio
from text_cleaner import clean_text_for_tts, validate_text


# Danh sách giọng tiếng Việt
VIETNAMESE_VOICES = {
    "female": "vi-VN-HoaiMyNeural",
    "male": "vi-VN-NamMinhNeural"
}


async def _tts_with_ssml(text, output_path, voice="female", rate="+0%", pitch="+0Hz", volume="+0%"):
    """
    TTS đơn giản với parameters trực tiếp (không dùng SSML)
    """
    voice_name = VIETNAMESE_VOICES.get(voice, VIETNAMESE_VOICES["female"])
    
    # Dùng plain text với parameters - Edge TTS sẽ tự xử lý
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice_name,
        rate=rate,
        pitch=pitch,
        volume=volume
    )
    await communicate.save(output_path)


def extract_segment_audio(original_audio_path, start_time, end_time, output_path):
    """
    Trích xuất một segment audio từ audio gốc
    
    Args:
        original_audio_path: Audio gốc
        start_time: Thời gian bắt đầu (seconds)
        end_time: Thời gian kết thúc (seconds)
        output_path: Đường dẫn output
    """
    try:
        audio = AudioSegment.from_file(original_audio_path)
        
        # Extract segment
        start_ms = int(start_time * 1000)
        end_ms = int(end_time * 1000)
        segment = audio[start_ms:end_ms]
        
        # Export
        segment.export(output_path, format="wav")
        return True
    except Exception as e:
        print(f"  ⚠️ Lỗi extract segment: {e}")
        return False


def mix_audio_segments(original_segment, tts_segment, output_path, tts_volume=1.0, original_volume=0.2):
    """
    Mix audio gốc (giảm volume) với TTS để giữ background emotion
    
    Args:
        original_segment: Audio gốc của segment
        tts_segment: Audio TTS tiếng Việt
        output_path: Output path
        tts_volume: Volume của TTS (0.0-1.0)
        original_volume: Volume của audio gốc (0.0-0.5) - nhỏ để làm background
    """
    try:
        # Load both audio
        original = AudioSegment.from_file(original_segment)
        tts = AudioSegment.from_file(tts_segment)
        
        # Điều chỉnh volume
        original_bg = original - (60 - int(original_volume * 60))  # Giảm volume original
        tts_main = tts - (60 - int(tts_volume * 60))
        
        # Normalize
        original_bg = normalize(original_bg)
        tts_main = normalize(tts_main)
        
        # Match duration
        if len(tts_main) > len(original_bg):
            # TTS dài hơn → pad original
            silence = AudioSegment.silent(duration=len(tts_main) - len(original_bg))
            original_bg = original_bg + silence
        else:
            # Original dài hơn → truncate
            original_bg = original_bg[:len(tts_main)]
        
        # Mix (overlay)
        mixed = original_bg.overlay(tts_main)
        
        # Export
        mixed.export(output_path, format="mp3")
        return True
        
    except Exception as e:
        print(f"  ⚠️ Lỗi mix audio: {e}")
        return False


def tts_segments_advanced(segments_json, original_audio, out_dir, auto_voice=True, enable_mixing=False):
    """
    TTS nâng cao với:
    - Auto gender selection
    - Prosody control dựa trên emotion
    - Optional: Mix với audio gốc để giữ emotion
    
    Args:
        segments_json: JSON chứa segments
        original_audio: Audio gốc (để extract background)
        out_dir: Output directory
        auto_voice: Tự động chọn giọng nam/nữ
        enable_mixing: Mix audio gốc với TTS (experimental)
    """
    print("🗣️ Đang khởi tạo Advanced TTS...")
    print(f"   📊 Auto voice: {auto_voice}")
    print(f"   🎵 Audio mixing: {'Enabled' if enable_mixing else 'Disabled'}")
    
    try:
        # Load segments
        with open(segments_json, encoding="utf-8") as f:
            segments = json.load(f)
        
        # Tạo thư mục
        os.makedirs(out_dir, exist_ok=True)
        temp_dir = os.path.join(out_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        print(f"🎙️ Đang tổng hợp giọng nói cho {len(segments)} câu...")
        
        for i, seg in enumerate(segments):
            if not seg.get("vi_text", "").strip():
                seg["vi_audio_path"] = None
                continue
            
            # Clean và validate text trước khi TTS
            is_valid, cleaned_text, warning = validate_text(seg["vi_text"])
            
            if not is_valid:
                print(f"  [{i+1}/{len(segments)}] ⚠️ Skip: {warning}")
                seg["vi_audio_path"] = None
                continue
            
            if warning:
                print(f"  [{i+1}/{len(segments)}] ⚠️ {warning}")
            
            # Cập nhật text đã clean
            seg["vi_text_cleaned"] = cleaned_text
            
            final_path = os.path.join(out_dir, f"{i:04d}.mp3")
            
            try:
                # 1. Lấy voice info
                if auto_voice and "voice_gender" in seg:
                    voice = seg["voice_gender"]
                    rate = seg.get("tts_rate_adjust", "+0%")
                    emotion = seg.get("voice_emotion", "neutral")
                    
                    # Điều chỉnh pitch theo emotion
                    if emotion == "excited":
                        pitch = "+8Hz"
                        volume = "+5%"
                    elif emotion == "calm":
                        pitch = "-5Hz"
                        volume = "-5%"
                    elif emotion == "urgent":
                        pitch = "+3Hz"
                        volume = "+10%"
                    else:
                        pitch = "+0Hz"
                        volume = "+0%"
                else:
                    voice = "female"
                    rate = "+0%"
                    pitch = "+0Hz"
                    volume = "+0%"
                    emotion = "neutral"
                
                # 2. Generate TTS với cleaned text
                tts_temp = os.path.join(temp_dir, f"{i:04d}_tts.mp3")
                asyncio.run(_tts_with_ssml(
                    cleaned_text,  # Dùng cleaned text
                    tts_temp,
                    voice,
                    rate,
                    pitch,
                    volume
                ))
                
                # 3. Mix với audio gốc nếu enabled
                if enable_mixing:
                    # Extract original segment
                    orig_segment = os.path.join(temp_dir, f"{i:04d}_orig.wav")
                    if extract_segment_audio(original_audio, seg["start"], seg["end"], orig_segment):
                        # Mix
                        if mix_audio_segments(orig_segment, tts_temp, final_path):
                            print(f"  [{i+1}/{len(segments)}] 🎵 {voice.upper()} | "
                                  f"{emotion} | MIXED")
                        else:
                            # Fallback: dùng TTS only
                            os.rename(tts_temp, final_path)
                            print(f"  [{i+1}/{len(segments)}] 🎤 {voice.upper()} | "
                                  f"{emotion} | TTS only")
                    else:
                        os.rename(tts_temp, final_path)
                        print(f"  [{i+1}/{len(segments)}] 🎤 {voice.upper()} | "
                              f"{emotion} | TTS only")
                else:
                    # Chỉ dùng TTS
                    os.rename(tts_temp, final_path)
                    if auto_voice and "voice_gender" in seg:
                        print(f"  [{i+1}/{len(segments)}] 🎤 {voice.upper()} | "
                              f"{emotion} | Rate: {rate}")
                    else:
                        print(f"  [{i+1}/{len(segments)}] ✅ {seg['vi_text'][:40]}...")
                
                seg["vi_audio_path"] = final_path
                
            except Exception as e:
                print(f"  ⚠️ Lỗi TTS câu {i+1}: {e}")
                seg["vi_audio_path"] = None
        
        # Lưu lại
        with open(segments_json, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)
        
        # Cleanup temp
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except:
            pass
        
        print(f"✅ TTS hoàn tất. Audio lưu tại: {out_dir}")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi TTS: {e}")
        return False


if __name__ == "__main__":
    # Test
    tts_segments_advanced(
        "../subtitles/vi.json",
        "../audio/original.wav",
        "../audio/vi_segments",
        auto_voice=True,
        enable_mixing=True
    )
