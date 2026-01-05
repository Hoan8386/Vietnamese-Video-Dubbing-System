# 🎬 Tool Lồng Tiếng với RVC Voice Cloning

Tool tự động lồng tiếng video với công nghệ Voice Cloning sử dụng RVC (Retrieval-based Voice Conversion), tối ưu cho **RTX 3050 4GB**.

## ✨ Tính Năng

- ✅ **ASR (Whisper)**: Transcribe audio từ video
- ✅ **Translation**: Dịch tự động English → Vietnamese
- ✅ **TTS (Edge TTS)**: Text-to-Speech tiếng Việt chất lượng cao, miễn phí
- ✅ **Voice Cloning (RVC)**: Clone giọng nói từ video gốc với RVC
- ✅ **Background Audio**: Giữ nhạc nền và sound effects
- ✅ **GPU Optimization**: Tối ưu cho RTX 3050 4GB VRAM

## 🚀 Quick Start

### 1. Cài Đặt

#### Windows

```bash
# Clone repository
git clone <your-repo>
cd tool_01

# Chạy setup script
setup_rvc.bat
```

#### Manual Setup

```bash
# 1. Cài PyTorch với CUDA 11.7
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

# 2. Cài dependencies
pip install -r requirements.txt

# 3. Clone RVC
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
cd Retrieval-based-Voice-Conversion-WebUI
pip install -r requirements.txt
cd ..

# 4. Download models (xem INSTALL_RVC.md)
```

Xem hướng dẫn chi tiết: **[INSTALL_RVC.md](INSTALL_RVC.md)**

### 2. Sử Dụng

**Lưu ý: RVC là BẮT BUỘC trong phiên bản này**

#### Basic Usage

```bash
python src/main_rvc.py input/video.mp4 \
    --rvc-model logs/my_model/added_model.pth \
    --rvc-index logs/my_model/added_index.index
```

#### Advanced Options

```bash
python src/main_rvc.py input/video.mp4 ^
    --enable-rvc ^
    --rvc-model Retrieval-based-Voice-Conversion-WebUI/logs/my_model/added_model.pth ^
    --rvc-index Retrieval-based-Voice-Conversion-WebUI/logs/my_model/added_index.index
```

#### Advanced Options

```bash
python src/main_rvc.py input/video.mp4 ^
    --rvc-model <path_to_model.pth> ^
    --rvc-index <path_to_index.index> ^
    --output output/video_final.mp4 ^
    --model small ^
    --rvc-index-rate 0.75 ^
    --rvc-f0-method rmvpe ^
    --background-volume 0.20 ^
    --clean
```

## 📋 Options

### Main Arguments

| Argument       | Mô Tả                                             | Mặc Định                  |
| -------------- | ------------------------------------------------- | ------------------------- |
| `input`        | Video input path                                  | `input/video.mp4`         |
| `-o, --output` | Video output path                                 | `output/video_vi_rvc.mp4` |
| `-m, --model`  | Whisper model size (tiny/base/small/medium/large) | `small`                   |

### RVC Options

| Argument           | Mô Tả                                    | Mặc Định |
| ------------------ | ---------------------------------------- | -------- |
| `--rvc-model`      | Path đến RVC model (.pth) - **BẮT BUỘC** | -        |
| `--rvc-index`      | Path đến RVC index (.index)              | -        |
| `--rvc-index-rate` | Index rate (0.0-1.0)                     | `0.75`   |
| `--rvc-f0-method`  | F0 method (rmvpe/harvest/crepe/pm)       | `rmvpe`  |

### Audio Options

| Argument              | Mô Tả                                 | Mặc Định |
| --------------------- | ------------------------------------- | -------- |
| `--background-volume` | Volume của background audio (0.0-1.0) | `0.20`   |
| `--clean`             | Xóa file trung gian                   | `False`  |

## 🎯 Workflow

```
Input Video
    ↓
[1] Extract Audio
    ↓
[2] Transcribe (Whisper)
    ↓
[3] Translate EN→VI
    ↓
[4] Text-to-Speech VI (Edge TTS)
    ↓
[5] Voice Cloning (RVC) ← BẮT BUỘC
    ↓
[6] Merge Audio + Background
    ↓
[7] Merge Video + Audio
    ↓
Output Video
```

## 🎓 Training RVC Model

### 1. Chuẩn Bị Data

- **Audio sạch**: Không noise, echo
- **Độ dài**: 10-30 phút (tối thiểu 10 phút)
- **Format**: WAV, 16-48kHz
- **Đặt vào**: `Retrieval-based-Voice-Conversion-WebUI/dataset/<speaker_name>/`

### 2. Train qua WebUI

```bash
cd Retrieval-based-Voice-Conversion-WebUI
python infer-web.py
```

1. Mở browser: `http://localhost:7865`
2. Tab **"训练"** (Training)
3. Set parameters:
   - Tên model: `my_model`
   - Dataset path: `dataset/my_speaker`
   - Epochs: `500` (RTX 3050: ~2-4 giờ)
   - Batch size: `4-6`
4. Click **"训练模型"** → **"训练特征索引"**

### 3. Sử Dụng Model

Model được lưu tại:

- Model: `logs/my_model/added_*.pth`
- Index: `logs/my_model/added_*.index`

## ⚙️ Tối Ưu cho RTX 3050 4GB

### Memory Management

