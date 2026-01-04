"""
Tool Lồng Tiếng với OpenVoice - Voice Cloning (GPU Version)
Giữ nguyên giọng, cảm xúc và nhịp điệu từ video gốc

Tối ưu cho GPU NVIDIA
- Voice cloning từ audio gốc
- Giữ emotion, rhythm, intonation
- GPU accelerated

Author: Auto Dubbing Tool
Date: 2026-01-04
"""

import os
import sys
import json
import argparse
from pathlib import Path
from tqdm import tqdm

# Import các module
from extract_audio import extract_audio
from asr_whisper import transcribe
from translate import translate_segments
from tts_openvoice import tts_openvoice_segments
from merge_audio_v3 import merge_segments_with_background
from merge_video import merge_video
from utils import validate_video_file, get_video_duration, format_time
import config


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='🎬 Tool Lồng Tiếng với OpenVoice - Voice Cloning (GPU)'
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        help='Đường dẫn video input (mặc định: input/video.mp4)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Đường dẫn video output (mặc định: output/video_vi_cloned.mp4)'
    )
    
    parser.add_argument(
        '-m', '--model',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        default='small',
        help='Kích thước Whisper model (mặc định: small - tối ưu GPU)'
    )
    
    parser.add_argument(
        '--segment-reference',
        action='store_true',
        help='Clone giọng từng segment riêng (chính xác hơn nhưng chậm hơn)'
    )
    
    parser.add_argument(
        '--background-volume',
        type=float,
        default=0.20,
        help='Volume audio gốc làm background (0.0-1.0, mặc định: 0.20)'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Xóa các file trung gian sau khi hoàn thành'
    )
    
    return parser.parse_args()


