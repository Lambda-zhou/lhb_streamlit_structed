import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import pickle
from datetime import datetime

def show_history_panel(data_persistence):
    """显示历史记录面板"""
    st.header("📚 操作历史记录")
    
    history = data_persistence.load_operation_history()
    
    if not history:
        st.info("暂无历史记录")
        return
    
    # 操作统计
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总操作数", len(history))
    with col2:
        operation_types = [entry.get("operation_type", "unknown") for entry in history]
        unique_types = len(set(operation_types))
        st.metric("操作类型", unique_types)
    with col3:
        recent_operations = len([h for h in history if 
                               (datetime.now() - datetime.fromisoformat(h["timestamp"])).days < 1])
        st.metric("今日操作", recent_operations)
    with col4:
        if st.button("清空历史记录", type="secondary"):
            if data_persistence.clear_history():
                st.success("历史记录已清空")
                st.rerun()
            else:
                st.error("清空历史记录失败")
    
    # 筛选选项
    st.subheader("筛选历史记录")
    col1, col2 = st.columns(2)
    
    with col1:
        operation_filter = st.selectbox(
            "按操作类型筛选",
            ["全部"] + list(set(operation_types)),
            index=0
        )
    
    with col2:
        days_filter = st.selectbox(
            "按时间筛选",
            ["全部", "今天", "最近3天", "最近7天", "最近30天"],
            index=0
        )
    
    # 应用筛选
    filtered_history = history.copy()
    
    if operation_filter != "全部":
        filtered_history = [h for h in filtered_history if h.get("operation_type") == operation_filter]
    
    if days_filter != "全部":
        days_map = {"今天": 1, "最近3天": 3, "最近7天": 7, "最近30天": 30}
        days = days_map[days_filter]
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        filtered_history = [h for h in filtered_history if 
                          datetime.fromisoformat(h["timestamp"]) >= cutoff_date]
    
    # 显示历史记录
    st.subheader(f"历史记录 ({len(filtered_history)} 条)")
    
    for i, entry in enumerate(reversed(filtered_history[-50:])):  # 显示最近50条
        operation_type = entry.get('operation_type', 'unknown')
        timestamp = entry.get('timestamp', '')[:19]
        
        # 构建更友好的标题
        if operation_type == 'stock_query':
            metadata = entry.get('metadata', {})
            title = f"📊 股票查询: {metadata.get('stock_name', 'N/A')} ({metadata.get('stock_code', 'N/A')}) - {timestamp}"
        elif operation_type == 'lhb_search':
            metadata = entry.get('metadata', {})
            title = f"🏆 龙虎榜查询: {metadata.get('target_code', 'N/A')} - {timestamp}"
        elif operation_type == 'ths_hot':
            title = f"🔥 同花顺热榜  - {timestamp}"
        elif operation_type == 'concept_count':
            title = f"📊 概念统计 - {timestamp}"
        else:
            title = f"{operation_type} - {timestamp}"
        
        with st.expander(title):
            # 检查是否为K线图相关操作
            if operation_type in ['stock_query', 'hot_stock_kline']:
                metadata = entry.get('metadata', {})
                stock_code = metadata.get('stock_code')
                if stock_code:
                    # 尝试显示K线图
                    kline_image_path = f"image/{stock_code}.png"
                    if os.path.exists(kline_image_path):
                        st.image(kline_image_path, caption=f"{metadata.get('stock_name', 'N/A')} ({stock_code}) K线图", use_column_width=True)
                    else:
                        st.warning("K线图文件不存在")
            
            # 显示历史数据（如果存在且不是K线图操作）
            if entry.get('data_file'):
                data = data_persistence.load_operation_data(entry['data_file'])
                if data is not None:
                    if isinstance(data, pd.DataFrame):
                        # 显示数据形状信息
                        st.info(f"数据形状: {data.shape[0]} 行 × {data.shape[1]} 列")
                        
                        # 查看方式选择
                        view_option = st.radio(
                            "查看方式",
                            ["完整数据", "前10行", "后10行", "数据统计"],
                            horizontal=True,
                            key=f"view_option_{i}"
                        )
                        
                        if view_option == "完整数据":
                            st.dataframe(data, use_container_width=True, height=400)
                        elif view_option == "前10行":
                            st.dataframe(data.head(10), use_container_width=True)
                        elif view_option == "后10行":
                            st.dataframe(data.tail(10), use_container_width=True)
                        elif view_option == "数据统计":
                            if data.select_dtypes(include=[np.number]).shape[1] > 0:
                                st.subheader("📈 数值列统计")
                                st.dataframe(data.describe(), use_container_width=True)
                            
                            st.subheader("📋 数据信息")
                            info_data = {
                                "列名": data.columns.tolist(),
                                "数据类型": data.dtypes.astype(str).tolist(),
                                "非空值数量": data.count().tolist(),
                                "空值数量": data.isnull().sum().tolist()
                            }
                            info_df = pd.DataFrame(info_data)
                            st.dataframe(info_df, use_container_width=True)
                        
                        # 数据导出功能
                        csv = data.to_csv(index=False)
                        st.download_button(
                            label="💾 导出CSV文件",
                            data=csv,
                            file_name=f"{operation_type}_{timestamp.replace(':', '-')}.csv",
                            mime="text/csv",
                            key=f"download_{i}"
                        )
                    else:
                        # 对于非DataFrame数据，使用JSON显示
                        st.json(data)
                else:
                    st.error("❌ 无法加载历史数据，文件可能已损坏或被删除")

