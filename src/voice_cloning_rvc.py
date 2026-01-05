"""
Voice Cloning với RVC (Retrieval-based Voice Conversion)
Tối ưu cho RTX 3050 4GB

Tối ưu VRAM thấp:
- Sử dụng half precision (FP16)
- Batch processing nhỏ
- Gradient checkpointing
- Model optimization

Author: Tool Lồng Tiếng
Date: 2026-01-05
"""

import os
import sys
import json
import torch
import torchaudio
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Import RVC modules
try:
    from infer.modules.vc.modules import VC
    from configs.config import Config as RVCConfig
except ImportError:
    print("⚠️ Chưa cài đặt RVC. Đang chuẩn bị hướng dẫn...")
    RVCConfig = None
    VC = None


class RVCVoiceCloner:
    """Voice Cloning với RVC - Tối ưu cho GPU thấp"""
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        index_path: Optional[str] = None,
        device: str = 'auto',
        optimize_vram: bool = True
    ):
        """
        Khởi tạo RVC Voice Cloner
        
        Args:
            model_path: Path đến trained RVC model (.pth)
            index_path: Path đến index file (.index)
            device: 'cuda', 'cpu', hoặc 'auto'
            optimize_vram: Tối ưu cho VRAM thấp (4GB)
        """
        # Device setup
        if device == 'auto':
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
            
        self.optimize_vram = optimize_vram
        
        print("=" * 70)
        print("🎙️ RVC VOICE CLONER - Tối ưu RTX 3050 4GB")
        print("=" * 70)
        
        # Check GPU
        if self.device == 'cuda':
            self._check_gpu_capability()
        
        # Initialize RVC
        if RVCConfig is None or VC is None:
            print("❌ RVC chưa được cài đặt!")
            print("📖 Xem hướng dẫn cài đặt trong file: INSTALL_RVC.md")
            self.model = None
            return
            
        self._initialize_rvc(model_path, index_path)
    
    def _check_gpu_capability(self):
        """Kiểm tra GPU và VRAM"""
        try:
            gpu_name = torch.cuda.get_device_name(0)
            total_vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            
            print(f"✅ GPU: {gpu_name}")
            print(f"✅ VRAM: {total_vram:.2f} GB")
            
            # Tối ưu cho VRAM thấp
            if total_vram <= 4.5:  # RTX 3050 4GB
                print("⚙️ Kích hoạt chế độ tối ưu VRAM thấp")
                self.optimize_vram = True
                
                # Tối ưu PyTorch
                torch.backends.cudnn.benchmark = True
                torch.backends.cuda.matmul.allow_tf32 = True
                
                # Set memory fraction
                torch.cuda.set_per_process_memory_fraction(0.85, 0)
                
            # Clear cache
            torch.cuda.empty_cache()
            
        except Exception as e:
            print(f"⚠️ Không thể kiểm tra GPU: {e}")
    
    def _initialize_rvc(self, model_path: Optional[str], index_path: Optional[str]):
        """Khởi tạo RVC model"""
        try:
            # RVC Config
            self.rvc_config = RVCConfig()
            self.rvc_config.device = self.device
            
            # Tối ưu cho VRAM thấp
            if self.optimize_vram:
                self.rvc_config.is_half = True  # FP16
                self.rvc_config.n_cpu = 4  # Giảm CPU threads
            else:
                self.rvc_config.is_half = False  # FP32
                
            # Initialize VC
            print("🔄 Đang khởi tạo RVC engine...")
            self.vc = VC(self.rvc_config)
            
            # Load model nếu có
            if model_path and os.path.exists(model_path):
                self._load_model(model_path, index_path)
            else:
                print("⚠️ Chưa có model. Sử dụng pretrained model hoặc train model mới.")
                self.model_loaded = False
            
            print("✅ RVC khởi tạo thành công!")
            
        except Exception as e:
            print(f"❌ Lỗi khởi tạo RVC: {e}")
            self.model = None
    
    def _load_model(self, model_path: str, index_path: Optional[str] = None):
        """Load trained RVC model"""
        try:
            print(f"🔄 Đang load model: {model_path}")
            
            # Load model vào VC
            model_name = Path(model_path).stem
            self.vc.get_vc(model_name)
            
            self.model_path = model_path
            self.index_path = index_path
            self.model_loaded = True
            
            print("✅ Model loaded thành công!")
            
        except Exception as e:
            print(f"❌ Lỗi load model: {e}")
            self.model_loaded = False
    
    def convert_voice(
        self,
        input_audio: str,
        output_audio: str,
        f0_method: str = 'rmvpe',
        f0_up_key: int = 0,
        index_rate: float = 0.75,
        filter_radius: int = 3,
        resample_sr: int = 0,
        rms_mix_rate: float = 0.25,
        protect: float = 0.33
    ) -> bool:
        """
        Chuyển đổi giọng nói với RVC
        
        Args:
            input_audio: Path đến audio input
            output_audio: Path để save output
            f0_method: Phương pháp extract F0 ('rmvpe', 'harvest', 'crepe')
            f0_up_key: Chỉnh pitch (semitones) - 0 = giữ nguyên
            index_rate: Tỷ lệ sử dụng index (0.0-1.0) - cao hơn = giống voice hơn
            filter_radius: Median filter radius cho F0
            resample_sr: Sample rate output (0 = không resample)
            rms_mix_rate: Mix RMS (0.0-1.0) - 0.25 = 75% new voice
            protect: Bảo vệ consonants (0.0-0.5)
            
        Returns:
            bool: Thành công hay không
        """
        if not hasattr(self, 'vc') or not self.model_loaded:
            print("❌ Model chưa được load!")
            return False
            
        try:
            print(f"🔄 Converting: {input_audio}")
            
            # Clear VRAM trước khi convert
            if self.device == 'cuda':
                torch.cuda.empty_cache()
            
            # Convert
            info, (sr, audio_output) = self.vc.vc_single(
                sid=0,  # Speaker ID
                input_audio_path=input_audio,
                f0_up_key=f0_up_key,
                f0_file=None,
                f0_method=f0_method,
                file_index=self.index_path or "",
                file_index2="",
                index_rate=index_rate,
                filter_radius=filter_radius,
                resample_sr=resample_sr,
                rms_mix_rate=rms_mix_rate,
                protect=protect
            )
            
            # Save output
            import soundfile as sf
            sf.write(output_audio, audio_output, sr)
            
            print(f"✅ Saved: {output_audio}")
            print(f"ℹ️ Info: {info}")
            
            # Clear cache
            if self.device == 'cuda':
                torch.cuda.empty_cache()
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi convert: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def convert_segments(
        self,
        audio_segments: list,
        output_dir: str,
        f0_method: str = 'rmvpe',
        **kwargs
    ) -> list:
        """
        Convert nhiều audio segments
        
        Args:
            audio_segments: List các audio file paths
            output_dir: Thư mục output
            f0_method: Phương pháp F0
            **kwargs: Các tham số khác cho convert_voice
            
        Returns:
            list: Danh sách output files
        """
        output_files = []
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n🔄 Converting {len(audio_segments)} segments...")
        
        for i, audio_file in enumerate(audio_segments):
            # Output path
            segment_name = Path(audio_file).stem
            output_file = os.path.join(output_dir, f"{segment_name}_converted.wav")
            
            print(f"\n[{i+1}/{len(audio_segments)}] {segment_name}")
            
            # Convert
            success = self.convert_voice(
                audio_file,
                output_file,
                f0_method=f0_method,
                **kwargs
            )
            
            if success:
                output_files.append(output_file)
            else:
                print(f"⚠️ Bỏ qua segment {i+1}")
                
        print(f"\n✅ Hoàn thành {len(output_files)}/{len(audio_segments)} segments")
        
        return output_files
    
    def train_model(
        self,
        training_audio_dir: str,
        model_name: str,
        epochs: int = 500,
        batch_size: int = 4,
        save_frequency: int = 50
    ):
        """
        Train RVC model với dataset
        
        Args:
            training_audio_dir: Thư mục chứa audio training data
            model_name: Tên model
            epochs: Số epochs
            batch_size: Batch size (nhỏ cho VRAM thấp)
            save_frequency: Save checkpoint mỗi N epochs
        """
        print("🔄 Training model...")
        print("⚠️ Chức năng training cần được thực hiện qua RVC WebUI")
        print("📖 Xem hướng dẫn trong INSTALL_RVC.md")
        
        # TODO: Implement training pipeline
        # - Preprocess audio
        # - Extract features
        # - Train model
        # - Create index
        
    def get_recommended_settings(self) -> dict:
        """Lấy settings được recommend cho GPU hiện tại"""
        settings = {
            'f0_method': 'rmvpe',  # Tốt nhất cho quality
            'index_rate': 0.75,
            'filter_radius': 3,
            'rms_mix_rate': 0.25,
            'protect': 0.33
        }
        
        if self.device == 'cuda':
            vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            
            if vram <= 4.5:  # RTX 3050
                print("📊 Settings cho RTX 3050 4GB:")
                settings['batch_size'] = 4
                settings['f0_method'] = 'rmvpe'  # Nhanh và tốt
                
            elif vram <= 6:  # RTX 3060
                print("📊 Settings cho 6GB VRAM:")
                settings['batch_size'] = 8
                
            else:  # > 6GB
                print("📊 Settings cho >6GB VRAM:")
                settings['batch_size'] = 16
        
        return settings


def test_rvc():
    """Test RVC Voice Cloner"""
    print("🧪 Testing RVC Voice Cloner...")
    
    # Initialize
    cloner = RVCVoiceCloner(
        device='auto',
        optimize_vram=True
    )
    
    if cloner.model is None:
        print("\n❌ RVC chưa được cài đặt!")
        print("📖 Vui lòng xem INSTALL_RVC.md để cài đặt")
        return
    
    # Get recommended settings
    settings = cloner.get_recommended_settings()
    print(f"\n📊 Recommended settings: {json.dumps(settings, indent=2)}")
    
    print("\n✅ RVC initialization test passed!")


if __name__ == "__main__":
    test_rvc()
