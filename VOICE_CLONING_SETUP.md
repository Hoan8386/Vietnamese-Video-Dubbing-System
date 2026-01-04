# 🎤 Voice Cloning Setup Guide

## 📦 Cài Đặt OpenVoice

### Bước 1: Cài đặt OpenVoice từ GitHub

```bash
# Clone repository
git clone https://github.com/myshell-ai/OpenVoice.git
cd OpenVoice

# Cài đặt
pip install -e .
```

### Bước 2: Download Models

OpenVoice cần các model checkpoints. Có 2 cách:

**Cách 1: Download tự động (khuyến nghị)**

```python
from openvoice.utils import download_pretrained_model
download_pretrained_model()
```

**Cách 2: Download thủ công**

1. Base TTS Model: https://myshell-public-repo-host.s3.amazonaws.com/openvoice/basespeakers_se.pth
2. Tone Converter: https://myshell-public-repo-host.s3.amazonaws.com/openvoice/converter.pth

Đặt vào thư mục:

```
tool_01/
├── checkpoints/
│   ├── base_speakers/
│   │   └── EN/
│   │       ├── config.json
│   │       └── checkpoint.pth
│   └── converter/
│       ├── config.json
│       └── checkpoint.pth
```

### Bước 3: Cài dependencies bổ sung

```bash
pip install -r requirements_voice_cloning.txt
```

---

## 🚀 Sử Dụng

### Chế độ 1: Edge TTS (Nhanh, mặc định)

```bash
cd src
python main.py
```

### Chế độ 2: Voice Cloning (Clone giọng gốc)

```bash
cd src
python main_voice_cloning.py
```

### Chế độ 3: Menu lựa chọn

```bash
cd src
python run.py
```

---

## ⚡ So Sánh

| Tính năng            | Edge TTS      | Voice Cloning    |
| -------------------- | ------------- | ---------------- |
| **Tốc độ**           | 5-10s/câu     | 30-60s/câu (CPU) |
| **Chất lượng giọng** | Tự nhiên      | Giống gốc 100%   |
| **Auto Gender**      | ✅ Yes        | ✅ Yes (auto)    |
| **Emotion**          | ⚠️ Limited    | ✅ Preserved     |
| **Internet**         | ✅ Required   | ❌ Not required  |
| **GPU**              | ❌ Not needed | ⚠️ Recommended   |

---

## 🔧 Troubleshooting

### Lỗi: "OpenVoice not found"

```bash
pip install git+https://github.com/myshell-ai/OpenVoice.git
```

### Lỗi: "Checkpoints not found"

Kiểm tra cấu trúc thư mục `checkpoints/` theo hướng dẫn trên.

### Quá chậm trên CPU?

- Dùng Edge TTS thay thế
- Hoặc chạy trên máy có GPU CUDA

### Out of Memory?

- Giảm batch size trong code
- Close các ứng dụng khác
- Dùng smaller Whisper model: `model_size="tiny"`

---

## 📊 Hiệu Năng

| Video   | CPU (Intel i7) | GPU (RTX 3060) |
| ------- | -------------- | -------------- |
| 5 phút  | ~40 phút       | ~8 phút        |
| 10 phút | ~80 phút       | ~15 phút       |
| 30 phút | ~240 phút      | ~45 phút       |

**Khuyến nghị:** Dùng GPU để xử lý video dài hơn 10 phút.

---

## 🎯 Tips

1. **Quality vs Speed:**

   - Video ngắn (<5 phút): Dùng Voice Cloning
   - Video dài (>10 phút): Dùng Edge TTS

2. **Best Results:**

   - Video input nên có audio rõ ràng
   - Ít background noise
   - Single speaker tốt hơn multiple speakers

3. **Hybrid Approach:**
   - Dùng Voice Cloning cho các câu quan trọng
   - Edge TTS cho phần còn lại
