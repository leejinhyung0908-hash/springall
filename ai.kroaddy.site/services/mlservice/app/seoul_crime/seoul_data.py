from dataclasses import dataclass
from pathlib import Path
import pandas as pd

@dataclass

class SeoulData(object): 

    _fname: str = '' # file name
    # titanic_service.py와 동일한 방식으로 경로 설정
    # seoul_data.py 위치: app/seoul_crime/seoul_data.py
    # 데이터 파일 위치: app/resources/crime/
    # 저장 파일 위치: app/save/
    current_file = Path(__file__).resolve()
    app_dir = current_file.parent.parent  # app/
    _dname: str = str(app_dir / "resources" / "crime") # data path
    _sname: str = str(app_dir / "save") # save path (app/save/)
    _cctv: pd.DataFrame = None
    _crime: pd.DataFrame = None
    _pop: pd.DataFrame = None

    @property
    def fname(self) -> str: return self._fname

    @fname.setter
    def fname(self, fname): self._fname = fname

    @property
    def dname(self) -> str: return self._dname

    @dname.setter
    def dname(self, dname): self._dname = dname

    @property
    def sname(self) -> str: return self._sname

    @sname.setter
    def sname(self, sname): self._sname = sname

    @property
    def cctv(self) -> pd.DataFrame: return self._cctv

    @cctv.setter
    def cctv(self, cctv): self._cctv = cctv

    @property
    def crime(self) -> pd.DataFrame: return self._crime

    @crime.setter
    def crime(self, crime): self._crime = crime

    @property
    def pop(self) -> pd.DataFrame: return self._pop

    @pop.setter
    def pop(self, pop): self._pop = pop
