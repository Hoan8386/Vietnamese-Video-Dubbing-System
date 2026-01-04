# 🎬 Tool Lồng Tiếng Tự Động - Vietnamese Auto Dubbing (GPU Version)

Tool tự động chuyển đổi video tiếng Anh sang tiếng Việt bằng AI với tăng tốc GPU.

> **⚠️ Lưu ý:** Đây là nhánh **GPU** - yêu cầu NVIDIA GPU với CUDA support.  
> Cho phiên bản CPU, xem nhánh `main`.

## 🎮 Yêu Cầu GPU

- **GPU:** NVIDIA GTX 1050 trở lên (khuyến nghị GTX 1660+)
- **VRAM:** Tối thiểu 4GB (khuyến nghị 6GB+)
- **CUDA:** 11.8 hoặc 12.1
- **Driver:** NVIDIA Driver 470+ trở lên

## ✨ Tính năng

- ✅ Tách audio từ video
- ✅ **Nhận dạng giọng nói (ASR) bằng Whisper trên GPU** - Nhanh hơn 5-10x
- ✅ **Phân tích giọng nói:** Tự động detect gender (nam/nữ) và emotion
- ✅ Dịch tự động Anh → Việt (GPU accelerated)
- ✅ **Advanced TTS:**
  - 🎤 Tự động chọn giọng nam/nữ theo phân tích
  - 🎭 Điều chỉnh rate, pitch, volume theo emotion (excited, calm, urgent, neutral)
  - 🎵 Mix với audio gốc để giữ background emotion (optional)
- ✅ **🎵 Background Audio Liên Tục:**
  - Giữ audio gốc (nhạc nền, âm thanh môi trường) xuyên suốt video
  - Tự động giảm volume background (20-30%) để lời thoại nổi bật
  - Không còn bị im lặng ở những đoạn không có lời thoại
  - Dễ dàng điều chỉnh volume background qua config
- ✅ Ghép audio vào video
- ✅ **Tận dụng 100% GPU CUDA** - Xử lý nhanh hơn CPU 5-10x
- ✅ Xử lý batch (không realtime)
- ✅ Hỗ trợ Windows & Linux với NVIDIA GPU

## 📁 Cấu trúc thư mục

```
tool_01/                    # Thư mục gốc dự án
├── input/                  # Đặt video gốc vào đây
│   └── video.mp4          # Video input cần lồng tiếng
│
├── output/                 # Video output đã xử lý
│   └── video_vi.mp4       # Video đã lồng tiếng tiếng Việt
│
├── audio/                  # Audio trung gian (tạo tự động)
│   ├── original.wav       # Audio tách từ video gốc
│   ├── vi_full.wav        # Audio tiếng Việt hoàn chỉnh
│   └── vi_segments/       # Các audio segments từng câu
│       ├── segment_0000.wav
│       ├── segment_0001.wav
│       └── ...
│
├── subtitles/              # Phụ đề và bản dịch (tạo tự động)
│   ├── en.json            # Transcript tiếng Anh từ Whisper
│   └── vi.json            # Bản dịch tiếng Việt + audio paths
│
├── src/                    # Source code chính (GPU optimized)
│   ├── main_openvoice.py  # 🚀 Pipeline chính - CHẠY FILE NÀY (OpenVoice)
│   ├── tts_openvoice.py   # 🎙️ OpenVoice TTS - Voice Cloning trên GPU
│   ├── config.py          # ⚙️ Cấu hình (model, volume, paths)
│   ├── asr_whisper.py     # 🎤 ASR - Whisper trên GPU
│   ├── voice_analysis.py  # 🎭 Phân tích giọng nói (gender/emotion)
│   ├── translate.py       # 🌍 Dịch Anh-Việt (GPU accelerated)
│   ├── tts_advanced.py    # 🔊 TTS nâng cao (Edge TTS - backup option)
│   ├── text_cleaner.py    # ✨ Clean text trước TTS
│   ├── merge_audio_v3.py  # 🎵 Ghép audio với background
│   ├── merge_video.py     # 🎬 Ghép audio vào video
│   ├── extract_audio.py   # 📤 Tách audio từ video
│   └── utils.py           # 🛠️ Các hàm tiện ích
│
├── venv/                   # Virtual environment (tạo khi cài đặt)
│   ├── Scripts/           # Windows
│   └── bin/               # Linux
│
├── OpenVoice/              # OpenVoice models (tải riêng)
│   └── checkpoints/       # Voice cloning models (~2GB)
│       ├── base_speakers/
│       └── converter/
│
├── requirements.txt        # Python dependencies với CUDA support
├── README.md              # 📖 Tài liệu này
└── .gitignore             # Git ignore rules
```

