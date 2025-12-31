import pandas as pd
import numpy as np
from pandas import DataFrame
import logging
from app.seoul_crime.seoul_data import SeoulData

logger = logging.getLogger(__name__)

class SeoulMethod(object): 

    def __init__(self):
        self.dataset = SeoulData()

    def csv_to_df(self, fname: str) -> pd.DataFrame:
        return pd.read_csv(fname)

    def xlsx_to_df(self, fname: str) -> pd.DataFrame:
        return pd.read_excel(fname)

    def df_merge(self, left: pd.DataFrame, right: pd.DataFrame, 
                 left_on: str = None, right_on: str = None, 
                 on: str = None, how: str = 'inner') -> pd.DataFrame:
        """
        두 DataFrame을 머지합니다.
        
        Args:
            left: 왼쪽 DataFrame
            right: 오른쪽 DataFrame
            left_on: 왼쪽 DataFrame의 키 컬럼명 (left_on과 right_on이 다를 때 사용)
            right_on: 오른쪽 DataFrame의 키 컬럼명 (left_on과 right_on이 다를 때 사용)
            on: 양쪽 DataFrame에 공통으로 존재하는 키 컬럼명 (left_on/right_on이 None일 때 사용)
            how: 머지 방식 ('inner', 'left', 'right', 'outer')
        
        Returns:
            머지된 DataFrame
        """
        if left_on is not None and right_on is not None:
            # 서로 다른 키 컬럼명으로 머지
            merged = pd.merge(left, right, left_on=left_on, right_on=right_on, how=how, suffixes=('', '_y'))
        elif on is not None:
            # 공통 키 컬럼명으로 머지
            merged = pd.merge(left, right, on=on, how=how, suffixes=('', '_y'))
        else:
            raise ValueError("left_on/right_on 또는 on 파라미터 중 하나는 반드시 제공되어야 합니다.")
        
        # 중복된 컬럼 제거 (suffix '_y'가 붙은 컬럼 중 왼쪽과 동일한 값인 경우)
        duplicate_cols = [col for col in merged.columns if col.endswith('_y')]
        for col in duplicate_cols:
            original_col = col[:-2]  # '_y' 제거
            if original_col in merged.columns:
                # 값이 동일하면 중복 컬럼 제거
                if merged[original_col].equals(merged[col]):
                    merged = merged.drop(columns=[col])
                else:
                    # 값이 다르면 원본 컬럼명 유지하고 '_y' 컬럼은 제거 (또는 다른 처리)
                    logger.warning(f"컬럼 '{original_col}'와 '{col}'의 값이 다릅니다. '{col}' 컬럼을 제거합니다.")
                    merged = merged.drop(columns=[col])
        
        return merged

    def geocode(self, address: str, language: str = 'ko'):
        """ 주소를 위도, 경도로 반환하는 메소드 """
        pass
    
    def get_api_key(self) -> str:
        """ API 키를 가져오는 메소드 """
        pass
