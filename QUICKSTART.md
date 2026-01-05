# 🚀 Quick Start - RVC Voice Cloning

## 1. Cài Đặt (5 phút)

```bash
# Windows: Chạy setup script
setup_rvc.bat

# Hoặc manual:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
pip install -r requirements.txt
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
```

## 2. Download Models (Bắt buộc)

### A. Hubert Base (Bắt buộc)

```
URL: https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/hubert_base.pt
Lưu: Retrieval-based-Voice-Conversion-WebUI/assets/hubert/hubert_base.pt
```

### B. RMVPE (Bắt buộc)

```
URL: https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rmvpe.pt
Lưu: Retrieval-based-Voice-Conversion-WebUI/rmvpe.pt
```

## 3. Test Setup

```bash
python test_setup.py
```

## 4. Sử Dụng

**Lưu ý: RVC là BẮT BUỘC - phải train model trước**

### Basic Usage

```bash
python src/main_rvc.py input/video.mp4 \
    --rvc-model <path_to_model.pth> \
    --rvc-index <path_to_index.index>
```

## 5. Train RVC Model (BẮT BUỘC)

```bash
# 1. Chuẩn bị data (10-30 phút audio WAV sạch)
# Đặt vào: Retrieval-based-Voice-Conversion-WebUI/dataset/my_speaker/

# 2. Mở WebUI
cd Retrieval-based-Voice-Conversion-WebUI
python infer-web.py

# 3. Browser: http://localhost:7865
# Tab "训练" → Train model + index

# 4. Sử dụng model
python src/main_rvc.py input/video.mp4 \
    --rvc-model logs/my_speaker/added_model.pth \
    --rvc-index logs/my_speaker/added_index.index
```

## ⚙️ RTX 3050 Settings

| Setting                    | Value   |
| -------------------------- | ------- |
| Whisper Model              | small   |
| Batch Size                 | 4-6     |
| F0 Method                  | rmvpe   |
| FP16                       | ✅      |
| Training Time (500 epochs) | 2-4 giờ |

## 🆘 Troubleshooting

### CUDA Out of Memory

```bash
# Giảm batch size
--batch-size 2
```

### RVC Not Found

```bash
# Re-install
cd Retrieval-based-Voice-Conversion-WebUI
pip install -r requirements.txt
```

## 📖 Chi Tiết

- **Hướng dẫn đầy đủ**: [INSTALL_RVC.md](INSTALL_RVC.md)
- **README đầy đủ**: [README_RVC.md](README_RVC.md)
- **Config**: [src/config_rvc.py](src/config_rvc.py)

## 🎯 Examples

```bash
# Basic
python src/main_rvc.py input/video.mp4 \
    --rvc-model logs/voice/added.pth \
    --rvc-index logs/voice/added.index

# High quality
python src/main_rvc.py input/video.mp4 \
    --model medium \
    --rvc-model logs/voice/added.pth \
    --rvc-index logs/voice/added.index \
    --background-volume 0.15
```

---

**Need help?** See [INSTALL_RVC.md](INSTALL_RVC.md) for detailed guide.
