from transformers import pipeline
import json
import os


def translate_segments(in_json, out_json):
    """
    Dịch các segments từ tiếng Anh sang tiếng Việt
    
    Args:
        in_json: Đường dẫn JSON input (tiếng Anh)
        out_json: Đường dẫn JSON output (đã dịch tiếng Việt)
    """
    print("🌏 Đang khởi tạo model dịch Helsinki-NLP/opus-mt-en-vi...")
    
    try:
        # Khởi tạo translator
        translator = pipeline(
            "translation",
            model="Helsinki-NLP/opus-mt-en-vi",
            device=-1  # CPU mode
        )
        
        # Load segments
        with open(in_json, encoding="utf-8") as f:
            segments = json.load(f)
        
        print(f"📝 Đang dịch {len(segments)} câu...")
        
        # Dịch từng segment
        for i, seg in enumerate(segments):
            if seg["text"]:
                try:
                    vi_text = translator(seg["text"], max_length=512)[0]["translation_text"]
                    seg["vi_text"] = vi_text
                    print(f"  [{i+1}/{len(segments)}] EN: {seg['text'][:50]}...")
                    print(f"           VI: {vi_text[:50]}...")
                except Exception as e:
                    print(f"  ⚠️ Lỗi dịch câu {i+1}: {e}")
                    seg["vi_text"] = seg["text"]  # Giữ nguyên nếu lỗi
            else:
                seg["vi_text"] = ""
        
        # Lưu kết quả
        os.makedirs(os.path.dirname(out_json), exist_ok=True)
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Dịch hoàn tất: {out_json}")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi dịch: {e}")
        return False


if __name__ == "__main__":
    # Test
    translate_segments("../subtitles/en.json", "../subtitles/vi.json")
