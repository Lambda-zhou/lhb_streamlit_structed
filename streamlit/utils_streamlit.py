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

# 忽略警告信息
warnings.filterwarnings('ignore')
plt.switch_backend('Agg')

# 创建必要的文件夹
for folder in ['image', 'data_cache', 'history']:
    if not os.path.exists(folder):
        os.makedirs(folder)

# 数据持久化类
class DataPersistence:
    def __init__(self):
        self.cache_dir = "data_cache"
        self.history_dir = "history"
        self.history_file = os.path.join(self.history_dir, "operation_history.json")
        self.ensure_directories()
    
    def ensure_directories(self):
        """确保目录存在"""
        for directory in [self.cache_dir, self.history_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def save_operation_history(self, operation_type, data, metadata=None):
        """保存操作历史"""
        try:
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "operation_type": operation_type,
                "metadata": metadata or {},
                "data_file": None
            }
            
            # 保存数据到单独文件
            if data is not None:
                timestamp = int(time.time())
                data_filename = f"{operation_type}_{timestamp}.pkl"
                data_filepath = os.path.join(self.cache_dir, data_filename)
                
                with open(data_filepath, 'wb') as f:
                    pickle.dump(data, f)
                
                history_entry["data_file"] = data_filename
            
            # 读取现有历史
            history = self.load_operation_history()
            history.append(history_entry)
            
            # 保持最近100条记录
            if len(history) > 100:
                # 删除旧的数据文件
                old_entry = history[0]
                if old_entry.get("data_file"):
                    old_file_path = os.path.join(self.cache_dir, old_entry["data_file"])
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                history = history[-100:]
            
            # 保存历史记录
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            st.error(f"保存操作历史失败: {str(e)}")
            return False
    
    def load_operation_history(self):
        """加载操作历史"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            st.error(f"加载操作历史失败: {str(e)}")
            return []
    
    def load_operation_data(self, data_filename):
        """加载操作数据"""
        try:
            data_filepath = os.path.join(self.cache_dir, data_filename)
            if os.path.exists(data_filepath):
                with open(data_filepath, 'rb') as f:
                    return pickle.load(f)
            return None
        except Exception as e:
            st.error(f"加载操作数据失败: {str(e)}")
            return None
    
    def clear_history(self):
        """清空历史记录"""
        try:
            # 删除所有缓存文件
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            # 清空历史记录文件
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
            
            return True
        except Exception as e:
            st.error(f"清空历史记录失败: {str(e)}")
            return False

# 安全导入模块
def safe_import():
    """安全导入模块"""
    modules = {}
    import_status = {}
    
    module_configs = [
        ('api_search', ['function.api_search_draw'], ['api_search_code_draw', 'api_search_name_draw']),
        ('db_search', ['function.db_search_draw'], ['database_search_name_draw', 'database_search_code_draw']),
        ('lhb', ['function.find_lhs'], ['search_in_lh', 'find_lhb']),
        ('ths_hot', ['function.ths_hot'], ['code_draw', 'concept_count']),
        ('db_connect', ['function.db_connect'], ['db_connect']),
        ('flush_db', ['function.flush_db'], ['flush_database']),
        ('k_line', ['function.k_line'], ['draw_kline'])
    ]
    
    for module_name, import_paths, function_names in module_configs:
        try:
            module_dict = {}
            for path in import_paths:
                module = __import__(path, fromlist=[''])
                for func_name in function_names:
                    if hasattr(module, func_name):
                        module_dict[func_name] = getattr(module, func_name)
                # 对于ths_hot模块，特殊处理main函数
                if module_name == 'ths_hot' and hasattr(module, 'main'):
                    module_dict['main'] = getattr(module, 'main')
            modules[module_name] = module_dict
            import_status[module_name] = True
        except ImportError as e:
            st.warning(f"{module_name}模块导入失败: {e}")
            import_status[module_name] = False
    
    return modules, import_status

# 缓存函数
@st.cache_data(ttl=1800)
def get_all_stock_codes():
    """获取所有股票代码和名称"""
    try:
        return adata.stock.info.all_code()
    except Exception as e:
        st.error(f"获取股票代码失败: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=180)
def get_stock_data_cached(stock_code):
    """缓存股票数据获取"""
    try:
        return adata.stock.market.get_market_min(stock_code)
    except Exception as e:
        return None

def get_stock_name_by_code(stock_code):
    """通过股票代码获取股票名称"""
    try:
        all_codes = get_all_stock_codes()
        if not all_codes.empty:
            result = all_codes[all_codes['stock_code'] == stock_code]
            if not result.empty:
                return result['short_name'].values[0]
    except:
        pass
    return "未知"

def get_stock_code_by_name(short_name):
    """通过股票名称获取股票代码"""
    try:
        all_codes = get_all_stock_codes()
        if not all_codes.empty:
            result = all_codes[all_codes['short_name'] == short_name]
            if not result.empty:
                return result['stock_code'].values[0]
    except:
        pass
    return None

def save_kline_image(df, stock_code, stock_name, MODULES):
    """保存K线图"""
    try:
        fig = MODULES['k_line']['draw_kline'](df, stock_code)
        timestamp = int(time.time())
        filename = f"image/{stock_code}_{timestamp}.png"
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return filename
    except Exception as e:
        st.error(f"保存K线图失败: {str(e)}")
        return None

def save_kline_image_for_history(df, stock_code, stock_name, MODULES):
    """为历史记录保存K线图（使用stock_code命名）"""
    try:
        fig = MODULES['k_line']['draw_kline'](df, stock_code)
        filename = f"image/{stock_code}.png"
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return filename
    except Exception as e:
        st.error(f"保存K线图失败: {str(e)}")
        return None

def get_latest_kline_image(stock_code):
    """获取最新的K线图"""
    try:
        image_files = [f for f in os.listdir('image') if f.startswith(f"{stock_code}_")]
        if image_files:
            image_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]), reverse=True)
            return os.path.join('image', image_files[0])
        return None
    except Exception as e:
        return None

def get_stock_name_from_db(stock_code):
    """从数据库获取股票名称"""
    try:
        # 使用新增的不绘图函数
        from function.db_search_draw import database_get_stock_name
        result = database_get_stock_name(stock_code)
        return result if result else None
    except Exception as e:
        st.error(f"数据库查询股票名称失败: {str(e)}")
        return None

def get_stock_code_from_db(short_name):
    """从数据库获取股票代码"""
    try:
        # 使用新增的不绘图函数
        from function.db_search_draw import database_get_stock_code
        result = database_get_stock_code(short_name)
        return result if result else None
    except Exception as e:
        st.error(f"数据库查询股票代码失败: {str(e)}")
        return None

def fuzzy_search_stocks_from_db(keyword):
    """从数据库模糊查询股票"""
    try:
        from function.db_search_draw import database_fuzzy_search
        result = database_fuzzy_search(keyword)
        return result if result is not None else None
    except Exception as e:
        st.error(f"数据库模糊查询失败: {str(e)}")
        return None

def query_stock_data(stock_code, stock_name, data_source, get_stock_name_from_db, get_stock_code_from_db):
    """查询股票数据"""
    try:
        # 获取股票名称
        final_stock_name = stock_name
        if not stock_name or stock_name == "未知":
            if data_source == "数据库查询":
                db_stock_name = get_stock_name_from_db(stock_code)
                if db_stock_name:
                    final_stock_name = db_stock_name
            else:
                final_stock_name = get_stock_name_by_code(stock_code)
        
        # 获取股票数据
        k_data = None
        if data_source == "API查询":
            k_data = get_stock_data_cached(stock_code)
        elif data_source == "数据库查询":
            # 先查询数据库获取股票名称，再获取数据
            db_stock_name = get_stock_name_from_db(stock_code)
            if db_stock_name:
                final_stock_name = db_stock_name
                k_data = get_stock_data_cached(stock_code)
            else:
                st.error("数据库查询模块未正确加载")
                return None, None, None
        
        return k_data, final_stock_name, stock_code
    except Exception as e:
        st.error(f"查询股票数据失败: {str(e)}")
        return None, None, None
