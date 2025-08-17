#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目启动验证脚本
用于验证新的项目结构是否正确
"""

def test_project_structure():
    """测试项目结构"""
    print("🔍 验证项目结构...")
    
    try:
        # 测试导入function模块
        print("📦 测试 function 模块导入...")
        from function import api_search_draw, db_search_draw, find_lhs, ths_hot
        from function import db_connect, flush_db, k_line, trade_day, utils
        print("✅ function 模块导入成功")
        
        # 测试导入streamlit模块
        print("📱 测试 streamlit 模块导入...")
        from streamlit import utils_streamlit, stock_streamlit, lhb_streamlit
        from streamlit import ths_streamlit, db_streamlit, history_streamlit
        print("✅ streamlit 模块导入成功")
        
        # 测试导入主模块
        print("🚀 测试主模块导入...")
        from main import main
        print("✅ 主模块导入成功")
        
        print("\n🎉 项目结构验证通过！")
        print("💡 现在可以使用以下命令启动程序:")
        print("   streamlit run main.py")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("💡 请检查文件是否已正确移动到对应文件夹")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def show_project_info():
    """显示项目信息"""
    print("\n📋 项目结构信息:")
    print("=" * 50)
    print("📁 function/     - 功能函数模块")
    print("📁 streamlit/    - Streamlit界面模块")
    print("📄 main.py       - 主程序入口")
    print("📄 test_modules.py - 模块测试脚本")
    print("📄 README_STRUCTURED.md - 结构化说明文档")
    print("=" * 50)

if __name__ == "__main__":
    print("🚀 股票分析系统 Pro - 结构化版本启动验证")
    print("=" * 60)
    
    show_project_info()
    
    if test_project_structure():
        print("\n✅ 项目启动验证成功！")
    else:
        print("\n❌ 项目启动验证失败，请检查项目结构")
