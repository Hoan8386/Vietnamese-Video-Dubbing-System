"""
Text-to-Speech với OpenVoice - Voice Cloning
Giữ nguyên cảm xúc và nhịp điệu từ video gốc

OpenVoice: Instant voice cloning với control tốt
- GPU: GTX 1050+ (4GB+ VRAM)
- Clones voice từ reference audio 
- Giữ emotion, rhythm, intonation
"""

import os
import json
import torch
import numpy as np
from pathlib import Path
from pydub import AudioSegment
import warnings
warnings.filterwarnings('ignore')


class OpenVoiceTTS:
    """OpenVoice TTS wrapper cho voice cloning"""
    
    def __init__(self, device='auto'):
        """
        Khởi tạo OpenVoice model
        
        Args:
            device: 'cuda', 'cpu', hoặc 'auto'
        """
        # Detect device
        if device == 'auto':
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        
        print(f"🎙️ Khởi tạo OpenVoice TTS trên {self.device.upper()}...")
        
        # Check CUDA memory nếu có GPU
        if self.device == 'cuda':
            gpu_mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print(f"   VRAM: {gpu_mem:.1f} GB")
            
            # Tối ưu cho GPU
            torch.backends.cudnn.benchmark = True
            torch.backends.cuda.matmul.allow_tf32 = True
        
        self.model = None
        self.tone_converter = None
        self._load_models()
    
    def _load_models(self):
        """Load OpenVoice models (base + tone converter)"""
        try:
            from openvoice import se_extractor
            from openvoice.api import ToneColorConverter, BaseSpeakerTTS
            
            # Model paths
            base_dir = Path(__file__).parent.parent
            ckpt_base = base_dir / 'OpenVoice' / 'checkpoints' / 'base_speakers' / 'EN'
            ckpt_converter = base_dir / 'OpenVoice' / 'checkpoints' / 'converter'
            
            # Load base TTS
            print("   📥 Loading Base TTS model...")
            self.model = BaseSpeakerTTS(
                str(ckpt_base / 'config.json'),
                device=self.device
            )
            self.model.load_ckpt(str(ckpt_base / 'checkpoint.pth'))
            
            # Load Tone Converter (để clone voice)
            print("   📥 Loading Tone Color Converter...")
            self.tone_converter = ToneColorConverter(
                str(ckpt_converter / 'config.json'),
                device=self.device
            )
            self.tone_converter.load_ckpt(str(ckpt_converter / 'checkpoint.pth'))
            
            # SE extractor (để extract voice characteristics)
            self.se_extractor = se_extractor
            
            print("   ✅ Models loaded successfully")
            
        except ImportError:
            print("   ⚠️ OpenVoice chưa cài đặt!")
            print("   📦 Cài đặt: pip install git+https://github.com/myshell-ai/OpenVoice.git")
            raise
        except Exception as e:
            print(f"   ❌ Lỗi load model: {e}")
            raise
    
    def extract_voice_embedding(self, audio_path, output_path='reference_se.pth'):
        """
        Extract voice embedding từ audio reference
        
        Args:
            audio_path: Đường dẫn audio gốc (giọng cần clone)
            output_path: Đường dẫn lưu embedding
        
        Returns:
            Đường dẫn file embedding
        """
        print(f"   🎯 Extracting voice characteristics từ: {Path(audio_path).name}")
        
        try:
            # Extract speaker embedding
            target_se, audio_name = self.se_extractor.get_se(
                audio_path,
                self.tone_converter,
                target_dir='processed',
                vad=True  # Voice Activity Detection
            )
            
            # Save embedding
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            torch.save(target_se, output_path)
            
            print(f"   ✅ Voice embedding saved: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"   ❌ Lỗi extract embedding: {e}")
            return None
    
    def synthesize_with_cloning(self, text, reference_se, output_path, 
                                speed=1.0, language='Vietnamese'):
        """
        Tổng hợp giọng nói với voice cloning
        
        Args:
            text: Text tiếng Việt cần tổng hợp
            reference_se: Đường dẫn hoặc tensor của reference embedding
            output_path: Đường dẫn lưu audio
            speed: Tốc độ nói (0.5-2.0)
            language: Ngôn ngữ ('English', 'Vietnamese', 'Chinese')
        """
        try:
            # Load reference embedding nếu là path
            if isinstance(reference_se, str):
                reference_se = torch.load(reference_se, map_location=self.device)
            
            # Temporary output (trước khi clone voice)
            temp_output = output_path.replace('.wav', '_temp.wav')
            
            # Step 1: Base TTS synthesis
            # Sử dụng base speaker để tạo audio tạm
            base_dir = Path(__file__).parent.parent
            src_path = base_dir / 'OpenVoice' / 'checkpoints' / 'base_speakers' / 'EN' / 'en_default_se.pth'
            
            self.model.tts(
                text,
                temp_output,
                speaker=str(src_path),
                language=language,
                speed=speed
            )
            
            # Step 2: Tone Color Conversion (clone voice)
            # Convert sang giọng của reference
            source_se = torch.load(str(src_path), map_location=self.device)
            
            self.tone_converter.convert(
                audio_src_path=temp_output,
                src_se=source_se,
                tgt_se=reference_se,
                output_path=output_path,
                message="@MyShell"
            )
            
            # Cleanup temp file
            if os.path.exists(temp_output):
                os.remove(temp_output)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Lỗi synthesize: {e}")
            return False
    
    def clear_cache(self):
        """Xóa GPU cache"""
        if self.device == 'cuda':
            torch.cuda.empty_cache()


def extract_segment_audio(original_audio, start_time, end_time, output_path):
    """
    Cắt một đoạn audio từ audio gốc
    Dùng để tạo reference audio cho từng segment
    
    Args:
        original_audio: Đường dẫn audio gốc
        start_time: Thời gian bắt đầu (giây)
        end_time: Thời gian kết thúc (giây)
        output_path: Đường dẫn lưu segment
    """
    try:
        audio = AudioSegment.from_file(original_audio)
        
        # Convert to milliseconds
        start_ms = int(start_time * 1000)
        end_ms = int(end_time * 1000)
        
        # Extract segment
        segment = audio[start_ms:end_ms]
        
        # Export
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        segment.export(output_path, format="wav")
        
        return True
    except Exception as e:
        print(f"   ⚠️ Lỗi extract segment: {e}")
        return False


def tts_openvoice_segments(segments_json, original_audio, output_dir, 
                           use_segment_reference=False):
    """
    TTS cho tất cả segments với OpenVoice voice cloning
    
    Args:
        segments_json: JSON chứa segments với text tiếng Việt
        original_audio: Audio gốc (để extract voice characteristics)
        output_dir: Thư mục lưu audio segments
        use_segment_reference: True = clone từng segment riêng, False = clone toàn bộ
    
    Returns:
        True nếu thành công
    """
    print("🎙️ TTS với OpenVoice - Voice Cloning...")
    
    try:
        # Load segments
        with open(segments_json, encoding="utf-8") as f:
            segments = json.load(f)
        
        # Tạo thư mục
        os.makedirs(output_dir, exist_ok=True)
        temp_dir = os.path.join(output_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Khởi tạo OpenVoice TTS
        tts = OpenVoiceTTS(device='auto')
        
        # Extract voice embedding từ audio gốc (toàn bộ video)
        print("\n📊 Extracting voice characteristics từ video gốc...")
        global_se_path = os.path.join(temp_dir, "global_voice_embedding.pth")
        if not use_segment_reference:
            tts.extract_voice_embedding(original_audio, global_se_path)
        
        print(f"\n🎵 Tổng hợp {len(segments)} segments...")
        
        success_count = 0
        failed_segments = []
        
        for i, seg in enumerate(segments):
            vi_text = seg.get("vi_text", "").strip()
            
            if not vi_text:
                print(f"  [{i+1}/{len(segments)}] ⚠️ Segment rỗng, bỏ qua")
                continue
            
            output_path = os.path.join(output_dir, f"segment_{i:04d}.wav")
            
            try:
                # Chọn reference embedding
                if use_segment_reference:
                    # Clone từng segment riêng (chính xác hơn nhưng chậm hơn)
                    seg_audio = os.path.join(temp_dir, f"ref_{i:04d}.wav")
                    
                    # Extract audio segment gốc
                    if extract_segment_audio(original_audio, seg["start"], seg["end"], seg_audio):
                        # Extract embedding cho segment này
                        se_path = os.path.join(temp_dir, f"se_{i:04d}.pth")
                        tts.extract_voice_embedding(seg_audio, se_path)
                    else:
                        # Fallback to global
                        se_path = global_se_path
                else:
                    # Clone từ toàn bộ audio (nhanh hơn, quality vẫn tốt)
                    se_path = global_se_path
                
                # Tính tốc độ nói
                duration = seg["end"] - seg["start"]
                char_count = len(vi_text)
                # Ước lượng: ~5 ký tự/giây cho tiếng Việt ở tốc độ bình thường
                estimated_duration = char_count / 5.0
                speed = estimated_duration / duration if duration > 0 else 1.0
                speed = max(0.5, min(2.0, speed))  # Giới hạn 0.5-2.0x
                
                # Synthesize với voice cloning
                success = tts.synthesize_with_cloning(
                    vi_text,
                    se_path,
                    output_path,
                    speed=speed,
                    language='Vietnamese'
                )
                
                if success:
                    # Lưu path vào segment
                    seg["vi_audio_path"] = output_path
                    success_count += 1
                    print(f"  [{i+1}/{len(segments)}] ✅ {seg['start']:.1f}s-{seg['end']:.1f}s | Speed: {speed:.2f}x")
                else:
                    failed_segments.append(i)
                    print(f"  [{i+1}/{len(segments)}] ❌ Failed")
                
                # Clear cache mỗi 10 segments
                if (i + 1) % 10 == 0:
                    tts.clear_cache()
                
            except Exception as e:
                print(f"  [{i+1}/{len(segments)}] ❌ Lỗi: {e}")
                failed_segments.append(i)
        
        # Update JSON với audio paths
        with open(segments_json, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ TTS hoàn tất:")
        print(f"   - Thành công: {success_count}/{len(segments)}")
        if failed_segments:
            print(f"   - Thất bại: {len(failed_segments)} segments: {failed_segments[:10]}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Lỗi TTS: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test
    tts_openvoice_segments(
        "../subtitles/vi.json",
        "../audio/original.wav",
        "../audio/vi_segments"
    )
