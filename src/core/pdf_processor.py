import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import zipfile
from typing import List, Tuple, Dict, Callable
from .utils import extract_tracking, safe_filename

def ocr_page(page) -> str | None:
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
        # 这里不抛出异常，而是返回 None，让调用者处理
        return None

def process_pdf(pdf_file, name_list: str, progress_callback: Callable[[float, str], None] = None) -> Tuple[List[Tuple[str, bytes]], List[str]]:
    """
    核心业务逻辑：处理 PDF 拆分
    """
    # 解析 Name List
    tracking_suffix_map = {}
    lines = name_list.strip().split('\n')
    valid_lines_count = 0
    for line in lines:
        line = line.strip()
        if not line: continue
        valid_lines_count += 1
        parts = line.split('-')
        if len(parts) >= 2:
            suffix = parts[1].strip()
            tracking_suffix_map[suffix] = line
    
    # 打开 PDF
    try:
        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        raise Exception(f"无法打开 PDF 文件: {e}")

    total_pages = doc.page_count
    
    # 检查页数匹配 (作为日志返回，不中断)
    logs = []
    if total_pages != valid_lines_count:
        logs.append(f"⚠️ PDF 页数 ({total_pages}) 与 名称列表行数 ({valid_lines_count}) 不一致，请仔细检查！")

    processed_files = [] # List of (filename, pdf_bytes)
    
    for i, page in enumerate(doc):
        # 更新进度
        if progress_callback:
            progress = (i + 1) / total_pages
            progress_callback(progress, f"正在处理第 {i+1}/{total_pages} 页...")

        page_text = page.get_text()
        tracking = extract_tracking(page_text)
        
        ocr_used = False
        if not tracking:
            ocr_used = True
            # 尝试 OCR
            ocr_text = ocr_page(page)
            if ocr_text:
                tracking = extract_tracking(ocr_text)
        
        filename = ""
        
        if not tracking:
            filename = f"UNKNOWN_TRACKING-Page{i+1}.pdf"
            logs.append(f"Page {i+1}: ❌ 未识别 Tracking (OCR used: {ocr_used})")
        else:
            tracking_suffix = tracking[-4:]
            if tracking_suffix in tracking_suffix_map:
                target_name = tracking_suffix_map[tracking_suffix]
                filename = f"{target_name}.pdf"
                logs.append(f"Page {i+1}: ✅ 匹配成功 {tracking_suffix} -> {target_name}")
            else:
                filename = f"UNMATCHED-{tracking_suffix}-Page{i+1}.pdf"
                logs.append(f"Page {i+1}: ⚠️ 未匹配 Suffix: {tracking_suffix}")

        filename = safe_filename(filename)
        
        # 保存单页 PDF 到内存
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=i, to_page=i)
        
        out_buffer = io.BytesIO()
        new_doc.save(out_buffer)
        new_doc.close()
        
        processed_files.append((filename, out_buffer.getvalue()))
    
    return processed_files, logs

def create_zip(files: List[Tuple[str, bytes]]) -> bytes:
    """
    将文件列表打包成 ZIP
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for fname, data in files:
            zf.writestr(fname, data)
    return zip_buffer.getvalue()
