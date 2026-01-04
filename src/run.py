"""
Main entry với lựa chọn TTS method:
- Edge TTS (fast, internet required)
- Voice Cloning (slow, clone voice from input)
"""
import sys
from pathlib import Path

# Import main pipelines
from main import main as main_edge_tts
from main_voice_cloning import main as main_voice_cloning


def show_menu():
    """Hiển thị menu lựa chọn"""
    print("=" * 70)
    print("🎬 TOOL LỒNG TIẾNG TỰ ĐỘNG - VIETNAMESE AUTO DUBBING")
    print("=" * 70)
    print("\nChọn phương pháp TTS:\n")
    print("1️⃣  Edge TTS (Nhanh, cần internet)")
    print("    ✅ Nhanh: ~5-10s/câu")
    print("    ✅ Giọng tự nhiên")
    print("    ✅ Tự động chọn nam/nữ")
    print("    ❌ Không giống giọng gốc\n")
    
    print("2️⃣  Voice Cloning (Chậm, giống giọng gốc 100%)")
    print("    ✅ Clone giọng từ video input")
    print("    ✅ Giữ nguyên tone & emotion")
    print("    ✅ Không cần internet")
    print("    ❌ Chậm: ~30-60s/câu (CPU)")
    print("    ⚠️  Cần cài OpenVoice\n")
    
    print("=" * 70)
    choice = input("Nhập lựa chọn (1 hoặc 2): ").strip()
    return choice


def main():
    """Entry point chính"""
    choice = show_menu()
    
    if choice == "1":
        print("\n✅ Chọn: Edge TTS (Auto Gender + Emotion)")
        print("🚀 Bắt đầu xử lý...\n")
        success = main_edge_tts()
        
    elif choice == "2":
        print("\n✅ Chọn: Voice Cloning (Clone giọng gốc)")
        print("🚀 Bắt đầu xử lý...\n")
        success = main_voice_cloning()
        
    else:
        print("❌ Lựa chọn không hợp lệ!")
        return False
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
