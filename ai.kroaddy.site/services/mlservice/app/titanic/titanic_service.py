"""
타이타닉 데이터 서비스
판다스, 넘파이, 사이킷런을 사용한 데이터 처리 및 머신러닝 서비스
"""
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any, ParamSpecArgs
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# LightGBM import (선택적)
try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
from app.titanic.titanic_method import TitanicMethod
from app.titanic.titanic_dataset import TitanicDataSet

# 공통 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# 로깅 설정
try:
    from common.utils import setup_logging
    logger = setup_logging("titanic_service")
except ImportError:
    import logging
    logger = logging.getLogger("titanic_service")

# LightGBM 경고 메시지
if not LIGHTGBM_AVAILABLE:
    logger.warning("LightGBM이 설치되지 않았습니다. LightGBM 모델을 사용할 수 없습니다.")


class TitanicService:
    """타이타닉 데이터 처리 및 머신러닝 서비스"""
    
    def __init__(self):
        # CSV 파일 경로 설정
        # titanic_service.py 위치: app/titanic/titanic_service.py
        # CSV 파일 위치: app/resources/titanic/
        current_file = Path(__file__).resolve()
        # app/titanic/titanic_service.py -> app/ -> app/resources/titanic/
        app_dir = current_file.parent.parent  # app/
        resources_dir = app_dir / "resources" / "titanic"
        
        self.train_csv_path = resources_dir / "train.csv"
        self.test_csv_path = resources_dir / "test.csv"
        
        # 전처리된 데이터 저장용
        self.processed_data: Optional[TitanicDataSet] = None
        self.models: Dict[str, Any] = {}
        
        # 경로 검증
        if not self.train_csv_path.exists():
            logger.warning(f"Train CSV 파일을 찾을 수 없습니다: {self.train_csv_path}")
        if not self.test_csv_path.exists():
            logger.warning(f"Test CSV 파일을 찾을 수 없습니다: {self.test_csv_path}")
    
    def _get_csv_path(self, filename: str) -> Path:
        """
        CSV 파일의 전체 경로를 반환
        Args:
            filename: CSV 파일명 (train.csv 또는 test.csv)
        Returns:
            CSV 파일의 Path 객체
        """
        if filename == "train.csv":
            return self.train_csv_path
        elif filename == "test.csv":
            return self.test_csv_path
        else:
            # 기본적으로 resources/titanic 폴더에서 찾기
            current_file = Path(__file__).resolve()
            app_dir = current_file.parent.parent  # app/
            resources_dir = app_dir / "resources" / "titanic"
            return resources_dir / filename

    def preprocess(self) -> Dict[str, Any]:
        """
        타이타닉 데이터 전처리 실행
        Returns:
            전처리 결과 정보 딕셔너리
        """
        logger.info("=" * 80)
        logger.info("전처리 시작")
        logger.info("=" * 80)
        
        the_method = TitanicMethod()

        train_csv_path = self._get_csv_path('train.csv')
        logger.info(f"Train CSV 파일 경로: {train_csv_path}")
        logger.info(f"Train CSV 파일 존재 여부: {train_csv_path.exists()}")
        
        df_train = the_method.read_csv(str(train_csv_path))
        # Survived 라벨을 유지한 상태로 복사 (평가 시 필요)
        this_train = df_train.copy()
        
        logger.info("-" * 80)
        logger.info("[Train 데이터셋 정보]")
        logger.info(f"  타입: {type(this_train).__name__}")
        logger.info(f"  컬럼 수: {len(this_train.columns)}")
        logger.info(f"  컬럼 목록: {', '.join(this_train.columns.tolist())}")
        logger.info(f"  행 수: {len(this_train)}")
        logger.info(f"  Null 값 개수: {the_method.check_null(this_train)}개")
        logger.info("-" * 80)
        logger.info("[Train 데이터 상위 5개 행]")
        logger.info(f"\n{this_train.head(5).to_string()}\n")

        test_csv_path = self._get_csv_path('test.csv')
        logger.info(f"Test CSV 파일 경로: {test_csv_path}")
        logger.info(f"Test CSV 파일 존재 여부: {test_csv_path.exists()}")
        
        df_test = the_method.read_csv(str(test_csv_path))
        this_test = the_method.create_df(df_test, 'Survived')
        
        logger.info("-" * 80)
        logger.info("[Test 데이터셋 정보]")
        logger.info(f"  타입: {type(this_test).__name__}")
        logger.info(f"  컬럼 수: {len(this_test.columns)}")
        logger.info(f"  컬럼 목록: {', '.join(this_test.columns.tolist())}")
        logger.info(f"  행 수: {len(this_test)}")
        logger.info(f"  Null 값 개수: {the_method.check_null(this_test)}개")
        logger.info("-" * 80)
        logger.info("[Test 데이터 상위 5개 행]")
        logger.info(f"\n{this_test.head(5).to_string()}\n")
        
        this = TitanicDataSet()

        this.train = this_train
        this.test = this_test

        drop_features = ['SibSp', 'Parch', 'Cabin', 'Ticket']
        this = the_method.drop_feature(this, *drop_features)
        this = the_method.pclass_ordinal(this)
        this = the_method.fare_ordinal(this)
        this = the_method.embarked_nominal(this)
        this = the_method.gender_nominal(this)
        this = the_method.extract_title_from_name(this)  # Name에서 Title 추출
        this = the_method.age_ratio(this)
        this = the_method.title_nominal(this)
        drop_name = ['Name']
        this = the_method.drop_feature(this, *drop_name)

        logger.info("=" * 80)
        logger.info("[Train 전처리 완료]")
        logger.info("-" * 80)
        logger.info(f"  타입: {type(this.train).__name__}")
        logger.info(f"  컬럼 수: {len(this.train.columns)}")
        logger.info(f"  컬럼 목록: {', '.join(this.train.columns.tolist())}")
        logger.info(f"  행 수: {len(this.train)}")
        logger.info(f"  Null 값 개수: {the_method.check_null(this.train)}개")
        logger.info("-" * 80)
        logger.info("[Train 전처리 후 상위 5개 행]")
        logger.info(f"\n{this.train.head(5).to_string()}\n")

        logger.info("=" * 80)
        logger.info("[Test 전처리 완료]")
        logger.info("-" * 80)
        logger.info(f"  타입: {type(this.test).__name__}")
        logger.info(f"  컬럼 수: {len(this.test.columns)}")
        logger.info(f"  컬럼 목록: {', '.join(this.test.columns.tolist())}")
        logger.info(f"  행 수: {len(this.test)}")
        logger.info(f"  Null 값 개수: {the_method.check_null(this.test)}개")
        logger.info("-" * 80)
        logger.info("[Test 전처리 후 상위 5개 행]")
        logger.info(f"\n{this.test.head(5).to_string()}\n")
        
        # 전처리된 데이터 저장
        self.processed_data = this
        
        # 전처리 결과 정보 반환
        return {
            "status": "success",
            "rows": len(this_train),
            "columns": this_train.columns.tolist(),
            "column_count": len(this_train.columns),
            "null_count": int(the_method.check_null(this_train)),
            "sample_data": this_train.head(5).to_dict(orient="records"),
            "dtypes": this_train.dtypes.astype(str).to_dict()
        }

    def modeling(self):
        """모델 초기화"""
        logger.info("=" * 80)
        logger.info("모델링 시작")
        logger.info("=" * 80)
        
        # 로지스틱 회귀
        self.models['logistic_regression'] = LogisticRegression(random_state=42, max_iter=1000)
        logger.info("로지스틱 회귀 모델 초기화 완료")
        
        # 나이브 베이즈
        self.models['naive_bayes'] = GaussianNB()
        logger.info("나이브 베이즈 모델 초기화 완료")
        
        # 랜덤 포레스트
        self.models['random_forest'] = RandomForestClassifier(n_estimators=100, random_state=42)
        logger.info("랜덤 포레스트 모델 초기화 완료")
        
        # LightGBM
        if LIGHTGBM_AVAILABLE:
            self.models['lightgbm'] = lgb.LGBMClassifier(random_state=42, verbose=-1)
            logger.info("LightGBM 모델 초기화 완료")
        else:
            logger.warning("LightGBM이 설치되지 않아 모델을 초기화하지 않았습니다.")
        
        # SVM
        self.models['svm'] = SVC(random_state=42, probability=True)
        logger.info("SVM 모델 초기화 완료")
        
        logger.info("=" * 80)
        logger.info("모델링 완료")
        logger.info("=" * 80)
        
        return self.models

    def learning(self):
        """모델 학습 (K-Fold 교차 검증을 사용하므로 별도 학습 불필요)"""
        logger.info("=" * 80)
        logger.info("학습 시작")
        logger.info("=" * 80)
        
        if self.processed_data is None:
            raise ValueError("전처리된 데이터가 없습니다. 먼저 preprocess()를 실행해주세요.")
        
        # 전처리된 데이터 준비
        train_data = self.processed_data.train.copy()
        
        # Survived 컬럼이 있는지 확인 (train 데이터에만 있음)
        if 'Survived' not in train_data.columns:
            raise ValueError("Survived 컬럼을 찾을 수 없습니다. 전처리 과정을 확인해주세요.")
        
        # 피처와 타겟 분리
        X_train = train_data.drop(columns=['Survived'])
        y_train = train_data['Survived']
        
        # 데이터 타입 확인 및 변환
        X_train = X_train.select_dtypes(include=[np.number])  # 숫자형 컬럼만 선택
        
        logger.info(f"학습 데이터 shape: {X_train.shape}")
        logger.info(f"학습 피처: {X_train.columns.tolist()}")
        
        logger.info("K-Fold 교차 검증을 사용하므로 별도 학습 단계는 필요하지 않습니다.")
        logger.info("evaluate() 메서드에서 자동으로 학습 및 평가가 수행됩니다.")
        
        logger.info("=" * 80)
        logger.info("학습 완료")
        logger.info("=" * 80)
        
        return {"status": "ready_for_evaluation"}

    def evaluate(self) -> Dict[str, Any]:
        """모델 평가 - K-Fold 교차 검증 사용"""
        logger.info("=" * 80)
        logger.info("평가 시작 (K-Fold 교차 검증)")
        logger.info("=" * 80)
        
        if self.processed_data is None:
            raise ValueError("전처리된 데이터가 없습니다. 먼저 preprocess()를 실행해주세요.")
        
        # 전처리된 데이터 준비
        train_data = self.processed_data.train.copy()
        
        # 피처와 타겟 분리
        X_train = train_data.drop(columns=['Survived'])
        y_train = train_data['Survived']
        
        # 데이터 타입 확인 및 변환
        X_train = X_train.select_dtypes(include=[np.number])  # 숫자형 컬럼만 선택
        
        logger.info(f"평가 데이터 shape: {X_train.shape}")
        logger.info(f"평가 피처: {X_train.columns.tolist()}")
        
        # TitanicMethod 인스턴스 생성 (K-Fold 교차 검증 메서드 사용)
        the_method = TitanicMethod()
        
        # 각 모델 평가 (K-Fold 교차 검증)
        results = {}
        
        # KNN 평가
        try:
            logger.info("- KNN 평가 중...")
            accuracy = the_method.accuracy_by_knn(X_train.values, y_train.values)
            results['knn'] = {
                "accuracy": float(accuracy),
                "status": "success"
            }
            logger.info(f"  KNN 검증 정확도: {accuracy}%")
        except Exception as e:
            logger.error(f"  KNN 평가 실패: {str(e)}")
            results['knn'] = {
                "accuracy": None,
                "status": f"error: {str(e)}"
            }
        
        # Decision Tree 평가
        try:
            logger.info("- Decision Tree 평가 중...")
            accuracy = the_method.accuracy_by_dtree(X_train.values, y_train.values)
            results['decision_tree'] = {
                "accuracy": float(accuracy),
                "status": "success"
            }
            logger.info(f"  Decision Tree 검증 정확도: {accuracy}%")
        except Exception as e:
            logger.error(f"  Decision Tree 평가 실패: {str(e)}")
            results['decision_tree'] = {
                "accuracy": None,
                "status": f"error: {str(e)}"
            }
        
        # Random Forest 평가
        try:
            logger.info("- Random Forest 평가 중...")
            accuracy = the_method.accuracy_by_rforest(X_train.values, y_train.values)
            results['random_forest'] = {
                "accuracy": float(accuracy),
                "status": "success"
            }
            logger.info(f"  Random Forest 검증 정확도: {accuracy}%")
        except Exception as e:
            logger.error(f"  Random Forest 평가 실패: {str(e)}")
            results['random_forest'] = {
                "accuracy": None,
                "status": f"error: {str(e)}"
            }
        
        # Naive Bayes 평가
        try:
            logger.info("- Naive Bayes 평가 중...")
            accuracy = the_method.accuracy_by_nb(X_train.values, y_train.values)
            results['naive_bayes'] = {
                "accuracy": float(accuracy),
                "status": "success"
            }
            logger.info(f"  Naive Bayes 검증 정확도: {accuracy}%")
        except Exception as e:
            logger.error(f"  Naive Bayes 평가 실패: {str(e)}")
            results['naive_bayes'] = {
                "accuracy": None,
                "status": f"error: {str(e)}"
            }
        
        # SVM 평가
        try:
            logger.info("- SVM 평가 중...")
            accuracy = the_method.accuracy_by_svm(X_train.values, y_train.values)
            results['svm'] = {
                "accuracy": float(accuracy),
                "status": "success"
            }
            logger.info(f"  SVM 검증 정확도: {accuracy}%")
        except Exception as e:
            logger.error(f"  SVM 평가 실패: {str(e)}")
            results['svm'] = {
                "accuracy": None,
                "status": f"error: {str(e)}"
            }
        
        logger.info("=" * 80)
        logger.info("평가 완료")
        logger.info("=" * 80)
        
        # 요약 정보
        summary = {
            "best_model": max(
                [(name, result["accuracy"]) for name, result in results.items() 
                 if result.get("accuracy") is not None],
                key=lambda x: x[1],
                default=(None, None)
            )[0] if any(r.get("accuracy") is not None for r in results.values()) else None,
            "results": results
        }
        
        return summary

    def submit(self):
        """Kaggle 제출용 CSV 생성 (SVM 사용)"""
        logger.info("=" * 80)
        logger.info("제출 시작 (SVM 전체 학습 후 예측)")
        logger.info("=" * 80)

        # 전처리 확인
        if self.processed_data is None:
            logger.info("전처리가 수행되지 않아 preprocess()를 먼저 실행합니다.")
            self.preprocess()

        # 전처리된 데이터
        train_data = self.processed_data.train.copy()
        test_data = self.processed_data.test.copy()

        # Survived 존재 여부 확인
        if "Survived" not in train_data.columns:
            raise ValueError("Survived 컬럼이 없어 제출 파일을 생성할 수 없습니다.")

        # 피처/타겟 분리
        X_train = train_data.drop(columns=["Survived"])
        y_train = train_data["Survived"]
        X_train = X_train.select_dtypes(include=[np.number])
        X_test = test_data.select_dtypes(include=[np.number])

        # SVM 학습 (전체 데이터)
        svm_model = SVC(random_state=42, probability=True)
        logger.info("SVM 전체 학습 중...")
        svm_model.fit(X_train, y_train)
        logger.info("SVM 전체 학습 완료")

        # 예측
        logger.info("SVM 테스트 예측 중...")
        test_pred = svm_model.predict(X_test)
        logger.info("SVM 테스트 예측 완료")

        # 제출 DataFrame 구성
        submission = pd.DataFrame({
            "PassengerId": test_data["PassengerId"],
            "Survived": test_pred.astype(int)
        })

        # 저장 경로
        submission_path = self.test_csv_path.parent / "submission.csv"
        submission.to_csv(submission_path, index=False)
        logger.info(f"제출 파일 저장 완료: {submission_path}")

        logger.info("=" * 80)
        logger.info("제출 완료")
        logger.info("=" * 80)

        return {
            "status": "success",
            "saved_path": str(submission_path),
            "rows": len(submission),
            "head": submission.head(5).to_dict(orient="records")
        }