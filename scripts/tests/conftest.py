"""测试 bootstrap：让 briefing_tools 可导入"""

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
