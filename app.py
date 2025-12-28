import streamlit as st
from src.ui.styles import apply_apple_style
from src.ui.views import tk_label_split_by_tracking, tk_orders_transfer, changelog
from src.core.version_control import get_current_version

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
            "PDF 拆分工具": "tk_label_split_by_tracking",
            "订单 CSV 转换": "tk_orders_transfer",
            "更新日志": "changelog",
        }
        
        selection = st.radio(
            "选择工具", 
            list(menu_options.keys()),
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.caption(f"© 2025 TK 工具箱 v{get_current_version()}")

    # 路由分发
    if selection == "PDF 拆分工具":
        tk_label_split_by_tracking.render()
    elif selection == "订单 CSV 转换":
        tk_orders_transfer.render()
    elif selection == "更新日志":
        changelog.render()

    # elif selection == "Label Generator":
    #     label_generator.render()

if __name__ == "__main__":
    main()
