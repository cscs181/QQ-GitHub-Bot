import sys
from pathlib import Path

root = Path(__file__).parent.parent

sys.path.append(str(root))

import bot  # noqa: F401

# isort: split

from nonebot_plugin_orm.__main__ import main

if __name__ == "__main__":
    main()
