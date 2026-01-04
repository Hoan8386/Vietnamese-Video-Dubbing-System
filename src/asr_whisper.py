import whisper
import json
import os


def transcribe(audio_path, out_json, model_size="small"):
    """
    Nhận dạng giọng nói bằng Whisper
    
    Args:
        audio_path: Đường dẫn audio input
        out_json: Đường dẫn JSON output chứa segments
        model_size: Kích thước model (tiny, base, small, medium, large)
    """
    print(f"🎤 Đang nhận dạng giọng nói với Whisper model '{model_size}'...")
    
    # Tạo thư mục nếu chưa tồn tại
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    
    try:
        # Load model (fp16=False để chạy trên CPU)
        model = whisper.load_model(model_size)
        
        # Transcribe với timestamp chi tiết
        result = model.transcribe(
            audio_path,
            fp16=False,  # CPU mode
            language="en",  # Có thể để None để auto-detect
            verbose=True
        )
        
        # Lưu segments với timestamp
        segments_data = []
        for seg in result["segments"]:
            segments_data.append({
                "id": seg["id"],
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip(),
                "vi_text": ""  # Sẽ được điền ở bước translate
            })
        
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(segments_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Nhận dạng hoàn tất: {len(segments_data)} câu")
        print(f"📄 Kết quả lưu tại: {out_json}")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi nhận dạng: {e}")
        return False


if __name__ == "__main__":
    # Test
    transcribe("../audio/original.wav", "../subtitles/en.json")
