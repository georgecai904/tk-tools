import streamlit as st
from src.core.tk_label_split_by_tracking import process_pdf, create_zip
from src.ui.components import card_container, section_header, success_message, error_message
import tempfile
import os

def render():
    st.title("📄 TK面单PDF拆分工具")
    st.markdown("根据 Tracking Number 将批量 PDF 订单拆分为单独的文件。")
    
    # 1. Input Section
    def input_section():
        section_header("1. 上传与配置", "上传 PDF 文件并提供订单列表。")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            uploaded_file = st.file_uploader("上传 PDF", type=["pdf"])
            
        with col2:
            default_name_list = """577241585786458605-7712-VEXON 4.5QT Black
577241751138636673-9327-BOSWELL 7.5QT White
577241894323721207-9358-VEXON 4.5QT Black
577241969624059925-9365-VEXON 4.5QT Black
577241992699614087-9372-VEXON 4.5QT Black
577242007482569246-9334-BOSWELL 7.5QT Black
577242026569666765-9341-BOSWELL 7.5QT Black"""
            name_list_text = st.text_area(
                "订单列表 (ID-Suffix-Product)", 
                value=default_name_list,
                height=200,
                help="格式：ID-Suffix-Product。程序将提取 Suffix（4位数字）进行匹配。"
            )
            
        return uploaded_file, name_list_text

    # 使用容器包裹输入部分
    uploaded_file, name_list_text = input_section()
    # card_container(lambda: input_section()) # Streamlit columns don't nest well inside markdown divs sometimes, simplified structure

    if uploaded_file and name_list_text:
        st.markdown("---")
        section_header("2. 处理与下载")
        
        if st.button("开始拆分", type="primary", use_container_width=True):
            try:
                # Progress elements
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(p, msg):
                    progress_bar.progress(p)
                    status_text.text(msg)
                
                # 重置指针
                uploaded_file.seek(0)
                
                # 处理
                results, logs = process_pdf(uploaded_file, name_list_text, update_progress)
                
                status_text.text("处理完成！")
                
                # Display Logs
                with st.expander("查看处理日志", expanded=True):
                    for log in logs:
                        if "❌" in log:
                            st.error(log)
                        elif "⚠️" in log:
                            st.warning(log)
                        else:
                            st.success(log)
                            
                # Download
                if results:
                    zip_data = create_zip(results)
                    st.success(f"🎉 成功拆分 {len(results)} 个文件！")
                    st.download_button(
                        label="⬇️ 下载所有文件 (ZIP)",
                        data=zip_data,
                        file_name="split_orders.zip",
                        mime="application/zip",
                        type="primary"
                    )
                    
            except Exception as e:
                st.error(f"发生错误: {str(e)}")
