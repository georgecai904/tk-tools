import re

def safe_filename(name: str) -> str:
    """
    清理文件名中的非法字符
    """
    return re.sub(r'[\\/:*?"<>|]', "_", name)

def extract_tracking(text: str) -> str | None:
    """
    提取 USPS Tracking Number（20~30 位，允许中间有空格）
    """
    # 匹配连续的数字，中间可能包含空格或换行
    matches = re.findall(r"(?:\d[\s]*){20,34}", text)
    if not matches:
        return None
    
    # 清理空格并验证长度
    for match in matches:
        clean_match = re.sub(r"\s+", "", match)
        if 20 <= len(clean_match) <= 34:
            return clean_match
            
    return None
