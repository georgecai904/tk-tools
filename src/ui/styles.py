import streamlit as st

def apply_apple_style():
    """
    注入 Apple Design 风格的 CSS
    """
    st.markdown("""
    <style>
        /* 全局字体 */
        body, .stApp {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
            color: #1d1d1f;
            background-color: #fbfbfd;
        }
        
        /* 标题样式 */
        h1, h2, h3 {
            font-weight: 600;
            letter-spacing: -0.02em;
        }
        
        /* 卡片容器 */
        .apple-card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            margin-bottom: 20px;
            border: 1px solid rgba(0, 0, 0, 0.05);
        }
        
        /* 按钮样式 */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
            border: none;
            padding: 0.5rem 1rem;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            transform: scale(1.02);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* 输入框样式 */
        .stTextInput > div > div > input, .stTextArea > div > div > textarea {
            border-radius: 8px;
            border: 1px solid #d2d2d7;
            background-color: #ffffff;
        }
        
        .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
            border-color: #0071e3;
            box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.1);
        }
        
        /* 侧边栏样式 */
        section[data-testid="stSidebar"] {
            background-color: #f5f5f7;
            border-right: 1px solid rgba(0, 0, 0, 0.05);
        }
        
        /* 状态消息 */
        .stSuccess, .stInfo, .stWarning, .stError {
            border-radius: 10px;
            border: none;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }
    </style>
    """, unsafe_allow_html=True)
