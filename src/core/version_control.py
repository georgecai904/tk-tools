
CURRENT_VERSION = "1.2"

CHANGELOG_HISTORY = [
    {
        "version": "1.2",
        "date": "2025-12-28",
        "title": "CSV 订单转换与数据库集成",
        "changes": [
            "✨ 新增 CSV 订单转换工具，支持将 TK 订单转换为发货格式",
            "🗄️ 集成 SQLite 数据库，实现 SKU 映射关系的持久化存储",
            "🛠️ 优化项目结构，重构核心逻辑与 UI 分离",
            "🔄 PDF 拆分工具模块重命名与路径优化"
        ]
    },
    {
        "version": "1.1",
        "date": "2025-12-28",
        "title": "PDF 拆分工具与 UI 升级",
        "changes": [
            "✨ 发布 PDF 拆分工具 (Web 版)",
            "🎨 引入 Apple Design 设计风格 (圆角卡片、模糊背景)",
            "🌐 全面中文化界面",
            "⚡️ 优化 Streamlit 配置，提升启动速度"
        ]
    },
    {
        "version": "1.0",
        "date": "2025-12-27",
        "title": "项目初始化",
        "changes": [
            "🚀 建立基础 Streamlit 应用框架",
            "🔧 配置 Python 虚拟环境与依赖管理"
        ]
    }
]

def get_current_version():
    return CURRENT_VERSION

def get_changelog():
    return CHANGELOG_HISTORY
