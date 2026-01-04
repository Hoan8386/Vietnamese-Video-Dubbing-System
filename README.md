# 🎬 Tool Lồng Tiếng Tự Động - Vietnamese Auto Dubbing

Tool tự động chuyển đổi video tiếng Anh sang tiếng Việt bằng AI.

## ✨ Tính năng

- ✅ Tách audio từ video
- ✅ Nhận dạng giọng nói (ASR) bằng Whisper
- ✅ **Phân tích giọng nói:** Tự động detect gender (nam/nữ) và emotion
- ✅ Dịch tự động Anh → Việt
- ✅ **Advanced TTS:**
  - 🎤 Tự động chọn giọng nam/nữ theo phân tích
  - 🎭 Điều chỉnh rate, pitch, volume theo emotion (excited, calm, urgent, neutral)
  - 🎵 Mix với audio gốc để giữ background emotion (optional)
- ✅ Ghép audio vào video
- ✅ Chạy 100% trên CPU (không cần GPU)
- ✅ Xử lý batch (không realtime)
- ✅ Hỗ trợ Windows & Linux
- ✅ Không cần Microsoft Build Tools

## 📁 Cấu trúc thư mục

```
project/
├── input/          # Đặt video gốc vào đây
│   └── video.mp4
├── output/         # Video đã lồng tiếng
│   └── video_vi.mp4
├── audio/          # Audio trung gian
│   ├── original.wav
│   ├── vi_segments/
│   └── vi_full.wav
├── subtitles/      # Phụ đề và dịch
│   ├── en.json
│   └── vi.json
├── src/            # Source code
│   ├── extract_audio.py
│   ├── asr_whisper.py
│   ├── translate.py
│   ├── tts_vi.py
│   ├── merge_audio.py
│   ├── merge_video.py
│   └── main.py
└── requirements.txt
```

## 🚀 Cài đặt

### 1. Cài đặt FFmpeg

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

### 2. Cài đặt Python packages

```bash
# Tạo virtual environment (khuyến nghị)
python -m venv venv

# Kích hoạt
# Windows:
venv\Scripts\activate
# Linux:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

⏱️ **Lưu ý:** Quá trình cài đặt có thể mất 5-10 phút do download models.

## 📖 Sử dụng

### Bước 1: Đặt video vào thư mục input

```bash
# Copy video của bạn vào:
input/video.mp4
```

### Bước 2: Chọn chế độ TTS

**Chế độ A: Edge TTS (Nhanh - Khuyến nghị cho người mới)**

```bash
cd src
python main.py
```

- ⚡ Nhanh: ~5-10 phút cho video 5 phút
- 🎭 Tự động chọn giọng nam/nữ
- 🎵 Điều chỉnh emotion cơ bản

**Chế độ B: Voice Cloning (Chất lượng cao - Clone giọng gốc)**

```bash
cd src
python main_voice_cloning.py
```

- 🎤 Clone 100% giọng từ video gốc
- 💯 Giữ nguyên tone & emotion
- ⏱️ Chậm hơn: ~30-60 phút cho video 5 phút
- 📦 Cần cài OpenVoice: Xem [VOICE_CLONING_SETUP.md](VOICE_CLONING_SETUP.md)

**Chế độ C: Menu lựa chọn**

```bash
cd src
python run.py
# Chọn 1 hoặc 2 theo nhu cầu
```

### Bước 3: Lấy kết quả

Video đã lồng tiếng sẽ có tại:

- Edge TTS: `output/video_vi.mp4`
- Voice Cloning: `output/video_vi_cloned.mp4`

## ⚙️ Cấu hình nâng cao

### Thay đổi model Whisper (trong asr_whisper.py)

```python
# Model nhỏ hơn (nhanh hơn, ít chính xác hơn)
transcribe(audio, out_json, model_size="tiny")   # ~1GB RAM
transcribe(audio, out_json, model_size="base")   # ~1GB RAM

# Model lớn hơn (chậm hơn, chính xác hơn)
transcribe(audio, out_json, model_size="medium") # ~5GB RAM
transcribe(audio, out_json, model_size="large")  # ~10GB RAM
```

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

```bash
# Kiểm tra ffmpeg đã cài
ffmpeg -version

# Nếu chưa có, cài theo hướng dẫn phần "Cài đặt FFmpeg"
```

### Lỗi: Out of Memory

```bash
# Giảm model size trong main.py:
transcribe(..., model_size="tiny")  # Thay vì "small"
```

### Lỗi: "Microsoft Visual C++ 14.0 required"

```bash
# Đã fix: Tool hiện dùng Edge TTS, không cần Build Tools nữa
# Nếu vẫn gặp lỗi, chạy:
pip install edge-tts
```

### Thay đổi giọng TTS

Mặc định dùng giọng nữ. Để đổi sang giọng nam, sửa trong [src/tts_vi.py](src/tts_vi.py):

```python
# Đổi từ "female" sang "male"
tts_segments(vi_json, audio_out_dir, voice="male")
```

**Chế độ Edge TTS:**

- **Whisper**: openai/whisper (small - 244M params)

### Edge TTS Mode (CPU)

| Video   | Thời lượng | Thời gian xử lý |
| ------- | ---------- | --------------- |
| 5 phút  | 300s       | ~10-15 phút     |
| 10 phút | 600s       | ~20-30 phút     |
| 30 phút | 1800s      | ~60-90 phút     |

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

- ❌ Không lip-sync (môi không khớp)
- ❌ Chất lượng dịch phụ thuộc vào model
- ❌ Không xử lý realtime (chỉ batch)

**Edge TTS:**

- ⚠️ Cần internet
- ⚠x] Thêm tùy chọn chọn giọng TTS
- [x] Tự động phân biệt giọng nam/nữ
- [x] Voice cloning (clone giọng từ video gốc)
- [ ] Hỗ trợ nhiều ngôn ngữ
- [ ] UI web đơn giản
- [ ] Tối ưu tốc độ xử lý (parallel processing)
- [ ] Thêm option giữ audio gốc + mix với audio VI
- [ ] Lip-sync với Wav2Lip
- ⚠️ Chất lượng phụ thuộc audio gốc (cần rõ ràng, ít noisevi
- **TTS**: Microsoft Edge TTS (vi-VN-HoaiMyNeural)

## ⚠️ Hạn chế

- ❌ Không lip-sync (môi không khớp)
- ❌ Chất lượng dịch phụ thuộc vào model
- ❌ Không xử lý realtime (chỉ batch)
- ⚠️ TTS cần internet (sử dụng Edge TTS API)

## 🎯 Roadmap

- [ ] Thêm tùy chọn chọn giọng TTS
- [ ] Hỗ trợ nhiều ngôn ngữ
- [ ] UI web đơn giản
- [ ] Tối ưu tốc độ xử lý
- [ ] Thêm option giữ audio gốc + mix với audio VI

## 📄 License

MIT License - Tự do sử dụng và chỉnh sửa

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Tạo Pull Request hoặc Issue trên GitHub.

---

**Chúc bạn sử dụng tool hiệu quả! 🎉**
