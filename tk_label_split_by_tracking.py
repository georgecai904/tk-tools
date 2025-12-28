import fitz  # PyMuPDF
import re
import os
import pytesseract
from PIL import Image
import io

# =========================
# 1. 配置区（你只需要改这里）
# =========================

PDF_PATH = "/Users/georgec/Desktop/11.pdf"          # 原始多页 PDF
OUTPUT_DIR = "/Users/georgec/Desktop/Orders/Output"     # 拆分后保存的文件夹

NAME_LIST = [
"577241585786458605-7712-VEXON 4.5QT Black",
"577241751138636673-9327-BOSWELL 7.5QT White",
"577241894323721207-9358-VEXON 4.5QT Black",
"577241969624059925-9365-VEXON 4.5QT Black",
"577241992699614087-9372-VEXON 4.5QT Black",
"577242007482569246-9334-BOSWELL 7.5QT Black",
"577242026569666765-9341-BOSWELL 7.5QT Black",
]

# 预处理 NAME_LIST，建立 后四位 -> 完整名称 的映射
TRACKING_SUFFIX_MAP = {}
for name in NAME_LIST:
    # 假设格式为：ID-Suffix-Product
    parts = name.split('-')
    if len(parts) >= 2:
        suffix = parts[1].strip()
        TRACKING_SUFFIX_MAP[suffix] = name

# =========================
# 2. 工具函数
# =========================

def extract_tracking(text: str):
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

def ocr_page(page):
    """
    对 PDF 页面进行 OCR，返回识别到的文本
    """
    try:
        # 将页面转换为图像 (DPI 300 以保证清晰度)
        pix = page.get_pixmap(dpi=300)
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))
        
        # 使用 tesseract 进行 OCR
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"OCR 失败: {e}")
        return ""

def safe_filename(name: str):
    """
    清理文件名中的非法字符
    """
    return re.sub(r'[\\/:*?"<>|]', "_", name)

# =========================
# 3. 主逻辑
# =========================

doc = fitz.open(PDF_PATH)

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

if doc.page_count != len(NAME_LIST):
    print("⚠️ 警告：PDF 页数 与 名称数量不一致")
    print(f"PDF 页数: {doc.page_count}, 名称数量: {len(NAME_LIST)}")

print(f"📄 开始处理 PDF，共 {doc.page_count} 页\n")

for i, page in enumerate(doc):
    page_text = page.get_text()
    tracking = extract_tracking(page_text)

    # 如果直接提取失败，尝试 OCR
    if not tracking:
        print(f"⚠️ 第 {i+1} 页文本层提取失败，正在尝试 OCR 识别...")
        ocr_text = ocr_page(page)
        tracking = extract_tracking(ocr_text)

    if not tracking:
        filename = f"UNKNOWN_TRACKING-Page{i+1}.pdf"
    else:
        # 只保留后四位
        tracking_suffix = tracking[-4:]
        
        # 查找匹配的名称
        if tracking_suffix in TRACKING_SUFFIX_MAP:
            target_name = TRACKING_SUFFIX_MAP[tracking_suffix]
            filename = f"{target_name}.pdf"
        else:
            filename = f"UNMATCHED-{tracking_suffix}-Page{i+1}.pdf"
            print(f"⚠️ 警告：追踪号后四位 {tracking_suffix} 未在列表中找到匹配项")

    # 生成文件名
    filename = safe_filename(filename)
    output_path = os.path.join(OUTPUT_DIR, filename)

    # 拆分并保存单页 PDF
    new_doc = fitz.open()
    new_doc.insert_pdf(doc, from_page=i, to_page=i)
    new_doc.save(output_path)
    new_doc.close()

    print(f"✅ 第 {i+1} 页已保存：{filename}")

print("\n🎉 全部 PDF 已成功拆分并保存完成！")