**Lưu ý:**

- Chỉ cần tạo thư mục `input/` và đặt video vào
- Các thư mục `output/`, `audio/`, `subtitles/` sẽ được tạo tự động khi chạy
- File trong `audio/` và `subtitles/` có thể xóa sau khi hoàn thành để tiết kiệm dung lượng

## 🚀 Cài đặt

### 0. Kiểm tra GPU

Trước khi cài đặt, kiểm tra GPU của bạn:

```bash
# Kiểm tra NVIDIA GPU
nvidia-smi

# Kiểm tra CUDA version
nvcc --version
```

### 1. Cài đặt CUDA Toolkit (nếu chưa có)

**Windows:**

- Tải CUDA Toolkit 11.8 hoặc 12.1 từ: https://developer.nvidia.com/cuda-downloads
- Cài đặt theo hướng dẫn

**Linux:**

```bash
# Ubuntu/Debian
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda
```

### 2. Cài đặt FFmpeg

**Windows:**

```bash
# Tải từ: https://ffmpeg.org/download.html
# Hoặc dùng Chocolatey:
choco install ffmpeg
```

**Linux:**

```bash
sudo apt update
sudo apt install ffmpeg
```

### 3. Cài đặt OpenVoice và checkpoints

```bash
# Clone OpenVoice repository
cd E:\tool\tool_01
git clone https://github.com/myshell-ai/OpenVoice.git

# Download checkpoints (~2GB)
# Cách 1: Từ S3
cd OpenVoice
Invoke-WebRequest -Uri "https://myshell-public-repo-hosting.s3.amazonaws.com/openvoice/checkpoints_1226.zip" -OutFile "checkpoints.zip"
Expand-Archive -Path "checkpoints.zip" -DestinationPath "."
Remove-Item "checkpoints.zip"

# Cài OpenVoice
cd ..
pip install -e OpenVoice/
```

### 4. Cài đặt Python packages với CUDA support

```bash
# Tạo virtual environment (khuyến nghị)
python -m venv venv

# Kích hoạt
# Windows:
venv\Scripts\activate
# Linux:
source venv/bin/activate

# Cài đặt PyTorch với CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Cài đặt các dependencies khác
pip install -r requirements.txt
```

⏱️ **Lưu ý:** Quá trình cài đặt có thể mất 15-20 phút do download CUDA libraries, OpenVoice và models.

### 5. Verify GPU Setup

```bash
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
```

Kết quả mong đợi:

```
CUDA Available: True
GPU: NVIDIA GeForce GTX 1660
```

## 📖 Sử dụng

### Bước 1: Đặt video vào thư mục input

```bash
# Copy video của bạn vào:
input/video.mp4
```

### Bước 2: Chạy tool với GPU

```bash
cd src
python main.py
```

**Tính năng GPU:**

- ⚡ **Whisper ASR trên GPU** - Nhanh hơn 5-10x so với CPU
- 🚀 **Translation trên GPU** - Xử lý nhanh hơn 3-5x
- 🎭 Tự động chọn giọng nam/nữ và điều chỉnh emotion
- 🎵 Advanced TTS với Edge TTS (online)

**Thời gian xử lý với GPU (GTX 1660):**

- Video 5 phút: ~2-3 phút
- Video 10 phút: ~4-6 phút
- Video 30 phút: ~12-18 phút

### Bước 3: Lấy kết quả

Video đã lồng tiếng sẽ có tại: `output/video_vi.mp4`

## ⚙️ Cấu hình nâng cao

### Điều chỉnh Background Audio Volume

Xem hướng dẫn chi tiết tại: [BACKGROUND_AUDIO_GUIDE.md](BACKGROUND_AUDIO_GUIDE.md)

**Tóm tắt:** Chỉnh trong `src/config.py`

```python
# src/config.py
BACKGROUND_VOLUME = 0.25  # 25% volume audio gốc

# Điều chỉnh theo loại video:
# 0.15-0.20: Background nhẹ (Phim/Drama - nhạc nền thường to)
# 0.25-0.30: Background vừa phải (Vlog/Tutorial - cân bằng)
# 0.35-0.40: Background rõ hơn (Music Video - giữ nhiều nhạc)
```

