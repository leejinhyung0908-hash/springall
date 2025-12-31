"""
Finance Service App Package
"""
import sys
from pathlib import Path

# 공통 모듈 경로 추가 (erp.kroaddy.site/common)
# financeservice는 orderservice 안에 있으므로 한 단계 더 올라가야 함
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
