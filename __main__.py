"""
artfish 模块入口点。

支持通过以下方式调用：
- python -m artfish (从项目目录)
- python -m artfish (从任何目录，自动添加路径)
- python main.py (直接运行)
"""
import sys
from pathlib import Path

# 获取artfish包所在目录
artfish_dir = Path(__file__).parent.absolute()

# 确保artfish目录在Python路径中
if str(artfish_dir) not in sys.path:
    sys.path.insert(0, str(artfish_dir))

# 导入并运行main函数
from artfish.main import main

if __name__ == "__main__":
    main()
