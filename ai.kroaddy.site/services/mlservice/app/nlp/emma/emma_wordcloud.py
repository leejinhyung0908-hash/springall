"""
Emma 워드클라우드 생성 서비스
NLTK를 사용하여 Jane Austen의 Emma 소설에서 워드클라우드를 생성합니다.
"""
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize, RegexpTokenizer
from nltk.stem import PorterStemmer, LancasterStemmer, WordNetLemmatizer
from nltk.tag import pos_tag, untag
from nltk import Text, FreqDist
from nltk.corpus import gutenberg
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')  # GUI 백엔드 없이 사용
import matplotlib.pyplot as plt
import io
import base64

# 공통 모듈 경로 추가
# app/nlp/emma/emma_wordcloud.py -> app/ -> mlservice/ -> ai.kroaddy.site/ -> services/
base_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(base_path))

# 로깅 설정
try:
    from common.utils import setup_logging
    logger = setup_logging("emma_wordcloud")
except ImportError:
    import logging
    logger = logging.getLogger("emma_wordcloud")


class EmmaWordCloudService:
    """Emma 워드클라우드 생성 서비스"""
    
    def __init__(self):
        """서비스 초기화"""
        self.corpus_downloaded = False
        self.emma_raw: Optional[str] = None
        self.text_obj: Optional[Text] = None
        self.fd_names: Optional[FreqDist] = None
        
        # 말뭉치 다운로드
        self._download_corpus()
    
    def _download_corpus(self) -> None:
        """NLTK 말뭉치 다운로드"""
        try:
            nltk.download('book', quiet=True)
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)  # 최신 NLTK 버전에서 필요
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            self.corpus_downloaded = True
            logger.info("NLTK 말뭉치 다운로드 완료")
        except Exception as e:
            logger.error(f"말뭉치 다운로드 실패: {e}")
            self.corpus_downloaded = False
    
    def load_emma_text(self, length: Optional[int] = None) -> str:
        """
        Emma 원문 로드
        
        Args:
            length: 반환할 문자 수 (None이면 전체)
        
        Returns:
            원문 문자열
        """
        try:
            emma_raw = gutenberg.raw("austen-emma.txt")
            if length:
                self.emma_raw = emma_raw[:length]
            else:
                self.emma_raw = emma_raw
            logger.info(f"Emma 원문 로드 완료: {len(self.emma_raw)} 문자")
            return self.emma_raw
        except Exception as e:
            logger.error(f"Emma 원문 로드 실패: {e}")
            return ""
    
    def tokenize_text(self, text: str, method: str = "regex") -> List[str]:
        """
        텍스트 토큰화
        
        Args:
            text: 입력 텍스트
            method: 토큰화 방법 ("word", "regex")
        
        Returns:
            토큰 리스트
        """
        try:
            if method == "word":
                return word_tokenize(text)
            elif method == "regex":
                retokenize = RegexpTokenizer(r"[\w]+")
                return retokenize.tokenize(text)
            else:
                return word_tokenize(text)
        except Exception as e:
            logger.error(f"토큰화 실패: {e}")
            return []
    
    def create_text_object(self, tokens: List[str]) -> Text:
        """
        NLTK Text 객체 생성
        
        Args:
            tokens: 토큰 리스트
        
        Returns:
            Text 객체
        """
        try:
            self.text_obj = Text(tokens, name="Emma")
            logger.info(f"Text 객체 생성 완료: {len(tokens)} 토큰")
            return self.text_obj
        except Exception as e:
            logger.error(f"Text 객체 생성 실패: {e}")
            raise
    
    def extract_proper_nouns(self, tokens: List[str], stopwords: Optional[List[str]] = None) -> List[str]:
        """
        고유명사 추출
        
        Args:
            tokens: 토큰 리스트
            stopwords: 제외할 불용어 리스트
        
        Returns:
            고유명사 리스트
        """
        try:
            if stopwords is None:
                stopwords = ["Mr.", "Mrs.", "Miss", "Mr", "Mrs", "Dear"]
            
            tagged = pos_tag(tokens)
            proper_nouns = [t[0] for t in tagged if t[1] == "NNP" and t[0] not in stopwords]
            logger.info(f"고유명사 추출 완료: {len(proper_nouns)} 개")
            return proper_nouns
        except Exception as e:
            logger.error(f"고유명사 추출 실패: {e}")
            return []
    
    def extract_nouns_from_tokens(self, tokens: List[str], stopwords: Optional[List[str]] = None) -> List[str]:
        """
        토큰에서 명사 추출 (고유명사 + 일반명사)
        
        Args:
            tokens: 토큰 리스트
            stopwords: 제외할 불용어 리스트
        
        Returns:
            명사 리스트
        """
        try:
            if stopwords is None:
                stopwords = ["Mr.", "Mrs.", "Miss", "Mr", "Mrs", "Dear"]
            
            tagged = pos_tag(tokens)
            # NNP (고유명사) + NN (명사) 추출
            nouns = [t[0] for t in tagged if t[1] in ["NN", "NNP", "NNS", "NNPS"] and t[0] not in stopwords]
            logger.info(f"명사 추출 완료: {len(nouns)} 개")
            return nouns
        except Exception as e:
            logger.error(f"명사 추출 실패: {e}")
            return []
    
    def create_freq_dist(self, words: List[str]) -> FreqDist:
        """
        빈도 분포 생성
        
        Args:
            words: 단어 리스트
        
        Returns:
            FreqDist 객체
        """
        try:
            self.fd_names = FreqDist(words)
            logger.info(f"FreqDist 생성 완료: {self.fd_names.N()} 토큰, {self.fd_names.B()} 고유 토큰")
            return self.fd_names
        except Exception as e:
            logger.error(f"FreqDist 생성 실패: {e}")
            raise
    
    def generate_wordcloud(
        self,
        freq_dist: Optional[FreqDist] = None,
        width: int = 1000,
        height: int = 600,
        background_color: str = "white",
        return_base64: bool = True
    ) -> Dict[str, Any]:
        """
        워드클라우드 생성
        
        Args:
            freq_dist: FreqDist 객체 (None이면 self.fd_names 사용)
            width: 이미지 너비
            height: 이미지 높이
            background_color: 배경색
            return_base64: Base64 인코딩된 이미지 반환 여부
        
        Returns:
            결과 딕셔너리 (이미지 Base64 또는 파일 경로)
        """
        try:
            if freq_dist is None:
                if self.fd_names is None:
                    raise ValueError("FreqDist가 생성되지 않았습니다. 먼저 create_freq_dist를 호출하세요.")
                freq_dist = self.fd_names
            
            # 단어 개수 확인
            if freq_dist.N() == 0:
                raise ValueError("워드클라우드를 생성할 단어가 없습니다. FreqDist에 단어가 없습니다.")
            
            # 워드클라우드 생성
            wc = WordCloud(
                width=width,
                height=height,
                background_color=background_color,
                random_state=0
            )
            wc.generate_from_frequencies(freq_dist)
            
            # 항상 save 폴더에 파일 저장
            save_dir = Path(__file__).parent.parent.parent / "save"
            save_dir.mkdir(exist_ok=True)
            output_path = save_dir / "emma_wordcloud.png"
            
            plt.figure(figsize=(10, 6))
            plt.imshow(wc, interpolation='bilinear')
            plt.axis("off")
            plt.tight_layout(pad=0)
            plt.savefig(str(output_path), format='png', bbox_inches='tight', dpi=100)
            plt.close()
            
            logger.info(f"워드클라우드 저장 완료: {output_path}")
            
            result = {
                "file_path": str(output_path),
                "format": "png",
                "width": width,
                "height": height
            }
            
            # Base64도 함께 반환 (요청 시)
            if return_base64:
                # 저장된 파일을 읽어서 Base64로 인코딩
                with open(output_path, "rb") as f:
                    img_data = f.read()
                img_base64 = base64.b64encode(img_data).decode('utf-8')
                result["image_base64"] = img_base64
            
            return result
        except Exception as e:
            logger.error(f"워드클라우드 생성 실패: {e}")
            raise
    
    def get_freq_stats(self, freq_dist: Optional[FreqDist] = None) -> Dict[str, Any]:
        """
        빈도 분포 통계 조회
        
        Args:
            freq_dist: FreqDist 객체 (None이면 self.fd_names 사용)
        
        Returns:
            통계 정보 딕셔너리
        """
        try:
            if freq_dist is None:
                if self.fd_names is None:
                    raise ValueError("FreqDist가 생성되지 않았습니다.")
                freq_dist = self.fd_names
            
            return {
                "total_tokens": freq_dist.N(),
                "unique_tokens": freq_dist.B(),
                "most_common": freq_dist.most_common(10),
                "max_frequency": freq_dist.max(),
                "max_frequency_count": freq_dist[freq_dist.max()]
            }
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")
            return {}
    
    def process_emma_full(
        self,
        text_length: Optional[int] = None,
        stopwords: Optional[List[str]] = None,
        width: int = 1000,
        height: int = 600,
        background_color: str = "white"
    ) -> Dict[str, Any]:
        """
        Emma 전체 처리 파이프라인
        
        Args:
            text_length: 텍스트 길이 제한 (None이면 전체)
            stopwords: 제외할 불용어 리스트
            width: 워드클라우드 너비
            height: 워드클라우드 높이
            background_color: 배경색
        
        Returns:
            처리 결과 딕셔너리
        """
        try:
            # 1. 원문 로드 (text_length가 None이면 기본값 100000 사용)
            if text_length is None:
                text_length = 100000  # 기본값: 10만자
                logger.info(f"text_length가 None이므로 기본값 {text_length}을 사용합니다.")
            
            emma_raw = self.load_emma_text(text_length)
            if not emma_raw or len(emma_raw) == 0:
                raise ValueError("Emma 원문을 로드할 수 없습니다.")
            
            logger.info(f"로드된 텍스트 길이: {len(emma_raw)} 문자")
            
            # 2. 토큰화
            tokens = self.tokenize_text(emma_raw, method="regex")
            logger.info(f"토큰화 완료: {len(tokens)} 개의 토큰")
            
            if len(tokens) == 0:
                raise ValueError("토큰화된 단어가 없습니다. 텍스트 길이를 늘려주세요.")
            
            # 3. Text 객체 생성
            text_obj = self.create_text_object(tokens)
            
            # 4. 고유명사 추출
            proper_nouns = self.extract_proper_nouns(tokens, stopwords)
            logger.info(f"고유명사 추출: {len(proper_nouns)} 개")
            
            # 고유명사가 없으면 일반 명사도 포함
            if len(proper_nouns) == 0:
                logger.warning("고유명사가 없습니다. 일반 명사도 포함합니다.")
                nouns = self.extract_nouns_from_tokens(tokens, stopwords)
                logger.info(f"일반 명사 추출: {len(nouns)} 개")
                if len(nouns) == 0:
                    # 모든 단어 사용 (품사 태깅 실패 시)
                    logger.warning("명사 추출 실패. 상위 빈도 단어를 사용합니다.")
                    # 최소 3글자 이상의 단어만 사용
                    filtered_tokens = [t for t in tokens if len(t) >= 3 and t.isalpha()]
                    if len(filtered_tokens) == 0:
                        raise ValueError("워드클라우드를 생성할 단어가 없습니다. 텍스트 길이를 늘려주세요.")
                    proper_nouns = filtered_tokens
                else:
                    proper_nouns = nouns
            
            # 5. 빈도 분포 생성
            fd_names = self.create_freq_dist(proper_nouns)
            
            # 단어 개수 확인
            if fd_names.N() == 0:
                raise ValueError("워드클라우드를 생성할 단어가 없습니다. 텍스트 길이를 늘려주세요.")
            
            # 6. 통계 조회
            stats = self.get_freq_stats(fd_names)
            
            # 7. 워드클라우드 생성
            wordcloud_result = self.generate_wordcloud(
                freq_dist=fd_names,
                width=width,
                height=height,
                background_color=background_color,
                return_base64=True
            )
            
            return {
                "text_length": len(emma_raw),
                "token_count": len(tokens),
                "proper_noun_count": len(proper_nouns),
                "stats": stats,
                "wordcloud": wordcloud_result
            }
        except Exception as e:
            logger.error(f"Emma 전체 처리 실패: {e}")
            raise

