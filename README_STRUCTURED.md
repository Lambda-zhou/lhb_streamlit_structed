# 股票分析系统 Pro - 结构化版本

## 项目结构

本项目已经成功重构为清晰的结构化布局，将功能函数和Streamlit界面分离到不同的文件夹中，提高了代码的组织性和可维护性。

### 文件结构

```
lhb_streamlit-master/
├── main.py                           # 主程序入口文件
├── streamlit_explan.py               # 项目介绍模块
├── requirements.txt                  # 依赖包列表
├── README.md                         # 原始说明文档
├── README_MODULAR.md                # 模块化版本说明
├── README_STRUCTURED.md             # 结构化版本说明（本文件）
├── test_modules.py                  # 模块测试脚本
├── lhb_streamlit_pro.py             # 原始文件（保留作为备份）
├── bash.sh                          # 脚本文件
├── python文件介绍                    # 项目介绍文件
│
├── function/                         # 功能函数模块文件夹
│   ├── __init__.py                  # 功能模块初始化文件
│   ├── api_search_draw.py           # API搜索绘图功能
│   ├── db_search_draw.py            # 数据库搜索绘图功能
│   ├── find_lhs.py                  # 龙虎榜查询功能
│   ├── ths_hot.py                   # 同花顺热榜功能
│   ├── db_connect.py                # 数据库连接功能
│   ├── flush_db.py                  # 数据库更新功能
│   ├── k_line.py                    # K线图绘制功能
│   ├── trade_day.py                 # 交易日功能
│   └── utils.py                     # 通用工具函数
│
└── streamlit/                        # Streamlit界面模块文件夹
    ├── __init__.py                  # Streamlit模块初始化文件
    ├── utils_streamlit.py           # Streamlit工具函数和核心类
    ├── stock_streamlit.py           # 股票查询与K线图界面
    ├── lhb_streamlit.py             # 龙虎榜查询界面
    ├── ths_streamlit.py             # 同花顺热榜界面
    ├── db_streamlit.py              # 数据库管理界面
    └── history_streamlit.py         # 历史记录面板界面
```

## 结构说明

### 1. 根目录 (Root Directory)
- **main.py**: 主程序入口，整合所有模块
- **streamlit_explan.py**: 项目介绍和UI组件
- **requirements.txt**: 项目依赖包列表
- **测试和文档文件**: 各种说明文档和测试脚本

### 2. function/ 文件夹
- **功能函数模块**: 包含所有核心业务逻辑和数据处理函数
- **独立性强**: 每个模块都可以独立运行和测试
- **可复用性**: 这些函数可以被多个界面模块调用

### 3. streamlit/ 文件夹
- **界面模块**: 包含所有Streamlit相关的界面代码
- **业务逻辑**: 处理用户交互和界面展示逻辑
- **模块化**: 每个功能都有独立的界面模块

## 使用方法

### 运行主程序
```bash
streamlit run main.py
```

### 测试模块
```bash
python test_modules.py
```

### 开发新功能
1. **添加功能函数**: 在 `function/` 文件夹中创建新的功能模块
2. **添加界面**: 在 `streamlit/` 文件夹中创建对应的界面模块
3. **更新主程序**: 在 `main.py` 中导入和调用新模块

## 优势

### 1. 清晰的职责分离
- **功能层**: `function/` 文件夹专注于业务逻辑和数据处理
- **界面层**: `streamlit/` 文件夹专注于用户界面和交互
- **控制层**: `main.py` 负责模块协调和整体流程控制

### 2. 更好的代码组织
- **逻辑分离**: 功能函数和界面代码完全分离
- **易于维护**: 修改功能不影响界面，修改界面不影响功能
- **团队协作**: 不同开发者可以专注于不同层次的开发

### 3. 提高可维护性
- **模块化**: 每个功能都有独立的文件
- **可测试性**: 功能函数可以独立测试
- **可扩展性**: 新增功能不影响现有代码

## 导入路径说明

### 在main.py中导入模块
```python
# 导入Streamlit模块
from streamlit.utils_streamlit import DataPersistence, safe_import
from streamlit.stock_streamlit import handle_stock_query
from streamlit.lhb_streamlit import handle_lhb_query
# ... 其他模块
```

### 在streamlit模块中导入功能函数
```python
# 导入功能函数
from function.db_search_draw import database_get_stock_name
from function.k_line import draw_kline
# ... 其他功能函数
```

## 注意事项

### 1. 导入路径
- 所有导入路径都已更新为新的文件夹结构
- 使用相对导入确保模块间的正确引用

### 2. 模块依赖
- `streamlit` 模块依赖 `function` 模块
- `main.py` 依赖所有其他模块
- 避免循环导入问题

### 3. 文件移动
- 原始文件已移动到对应文件夹
- 导入路径已自动更新
- 功能完全保持不变

## 迁移说明

### 从原始版本迁移
1. 原始文件 `lhb_streamlit_pro.py` 保持不变，作为备份
2. 新版本使用 `main.py` 作为入口
3. 所有功能保持完全一致，用户体验无变化

### 兼容性
- 所有依赖包保持不变
- 数据文件格式保持不变
- 配置文件保持不变

## 未来扩展

### 1. 新功能模块
- 在 `function/` 文件夹中添加新的功能模块
- 在 `streamlit/` 文件夹中添加对应的界面模块
- 遵循现有的模块化架构

### 2. 插件系统
- 可以考虑实现动态加载功能模块
- 支持热插拔功能扩展

### 3. 配置管理
- 可以添加配置文件管理
- 支持模块级别的配置

## 总结

通过结构化重构，项目代码组织更加清晰，维护性大大提升。功能函数和界面代码完全分离，便于团队协作和功能扩展。同时保持了原有功能的完整性，用户体验无任何变化。

新的项目结构为：
- **功能层** (`function/`): 核心业务逻辑
- **界面层** (`streamlit/`): 用户界面和交互
- **控制层** (`main.py`): 整体协调和流程控制

这种分层架构使得代码更加清晰、易于维护和扩展。
