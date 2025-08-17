#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块化测试脚本
用于验证所有模块是否正确导入和配置
"""

def test_imports():
    """测试所有模块的导入"""
    print("🔍 开始测试模块导入...")
    
    try:
        # 测试工具模块
        print("📦 测试 utils_streamlit 模块...")
        from streamlit.utils_streamlit import DataPersistence, safe_import
        print("✅ utils_streamlit 模块导入成功")
        
        # 测试股票模块
        print("📊 测试 stock_streamlit 模块...")
        from streamlit.stock_streamlit import handle_stock_query, display_stock_info
        print("✅ stock_streamlit 模块导入成功")
        
        # 测试龙虎榜模块
        print("🏆 测试 lhb_streamlit 模块...")
        from streamlit.lhb_streamlit import handle_lhb_query
        print("✅ lhb_streamlit 模块导入成功")
        
        # 测试同花顺热榜模块
        print("🔥 测试 ths_streamlit 模块...")
        from streamlit.ths_streamlit import handle_ths_hot
        print("✅ ths_streamlit 模块导入成功")
        
        # 测试数据库模块
        print("💾 测试 db_streamlit 模块...")
        from streamlit.db_streamlit import handle_database_management
        print("✅ db_streamlit 模块导入成功")
        
        # 测试历史记录模块
        print("📚 测试 history_streamlit 模块...")
        from streamlit.history_streamlit import show_history_panel
        print("✅ history_streamlit 模块导入成功")
        
        # 测试主模块
        print("🚀 测试 main 模块...")
        from main import main
        print("✅ main 模块导入成功")
        
        print("\n🎉 所有模块导入测试通过！")
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def test_data_persistence():
    """测试数据持久化功能"""
    print("\n🔍 测试数据持久化功能...")
    
    try:
        from streamlit.utils_streamlit import DataPersistence
        
        # 创建实例
        dp = DataPersistence()
        print("✅ DataPersistence 实例创建成功")
        
        # 测试目录创建
        import os
        if os.path.exists("data_cache"):
            print("✅ data_cache 目录存在")
        if os.path.exists("history"):
            print("✅ history 目录存在")
        
        # 测试历史记录操作
        history = dp.load_operation_history()
        print(f"✅ 历史记录加载成功，当前记录数: {len(history)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据持久化测试失败: {e}")
        return False

def test_safe_import():
    """测试安全导入功能"""
    print("\n🔍 测试安全导入功能...")
    
    try:
        from streamlit.utils_streamlit import safe_import
        
        # 执行安全导入
        modules, import_status = safe_import()
        print("✅ safe_import 函数执行成功")
        
        # 显示导入状态
        print("📋 模块导入状态:")
        for module_name, status in import_status.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {module_name}: {'成功' if status else '失败'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 安全导入测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始模块化测试...\n")
    
    # 执行所有测试
    tests = [
        ("模块导入测试", test_imports),
        ("数据持久化测试", test_data_persistence),
        ("安全导入测试", test_safe_import)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"🔍 {test_name}")
        print("-" * 50)
        result = test_func()
        results.append((test_name, result))
        print()
    
    # 显示测试结果摘要
    print("📊 测试结果摘要")
    print("=" * 50)
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！模块化重构成功！")
        print("\n💡 现在可以使用以下命令运行程序:")
        print("   streamlit run main.py")
    else:
        print("⚠️  部分测试失败，请检查相关模块")

if __name__ == "__main__":
    main()
