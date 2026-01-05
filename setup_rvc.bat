@echo off
REM ========================================
REM Setup Script cho RVC Voice Cloning
REM Tối ưu cho RTX 3050 4GB
REM ========================================

echo ========================================
echo    RVC VOICE CLONING SETUP
echo    Tối ưu cho RTX 3050 4GB
echo ========================================
echo.

REM Check Python
echo [1/7] Kiểm tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python chưa được cài đặt!
    echo 📥 Download Python từ: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python đã cài đặt

REM Check CUDA
echo.
echo [2/7] Kiểm tra CUDA...
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo ⚠️  NVIDIA GPU không phát hiện hoặc driver chưa cài
    echo 📥 Download CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
    set USE_CPU=1
) else (
    echo ✅ NVIDIA GPU phát hiện
    nvidia-smi
    set USE_CPU=0
)

REM Install PyTorch
echo.
echo [3/7] Cài đặt PyTorch...
if %USE_CPU%==1 (
    echo 📦 Cài đặt PyTorch CPU version...
    pip install torch torchvision torchaudio
) else (
    echo 📦 Cài đặt PyTorch CUDA 11.7 (cho RTX 30xx)...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
)

REM Install dependencies
echo.
echo [4/7] Cài đặt dependencies chính...
pip install -r requirements.txt

REM Clone RVC
echo.
echo [5/7] Clone RVC repository...
if not exist "Retrieval-based-Voice-Conversion-WebUI" (
    echo 📥 Cloning RVC...
    git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
    echo ✅ RVC cloned
) else (
    echo ✅ RVC đã tồn tại
)

REM Install RVC dependencies
echo.
echo [6/7] Cài đặt RVC dependencies...
cd Retrieval-based-Voice-Conversion-WebUI
pip install -r requirements.txt
cd ..

REM Download models
echo.
echo [7/7] Download pre-trained models...
echo.
echo ⚠️  Cần download các models sau MANUALLY:
echo.
echo 1. Hubert Base Model:
echo    URL: https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/hubert_base.pt
echo    Lưu vào: Retrieval-based-Voice-Conversion-WebUI\assets\hubert\hubert_base.pt
echo.
echo 2. RMVPE Model:
echo    URL: https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rmvpe.pt
echo    Lưu vào: Retrieval-based-Voice-Conversion-WebUI\rmvpe.pt
echo.
echo 3. Pre-trained V2 Models (Optional):
echo    D40k.pth: https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/pretrained_v2/D40k.pth
echo    G40k.pth: https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/pretrained_v2/G40k.pth
echo    Lưu vào: Retrieval-based-Voice-Conversion-WebUI\assets\pretrained_v2\
echo.

REM Create directories
echo 📁 Tạo thư mục cần thiết...
if not exist "Retrieval-based-Voice-Conversion-WebUI\assets\hubert" mkdir "Retrieval-based-Voice-Conversion-WebUI\assets\hubert"
if not exist "Retrieval-based-Voice-Conversion-WebUI\assets\pretrained_v2" mkdir "Retrieval-based-Voice-Conversion-WebUI\assets\pretrained_v2"
if not exist "Retrieval-based-Voice-Conversion-WebUI\logs" mkdir "Retrieval-based-Voice-Conversion-WebUI\logs"
if not exist "Retrieval-based-Voice-Conversion-WebUI\weights" mkdir "Retrieval-based-Voice-Conversion-WebUI\weights"

REM Test installation
echo.
echo 🧪 Testing installation...
python src\voice_cloning_rvc.py

echo.
echo ========================================
echo ✅ SETUP HOÀN TẤT!
echo ========================================
echo.
echo 📖 Đọc hướng dẫn chi tiết: INSTALL_RVC.md
echo.
echo 🎯 Các bước tiếp theo:
echo    1. Download models (xem danh sách ở trên)
echo    2. Train model hoặc sử dụng pretrained
echo    3. Chạy: python src\main_rvc.py
echo.
echo 💡 Test RVC:
echo    python src\voice_cloning_rvc.py
echo.

pause
