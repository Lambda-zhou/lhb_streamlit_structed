# function模块初始化文件

# 导入所有功能模块
try:
    from . import api_search_draw
    from . import db_search_draw
    from . import find_lhs
    from . import ths_hot
    from . import db_connect
    from . import flush_db
    from . import k_line
    from . import trade_day
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    try:
        import api_search_draw
        import db_search_draw
        import find_lhs
        import ths_hot
        import db_connect
        import flush_db
        import k_line
        import trade_day
    except ImportError:
        pass
