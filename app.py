import streamlit as st
import fitz  # PyMuPDF
import re
import os
import pytesseract
from PIL import Image
import io
import zipfile

# 设置页面配置
st.set_page_config(page_title="PDF 拆分工具", layout="wide")

st.title("📄 PDF 订单拆分工具")
st.markdown("""
此工具用于根据 Tracking Number 将多页 PDF 拆分为单独的文件。
如果页面文本无法提取，会自动尝试 OCR 识别。
""")

# =========================
# 侧边栏：配置输入
# =========================
st.sidebar.header("1. 上传 PDF")
uploaded_file = st.sidebar.file_uploader("选择 PDF 文件", type=["pdf"])

st.sidebar.header("2. 输入名称列表")
default_name_list = """577241585786458605-7712-VEXON 4.5QT Black
577241751138636673-9327-BOSWELL 7.5QT White
577241894323721207-9358-VEXON 4.5QT Black
577241969624059925-9365-VEXON 4.5QT Black
577241992699614087-9372-VEXON 4.5QT Black
577242007482569246-9334-BOSWELL 7.5QT Black
577242026569666765-9341-BOSWELL 7.5QT Black"""

name_list_text = st.sidebar.text_area(
    "粘贴名称列表 (每行一个)", 
    value=default_name_list,
    height=300,
    help="格式通常为: ID-Suffix-Product，程序将提取 Suffix (4位数字) 进行匹配。"
)

# =========================
# 核心逻辑函数
# =========================

def extract_tracking(text: str):
    """提取 USPS Tracking Number"""
    # 匹配连续的数字，中间可能包含空格或换行
    matches = re.findall(r"(?:\d[\s]*){20,34}", text)
    if not matches:
        return None
    
    for match in matches:
        clean_match = re.sub(r"\s+", "", match)
        if 20 <= len(clean_match) <= 34:
            return clean_match
    return None

def ocr_page(page):
    """对 PDF 页面进行 OCR"""
    try:
        pix = page.get_pixmap(dpi=300)
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        # 这里不抛出异常，而是返回 None，让调用者处理
        return None

def safe_filename(name: str):
    return re.sub(r'[\\/:*?"<>|]', "_", name)

def process_pdf(pdf_file, name_list):
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
            # 尝试提取中间部分作为 suffix，原代码逻辑是 parts[1]
            tracking_suffix_map[suffix] = line
    
    # 打开 PDF
    try:
        # file_uploader 返回的是 BytesIO，PyMuPDF 可以直接打开
        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        st.error(f"无法打开 PDF 文件: {e}")
        return None, []

    total_pages = doc.page_count
    
    # 检查页数匹配
    if total_pages != valid_lines_count:
        st.warning(f"⚠️ PDF 页数 ({total_pages}) 与 名称列表行数 ({valid_lines_count}) 不一致，请仔细检查！")

    processed_files = [] # List of (filename, pdf_bytes)
    logs = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, page in enumerate(doc):
        # 更新进度
        progress = (i + 1) / total_pages
        progress_bar.progress(progress)
        status_text.text(f"正在处理第 {i+1}/{total_pages} 页...")

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
    
    status_text.text("处理完成！")
    return processed_files, logs

# =========================
# 主界面操作
# =========================

if uploaded_file and name_list_text:
    if st.button("开始拆分"):
        with st.spinner("正在处理..."):
            # 重置文件指针，以防多次点击
            uploaded_file.seek(0)
            results, logs = process_pdf(uploaded_file, name_list_text)
            
            if results:
                # 显示日志
                with st.expander("查看处理日志", expanded=True):
                    for log in logs:
                        if "❌" in log:
                            st.error(log)
                        elif "⚠️" in log:
                            st.warning(log)
                        else:
                            st.success(log)
                
                # 创建 ZIP 文件
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for fname, data in results:
                        zf.writestr(fname, data)
                
                st.success(f"🎉 成功拆分 {len(results)} 个文件！")
                
                # 下载按钮
                st.download_button(
                    label="⬇️ 下载所有文件 (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="split_orders.zip",
                    mime="application/zip"
                )
else:
    st.info("👋 请在左侧上传 PDF 文件并输入名称列表以开始。")
