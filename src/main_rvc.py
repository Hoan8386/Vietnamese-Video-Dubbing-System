"""
Tool Lồng Tiếng với RVC - Voice Cloning (GPU Version)
Tích hợp RVC cho voice cloning chất lượng cao
Tối ưu cho RTX 3050 4GB

Pipeline:
1. Extract audio từ video
2. ASR (Whisper) - transcribe
3. Translate English -> Vietnamese
4. TTS Vietnamese
5. Voice Cloning với RVC (OPTIONAL)
6. Merge audio + background
7. Merge với video

Author: Tool Lồng Tiếng
Date: 2026-01-05
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
from tts_edge import tts_segments
from merge_audio_v3 import merge_segments_with_background
from merge_video import merge_video
from utils import validate_video_file, get_video_duration, format_time
import config_rvc as config

# Import RVC
try:
    from voice_cloning_rvc import RVCVoiceCloner
    RVC_AVAILABLE = True
except ImportError:
    RVC_AVAILABLE = False
    print("⚠️ RVC không khả dụng. Sử dụng TTS cơ bản.")


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='🎬 Tool Lồng Tiếng với RVC Voice Cloning (GPU)'
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        help='Đường dẫn video input (mặc định: input/video.mp4)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Đường dẫn video output (mặc định: output/video_vi_rvc.mp4)'
    )
    
    parser.add_argument(
        '-m', '--model',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        default='small',
        help='Kích thước Whisper model (mặc định: small)'
    )
    
    # RVC options (BẮT BUỘC)
    parser.add_argument(
        '--rvc-model',
        required=True,
        help='Path đến RVC model (.pth) - BẮT BUỘC'
    )
    
    parser.add_argument(
        '--rvc-index',
        help='Path đến RVC index (.index)'
    )
    
    parser.add_argument(
        '--rvc-index-rate',
        type=float,
        default=0.75,
        help='RVC index rate (0.0-1.0, mặc định: 0.75)'
    )
    
    parser.add_argument(
        '--rvc-f0-method',
        choices=['rmvpe', 'harvest', 'crepe', 'pm'],
        default='rmvpe',
        help='Phương pháp extract F0 cho RVC (mặc định: rmvpe)'
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
    """Pipeline với RVC voice cloning"""
    
    # Parse arguments
    args = parse_args()
    
    print("=" * 70)
    print("🎬 TOOL LỒNG TIẾNG VỚI RVC VOICE CLONING")
    print("=" * 70)
    print("⚡ Tối ưu cho RTX 3050 4GB")
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
        output_video = base_dir / config.OUTPUT_DIR / "video_vi_rvc.mp4"
    
    # Validate input
    if not validate_video_file(str(input_video)):
        print(f"❌ Video không hợp lệ: {input_video}")
        return
    
    # Thời lượng video
    duration = get_video_duration(str(input_video))
    print(f"📹 Video: {input_video.name}")
    print(f"⏱️  Thời lượng: {format_time(duration)}")
    
    # Các thư mục làm việc
    audio_dir = base_dir / config.AUDIO_DIR
    subtitles_dir = base_dir / config.SUBTITLES_DIR
    audio_dir.mkdir(exist_ok=True)
    subtitles_dir.mkdir(exist_ok=True)
    
    # Paths
    original_audio = audio_dir / "original.wav"
    tts_audio_dir = audio_dir / "vi_segments"
    rvc_audio_dir = audio_dir / "rvc_segments"
    final_audio = audio_dir / "final_vi_with_bg.wav"
    
    en_subtitle = subtitles_dir / "en.json"
    vi_subtitle = subtitles_dir / "vi.json"
    
    try:
        # Step 1: Extract audio
        print("\n" + "=" * 70)
        print("📤 BƯỚC 1: EXTRACT AUDIO TỪ VIDEO")
        print("=" * 70)
        extract_audio(str(input_video), str(original_audio))
        
        # Step 2: ASR (Whisper)
        print("\n" + "=" * 70)
        print("🎤 BƯỚC 2: TRANSCRIBE AUDIO (WHISPER)")
        print("=" * 70)
        segments = transcribe(
            str(original_audio),
            str(en_subtitle),
            model_size=args.model
        )
        print(f"✅ Transcribed {len(segments)} segments")
        
        # Step 3: Translate
        print("\n" + "=" * 70)
        print("🌏 BƯỚC 3: TRANSLATE ENGLISH -> VIETNAMESE")
        print("=" * 70)
        vi_segments = translate_segments(segments, str(vi_subtitle))
        print(f"✅ Translated {len(vi_segments)} segments")
        
        # Step 4: TTS
        print("\n" + "=" * 70)
        print("🗣️  BƯỚC 4: TEXT-TO-SPEECH (VIETNAMESE)")
        print("=" * 70)
        tts_audio_dir.mkdir(exist_ok=True)
        
        tts_files = tts_segments(
            vi_segments,
            str(tts_audio_dir),
            voice='vi-VN-HoaiMyNeural',  # Female voice
            rate='+0%'
        )
        print(f"✅ Generated {len(tts_files)} TTS audio files")
        
        # Step 5: RVC Voice Cloning (BẮT BUỘC)
        print("\n" + "=" * 70)
        print("🎙️  BƯỚC 5: VOICE CLONING VỚI RVC")
        print("=" * 70)
        
        if not RVC_AVAILABLE:
            print("❌ RVC không khả dụng!")
            print("📖 Xem hướng dẫn cài đặt: INSTALL_RVC.md")
            sys.exit(1)
        
        # Initialize RVC
        rvc_cloner = RVCVoiceCloner(
            model_path=args.rvc_model,
            index_path=args.rvc_index,
            device='auto',
            optimize_vram=True
        )
        
        # Convert segments
        rvc_audio_dir.mkdir(exist_ok=True)
        
        rvc_files = rvc_cloner.convert_segments(
            audio_segments=tts_files,
            output_dir=str(rvc_audio_dir),
            f0_method=args.rvc_f0_method,
            index_rate=args.rvc_index_rate
        )
        
        if not rvc_files:
            print("❌ RVC conversion failed!")
            sys.exit(1)
        
        audio_files_for_merge = rvc_files
        print(f"✅ RVC converted {len(rvc_files)} segments")
        
        # Step 6: Merge audio
        print("\n" + "=" * 70)
        print("🎵 BƯỚC 6: MERGE AUDIO + BACKGROUND")
        print("=" * 70)
        
        # Prepare segments with audio files
        segments_with_audio = []
        for i, segment in enumerate(vi_segments):
            if i < len(audio_files_for_merge):
                segment_copy = segment.copy()
                segment_copy['audio_file'] = audio_files_for_merge[i]
                segments_with_audio.append(segment_copy)
        
        merge_segments_with_background(
            segments_with_audio,
            str(original_audio),
            str(final_audio),
            background_volume=args.background_volume
        )
        print(f"✅ Merged audio saved: {final_audio}")
        
        # Step 7: Merge video
        print("\n" + "=" * 70)
        print("🎬 BƯỚC 7: MERGE AUDIO + VIDEO")
        print("=" * 70)
        merge_video(str(input_video), str(final_audio), str(output_video))
        print(f"✅ Output video: {output_video}")
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ HOÀN THÀNH!")
        print("=" * 70)
        print(f"📹 Input:  {input_video}")
        print(f"📹 Output: {output_video}")
        print(f"🎤 Segments: {len(segments)}")
        print(f"🗣️  TTS files: {len(tts_files)}")
        print(f"🎙️  RVC files: {len(audio_files_for_merge)}")
        print(f"⏱️  Duration: {format_time(duration)}")
        
        # Clean up
        if args.clean:
            print("\n🧹 Cleaning intermediate files...")
            import shutil
            if tts_audio_dir.exists():
                shutil.rmtree(tts_audio_dir)
            if rvc_audio_dir.exists() and rvc_audio_dir != tts_audio_dir:
                shutil.rmtree(rvc_audio_dir)
            if original_audio.exists():
                original_audio.unlink()
            print("✅ Cleaned!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Đã hủy bởi người dùng")
        return
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    main()
