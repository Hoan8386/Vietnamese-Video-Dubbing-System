"""
Text Cleaning Utilities
Loại bỏ URLs, ký tự đặc biệt, và clean text trước khi TTS
"""
import re


def clean_text_for_tts(text):
    """
    Clean text trước khi gửi vào TTS
    Loại bỏ URLs, email, ký tự đặc biệt
    
    Args:
        text: Text cần clean
    
    Returns:
        Cleaned text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # 1. Loại bỏ URLs (http://, https://, www.)
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),])+', '', text)
    
    # 2. Loại bỏ email
    text = re.sub(r'\S+@\S+', '', text)
    
    # 3. Loại bỏ HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # 4. Loại bỏ markdown links [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # 5. Loại bỏ ký tự đặc biệt nhưng giữ dấu câu tiếng Việt
    # Giữ: a-z, A-Z, 0-9, tiếng Việt, dấu câu cơ bản
    text = re.sub(r'[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ.,!?;:\'"()-]', ' ', text)
    
    # 6. Loại bỏ nhiều spaces liên tiếp
    text = re.sub(r'\s+', ' ', text)
    
    # 7. Trim
    text = text.strip()
    
    return text


def validate_text(text, max_length=500):
    """
    Validate text trước khi TTS
    
    Args:
        text: Text cần validate
        max_length: Độ dài tối đa
    
    Returns:
        (is_valid, cleaned_text, warning_message)
    """
    if not text or not isinstance(text, str):
        return False, "", "Text rỗng hoặc không hợp lệ"
    
    # Clean text
    cleaned = clean_text_for_tts(text)
    
    # Check if empty after cleaning
    if not cleaned:
        return False, "", "Text rỗng sau khi clean"
    
    # Check length
    if len(cleaned) > max_length:
        return True, cleaned[:max_length], f"Text quá dài, cắt xuống {max_length} ký tự"
    
    # Check if too short (might be noise)
    if len(cleaned) < 3:
        return False, cleaned, "Text quá ngắn (< 3 ký tự)"
    
    return True, cleaned, None


if __name__ == "__main__":
    # Test
    test_texts = [
        "Xem thêm tại http://cwcw.org/example",
        "Email me at test@example.com",
        "Visit <a href='url'>this link</a>",
        "[Click here](http://example.com)",
        "Normal Vietnamese text: Xin chào, đây là văn bản tiếng Việt.",
        "Text with special chars: @#$%^&*()",
    ]
    
    for text in test_texts:
        print(f"Original: {text}")
        cleaned = clean_text_for_tts(text)
        print(f"Cleaned:  {cleaned}")
        print()
