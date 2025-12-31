from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import os
import re

# 딥러닝 라이브러리 추가
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# 기존 NLP 및 시각화 라이브러리
import nltk
from nltk.tokenize import word_tokenize
from nltk import FreqDist
from konlpy.tag import Okt
import pandas as pd
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg') # GUI 백엔드 없이 사용
import matplotlib.pyplot as plt
import io
import base64

# 로거 설정 (기존 코드에서 logger 설정 부분을 생략하고 필요한 모듈만 추가)
# from common.utils import setup_logging

# @dataclass를 사용하는 경우를 대비하여 정의
@dataclass
class SentimentResult:
    sentence: str
    label: str
    is_positive: int
    confidence: str


class EmotionInference:

    def __init__(self):
        # 1. 로컬 KoELECTRA 모델 로드 설정
        
        # 현재 파일 위치: /app/app/nlp/review/emotion_inference.py
        # 목표 경로: /app/app/resources/koelectra_local
        curr_path = os.path.dirname(os.path.abspath(__file__))
        # 상대 경로: ../.. -> /app/app, resources/koelectra_local
        self.model_path = os.path.abspath(
            os.path.join(curr_path, "..", "..", "resources", "koelectra_local")
        )
        
        print(f"Loading KoELECTRA model from: {self.model_path}")
        
        # 경로가 존재하는지 확인
        if not os.path.exists(self.model_path):
            print(f"Warning: Model path does not exist: {self.model_path}")
            # 대안 경로 시도
            alt_path = os.path.abspath(os.path.join(curr_path, "..", "..", "..", "resources", "koelectra_local"))
            if os.path.exists(alt_path):
                self.model_path = alt_path
                print(f"Using alternative path: {self.model_path}")
        
        try:
            # 2. 로컬 파일에서 토크나이저 및 모델 로드
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            
            # GPU/CPU 설정
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            self.model.eval() # 추론 모드 설정
            print("KoELECTRA 로컬 모델 로드 및 GPU/CPU 설정 완료.")

        except Exception as e:
            print(f"KoELECTRA 모델 로드 실패: {e}")
            self.tokenizer = None
            self.model = None

        # 3. 기타 NLP 도구 초기화
        self.okt = Okt()
        

    def classify(self, text: str) -> Optional[Dict[str, Any]]:
        """
        KoELECTRA 모델을 사용하여 문장의 감성을 분석합니다.
        """
        if self.model is None or self.tokenizer is None:
            return {"error": "Sentiment model not loaded."}
            
        # 4. 전처리 및 추론
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True, 
            max_length=128, 
            padding=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            
            # Softmax를 통해 확률 계산 (0: 부정, 1: 긍정)
            probs = F.softmax(logits, dim=-1)
            result = torch.argmax(probs, dim=-1).item()
            score = probs[0][result].item()

        label = "긍정" if result == 1 else "부정"
        
        return SentimentResult(
            sentence=text,
            label=label,
            is_positive=result,
            confidence=f"{score*100:.2f}%"
        ).__dict__ # 딕셔너리로 반환


    def create_wordcloud(self, text_list: List[str]) -> Optional[str]:
        """
        텍스트 리스트를 형태소 분석하여 워드 클라우드 이미지를 생성하고 Base64 문자열로 반환합니다.
        """
        if not text_list:
            return None
            
        # 텍스트 결합 및 형태소 분석 (KoNLPy Okt 사용)
        text = ' '.join(text_list)
        tokens = self.okt.nouns(text)
        
        # 두 글자 이상인 명사만 사용
        words = [t for t in tokens if len(t) > 1]
        
        # 워드 클라우드 객체 생성 및 생성
        wc = WordCloud(
            font_path='nanumfont', # 폰트 경로 필요
            background_color="white",
            max_words=100,
            width=800,
            height=400
        )
        word_cloud = wc.generate(' '.join(words))

        # 이미지를 Base64 문자열로 인코딩
        buf = io.BytesIO()
        plt.figure(figsize=(10, 5))
        plt.imshow(word_cloud, interpolation='bilinear')
        plt.axis("off")
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()

        # Base64 문자열로 변환
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        return image_base64


# --- 테스트 실행 (선택 사항) ---
if __name__ == "__main__":
    inference = EmotionInference()
    
    # 딥러닝 감성 분석 테스트
    test_sentences = ["정말 인생 최고의 영화였어요!", "돈 주고 보기 아까운 졸작입니다."]
    for sentence in test_sentences:
        res = inference.classify(sentence)
        print(f"Analysis: {res['sentence']} -> {res['label']} ({res['confidence']})")

    # 워드 클라우드 기능 테스트 (예시 데이터)
    sample_text = ["갤럭시 S24 울트라 디자인 정말 예쁘네요.", "이번에 삼성 폰이 너무 비싸게 나온 것 같아요."] * 20
    # base64_image = inference.create_wordcloud(sample_text)
    # print(f"\nWordCloud Base64 String Length: {len(base64_image) if base64_image else 'N/A'}")