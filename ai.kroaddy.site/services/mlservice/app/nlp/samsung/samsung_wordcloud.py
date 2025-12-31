"""
Samsung 워드클라우드 생성 서비스
한국어 텍스트 처리 및 워드클라우드 생성
"""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk import FreqDist
from konlpy.tag import Okt
import pandas as pd
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')  # GUI 백엔드 없이 사용
import matplotlib.pyplot as plt
import io
import base64

# 공통 모듈 경로 추가
base_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(base_path))

# 로깅 설정
try:
    from common.utils import setup_logging
    logger = setup_logging("samsung_wordcloud")
except ImportError:
    import logging
    logger = logging.getLogger("samsung_wordcloud")


@dataclass
class Entity:
    """엔티티 클래스 - 파일 경로 및 설정 정보"""
    context: str = ""
    fname: str = ""
    target: str = ""

    @property
    def context(self) -> str:
        return self._context

    @context.setter
    def context(self, context: str):
        self._context = context

    @property
    def fname(self) -> str:
        return self._fname

    @fname.setter
    def fname(self, fname: str):
        self._fname = fname

    @property
    def target(self) -> str:
        return self._target

    @target.setter
    def target(self, target: str):
        self._target = target


class SamsungWordCloudService:
    """Samsung 워드클라우드 생성 서비스"""
    
    def __init__(self):
        """서비스 초기화"""
        self.texts: str = ""
        self.tokens: List[str] = []
        self.stopwords: List[str] = []
        self.freqtxt: Optional[pd.Series] = None
        self.okt = Okt()
        self.corpus_downloaded = False
        
        # 기본 파일 경로 설정 (resources/data 폴더 기준)
        self.default_data_dir = Path(__file__).parent.parent.parent / "resources" / "data"
        self.default_text_file = self.default_data_dir / "kr-Report_2018.txt"
        self.default_stopwords_file = self.default_data_dir / "stopwords.txt"
        self.default_font_file = self.default_data_dir / "D2Coding.ttf"
        
        # 말뭉치 다운로드
        self._download_corpus()
    
    def _download_corpus(self) -> None:
        """NLTK 말뭉치 다운로드"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)  # 최신 NLTK 버전에서 필요
            nltk.download('stopwords', quiet=True)
            self.corpus_downloaded = True
            logger.info("NLTK 말뭉치 다운로드 완료")
        except Exception as e:
            logger.error(f"말뭉치 다운로드 실패: {e}")
            self.corpus_downloaded = False
    
    def extract_tokens(self, file_path: str) -> str:
        """
        텍스트 파일에서 토큰 추출
        
        Args:
            file_path: 텍스트 파일 경로
        
        Returns:
            읽은 텍스트
        """
        try:
            logger.info(f"텍스트 파일 읽기: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                self.texts = f.read()
            logger.info(f"텍스트 로드 완료: {len(self.texts)} 문자")
            return self.texts
        except FileNotFoundError:
            logger.error(f"파일을 찾을 수 없습니다: {file_path}")
            raise
        except Exception as e:
            logger.error(f"텍스트 추출 실패: {e}")
            raise
    
    def extract_hangeul(self) -> str:
        """
        한글만 추출
        
        Returns:
            한글로만 구성된 텍스트
        """
        try:
            logger.info("한글 추출 중...")
            texts = self.texts.replace('\n', ' ')
            tokenizer = re.compile(r'[^ ㄱ-힣]')
            self.texts = tokenizer.sub('', texts)
            logger.info(f"한글 추출 완료: {len(self.texts)} 문자")
            return self.texts
        except Exception as e:
            logger.error(f"한글 추출 실패: {e}")
            raise
    
    def conversion_token(self) -> List[str]:
        """
        텍스트를 토큰으로 변환
        
        Returns:
            토큰 리스트
        """
        try:
            logger.info("토큰 변환 중...")
            self.tokens = word_tokenize(self.texts)
            logger.info(f"토큰 변환 완료: {len(self.tokens)} 개")
            return self.tokens
        except Exception as e:
            logger.error(f"토큰 변환 실패: {e}")
            raise
    
    def compound_noun(self) -> str:
        """
        복합명사 추출 및 결합
        예: 삼성전자의 스마트폰은 --> 삼성전자 스마트폰
        
        Returns:
            명사로만 구성된 텍스트
        """
        try:
            logger.info("복합명사 추출 중...")
            noun_tokens = []
            for token in self.tokens:
                token_pos = self.okt.pos(token)
                temp = [txt_tag[0] for txt_tag in token_pos if txt_tag[1] == 'Noun']
                if len("".join(temp)) > 1:
                    noun_tokens.append("".join(temp))
            self.texts = " ".join(noun_tokens)
            logger.info(f"복합명사 추출 완료: {len(noun_tokens)} 개")
            return self.texts
        except Exception as e:
            logger.error(f"복합명사 추출 실패: {e}")
            raise
    
    def extract_stopword(self, file_path: str) -> List[str]:
        """
        스톱워드 추출
        
        Args:
            file_path: 스톱워드 파일 경로
        
        Returns:
            스톱워드 리스트
        """
        try:
            logger.info(f"스톱워드 파일 읽기: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                stopwords_text = f.read()
            self.stopwords = stopwords_text.split(' ')
            logger.info(f"스톱워드 추출 완료: {len(self.stopwords)} 개")
            return self.stopwords
        except FileNotFoundError:
            logger.warning(f"스톱워드 파일을 찾을 수 없습니다: {file_path}. 기본 스톱워드를 사용합니다.")
            self.stopwords = ['은', '는', '이', '가', '을', '를', '의', '에', '에서', '와', '과', '도', '로', '으로']
            return self.stopwords
        except Exception as e:
            logger.error(f"스톱워드 추출 실패: {e}")
            self.stopwords = []
            return self.stopwords
    
    def filtering_text_with_stopword(self) -> List[str]:
        """
        스톱워드 필터링
        
        Returns:
            필터링된 토큰 리스트
        """
        try:
            logger.info("스톱워드 필터링 중...")
            self.texts = word_tokenize(self.texts)
            self.texts = [text for text in self.texts if text not in self.stopwords]
            logger.info(f"스톱워드 필터링 완료: {len(self.texts)} 개")
            return self.texts
        except Exception as e:
            logger.error(f"스톱워드 필터링 실패: {e}")
            raise
    
    def frequent_text(self, top_n: int = 100) -> pd.Series:
        """
        빈도수로 정렬
        
        Args:
            top_n: 상위 N개 반환
        
        Returns:
            빈도수로 정렬된 Series
        """
        try:
            logger.info("빈도수 계산 중...")
            self.freqtxt = pd.Series(dict(FreqDist(self.texts))).sort_values(ascending=False)
            logger.info(f"빈도수 계산 완료: {len(self.freqtxt)} 개")
            logger.info(f"상위 {min(top_n, len(self.freqtxt))}개:\n{self.freqtxt[:top_n]}")
            return self.freqtxt
        except Exception as e:
            logger.error(f"빈도수 계산 실패: {e}")
            raise
    
    def generate_wordcloud(
        self,
        output_path: Optional[str] = None,
        font_path: Optional[str] = None,
        width: int = 1200,
        height: int = 1200,
        background_color: str = "white",
        relative_scaling: float = 0.2,
        return_base64: bool = True
    ) -> Dict[str, Any]:
        """
        워드클라우드 생성
        
        Args:
            output_path: 저장할 파일 경로 (None이면 save 폴더에 저장)
            font_path: 폰트 파일 경로 (한글 폰트, 선택적)
            width: 이미지 너비
            height: 이미지 높이
            background_color: 배경색
            relative_scaling: 상대적 크기 조정
            return_base64: Base64 인코딩된 이미지 반환 여부
        
        Returns:
            결과 딕셔너리
        """
        try:
            if len(self.texts) == 0:
                raise ValueError("워드클라우드를 생성할 텍스트가 없습니다.")
            
            logger.info("워드클라우드 생성 중...")
            
            # WordCloud 생성 옵션
            wordcloud_options = {
                'relative_scaling': relative_scaling,
                'background_color': background_color,
                'width': width,
                'height': height
            }
            
            # 폰트 경로가 제공되면 사용
            if font_path and Path(font_path).exists():
                wordcloud_options['font_path'] = font_path
                logger.info(f"폰트 사용: {font_path}")
            
            wcloud = WordCloud(**wordcloud_options).generate(" ".join(self.texts))
            
            # 저장 경로 설정
            if output_path is None:
                save_dir = Path(__file__).parent.parent.parent / "save"
                save_dir.mkdir(exist_ok=True)
                output_path = str(save_dir / "samsung_wordcloud.png")
            
            # 이미지 저장
            plt.figure(figsize=(12, 12))
            plt.imshow(wcloud, interpolation='bilinear')
            plt.axis('off')
            plt.tight_layout(pad=0)
            plt.savefig(output_path, format='png', bbox_inches='tight', dpi=100)
            plt.close()
            
            logger.info(f"워드클라우드 저장 완료: {output_path}")
            
            result = {
                "file_path": output_path,
                "format": "png",
                "width": width,
                "height": height
            }
            
            # Base64도 함께 반환 (요청 시)
            if return_base64:
                with open(output_path, "rb") as f:
                    img_data = f.read()
                img_base64 = base64.b64encode(img_data).decode('utf-8')
                result["image_base64"] = img_base64
            
            return result
        except Exception as e:
            logger.error(f"워드클라우드 생성 실패: {e}")
            raise
    
    def process_full_pipeline(
        self,
        text_file_path: Optional[str] = None,
        stopwords_file_path: Optional[str] = None,
        font_path: Optional[str] = None,
        width: int = 1200,
        height: int = 1200,
        background_color: str = "white",
        relative_scaling: float = 0.2,
        top_n: int = 100,
        return_base64: bool = True
    ) -> Dict[str, Any]:
        """
        전체 처리 파이프라인 실행
        
        Args:
            text_file_path: 텍스트 파일 경로 (None이면 기본값: kr-Report_2018.txt)
            stopwords_file_path: 스톱워드 파일 경로 (None이면 기본값: stopwords.txt)
            font_path: 폰트 파일 경로 (None이면 기본값: D2Coding.ttf)
            width: 워드클라우드 너비
            height: 워드클라우드 높이
            background_color: 배경색
            relative_scaling: 상대적 크기 조정
            top_n: 상위 N개 빈도수 반환
            return_base64: Base64 인코딩된 이미지 반환 여부
        
        Returns:
            처리 결과 딕셔너리
        """
        try:
            # 기본 파일 경로 설정
            if text_file_path is None:
                text_file_path = str(self.default_text_file)
                logger.info(f"기본 텍스트 파일 사용: {text_file_path}")
            
            if stopwords_file_path is None:
                stopwords_file_path = str(self.default_stopwords_file)
                logger.info(f"기본 스톱워드 파일 사용: {stopwords_file_path}")
            
            if font_path is None:
                font_path = str(self.default_font_file)
                logger.info(f"기본 폰트 파일 사용: {font_path}")
            
            # 1. 텍스트 추출
            self.extract_tokens(text_file_path)
            
            # 2. 한글 추출
            self.extract_hangeul()
            
            # 3. 토큰 변환
            self.conversion_token()
            
            # 4. 복합명사 추출
            self.compound_noun()
            
            # 5. 스톱워드 추출 및 필터링
            if stopwords_file_path and Path(stopwords_file_path).exists():
                self.extract_stopword(stopwords_file_path)
            else:
                # 기본 스톱워드 사용
                logger.warning("스톱워드 파일을 찾을 수 없습니다. 기본 스톱워드를 사용합니다.")
                self.stopwords = ['은', '는', '이', '가', '을', '를', '의', '에', '에서', '와', '과', '도', '로', '으로']
            
            self.filtering_text_with_stopword()
            
            # 6. 빈도수 계산
            freq_series = self.frequent_text(top_n=top_n)
            
            # 7. 워드클라우드 생성
            wordcloud_result = self.generate_wordcloud(
                font_path=font_path,
                width=width,
                height=height,
                background_color=background_color,
                relative_scaling=relative_scaling,
                return_base64=return_base64
            )
            
            return {
                "text_length": len(self.texts),
                "token_count": len(self.tokens),
                "filtered_token_count": len(self.texts),
                "stopwords_count": len(self.stopwords),
                "top_frequent_words": freq_series.head(top_n).to_dict(),
                "wordcloud": wordcloud_result
            }
        except Exception as e:
            logger.error(f"전체 처리 파이프라인 실패: {e}")
            raise
