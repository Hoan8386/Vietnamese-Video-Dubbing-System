"""
Tool Lồng Tiếng Tự Động - Version 2
Cải thiện: CLI args, progress tracking, checkpoint, validation

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
from tts_vi import tts_segments
from merge_audio_v2 import merge_segments_v2
from merge_video import merge_video
from utils import validate_video_file, get_video_duration, format_time, save_checkpoint, load_checkpoint
import config


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='🎬 Tool Lồng Tiếng Tự Động - Vietnamese Auto Dubbing'
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        help='Đường dẫn video input (mặc định: input/video.mp4)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Đường dẫn video output (mặc định: output/video_vi.mp4)'
    )
    
    parser.add_argument(
        '-m', '--model',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        default=config.WHISPER_MODEL_SIZE,
        help=f'Kích thước Whisper model (mặc định: {config.WHISPER_MODEL_SIZE})'
    )
    
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Tiếp tục từ checkpoint (nếu có)'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Xóa các file trung gian sau khi hoàn thành'
    )
    
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Tắt thanh tiến trình'
    )
    
    return parser.parse_args()


def main():
    """Pipeline chính với CLI và checkpoint support"""
    
    # Parse arguments
    args = parse_args()
    
    print("=" * 60)
    print("🎬 TOOL LỒNG TIẾNG TỰ ĐỘNG - VIETNAMESE DUBBING V2")
    print("=" * 60)
    
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
        output_video = base_dir / config.OUTPUT_DIR / "video_vi.mp4"
    
    # Các đường dẫn khác
    audio_dir = base_dir / config.AUDIO_DIR
    original_audio = audio_dir / "original.wav"
    vi_full_audio = audio_dir / "vi_full.wav"
    vi_segments_dir = audio_dir / "vi_segments"
    
    subtitles_dir = base_dir / config.SUBTITLES_DIR
    en_json = subtitles_dir / "en.json"
    vi_json = subtitles_dir / "vi.json"
    
    checkpoint_file = base_dir / ".checkpoint.json"
    
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
    
    # Kiểm tra checkpoint
    start_step = 1
    if args.resume:
        checkpoint = load_checkpoint(str(checkpoint_file))
        if checkpoint:
            print(f"\n♻️ Tìm thấy checkpoint tại bước: {checkpoint['step']}")
            response = input("Tiếp tục từ checkpoint? (y/n): ")
            if response.lower() == 'y':
                start_step = checkpoint.get('data', {}).get('step_number', 1) + 1
                print(f"▶️ Tiếp tục từ bước {start_step}")
    
    try:
        # Các bước xử lý
        steps = [
            ("Tách audio", lambda: extract_audio(str(input_video), str(original_audio))),
            ("Nhận dạng giọng nói", lambda: transcribe(str(original_audio), str(en_json), model_size=args.model)),
            ("Dịch sang tiếng Việt", lambda: translate_segments(str(en_json), str(vi_json))),
            ("Tổng hợp giọng nói", lambda: tts_segments(str(vi_json), str(vi_segments_dir))),
            ("Ghép audio segments", lambda: merge_segments_v2(str(vi_json), str(vi_full_audio), normalize=config.AUDIO_NORMALIZE)),
            ("Ghép audio vào video", lambda: merge_video(str(input_video), str(vi_full_audio), str(output_video)))
        ]
        
        # Progress bar cho các bước
        progress_bar = tqdm(
            enumerate(steps[start_step-1:], start=start_step),
            total=len(steps),
            initial=start_step-1,
            desc="Overall Progress",
            disable=args.no_progress,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
        )
        
        for step_num, (step_name, step_func) in progress_bar:
            print("\n" + "="*60)
            print(f"BƯỚC {step_num}/{len(steps)}: {step_name.upper()}")
            print("="*60)
            
            # Thực thi bước
            if not step_func():
                raise Exception(f"Lỗi tại bước: {step_name}")
            
            # Lưu checkpoint
            save_checkpoint(
                str(checkpoint_file),
                step=step_name,
                data={"step_number": step_num}
            )
            
            progress_bar.set_description(f"Completed: {step_name}")
        
        # Hoàn thành
        print("\n" + "="*60)
        print("🎉 HOÀN THÀNH!")
        print("="*60)
        print(f"✅ Video đã lồng tiếng: {output_video}")
        print(f"📁 Kích thước: {output_video.stat().st_size / (1024*1024):.2f} MB")
        
        if duration:
            output_duration = get_video_duration(str(output_video))
            if output_duration:
                print(f"📊 Thời lượng: {format_time(output_duration)}")
        
        print(f"\n📊 Các file trung gian:")
        print(f"   - Transcript EN: {en_json}")
        print(f"   - Transcript VI: {vi_json}")
        print(f"   - Audio VI: {vi_full_audio}")
        
        # Clean up nếu cần
        if args.clean:
            print("\n🧹 Dọn dẹp file trung gian...")
            try:
                os.remove(str(original_audio))
                os.remove(str(vi_full_audio))
                # Xóa vi_segments
                for f in vi_segments_dir.glob("*.wav"):
                    f.unlink()
                print("✅ Đã xóa file trung gian")
            except Exception as e:
                print(f"⚠️ Lỗi khi xóa: {e}")
        
        # Xóa checkpoint
        if checkpoint_file.exists():
            checkpoint_file.unlink()
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Đã hủy bởi người dùng")
        print(f"💾 Checkpoint đã lưu. Chạy lại với --resume để tiếp tục")
        return False
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        print(f"💾 Checkpoint đã lưu. Chạy lại với --resume để tiếp tục")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