def main():
    """Pipeline với OpenVoice voice cloning on GPU"""
    
    # Parse arguments
    args = parse_args()
    
    print("=" * 70)
    print("🎬 TOOL LỒNG TIẾNG VỚI OPENVOICE - VOICE CLONING (GPU)")
    print("=" * 70)
    print("🎯 Clone giọng nói từ video gốc với GPU acceleration")
    print("=" * 70)
    
    # Đường dẫn
    base_dir = Path(__file__).parent.parent
    
    # Input video
    if args.input:
        input_video = Path(args.input)
    else:
        input_video = base_dir / config.INPUT_DIR / "video.mp4"
    
    # Output video
    if args.output:
        output_video = Path(args.output)
    else:
        output_video = base_dir / config.OUTPUT_DIR / "video_vi_cloned.mp4"
    
    # Các đường dẫn khác
    audio_dir = base_dir / config.AUDIO_DIR
    original_audio = audio_dir / "original.wav"
    vi_full_audio = audio_dir / "vi_full_cloned.wav"
    vi_segments_dir = audio_dir / "vi_segments_cloned"
    
    subtitles_dir = base_dir / config.SUBTITLES_DIR
    en_json = subtitles_dir / "en.json"
    vi_json = subtitles_dir / "vi.json"
    
    # Validate input
    print("\n🔍 Kiểm tra file input...")
    if not validate_video_file(str(input_video)):
        return False
    
    # Thông tin video
    duration = get_video_duration(str(input_video))
    if duration:
        print(f"✅ Video hợp lệ: {input_video.name}")
        print(f"📊 Thời lượng: {format_time(duration)}")
        print(f"📁 Kích thước: {input_video.stat().st_size / (1024*1024):.2f} MB")
    
    # GPU info
    import torch
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"\n🎮 GPU: {gpu_name}")
        print(f"💾 VRAM: {gpu_memory:.1f} GB")
    else:
        print("\n⚠️  Không tìm thấy GPU, sẽ chạy trên CPU (rất chậm!)")
        response = input("Tiếp tục? (y/n): ")
        if response.lower() != 'y':
            return False
    
    try:
        # Bước 1: Tách audio
        print("\n" + "="*70)
        print("BƯỚC 1/6: TÁCH AUDIO TỪ VIDEO")
        print("="*70)
        if not extract_audio(str(input_video), str(original_audio)):
            raise Exception("Lỗi tách audio")
        
        # Bước 2: Nhận dạng giọng nói (ASR) - GPU accelerated
        print("\n" + "="*70)
        print("BƯỚC 2/6: NHẬN DẠNG GIỌNG NÓI (WHISPER GPU)")
        print("="*70)
        print(f"📌 Model: {args.model} | Device: {'GPU' if torch.cuda.is_available() else 'CPU'}")
        if not transcribe(str(original_audio), str(en_json), model_size=args.model):
            raise Exception("Lỗi nhận dạng giọng nói")
        
        # Bước 3: Dịch sang tiếng Việt - GPU accelerated
        print("\n" + "="*70)
        print("BƯỚC 3/6: DỊCH SANG TIẾNG VIỆT (GPU)")
        print("="*70)
        if not translate_segments(str(en_json), str(vi_json)):
            raise Exception("Lỗi dịch")
        
        # Bước 4: TTS với OpenVoice (Voice Cloning on GPU)
        print("\n" + "="*70)
        print("BƯỚC 4/6: VOICE CLONING VỚI OPENVOICE (GPU)")
        print("="*70)
        print("🎯 Clone giọng nói từ audio gốc...")
        if args.segment_reference:
            print("📌 Mode: Clone từng segment riêng (chính xác hơn)")
        else:
            print("📌 Mode: Clone từ toàn bộ video (nhanh hơn)")
        
        if not tts_openvoice_segments(
            str(vi_json),
            str(original_audio),
            str(vi_segments_dir),
            use_segment_reference=args.segment_reference
        ):
            raise Exception("Lỗi TTS")
        
        # Bước 5: Ghép audio segments với background
        print("\n" + "="*70)
        print("BƯỚC 5/6: GHÉP AUDIO SEGMENTS")
        print("="*70)
        print(f"📌 Background volume: {args.background_volume*100:.0f}%")
        
        if not merge_segments_with_background(
            str(vi_json),
            str(original_audio),
            str(vi_full_audio),
            background_volume=args.background_volume,
            normalize=True
        ):
            raise Exception("Lỗi ghép audio")
        
        # Bước 6: Ghép audio vào video
        print("\n" + "="*70)
        print("BƯỚC 6/6: GHÉP AUDIO VÀO VIDEO")
        print("="*70)
        if not merge_video(str(input_video), str(vi_full_audio), str(output_video)):
            raise Exception("Lỗi ghép video")
        
        # Hoàn thành
        print("\n" + "="*70)
        print("🎉 HOÀN THÀNH!")
        print("="*70)
        print(f"✅ Video đã lồng tiếng với voice cloning: {output_video}")
        print(f"📁 Kích thước: {output_video.stat().st_size / (1024*1024):.2f} MB")
        
        if duration:
            output_duration = get_video_duration(str(output_video))
            if output_duration:
                print(f"📊 Thời lượng: {format_time(output_duration)}")
        
        print(f"\n📊 Các file trung gian:")
        print(f"   - Transcript EN: {en_json}")
        print(f"   - Transcript VI: {vi_json}")
        print(f"   - Audio VI: {vi_full_audio}")
        print(f"   - Segments: {vi_segments_dir}")
        
        # Clean up nếu cần
        if args.clean:
            print("\n🧹 Dọn dẹp file trung gian...")
            try:
                os.remove(str(original_audio))
                os.remove(str(vi_full_audio))
                # Xóa temp files
                temp_dir = vi_segments_dir / "temp"
                if temp_dir.exists():
                    for f in temp_dir.glob("*"):
                        f.unlink()
                    temp_dir.rmdir()
                print("✅ Đã xóa file trung gian")
            except Exception as e:
                print(f"⚠️ Lỗi khi xóa: {e}")
        
        print("\n" + "="*70)
        print("💡 Tips:")
        print("   - Dùng --segment-reference để clone chính xác hơn (chậm hơn 3-4x)")
        print("   - Điều chỉnh --background-volume (0.15-0.30) tùy video")
        print("   - Whisper model 'small' cân bằng giữa tốc độ và độ chính xác")
        print("="*70)
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Đã hủy bởi người dùng")
        return False
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
