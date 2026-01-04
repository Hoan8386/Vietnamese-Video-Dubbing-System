# 🚀 Các cải tiến đã thêm vào Tool

## ✅ Đã cải thiện

### 1. **File cấu hình tập trung (config.py)**

- Tất cả settings ở một chỗ
- Dễ dàng tùy chỉnh model, audio settings
- Không cần sửa code cho mỗi thay đổi

### 2. **Utilities module (utils.py)**

- ✅ **Validate video** trước khi xử lý
- ✅ **Normalize audio** - chuẩn hóa âm lượng
- ✅ **Speed adjustment** - điều chỉnh tốc độ nói
- ✅ **Checkpoint system** - lưu tiến trình
- ✅ Format time, get video duration

### 3. **Merge audio v2 (merge_audio_v2.py)**

- ✅ **Tự động điều chỉnh tốc độ** audio tiếng Việt
- ✅ Nếu audio VI dài hơn → tăng tốc
- ✅ Nếu audio VI ngắn hơn → giảm tốc
- ✅ Normalize volume tự động
- ✅ Giữ timing chính xác với audio gốc

### 4. **Main v2 với CLI (main_v2.py)**

- ✅ **Command line arguments**
  - Chỉ định input/output
  - Chọn model size
  - Resume từ checkpoint
  - Clean up files
  - Tắt progress bar
- ✅ **Progress tracking**
  - Thanh tiến trình tổng thể
  - Hiển thị bước đang thực hiện
  - Estimated time remaining
- ✅ **Checkpoint/Resume**
  - Tự động lưu tiến trình
  - Resume nếu bị gián đoạn
  - Ctrl+C an toàn
- ✅ **Validation**
  - Kiểm tra video hợp lệ
  - Hiển thị thông tin video
  - Báo lỗi rõ ràng

## 📖 Cách sử dụng mới

### Sử dụng cơ bản (giống cũ)

```bash
cd src
python main_v2.py
```

### Chỉ định input/output

```bash
python main_v2.py path/to/video.mp4 -o path/to/output.mp4
```

### Chọn model nhỏ hơn (nhanh hơn)

```bash
python main_v2.py -m tiny
```

### Resume sau khi bị gián đoạn

```bash
python main_v2.py --resume
```

### Xóa file trung gian sau khi xong

```bash
python main_v2.py --clean
```

### Tắt progress bar

```bash
python main_v2.py --no-progress
```

### Kết hợp nhiều options

```bash
python main_v2.py video.mp4 -o output.mp4 -m small --clean
```

## 🎯 So sánh v1 vs v2

| Tính năng         | v1 (main.py) | v2 (main_v2.py) |
| ----------------- | ------------ | --------------- |
| CLI arguments     | ❌           | ✅              |
| Progress bar      | ❌           | ✅              |
| Checkpoint/Resume | ❌           | ✅              |
| Input validation  | ❌           | ✅              |
| Speed adjustment  | ❌           | ✅              |
| Volume normalize  | ❌           | ✅              |
| Config file       | ❌           | ✅              |
| Error handling    | Cơ bản       | Nâng cao        |
| Ctrl+C safe       | ❌           | ✅              |

## 🔄 Workflow cải tiến

### V1 (main.py):

```
Bắt đầu → Step 1 → Step 2 → ... → Step 6 → Xong
          ↓ Nếu lỗi ở Step 4 → Phải chạy lại từ đầu
```

### V2 (main_v2.py):

```
Bắt đầu → Step 1 ✓ → Step 2 ✓ → Step 3 ✓ → Step 4 ✗ (lỗi)
                                            ↓
          Resume → Step 4 ✓ → Step 5 ✓ → Step 6 ✓ → Xong
```

## 🎨 Tính năng nâng cao có thể thêm sau

### Short-term (dễ làm)

- [ ] Multi-threading cho TTS (xử lý nhiều câu song song)
- [ ] Support nhiều ngôn ngữ output (không chỉ VI)
- [ ] Subtitle embedding vào video
- [ ] Background music preservation
- [ ] Batch processing nhiều video

### Mid-term (cần research)

- [ ] Better TTS model (natural voice)
- [ ] Giảm noise từ audio gốc
- [ ] Auto-detect source language
- [ ] Voice cloning (giữ giọng gốc)
- [ ] GPU acceleration optional

### Long-term (phức tạp)

- [ ] Web UI (Flask/FastAPI + React)
- [ ] Real-time dubbing
- [ ] Lip-sync (sync môi)
- [ ] Multi-speaker detection
- [ ] Cloud processing service

## 💡 Tips sử dụng

1. **Video dài (>30 phút)**: Dùng `--resume` để có thể tạm dừng
2. **Máy yếu**: Dùng `-m tiny` hoặc `-m base`
3. **Chất lượng cao**: Dùng `-m medium` hoặc `-m large`
4. **Tiết kiệm disk**: Dùng `--clean` để xóa file tạm
5. **Debugging**: Không dùng `--clean` để xem file trung gian

## 🐛 Known Issues & Workarounds

### Issue 1: Audio VI ngắn hơn nhiều so với audio EN

**Nguyên nhân**: TTS nói nhanh, hoặc bản dịch ngắn hơn
**Fix**: v2 tự động tăng tốc, nhưng có thể điều chỉnh thêm trong config.py

### Issue 2: Giọng TTS còn máy móc

**Nguyên nhân**: Model TTS VI còn hạn chế
**Workaround**: Có thể thử các TTS service khác (Google TTS, Azure TTS)

### Issue 3: Chất lượng dịch chưa tốt

**Nguyên nhân**: Model dịch còn đơn giản
**Workaround**: Có thể sửa file vi.json thủ công sau bước 3

## 📝 Migration từ v1 sang v2

Nếu đang dùng v1 (main.py):

1. Cài thêm `tqdm`: `pip install tqdm`
2. Chạy v2: `python main_v2.py` thay vì `python main.py`
3. V1 vẫn hoạt động bình thường, không bị ảnh hưởng

## 🙏 Feedback

Nếu gặp bug hoặc có ý tưởng cải tiến, vui lòng tạo issue!
