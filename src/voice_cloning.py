"""
Voice Cloning Module using OpenVoice
Clone giọng từ video input và dùng để TTS tiếng Việt
"""
import os
import json
import torch
import torchaudio
from pathlib import Path


class VoiceCloner:
    """
    Voice Cloning với OpenVoice
    Zero-shot voice cloning: Không cần training
    """
    
    def __init__(self, device="cpu"):
        """
        Khởi tạo Voice Cloner
        
        Args:
            device: "cuda" hoặc "cpu"
        """
        self.device = device
        self.model = None
        self.tone_color_converter = None
        
        print(f"🎤 Khởi tạo Voice Cloner (device: {device})...")
        
    def load_models(self):
        """Load OpenVoice models"""
        try:
            # Import OpenVoice (cần cài đặt riêng)
            from openvoice import se_extractor
            from openvoice.api import ToneColorConverter, BaseSpeakerTTS
            
            # Load Base TTS model
            print("📥 Đang tải Base TTS model...")
            self.base_speaker = BaseSpeakerTTS(
                'checkpoints/base_speakers/EN/config.json',
                device=self.device
            )
            
            # Load Tone Color Converter
            print("📥 Đang tải Tone Color Converter...")
            self.tone_converter = ToneColorConverter(
                'checkpoints/converter/config.json',
                device=self.device
            )
            
            # Load SE Extractor (Speaker Embedding)
            print("📥 Đang tải Speaker Embedding Extractor...")
            self.se_extractor = se_extractor.get_se_model(device=self.device)
            
            print("✅ Models loaded successfully!")
            return True
            
        except ImportError:
            print("❌ OpenVoice chưa được cài đặt!")
            print("📦 Cài đặt: pip install git+https://github.com/myshell-ai/OpenVoice.git")
            return False
        except Exception as e:
            print(f"❌ Lỗi load models: {e}")
            return False
    
    def extract_speaker_embedding(self, reference_audio, output_path="se.pth"):
        """
        Trích xuất speaker embedding từ audio reference
        
        Args:
            reference_audio: Đường dẫn audio gốc (từ video input)
            output_path: Nơi lưu speaker embedding
        
        Returns:
            Path to speaker embedding file
        """
        print(f"🎯 Đang trích xuất speaker embedding từ: {reference_audio}")
        
        try:
            from openvoice import se_extractor
            
            # Extract speaker embedding
            se = se_extractor.get_se(
                reference_audio,
                self.se_extractor,
                target_dir=os.path.dirname(output_path)
            )
            
            # Save embedding
            torch.save(se, output_path)
            
            print(f"✅ Speaker embedding saved: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Lỗi extract speaker embedding: {e}")
            return None
    
    def clone_voice_tts(self, text, speaker_embedding, output_audio, language="Vietnamese"):
        """
        TTS với cloned voice
        
        Args:
            text: Text tiếng Việt cần TTS
            speaker_embedding: Path to speaker embedding file
            output_audio: Output audio path
            language: Ngôn ngữ (default: Vietnamese)
        """
        try:
            # Load speaker embedding
            target_se = torch.load(speaker_embedding).to(self.device)
            
            # Generate speech với base model
            temp_audio = output_audio.replace('.wav', '_temp.wav')
            self.base_speaker.tts(
                text,
                temp_audio,
                speaker='default',
                language=language
            )
            
            # Convert tone color (voice cloning)
            self.tone_converter.convert(
                audio_src_path=temp_audio,
                src_se=self.base_speaker.source_se,
                tgt_se=target_se,
                output_path=output_audio
            )
            
            # Clean up temp file
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi TTS: {e}")
            return False


def tts_with_voice_cloning(segments_json, reference_audio, out_dir):
    """
    TTS segments với voice cloning từ audio gốc
    
    Args:
        segments_json: JSON chứa segments đã dịch
        reference_audio: Audio gốc từ video (để clone giọng)
        out_dir: Thư mục output
    """
    print("=" * 60)
    print("🎤 VOICE CLONING TTS")
    print("=" * 60)
    
    # Kiểm tra device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🖥️ Device: {device.upper()}")
    
    if device == "cpu":
        print("⚠️ Chạy trên CPU sẽ chậm (30-60s/câu)")
        print("💡 Để nhanh hơn, dùng GPU với CUDA")
    
    # Khởi tạo Voice Cloner
    cloner = VoiceCloner(device=device)
    
    if not cloner.load_models():
        print("❌ Không thể load models. Quay về Edge TTS...")
        return False
    
    # Extract speaker embedding từ audio gốc
    print(f"\n🎯 Đang phân tích giọng nói từ video gốc...")
    se_path = os.path.join(out_dir, "speaker_embedding.pth")
    
    if not cloner.extract_speaker_embedding(reference_audio, se_path):
        print("❌ Không thể extract speaker embedding")
        return False
    
    print(f"✅ Đã clone giọng từ video gốc!")
    
    # Load segments
    with open(segments_json, encoding="utf-8") as f:
        segments = json.load(f)
    
    # Tạo thư mục output
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"\n🎙️ Đang tổng hợp giọng nói cho {len(segments)} câu...")
    print("⏱️ Thời gian ước tính: ~{:.0f} phút".format(len(segments) * 0.5))
    
    # TTS từng segment với cloned voice
    success_count = 0
    for i, seg in enumerate(segments):
        if seg.get("vi_text", "").strip():
            wav_path = os.path.join(out_dir, f"{i:04d}.wav")
            
            try:
                print(f"\n[{i+1}/{len(segments)}] 🎤 Cloning: {seg['vi_text'][:50]}...")
                
                if cloner.clone_voice_tts(seg["vi_text"], se_path, wav_path):
                    seg["vi_audio_path"] = wav_path
                    success_count += 1
                    print(f"  ✅ Success")
                else:
                    seg["vi_audio_path"] = None
                    print(f"  ❌ Failed")
                    
            except Exception as e:
                print(f"  ⚠️ Lỗi: {e}")
                seg["vi_audio_path"] = None
        else:
            seg["vi_audio_path"] = None
    
    # Lưu lại segments
    with open(segments_json, "w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"✅ TTS hoàn tất: {success_count}/{len(segments)} câu")
    print(f"📁 Audio lưu tại: {out_dir}")
    print("=" * 60)
    
    return success_count > 0


if __name__ == "__main__":
    # Test
    tts_with_voice_cloning(
        "../subtitles/vi.json",
        "../audio/original.wav",
        "../audio/vi_segments_cloned"
    )
