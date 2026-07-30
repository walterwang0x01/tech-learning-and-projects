"""测试 bootstrap：让 briefing_tools 可导入"""

import sys
from contextlib import contextmanager
from datetime import datetime as _datetime
from pathlib import Path
from unittest.mock import patch as _patch

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))


@contextmanager
def frozen_now(module, date_str: str):
    """把某模块内 datetime.now() 冻结到指定日期。

    凡是 fixture 用固定日期、被测逻辑又按 now() 算时间窗口（retention cutoff 等）的测试，
    都必须冻结时间，否则断言会随真实日期漂移而失效——不冻结的话测试只是"暂时通过"。

    用 datetime 子类而非 Mock，这样 strptime / timedelta 等原有行为不受影响。
    """
    fixed = _datetime.strptime(date_str, "%Y-%m-%d")

    class _FrozenDatetime(_datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed

    with _patch.object(module, "datetime", _FrozenDatetime):
        yield
