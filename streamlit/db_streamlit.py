import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import pickle
from datetime import datetime

def handle_database_management(data_persistence, MODULES, IMPORT_STATUS):
    """处理数据库管理"""
    st.header("💾 数据库管理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("数据库连接测试")
        if st.button("测试数据库连接", type="primary"):
            if not IMPORT_STATUS.get('db_connect', False):
                st.error("数据库连接模块未正确加载")
                return
            
            with st.spinner("正在测试数据库连接..."):
                try:
                    conn = MODULES['db_connect']['db_connect']()
                    if conn:
                        # 保存连接测试结果
                        metadata = {
                            "operation": "connection_test",
                            "result": "success"
                        }
                        data_persistence.save_operation_history("db_connection_test", {"status": "success"}, metadata)
                        
                        st.success("数据库连接成功！结果已保存到历史记录")
                        conn.close()
                    else:
                        metadata = {
                            "operation": "connection_test",
                            "result": "failed"
                        }
                        data_persistence.save_operation_history("db_connection_test", {"status": "failed"}, metadata)
                        st.error("数据库连接失败")
                except Exception as e:
                    metadata = {
                        "operation": "connection_test",
                        "result": "error",
                        "error": str(e)
                    }
                    data_persistence.save_operation_history("db_connection_test", {"status": "error", "error": str(e)}, metadata)
                    st.error(f"连接测试失败: {str(e)}")
    
    with col2:
        st.subheader("数据库更新")
        if st.button("更新数据库", type="secondary"):
            if not IMPORT_STATUS.get('flush_db', False):
                st.error("数据库更新模块未正确加载")
                return
            
            with st.spinner("正在更新数据库..."):
                try:
                    if 'flush_database' in MODULES['flush_db']:
                        result = MODULES['flush_db']['flush_database']()
                        
                        # 保存更新结果
                        metadata = {
                            "operation": "database_update"
                        }
                        data_persistence.save_operation_history("db_update", result, metadata)
                        
                        st.success("数据库更新完成！结果已保存到历史记录")
                        if result:
                            st.write(result)
                    else:
                        st.error("数据库更新功能暂时不可用")
                except Exception as e:
                    metadata = {
                        "operation": "database_update",
                        "error": str(e)
                    }
                    data_persistence.save_operation_history("db_update", {"error": str(e)}, metadata)
                    st.error(f"数据库更新失败: {str(e)}")

