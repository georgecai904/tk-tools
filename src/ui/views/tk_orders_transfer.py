import streamlit as st
import pandas as pd
from src.core.tk_orders_transfer import process_csv
from src.ui.components import section_header
from src.core.db_manager import get_all_skus, add_sku, delete_sku

def render():
    st.title("🔄 订单 CSV 转换工具")
    st.markdown("将 TK 平台的原始订单导出 CSV 转换为标准发货格式。")

    # 1. SKU 管理
    section_header("1. SKU 映射管理", "管理 SKU ID 与产品名称的对应关系。")
    
    with st.expander("📦 管理 SKU 映射表", expanded=False):
        # 添加新 SKU
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            new_sku_id = st.text_input("SKU ID", placeholder="输入 SKU ID")
        with c2:
            new_product_name = st.text_input("产品名称", placeholder="输入对应产品名称")
        with c3:
            st.write("") # Spacer
            st.write("") # Spacer
            if st.button("添加", use_container_width=True):
                if new_sku_id and new_product_name:
                    success, msg = add_sku(new_sku_id, new_product_name)
                    if success:
                        st.success("添加成功！")
                        st.rerun()
                    else:
                        st.error(f"添加失败: {msg}")
                else:
                    st.warning("请填写完整信息。")

        # 展示现有 SKU
        skus = get_all_skus()
        if skus:
            # 转换为 DataFrame 展示
            df_skus = pd.DataFrame(skus, columns=["id", "sku_id", "product_name", "created_at"])
            df_display = df_skus[["sku_id", "product_name", "created_at"]]
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # 删除功能
            sku_to_delete = st.selectbox("选择要删除的 SKU", df_skus["sku_id"].tolist(), index=None, placeholder="选择 SKU ID 删除...")
            if sku_to_delete:
                if st.button("🗑️ 确认删除", type="secondary"):
                    success, msg = delete_sku(sku_to_delete)
                    if success:
                        st.success("删除成功！")
                        st.rerun()
                    else:
                        st.error(f"删除失败: {msg}")
        else:
            st.info("暂无 SKU 映射数据，请添加。")

    # 2. 上传与转换
    st.markdown("---")
    section_header("2. 订单转换", "上传原始 CSV 进行转换。")
    
    uploaded_file = st.file_uploader("上传订单 CSV", type=["csv"])

    if uploaded_file:
        if st.button("开始转换", type="primary", use_container_width=True):
            try:
                # 重置指针
                uploaded_file.seek(0)
                
                # 处理 (无需传入 text，内部直接读取 DB)
                df_result = process_csv(uploaded_file)
                
                st.success(f"✅ 转换成功！共处理 {len(df_result)} 行数据。")
                
                # 预览前 5 行
                st.caption("数据预览 (前 5 行):")
                st.dataframe(df_result.head())
                
                # 下载按钮
                csv_data = df_result.to_csv(index=False, encoding="utf-8-sig")
                st.download_button(
                    label="⬇️ 下载转换后的 CSV",
                    data=csv_data,
                    file_name="converted_orders.csv",
                    mime="text/csv",
                    type="primary"
                )
                
            except Exception as e:
                st.error(f"转换失败: {str(e)}")
