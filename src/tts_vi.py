import edge_tts
import asyncio
import os
import json


# Danh sách giọng tiếng Việt của Edge TTS
VIETNAMESE_VOICES = {
    "female": "vi-VN-HoaiMyNeural",  # Giọng nữ (mặc định)
    "male": "vi-VN-NamMinhNeural"    # Giọng nam
}


async def _tts_single_with_prosody(text, output_path, voice="female", rate="+0%", pitch="+0Hz"):
    """
    Helper async function để TTS một câu với prosody control
    
    Args:
        text: Text cần TTS
        output_path: Đường dẫn output
        voice: "female" hoặc "male"
        rate: Speech rate adjustment (e.g., "+10%", "-5%")
        pitch: Pitch adjustment (e.g., "+5Hz", "-10Hz")
    """
    voice_name = VIETNAMESE_VOICES.get(voice, VIETNAMESE_VOICES["female"])
    
    # Tạo SSML với prosody tags để điều chỉnh rate và pitch
    if rate != "+0%" or pitch != "+0Hz":
        ssml_text = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="vi-VN">
            <voice name="{voice_name}">
                <prosody rate="{rate}" pitch="{pitch}">
                    {text}
                </prosody>
            </voice>
        </speak>
        """
        communicate = edge_tts.Communicate(ssml_text, voice_name)
    else:
        communicate = edge_tts.Communicate(text, voice_name)
    
    await communicate.save(output_path)


async def _tts_single(text, output_path, voice="female"):
    """Helper async function để TTS một câu (backward compatibility)"""
    await _tts_single_with_prosody(text, output_path, voice, "+0%", "+0Hz")


def tts_segments(segments_json, out_dir, voice="female", auto_voice=True):
    """
    Chuyển đổi text tiếng Việt thành giọng nói bằng Edge TTS
    Hỗ trợ tự động chọn giọng nam/nữ và điều chỉnh prosody
    
    Args:
        segments_json: Đường dẫn JSON chứa segments đã dịch
        out_dir: Thư mục output chứa các file audio
        voice: "female" hoặc "male" (mặc định khi auto_voice=False)
        auto_voice: Tự động chọn giọng nam/nữ từ voice_gender (default: True)
    """
    print(f"🗣️ Đang khởi tạo Edge TTS tiếng Việt...")
    if auto_voice:
        print(f"   📊 Chế độ: Tự động chọn giọng nam/nữ + điều chỉnh emotion")
    else:
        print(f"   📊 Chế độ: Giọng cố định ({voice})")
    
    try:
        # Load segments
        with open(segments_json, encoding="utf-8") as f:
            segments = json.load(f)
        
        # Tạo thư mục output
        os.makedirs(out_dir, exist_ok=True)
        
        print(f"🎙️ Đang tổng hợp giọng nói cho {len(segments)} câu...")
        
        # TTS cho từng segment
        for i, seg in enumerate(segments):
            if seg.get("vi_text", "").strip():
                wav_path = os.path.join(out_dir, f"{i:04d}.mp3")
                
                try:
                    # Lấy voice info từ phân tích (nếu có)
                    if auto_voice and "voice_gender" in seg:
                        selected_voice = seg["voice_gender"]
                        rate_adjust = seg.get("tts_rate_adjust", "+0%")
                        emotion = seg.get("voice_emotion", "neutral")
                        
                        # Điều chỉnh pitch theo emotion
                        if emotion == "excited":
                            pitch_adjust = "+5Hz"
                        elif emotion == "calm":
                            pitch_adjust = "-5Hz"
                        else:
                            pitch_adjust = "+0Hz"
                        
                        print(f"  [{i+1}/{len(segments)}] 🎤 {selected_voice.upper()} | "
                              f"{emotion} | Rate: {rate_adjust}")
                    else:
                        selected_voice = voice
                        rate_adjust = "+0%"
                        pitch_adjust = "+0Hz"
                    
                    # Chạy async TTS với prosody
                    asyncio.run(_tts_single_with_prosody(
                        seg["vi_text"], 
                        wav_path, 
                        selected_voice,
                        rate_adjust,
                        pitch_adjust
                    ))
                    
                    # Lưu đường dẫn vào segment
                    seg["vi_audio_path"] = wav_path
                    
                    if not auto_voice or "voice_gender" not in seg:
                        print(f"  [{i+1}/{len(segments)}] ✅ {seg['vi_text'][:40]}...")
                    
                except Exception as e:
                    print(f"  ⚠️ Lỗi TTS câu {i+1}: {e}")
                    seg["vi_audio_path"] = None
            else:
                seg["vi_audio_path"] = None
        
        # Lưu lại segments với đường dẫn audio
        with open(segments_json, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)
        
        print(f"✅ TTS hoàn tất. Audio lưu tại: {out_dir}")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi TTS: {e}")
        return False


if __name__ == "__main__":
    # Test
    tts_segments("../subtitles/vi.json", "../audio/vi_segments")
