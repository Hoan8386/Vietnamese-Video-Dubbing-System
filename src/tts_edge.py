"""
Text-to-Speech Vietnamese module
Sử dụng Edge TTS (free, không cần GPU)

Author: Tool Lồng Tiếng
Date: 2026-01-05
"""

import os
import asyncio
import edge_tts
from pathlib import Path
from tqdm import tqdm


# Giọng tiếng Việt tốt nhất từ Edge TTS
VIETNAMESE_VOICES = {
    'male': 'vi-VN-NamMinhNeural',      # Nam, tự nhiên
    'female': 'vi-VN-HoaiMyNeural',     # Nữ, tự nhiên
}

DEFAULT_VOICE = VIETNAMESE_VOICES['female']
DEFAULT_RATE = '+0%'  # Tốc độ nói (có thể điều chỉnh: -50% đến +100%)
DEFAULT_PITCH = '+0Hz'  # Cao độ (có thể điều chỉnh)


async def generate_tts_async(text: str, output_path: str, voice: str = DEFAULT_VOICE, rate: str = DEFAULT_RATE):
    """
    Generate TTS audio async
    
    Args:
        text: Text to convert
        output_path: Output audio file path
        voice: Voice name
        rate: Speaking rate
    """
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)


def generate_tts(text: str, output_path: str, voice: str = DEFAULT_VOICE, rate: str = DEFAULT_RATE):
    """
    Generate TTS audio (sync wrapper)
    
    Args:
        text: Text to convert
        output_path: Output audio file path  
        voice: Voice name
        rate: Speaking rate
    """
    asyncio.run(generate_tts_async(text, output_path, voice, rate))


def tts_segments(
    segments: list,
    output_dir: str,
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_RATE,
    **kwargs
) -> list:
    """
    Generate TTS for multiple segments
    
    Args:
        segments: List of segments với 'text' và 'start', 'end'
        output_dir: Directory to save audio files
        voice: Voice name
        rate: Speaking rate
        **kwargs: Additional arguments (ignored for compatibility)
        
    Returns:
        list: List of generated audio file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    
    audio_files = []
    
    print(f"🗣️  Generating TTS for {len(segments)} segments...")
    print(f"🎙️  Voice: {voice}")
    
    for i, segment in enumerate(tqdm(segments, desc="TTS")):
        text = segment.get('text', '')
        
        if not text.strip():
            print(f"⚠️ Segment {i+1} is empty, skipping")
            continue
        
        # Output filename
        output_file = os.path.join(output_dir, f"segment_{i+1:04d}.wav")
        
        try:
            # Generate TTS
            generate_tts(text, output_file, voice, rate)
            audio_files.append(output_file)
            
        except Exception as e:
            print(f"❌ Error generating TTS for segment {i+1}: {e}")
            continue
    
    print(f"✅ Generated {len(audio_files)}/{len(segments)} TTS files")
    
    return audio_files


def list_available_voices():
    """List all available Edge TTS voices"""
    async def list_voices_async():
        voices = await edge_tts.list_voices()
        
        # Filter Vietnamese voices
        vi_voices = [v for v in voices if v['Locale'].startswith('vi-')]
        
        print("\n🎙️ Available Vietnamese Voices:")
        print("=" * 70)
        for voice in vi_voices:
            gender = voice.get('Gender', 'Unknown')
            name = voice.get('ShortName', '')
            locale = voice.get('Locale', '')
            print(f"  {name}")
            print(f"    Gender: {gender}")
            print(f"    Locale: {locale}")
            print()
        
        return vi_voices
    
    return asyncio.run(list_voices_async())


# Alias for compatibility with old code
tts_openvoice_segments = tts_segments


if __name__ == "__main__":
    # Test
    print("Testing Edge TTS...")
    
    # List voices
    list_available_voices()
    
    # Test TTS
    test_segments = [
        {'text': 'Xin chào, đây là bài kiểm tra TTS tiếng Việt.', 'start': 0, 'end': 3},
        {'text': 'Công nghệ Edge TTS hoạt động rất tốt.', 'start': 3, 'end': 6},
    ]
    
    output_dir = "test_tts_output"
    files = tts_segments(test_segments, output_dir)
    
    print(f"\n✅ Generated {len(files)} files in {output_dir}/")
