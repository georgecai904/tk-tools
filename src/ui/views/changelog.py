import streamlit as st
from src.core.version_control import get_changelog, get_current_version
from src.ui.components import section_header

def render():
    st.title(f"📅 更新日志 (v{get_current_version()})")
    st.markdown("记录 TK 工具箱的版本更新与功能改进。")
    
    history = get_changelog()
    
    for item in history:
        st.markdown("---")
        
        # 标题行 (保持原生 Streamlit 布局)
        c1, c2 = st.columns([3, 1])
        with c1:
            st.subheader(f"v{item['version']} - {item['title']}")
        with c2:
            st.caption(f"发布日期: {item['date']}")
        
        # 内容卡片 (构建 HTML 字符串以确保样式正确应用)
        changes_html = ""
        for change in item['changes']:
            changes_html += f"<li style='margin-bottom: 8px;'>{change}</li>"
            
        card_html = f"""
        <div class="apple-card">
            <ul style="margin: 0; padding-left: 20px;">
                {changes_html}
            </ul>
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)
