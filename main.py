import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import warnings
import adata
import time
import json
from datetime import datetime
import pickle

# 导入项目介绍模块
try:
    import streamlit_explan as explan
    IMPORT_EXPLAN = True
except ImportError:
    IMPORT_EXPLAN = False
    st.warning("项目介绍模块导入失败")

# 导入自定义模块
from streamlit.utils_streamlit import (
    DataPersistence, safe_import, get_all_stock_codes, get_stock_data_cached,
    get_stock_name_by_code, get_stock_code_by_name, save_kline_image,
    save_kline_image_for_history, get_latest_kline_image, get_stock_name_from_db,
    get_stock_code_from_db, fuzzy_search_stocks_from_db, query_stock_data
)
from streamlit.stock_streamlit import handle_stock_query, display_stock_info
from streamlit.lhb_streamlit import handle_lhb_query
from streamlit.ths_streamlit import handle_ths_hot
from streamlit.db_streamlit import handle_database_management
from streamlit.history_streamlit import show_history_panel

# 忽略警告信息
warnings.filterwarnings('ignore')
plt.switch_backend('Agg')

# 设置页面配置
st.set_page_config(
    page_title="股票分析系统 Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据持久化
@st.cache_resource
def get_data_persistence():
    return DataPersistence()

data_persistence = get_data_persistence()

# 获取模块和导入状态
MODULES, IMPORT_STATUS = safe_import()

def main():
    st.title("📈 股票分析系统 Pro")
    st.markdown("---")
    
    # 欢迎信息
    if 'first_visit' not in st.session_state:
        st.session_state.first_visit = True
        if IMPORT_EXPLAN:
            explan.show_welcome_message()
        else:
            st.success("🎉 欢迎使用股票分析系统 Pro！")
            st.info("💡 Pro版本新增功能：所有操作结果都会自动保存到历史记录中，支持数据常驻和状态记录。")
    
    # 初始化session_state
    if 'query_result' not in st.session_state:
        st.session_state.query_result = None
        st.session_state.query_stock_code = None
        st.session_state.query_stock_name = None
        st.session_state.query_source = None
        st.session_state.hot_data = None
        st.session_state.hot_data_time = None
    
    # 顶部控制按钮
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        if st.button("📋 切换侧边栏", help="点击隐藏或显示侧边栏"):
            if 'sidebar_visible' not in st.session_state:
                st.session_state.sidebar_visible = True
            st.session_state.sidebar_visible = not st.session_state.sidebar_visible
    
    with col2:
        if st.button("🔧 系统状态", help="查看系统模块加载状态"):
            st.session_state.show_status = not st.session_state.get('show_status', False)
    
    with col3:
        if st.button("❓ 快速帮助", help="查看快速使用指南"):
            st.session_state.show_help = not st.session_state.get('show_help', False)
    
    with col4:
        if st.button("📚 历史记录", help="查看操作历史记录"):
            st.session_state.show_history = not st.session_state.get('show_history', False)
    
    # 显示UI组件
    if IMPORT_EXPLAN:
        explan.show_ui_components(
            import_status=IMPORT_STATUS,
            show_help=st.session_state.get('show_help', False),
            show_status=st.session_state.get('show_status', False),
            show_welcome=False
        )
    else:
        # 使用备用显示逻辑
        if hasattr(explan, 'show_fallback_ui'):
            explan.show_fallback_ui(
                import_status=IMPORT_STATUS,
                show_help=st.session_state.get('show_help', False),
                show_status=st.session_state.get('show_status', False)
            )
    
    # 显示历史记录面板
    if st.session_state.get('show_history', False):
        show_history_panel(data_persistence)
        st.markdown("---")
    
    # 侧边栏功能选择
    if 'sidebar_visible' not in st.session_state or st.session_state.sidebar_visible:
        st.sidebar.title("功能选择")
        function_choice = st.sidebar.selectbox(
            "选择功能模块",
            ["股票查询与K线图", "龙虎榜查询", "同花顺热榜", "数据库管理"]
        )
        
        # 项目介绍
        if IMPORT_EXPLAN and st.sidebar.checkbox("显示项目介绍", value=False):
            explan.show_explan()
        
        # 历史记录快捷访问
        st.sidebar.markdown("---")
        st.sidebar.subheader("📚 快捷访问")
        if st.sidebar.button("查看历史记录"):
            st.session_state.show_history = True
            st.rerun()
        
        # 显示最近操作
        recent_history = data_persistence.load_operation_history()[-5:]  # 最近5条
        if recent_history:
            st.sidebar.subheader("🕒 最近操作")
            for entry in reversed(recent_history):
                operation_type = entry.get('operation_type', 'unknown')
                timestamp = entry.get('timestamp', '')[:16]  # 只显示到分钟
                metadata = entry.get('metadata', {})
                
                # 构建显示文本
                if operation_type == 'stock_query':
                    display_text = f"股票查询: {metadata.get('stock_code', 'N/A')}"
                elif operation_type == 'lhb_search':
                    display_text = f"龙虎榜: {metadata.get('target_code', 'N/A')}"
                elif operation_type == 'ths_hot':
                    display_text = "同花顺热榜"
                else:
                    display_text = operation_type
                
                st.sidebar.text(f"{timestamp} - {display_text}")
    else:
        # 当侧边栏隐藏时，使用下拉菜单
        function_choice = st.selectbox(
            "选择功能模块",
            ["股票查询与K线图", "龙虎榜查询", "同花顺热榜", "数据库管理"]
        )
    
    # 主要输入区域
    col1, col2 = st.columns(2)
    with col1:
        stock_code = st.text_input("股票代码", placeholder="例如: 000001, 600519")
    with col2:
        short_name = st.text_input("股票名称", placeholder="例如: 平安银行, 贵州茅台")
    
    st.markdown("---")
    
    # 根据选择的功能显示不同内容
    if function_choice == "股票查询与K线图":
        handle_stock_query(
            stock_code, short_name, data_persistence, MODULES, IMPORT_STATUS,
            get_stock_name_from_db, get_stock_code_from_db, fuzzy_search_stocks_from_db,
            save_kline_image, save_kline_image_for_history, get_latest_kline_image,
            query_stock_data, get_stock_code_by_name
        )
    elif function_choice == "龙虎榜查询":
        handle_lhb_query(stock_code, short_name, data_persistence, MODULES, IMPORT_STATUS)
    elif function_choice == "同花顺热榜":
        handle_ths_hot(
            data_persistence, MODULES, IMPORT_STATUS,
            get_stock_name_by_code, get_stock_data_cached, save_kline_image_for_history
        )
    elif function_choice == "数据库管理":
        handle_database_management(data_persistence, MODULES, IMPORT_STATUS)

if __name__ == "__main__":
    main()