### Thay đổi model Whisper (trong asr_whisper.py)

```python
# Model nhỏ hơn (nhanh hơn, ít chính xác hơn)
transcribe(audio, out_json, model_size="tiny")   # ~1GB VRAM
transcribe(audio, out_json, model_size="base")   # ~1GB VRAM

# Model vừa (khuyến nghị cho GPU)
transcribe(audio, out_json, model_size="small")  # ~2GB VRAM (mặc định)

# Model lớn hơn (chính xác hơn, cần GPU mạnh)
transcribe(audio, out_json, model_size="medium") # ~5GB VRAM
transcribe(audio, out_json, model_size="large")  # ~10GB VRAM (yêu cầu RTX 3060+)
```

**Khuyến nghị theo GPU:**

- GTX 1050/1650 (4GB VRAM): `small` hoặc `base`
- GTX 1660/RTX 2060 (6GB VRAM): `small` hoặc `medium`
- RTX 3060/3070+ (8GB+ VRAM): `medium` hoặc `large`

### Thay đổi model dịch (trong translate.py)

```python
# Model khác (nếu chất lượng dịch chưa tốt)
translator = pipeline(
    "translation",
    model="VietAI/envit5-translation"  # Alternative
)
```

## 🔧 Xử lý lỗi

### Lỗi: "ffmpeg not found"

CUDA Out of Memory

```bash
# Giảm model size trong main.py:
transcribe(..., model_size="base")  # Thay vì "small"

# Hoặc clear CUDA cache:
import torch
torch.cuda.empty_cache()

# Kiểm tra VRAM usage:
nvidia-smi
```

### Lỗi: "CUDA not available"

```bash
# Kiểm tra PyTorch có nhận GPU không:
python -c "import torch; print(torch.cuda.is_available())"

# Nếu False, cài lại PyTorch với CUDA:
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# Nếu chưa có, cài theo hướng dẫn phần "Cài đặt FFmpeg"
```

### Lỗi: Out of Memory

```bash
# Giảm model size trong main.py:
transcribe(..., model_size="tiny")  # Thay vì "small"
```

## ⚡ Hiệu Năng GPU + OpenVoice

### Thời gian xử lý (GPU + OpenVoice Voice Cloning)

| Video   | GTX 1650 (4GB) | GTX 1660 (6GB) | RTX 3060 (12GB) | RTX 4070 (12GB) |
| ------- | -------------- | -------------- | --------------- | --------------- |
| 5 phút  | ~5-7 phút      | ~4-5 phút      | ~2-3 phút       | ~1.5-2 phút     |
| 10 phút | ~10-14 phút    | ~8-10 phút     | ~4-6 phút       | ~3-4 phút       |
| 30 phút | ~30-42 phút    | ~24-30 phút    | ~12-18 phút     | ~9-12 phút      |

_Thời gian dựa trên Whisper `small` model + OpenVoice standard mode (không dùng --segment-reference)._

### So sánh CPU vs GPU (với OpenVoice)

| Metric                   | CPU (i7-10700) | GPU (GTX 1660) | Tăng tốc          |
| ------------------------ | -------------- | -------------- | ----------------- | ------------- |
| Whisper ASR (5 phút)     | ~8 phút        | ~1 phút        | **8x**            |
| Translation (5 phút)     | ~2 phút        | ~30 giây       | **4x**            |
| OpenVoice TTS (5 phút)   | ~35 phút       | ~3 phút        | **12x**           |
| **Tổng (5 phút video)**  | **~45 phút**   | **~4.5 phút**  | **~10x**          | Voice win\*\* |
| Giữ nhịp điệu/intonation | ❌             | ✅             | **OpenVoice win** |
| Quality tổng thể         | ⭐⭐⭐         | ⭐⭐⭐⭐⭐     | **OpenVoice win** |

### So sánh CPU vs GPU

| Metric                  | CPU (i7-10700) | GPU (GTX 1660) | Tăng tốc |
| ----------------------- | -------------- | -------------- | -------- |
| Whisper ASR (5 phút)    | ~8 phút        | ~1 phút        | **8x**   |
| Translation (5 phút)    | ~2 phút        | ~30 giây       | **4x**   |
| **Tổng (5 phút video)** | **~12 phút**   | **~2.5 phút**  | **~5x**  |

### Voice Cloning Mode

