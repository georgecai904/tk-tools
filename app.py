import streamlit as st
from src.ui.styles import apply_apple_style
from src.ui.views import pdf_splitter

# 设置页面配置 (必须是第一个 Streamlit 命令)
st.set_page_config(
    page_title="TK Tools", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入样式
apply_apple_style()

def main():
    # 侧边栏导航
    with st.sidebar:
        st.title("TK 工具箱")
        st.markdown("---")
        
        # 导航菜单
        menu_options = {
            "PDF 拆分工具": "pdf_splitter",
            # 未来可以在这里添加更多工具
            # "Label Generator": "label_generator",
        }
        
        selection = st.radio(
            "选择工具", 
            list(menu_options.keys()),
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.caption("© 2025 TK 工具箱")

    # 路由分发
    if selection == "PDF 拆分工具":
        pdf_splitter.render()
    # elif selection == "Label Generator":
    #     label_generator.render()

if __name__ == "__main__":
    main()
