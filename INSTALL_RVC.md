# Hướng Dẫn Cài Đặt RVC (Retrieval-based Voice Conversion)

## Tối ưu cho RTX 3050 4GB

### 1. Clone RVC Repository

```bash
cd e:\tool\tool_01
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
cd Retrieval-based-Voice-Conversion-WebUI
```

### 2. Cài Đặt Dependencies

#### A. Cài PyTorch cho RTX 3050 (CUDA 11.7 hoặc 11.8)

```bash
# CUDA 11.7 (Recommend cho RTX 30xx)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

# Hoặc CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### B. Cài RVC Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download Pre-trained Models

#### A. Hubert Base Model

```bash
# Tạo thư mục assets
mkdir assets
mkdir assets\hubert

# Download hubert_base.pt
# URL: https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/hubert_base.pt
# Lưu vào: assets/hubert/hubert_base.pt
```

#### B. Pre-trained Models (Optional)

```bash
mkdir assets\pretrained_v2

# Download pretrained models v2
# D40k.pth: https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/pretrained_v2/D40k.pth
# G40k.pth: https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/pretrained_v2/G40k.pth
# Lưu vào: assets/pretrained_v2/
```

#### C. RMVPE Model (Pitch Extraction)

```bash
# Download rmvpe.pt
# URL: https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rmvpe.pt
# Lưu vào: Retrieval-based-Voice-Conversion-WebUI/rmvpe.pt
```

### 4. Cấu Trúc Thư Mục

```
tool_01/
├── src/
│   ├── voice_cloning_rvc.py (file mới)
│   ├── main_openvoice.py
│   └── ...
├── Retrieval-based-Voice-Conversion-WebUI/
│   ├── assets/
│   │   ├── hubert/
│   │   │   └── hubert_base.pt
│   │   └── pretrained_v2/
│   │       ├── D40k.pth
│   │       └── G40k.pth
│   ├── logs/
│   ├── weights/
│   ├── rmvpe.pt
│   ├── infer-web.py
│   └── ...
└── INSTALL_RVC.md
```

### 5. Test Installation

```bash
cd e:\tool\tool_01
python src\voice_cloning_rvc.py
```

## Train Model Mới (Optional)

### 1. Chuẩn Bị Training Data

- Audio sạch, không noise
- Độ dài: 10-30 phút (tối thiểu 10 phút)
- Format: WAV, 16-48kHz
- Đặt vào: `Retrieval-based-Voice-Conversion-WebUI/dataset/<tên_speaker>/`

### 2. Training qua WebUI

```bash
cd Retrieval-based-Voice-Conversion-WebUI
python infer-web.py
```

1. Mở browser: http://localhost:7865
2. Tab **"训练"** (Training):
   - Nhập tên model
   - Chọn dataset
   - Set epochs: 500-1000 (RTX 3050: 500 epochs ~ 2-4 giờ)
   - Batch size: 4-6 (cho 4GB VRAM)
3. Click **"训练模型"** (Train Model)
4. Sau khi train xong, click **"训练特征索引"** (Train Index)

### 3. Sử Dụng Model

Model được lưu tại:

- `logs/<tên_model>/added_*.pth` (model file)
- `logs/<tên_model>/added_*.index` (index file)

## Tối Ưu cho RTX 3050 4GB

### 1. Cấu Hình Training

**File**: `configs/config.py` hoặc WebUI settings

```python
# Training settings cho RTX 3050
batch_size = 4          # Giảm nếu bị OOM
total_epoch = 500       # Đủ cho quality tốt
save_every_epoch = 50   # Save checkpoint thường xuyên
cache_all_data = False  # Tiết kiệm VRAM
```

### 2. Inference Settings

```python
# Settings tối ưu trong code
f0_method = 'rmvpe'     # Nhanh + chất lượng tốt
index_rate = 0.75       # Cân bằng giữa giống giọng và tự nhiên
is_half = True          # FP16 - tiết kiệm 50% VRAM
```

### 3. Giảm VRAM Usage

- Close tất cả ứng dụng khác
- Giảm batch size xuống 2-4
- Sử dụng FP16 (half precision)
- Clear VRAM cache thường xuyên:
  ```python
  torch.cuda.empty_cache()
  ```

## Troubleshooting

### 1. Out of Memory (OOM)

**Triệu chứng**: `CUDA out of memory`

**Giải pháp**:

```python
# Trong voice_cloning_rvc.py
optimize_vram = True  # Đã enable
torch.cuda.set_per_process_memory_fraction(0.85, 0)

# Giảm batch size trong training
batch_size = 2  # Thay vì 4-6
```

### 2. Slow Training

**Triệu chứng**: Training chậm

**Giải pháp**:

- Enable CUDA optimizations:
  ```python
  torch.backends.cudnn.benchmark = True
  torch.backends.cuda.matmul.allow_tf32 = True
  ```
- Giảm sample rate: 40kHz thay vì 48kHz
- Cache dataset vào RAM (nếu có đủ RAM)

### 3. Index Search Failed

**Triệu chứng**: "Index search FAILED"

**Giải pháp**:

- Train index sau khi train model
- Kiểm tra index file path đúng
- Index rate: 0.5-0.9 (thử các giá trị khác nhau)

## Usage trong Code

### 1. Basic Usage

```python
from src.voice_cloning_rvc import RVCVoiceCloner

# Initialize
cloner = RVCVoiceCloner(
    model_path='Retrieval-based-Voice-Conversion-WebUI/logs/my_model/added_model.pth',
    index_path='Retrieval-based-Voice-Conversion-WebUI/logs/my_model/added_index.index',
    device='cuda',
    optimize_vram=True
)

# Convert single file
cloner.convert_voice(
    input_audio='audio/original.wav',
    output_audio='audio/converted.wav',
    f0_method='rmvpe',
    index_rate=0.75
)
```

### 2. Convert Multiple Segments

```python
# Convert nhiều segments
segments = ['audio/seg_001.wav', 'audio/seg_002.wav', ...]

output_files = cloner.convert_segments(
    audio_segments=segments,
    output_dir='audio/converted/',
    f0_method='rmvpe',
    index_rate=0.75
)
```

### 3. Get Recommended Settings

```python
# Lấy settings tối ưu cho GPU
settings = cloner.get_recommended_settings()
print(settings)
```

## Resources

- **RVC GitHub**: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
- **Hugging Face Models**: https://huggingface.co/lj1995/VoiceConversionWebUI
- **RVC Discord**: https://discord.gg/HcsmBBGyVk
- **Documentation**: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/wiki

## Performance

### RTX 3050 4GB - Expected Performance

| Task                      | Time       | Notes                 |
| ------------------------- | ---------- | --------------------- |
| Training (500 epochs)     | 2-4 giờ    | 10-30 phút audio data |
| Index Creation            | 1-5 phút   | Depends on data size  |
| Inference (1 phút audio)  | 2-5 giây   | FP16, RMVPE           |
| Batch Inference (10 phút) | 20-50 giây | 10 phút audio         |

### Tips để Train Nhanh Hơn

1. **Sử dụng Pre-trained Models**: Giảm epochs xuống 200-300
2. **Dataset nhỏ hơn**: 10-15 phút vẫn OK cho quality tốt
3. **Lower sample rate**: 32kHz hoặc 40kHz thay vì 48kHz
4. **Batch size**: 4-6 là optimal cho RTX 3050

---

**Author**: Tool Lồng Tiếng  
**Date**: 2026-01-05  
**Version**: 1.0
