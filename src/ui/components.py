import streamlit as st

def card_container(content_func):
    """
    创建一个带有 Apple 风格的卡片容器
    """
    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
    content_func()
    st.markdown('</div>', unsafe_allow_html=True)

def section_header(title: str, subtitle: str = None):
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)

def success_message(message: str):
    st.success(message, icon="✅")

def error_message(message: str):
    st.error(message, icon="⚠️")
