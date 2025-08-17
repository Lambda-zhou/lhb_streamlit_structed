import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import pickle
from datetime import datetime

def handle_ths_hot(data_persistence, MODULES, IMPORT_STATUS, 
                   get_stock_name_by_code, get_stock_data_cached, save_kline_image_for_history):
    """处理同花顺热榜"""
    st.header("🔥 同花顺热榜")
    
    if not IMPORT_STATUS.get('ths_hot', False):
        st.error("同花顺热榜模块未正确加载，无法使用此功能")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("获取同花顺热榜", type="primary"):
            with st.spinner("正在获取热榜数据..."):
                try:
                    if 'main' in MODULES['ths_hot']:
                        result = MODULES['ths_hot']['main']()
                    else:
                        st.error("热榜功能暂时不可用")
                        return
                    
                    if result is not None and (isinstance(result, pd.DataFrame) and not result.empty or 
                                              isinstance(result, (list, dict)) and result):
                        # 保存到持久化存储
                        metadata = {
                            "query_type": "hot_list"
                        }
                        data_persistence.save_operation_history("ths_hot", result, metadata)
                        
                        # 保存到session state
                        st.session_state.hot_data = result
                        st.session_state.hot_data_time = pd.Timestamp.now()
                        st.success("热榜数据获取成功！数据已保存到历史记录")
                    else:
                        st.error("获取热榜数据失败")
                except Exception as e:
                    st.error(f"获取热榜过程中出现错误: {str(e)}")
    
    # 显示热榜数据
    if hasattr(st.session_state, 'hot_data') and st.session_state.hot_data is not None:
        st.subheader("📊 热榜数据")
        if hasattr(st.session_state, 'hot_data_time') and st.session_state.hot_data_time:
            st.info(f"数据更新时间: {st.session_state.hot_data_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 筛选功能
        if isinstance(st.session_state.hot_data, pd.DataFrame) and not st.session_state.hot_data.empty:
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            with col_filter1:
                price_filter = st.number_input("价格上限", min_value=0.0, max_value=1000.0, value=50.0, step=1.0)
            with col_filter2:
                change_filter = st.number_input("涨跌幅下限(%)", min_value=-20.0, max_value=20.0, value=0.0, step=0.1)
            with col_filter3:
                volume_filter = st.number_input("成交量下限(万)", min_value=0.0, max_value=10000.0, value=0.0, step=100.0)
            
            filtered_data = st.session_state.hot_data.copy()
            
            # 数据类型转换和清理
            try:
                if 'price' in filtered_data.columns:
                    # 确保price列为数值类型
                    filtered_data['price'] = pd.to_numeric(filtered_data['price'], errors='coerce')
                    # 过滤掉NaN值
                    filtered_data = filtered_data[filtered_data['price'].notna() & (filtered_data['price'] <= price_filter)]
                
                if 'change_pct' in filtered_data.columns:
                    # 确保change_pct列为数值类型
                    filtered_data['change_pct'] = pd.to_numeric(filtered_data['change_pct'], errors='coerce')
                    # 过滤掉NaN值
                    filtered_data = filtered_data[filtered_data['change_pct'].notna() & (filtered_data['change_pct'] >= change_filter)]
                
                if 'volume' in filtered_data.columns:
                    # 确保volume列为数值类型
                    filtered_data['volume'] = pd.to_numeric(filtered_data['volume'], errors='coerce')
                    # 过滤掉NaN值
                    filtered_data = filtered_data[filtered_data['volume'].notna() & (filtered_data['volume'] >= volume_filter * 10000)]
            except Exception as e:
                st.warning(f"数据筛选过程中出现警告: {str(e)}")
                # 如果筛选失败，显示原始数据
                st.info("显示原始数据（筛选功能暂时不可用）")
            
            st.success(f"筛选结果: {len(filtered_data)} 只股票")
            st.dataframe(filtered_data, use_container_width=True)
        else:
            st.write(st.session_state.hot_data)
    
    with col2:
        st.subheader("绘制热榜股票K线图")
        hot_stock_code = st.text_input("输入热榜股票代码", key="hot_stock")
        if st.button("绘制K线图", disabled=not hot_stock_code):
            if hot_stock_code:
                with st.spinner("正在绘制K线图..."):
                    try:
                        stock_name = get_stock_name_by_code(hot_stock_code)
                        k_data = get_stock_data_cached(hot_stock_code)
                        if k_data is not None and not k_data.empty:
                            # 保存K线图到历史记录
                            save_kline_image_for_history(k_data, hot_stock_code, stock_name, MODULES)
                            
                            # 保存到持久化存储
                            metadata = {
                                "stock_code": hot_stock_code,
                                "stock_name": stock_name,
                                "query_type": "hot_stock_kline"
                            }
                            data_persistence.save_operation_history("hot_stock_kline", k_data, metadata)
                            
                            st.success("K线图绘制成功！数据已保存到历史记录")
                            fig = MODULES['k_line']['draw_kline'](k_data, hot_stock_code)
                            st.pyplot(fig)
                            
                            # 显示股票信息
                            current_price = k_data.iloc[-1]['price']
                            current_change = k_data.iloc[-1]['change']
                            current_change_pct = k_data.iloc[-1]['change_pct']
                            
                            st.info(f"""
                            **股票信息:**
                            - 股票代码: {hot_stock_code}
                            - 股票名称: {stock_name}
                            - 当前价格: {current_price:.2f}
                            - 涨跌额: {current_change:+.2f}
                            - 涨跌幅: {current_change_pct:+.2f}%
                            - 数据源: API查询
                            """)
                        else:
                            st.error("获取股票数据失败，请检查股票代码是否正确")
                    except Exception as e:
                        st.error(f"绘制过程中出现错误: {str(e)}")
    
    # 概念计数功能
    if hasattr(st.session_state, 'hot_data') and st.session_state.hot_data is not None:
        st.subheader("📊 概念统计")
        if st.button("统计概念出现次数", type="secondary"):
            if not IMPORT_STATUS.get('ths_hot', False):
                st.error("同花顺热榜模块未正确加载")
                return
            
            with st.spinner("正在统计概念..."):
                try:
                    if 'concept_count' in MODULES['ths_hot']:
                        concept_counts = MODULES['ths_hot']['concept_count'](st.session_state.hot_data)
                        if concept_counts is not None and not concept_counts.empty:
                            # 保存到持久化存储
                            metadata = {
                                "query_type": "concept_count"
                            }
                            data_persistence.save_operation_history("concept_count", concept_counts, metadata)
                            
                            st.success("概念统计完成！数据已保存到历史记录")
                            st.dataframe(concept_counts, use_container_width=True)
                            
                            # 显示统计信息
                            total_concepts = len(concept_counts)
                            total_stocks = concept_counts['count'].sum()
                            st.info(f"统计信息: 共发现 {total_concepts} 个概念，涉及 {total_stocks} 只股票")
                        else:
                            st.warning("未找到概念数据")
                    else:
                        st.error("概念统计功能暂时不可用")
                except Exception as e:
                    st.error(f"概念统计过程中出现错误: {str(e)}")
