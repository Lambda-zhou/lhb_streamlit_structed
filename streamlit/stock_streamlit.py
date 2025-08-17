import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import pickle
from datetime import datetime

def display_stock_info(k_data, stock_code, stock_name, data_source):
    """股票信息"""
    if k_data is not None and not k_data.empty:
        current_price = k_data.iloc[-1]['price']
        current_change = k_data.iloc[-1]['change']
        current_change_pct = k_data.iloc[-1]['change_pct']
        
        st.info(f"""
        **股票信息:**
        - 股票代码: {stock_code}
        - 股票名称: {stock_name}
        - 当前价格: {current_price:.2f}
        - 涨跌额: {current_change:+.2f}
        - 涨跌幅: {current_change_pct:+.2f}%
        - 数据源: {data_source}
        """)

def handle_stock_query(stock_code, short_name, data_persistence, MODULES, IMPORT_STATUS, 
                      get_stock_name_from_db, get_stock_code_from_db, fuzzy_search_stocks_from_db,
                      save_kline_image, save_kline_image_for_history, get_latest_kline_image,
                      query_stock_data, get_stock_code_by_name):
    """处理股票查询和K线图绘制"""
    st.header("📊 股票查询与K线图")
    
    if not IMPORT_STATUS.get('k_line', False):
        st.error("K线图模块未正确加载，无法使用此功能")
        return
    
    # 数据源选择
    data_source = st.radio(
        "选择查询方式",
        ["API查询", "数据库查询", "数据库模糊查询"],
        horizontal=True
    )
    
    if data_source == "数据库查询" and not IMPORT_STATUS.get('db_connect', False):
        st.warning("⚠️ 数据库连接模块未正确加载，请先测试数据库连接")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("通过股票代码查询", type="primary", disabled=not stock_code):
            if stock_code:
                with st.spinner("正在查询股票数据..."):
                    k_data, final_stock_name, final_code = query_stock_data(stock_code, "未知", data_source, 
                                                                          get_stock_name_from_db, get_stock_code_from_db)
                    if k_data is not None:
                        save_kline_image(k_data, final_code, final_stock_name, MODULES)
                        
                        # 保存K线图到历史记录
                        save_kline_image_for_history(k_data, final_code, final_stock_name, MODULES)
                        
                        # 保存到持久化存储
                        metadata = {
                            "stock_code": final_code,
                            "stock_name": final_stock_name,
                            "data_source": data_source,
                            "query_type": "by_code"
                        }
                        data_persistence.save_operation_history("stock_query", k_data, metadata)
                        
                        # 保存到session state
                        st.session_state.query_result = k_data
                        st.session_state.query_stock_code = final_code
                        st.session_state.query_stock_name = final_stock_name
                        st.session_state.query_source = data_source
                        
                        st.success("查询成功！数据已保存到历史记录")
                        display_stock_info(k_data, final_code, final_stock_name, data_source)
                    else:
                        st.error("查询失败，请检查股票代码是否正确")
    
    with col2:
        if st.button("通过股票名称查询", type="primary", disabled=not short_name):
            if short_name:
                with st.spinner("正在查询股票数据..."):
                    # 根据数据源选择不同的查询方式
                    if data_source == "数据库查询":
                        found_code = get_stock_code_from_db(short_name)
                    elif data_source == "数据库模糊查询":
                        # 模糊查询处理
                        fuzzy_results = fuzzy_search_stocks_from_db(short_name)
                        if fuzzy_results is not None and not fuzzy_results.empty:
                            st.success(f"找到 {len(fuzzy_results)} 只相关股票")
                            st.dataframe(fuzzy_results, use_container_width=True)
                            
                            # 保存模糊查询结果到历史记录
                            metadata = {
                                "keyword": short_name,
                                "results_count": len(fuzzy_results),
                                "query_type": "fuzzy_search"
                            }
                            data_persistence.save_operation_history("fuzzy_search", fuzzy_results, metadata)
                            st.info("模糊查询结果已保存到历史记录")
                            return
                        else:
                            st.info(f"未找到包含'{short_name}'的股票")
                            return
                    else:
                        found_code = get_stock_code_by_name(short_name)
                    
                    if found_code:
                        k_data, final_stock_name, final_code = query_stock_data(found_code, short_name, data_source,
                                                                              get_stock_name_from_db, get_stock_code_from_db)
                        if k_data is not None:
                            save_kline_image(k_data, final_code, final_stock_name, MODULES)
                            
                            # 保存K线图到历史记录
                            save_kline_image_for_history(k_data, final_code, final_stock_name, MODULES)
                            
                            # 保存到持久化存储
                            metadata = {
                                "stock_code": final_code,
                                "stock_name": final_stock_name,
                                "data_source": data_source,
                                "query_type": "by_name"
                            }
                            data_persistence.save_operation_history("stock_query", k_data, metadata)
                            
                            # 保存到session state
                            st.session_state.query_result = k_data
                            st.session_state.query_stock_code = final_code
                            st.session_state.query_stock_name = final_stock_name
                            st.session_state.query_source = data_source
                            
                            st.success("查询成功！数据已保存到历史记录")
                            display_stock_info(k_data, final_code, final_stock_name, data_source)
                        else:
                            st.error("获取股票数据失败")
                    else:
                        st.error("未找到相关股票，请检查股票名称是否正确")
    
    # 显示K线图
    if st.session_state.query_result is not None:
        st.subheader("📈 生成K线图")
        if st.button("显示K线图", type="primary"):
            try:
                image_path = get_latest_kline_image(st.session_state.query_stock_code)
                if image_path and os.path.exists(image_path):
                    st.success("K线图生成成功！")
                    st.image(image_path, caption=f"{st.session_state.query_stock_name} ({st.session_state.query_stock_code}) K线图", use_column_width=True)
                    display_stock_info(st.session_state.query_result, st.session_state.query_stock_code, st.session_state.query_stock_name, st.session_state.query_source)
                else:
                    st.error("未找到保存的K线图，请重新查询")
            except Exception as e:
                st.error(f"显示K线图时出现错误: {str(e)}")