```python
# Tự động được apply trong code
torch.cuda.set_per_process_memory_fraction(0.85, 0)
torch.backends.cudnn.benchmark = True
torch.backends.cuda.matmul.allow_tf32 = True
```

### Recommended Settings

| Setting               | RTX 3050 4GB | RTX 3060 6GB   | RTX 3080 10GB |
| --------------------- | ------------ | -------------- | ------------- |
| Batch Size (Training) | 4-6          | 8              | 16            |
| FP16                  | ✅ Bắt buộc  | ✅ Khuyên dùng | ⚠️ Tùy chọn   |
| F0 Method             | rmvpe        | rmvpe          | crepe         |
| Index Rate            | 0.75         | 0.75           | 0.8           |

### Giảm VRAM

```bash
# Close tất cả app khác
# Giảm batch size
--batch-size 2

# Giảm model size
--model base  # Thay vì small/medium
```

## 📊 Performance

### RTX 3050 4GB

| Task                               | Time       | GPU Usage |
| ---------------------------------- | ---------- | --------- |
| Training (500 epochs, 10min audio) | 2-4 giờ    | 95%       |
| Inference (1 min audio)            | 2-5 giây   | 80%       |
| Batch Inference (10 min audio)     | 20-50 giây | 90%       |

### Quality

- **Voice Similarity**: 85-95% (với good training data)
- **Naturalness**: 80-90%
- **Stability**: 90-95%

## 🐛 Troubleshooting

### 1. CUDA Out of Memory

**Triệu chứng**: `RuntimeError: CUDA out of memory`

**Giải pháp**:

```bash
# Giảm batch size
--batch-size 2

# Giảm model size
--model base

# Close apps khác
# Restart Python để clear cache
```

### 2. RVC Not Working

**Triệu chứng**: "RVC không khả dụng"

**Giải pháp**:

```bash
# Check RVC installation
cd Retrieval-based-Voice-Conversion-WebUI
python infer-web.py

# Re-install dependencies
pip install -r requirements.txt
```

### 3. Model Not Found

**Triệu chứng**: "Model chưa được load"

**Giải pháp**:

```bash
# Check model path
ls Retrieval-based-Voice-Conversion-WebUI/logs/my_model/

# Đảm bảo có:
# - added_*.pth
# - added_*.index
```

### 4. Poor Voice Quality

**Nguyên nhân**:

- Training data ít hoặc kém chất lượng
- Index rate không phù hợp
- F0 method không tối ưu

**Giải pháp**:

```bash
# Thử index rate khác nhau
--rvc-index-rate 0.5  # Hoặc 0.6, 0.7, 0.8, 0.9

# Thử F0 method khác
--rvc-f0-method harvest  # Hoặc crepe

# Train lại với data tốt hơn (15-30 min)
```

## 📁 Cấu Trúc Project

```
tool_01/
├── input/                          # Video input
│   └── video.mp4
├── output/                         # Video output
│   └── video_vi_rvc.mp4
├── audio/                          # Audio temp files
│   ├── original.wav
│   ├── vi_segments/               # TTS audio
│   ├── rvc_segments/              # RVC converted audio
│   └── final_vi_with_bg.wav
├── subtitles/                      # Subtitles
│   ├── en.json
│   └── vi.json
├── src/                            # Source code
│   ├── main_rvc.py                # Main pipeline với RVC
│   ├── voice_cloning_rvc.py       # RVC wrapper
│   ├── asr_whisper.py
│   ├── translate.py
│   ├── tts_openvoice.py
│   ├── merge_audio_v3.py
│   ├── merge_video.py
│   └── utils.py
├── Retrieval-based-Voice-Conversion-WebUI/  # RVC
│   ├── assets/
│   ├── logs/                       # Trained models
│   ├── weights/
│   └── infer-web.py
├── requirements.txt
├── setup_rvc.bat                   # Setup script
├── INSTALL_RVC.md                  # Hướng dẫn cài đặt
└── README_RVC.md                   # This file
```

## 🔗 Resources

- **RVC GitHub**: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
- **Models**: https://huggingface.co/lj1995/VoiceConversionWebUI
- **Discord**: https://discord.gg/HcsmBBGyVk
- **Whisper**: https://github.com/openai/whisper

## 📝 Examples

### Example 1: Basic Dubbing

```bash
python src/main_rvc.py input/movie.mp4 \
    --rvc-model logs/speaker/added_model.pth \
    --rvc-index logs/speaker/added_index.index \
    -o output/movie_vi.mp4
```

### Example 2: High Quality Settings

```bash
python src/main_rvc.py input/interview.mp4 \
    --rvc-model logs/interviewer_voice/added_model.pth \
    --rvc-index logs/interviewer_voice/added_index.index \
    --rvc-index-rate 0.8 \
    --rvc-f0-method rmvpe
```

### Example 3: Full Production

```bash
python src/main_rvc.py input/presentation.mp4 \
    --model medium \
    --rvc-model logs/speaker/added_model.pth \
    --rvc-index logs/speaker/added_index.index \
    --rvc-f0-method crepe \
    --background-volume 0.15 \
    -o output/presentation_vi_hq.mp4
```

## 📜 License

MIT License

## 👥 Credits

- **RVC**: RVC-Project Team
- **Whisper**: OpenAI
- **Tool**: Auto Dubbing Tool Team

---

**Version**: 1.0  
**Date**: 2026-01-05  
**Author**: Tool Lồng Tiếng

🌟 **Star this repo if you find it useful!**
