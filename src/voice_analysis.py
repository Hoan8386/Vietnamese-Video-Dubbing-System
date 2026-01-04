"""
Voice Analysis Module
Phân tích giọng nói để detect gender và emotion
"""
import librosa
import numpy as np
import json


def analyze_audio_segment(audio_path, start_time, end_time, sr=16000):
    """
    Phân tích một segment audio để detect gender và emotion
    
    Args:
        audio_path: Đường dẫn file audio
        start_time: Thời gian bắt đầu (giây)
        end_time: Thời gian kết thúc (giây)
        sr: Sample rate
    
    Returns:
        dict với gender và emotion info
    """
    try:
        # Load audio segment
        y, sr = librosa.load(audio_path, sr=sr, offset=start_time, duration=end_time-start_time)
        
        if len(y) == 0:
            return {"gender": "female", "emotion": "neutral", "pitch_avg": 180}
        
        # 1. Phân tích pitch để detect gender
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=50, fmax=400)
        
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        if len(pitch_values) > 0:
            avg_pitch = np.mean(pitch_values)
            pitch_std = np.std(pitch_values)
        else:
            avg_pitch = 180
            pitch_std = 20
        
        # Gender classification
        # Male: 85-180 Hz, Female: 165-255 Hz
        if avg_pitch < 165:
            gender = "male"
        elif avg_pitch > 200:
            gender = "female"
        else:
            # Ambiguous range, dùng pitch variance
            gender = "male" if pitch_std < 25 else "female"
        
        # 2. Phân tích emotion
        # Energy (volume)
        rms = librosa.feature.rms(y=y)[0]
        energy = np.mean(rms)
        
        # Speech rate (zero crossing)
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        speech_rate = np.mean(zcr)
        
        # Emotion classification (simple)
        if energy > 0.05 and pitch_std > 30:
            emotion = "excited"
            rate_adjust = "+15%"
        elif energy < 0.02 and pitch_std < 15:
            emotion = "calm"
            rate_adjust = "-10%"
        elif speech_rate > 0.15:
            emotion = "urgent"
            rate_adjust = "+20%"
        else:
            emotion = "neutral"
            rate_adjust = "0%"
        
        return {
            "gender": gender,
            "emotion": emotion,
            "pitch_avg": float(avg_pitch),
            "pitch_std": float(pitch_std),
            "energy": float(energy),
            "speech_rate": float(speech_rate),
            "rate_adjust": rate_adjust
        }
        
    except Exception as e:
        print(f"  ⚠️ Lỗi phân tích voice: {e}")
        return {"gender": "female", "emotion": "neutral", "pitch_avg": 180, "rate_adjust": "0%"}


def analyze_all_segments(audio_path, segments_json):
    """
    Phân tích tất cả segments và thêm voice info vào JSON
    
    Args:
        audio_path: Đường dẫn audio gốc
        segments_json: Đường dẫn file JSON chứa segments
    """
    print("🎤 Đang phân tích giọng nói (gender & emotion)...")
    
    try:
        # Load segments
        with open(segments_json, encoding="utf-8") as f:
            segments = json.load(f)
        
        # Phân tích từng segment
        for i, seg in enumerate(segments):
            analysis = analyze_audio_segment(
                audio_path,
                seg["start"],
                seg["end"]
            )
            
            # Thêm thông tin vào segment
            seg["voice_gender"] = analysis["gender"]
            seg["voice_emotion"] = analysis["emotion"]
            seg["voice_pitch"] = analysis["pitch_avg"]
            seg["tts_rate_adjust"] = analysis["rate_adjust"]
            
            print(f"  [{i+1}/{len(segments)}] {seg['voice_gender'].upper()} | "
                  f"Emotion: {seg['voice_emotion']} | "
                  f"Pitch: {seg['voice_pitch']:.0f}Hz")
        
        # Lưu lại
        with open(segments_json, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Phân tích hoàn tất. Thông tin lưu tại: {segments_json}")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi phân tích voice: {e}")
        return False


if __name__ == "__main__":
    # Test
    analyze_all_segments("../audio/original.wav", "../subtitles/en.json")