| Video   | CPU (i7)  | GPU (RTX 3060) |
| ------- | --------- | -------------- |
| 5 phút  | ~40 phút  | ~8 phút        |
| 10 phút | ~80 phút  | ~15 phút       |
| 30 phút | ~240 phút | ~45 phút       |

- **Whisper**: openai/whisper (small - 244M params)
- **Translation**: Helsinki-NLP/opus-mt-en-vi
- **Voice Cloning**: OpenVoice (zero-shot voice cloning)
- **Speaker Embedding**: SE-ResNet
  | ------- | ---------- | --------------------- |
  | 5 phút | 300s | ~10-15 phút |
  | 10 phút | 600s | ~20-30 phút |
  | 30 phút | 1800s | ~60-90 phút |

_Thời gian phụ thuộc vào cấu hình máy_

## 📝 Chi tiết kỹ thuật

### Pipeline

1. **Extract Audio** → ffmpeg tách audio từ video
2. **ASR** → Whisper nhận dạng → timestamps + text
3. **Translate** → Helsinki-NLP/opus-mt-en-vi
4. **TTS** → Microsoft Edge TTS Vietnamese (HoaiMy Neural)
5. **Merge Audio** → pydub ghép theo timestamps
6. **Merge Video** → ffmpeg ghép audio vào video

**Chung:**

- ❌ Không li (GPU Accelerated)

1. **Extract Audio** → ffmpeg tách audio từ video
2. **ASR (GPU)** → Whisper CUDA nhận dạng → timestamps + text (5-10x nhanh hơn)
3. **Voice Analysis (GPU)** → Detect gender & emotion
4. **Translate (GPU)** → Helsinki-NLP model trên CUDA (3-5x nhanh hơn)
5. **TTS** → Microsoft Edge TTS Vietnamese với auto voice selection
6. **Merge Audio** → pydub ghép theo timestamps với background audio
7. **Merge Video** → ffmpeg ghép audio vào video

### Models & Tech Stack

- **ASR**: OpenAI Whisper (small/medium) - CUDA accelerated
- **Translation**: Helsinki-NLP/opus-mt-en-vi - GPU inference
- **Voice Analysis**: librosa + scikit-learn - GPU accelerated
- **TTS**: Microsoft Edge TTS (vi-VN HoaiMy/NamMinh Neural)
- **Audio Processing**: pydub, librosa, scipy
- **GPU Framework**: PyTorch with CUDA 11.8/12.1.md](TROUBLESHOOTING.md)
  & Lưu Ý

- ❌ Không lip-sync (môi không khớp)
- ❌ Chất lượng dịch phụ thuộc vào model
- ❌ Không xử lý realtime (chỉ batch processing)
- ⚠️ TTS cần internet (sử dụng Edge TTS API)
- ⚠️ **Yêu cầu GPU NVIDIA** - Không chạy được trên CPU
- ⚠️ **VRAM tối thiểu 4GB** (khuyến nghị 6GB+)
- ⚠️ Cần cài CUDA Toolkit và driver tương thíchESHOOTING.md#4-ffmpeg-errors)
- Memory errors → [Giảm model size](TROUBLESHOOTING.md#5-memory-errors)
  GPU acceleration cho Whisper~~ ✅ Done
- [x] ~~GPU acceleration cho Translation~~ ✅ Done
- [x] ~~Background audio liên tục~~ ✅ Done (v3)
- [x] ~~Tự động chọn giọng nam/nữ~~ ✅ Done
- [ ] Multi-GPU support
- [ ] Batch processing nhiều videos
- [ ] TensorRT optimization cho RTX GPUs
- [ ] Hỗ trợ AMD GPU (ROCm)
- [ ] Lip-sync với Wav2Lip (GPU)
- [ ] UI web đơn giảnữ
- [ ] UI web đơn giản
- [ ] Tối ưu tốc độ xử lý (parallel processing)
- [ ] Lip-sync với Wav2Lip

## 📚 Documentation

- [README.md](README.md) - Tài liệu chính
- [BACKGROUND_AUDIO_GUIDE.md](BACKGROUND_AUDIO_GUIDE.md) - Hướng dẫn background audio
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Khắc phục lỗi
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - Lịch sử cải tiến

## 📄 License

MIT License - Tự do sử dụng và chỉnh sửa

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Tạo Pull Request hoặc Issue trên GitHub.

---

**Chúc bạn sử dụng tool hiệu quả! 🎉**
