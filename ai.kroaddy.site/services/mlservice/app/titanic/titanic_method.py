from pathlib import Path
from typing import Tuple
import pandas as pd
import numpy as np
from pandas import DataFrame
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn import metrics
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from app.titanic.titanic_dataset import TitanicDataSet
import logging

logger = logging.getLogger(__name__)

class TitanicMethod(object): 

    def __init__(self):
        self.dataset = TitanicDataSet()

    def read_csv(self, fname: str) -> pd.DataFrame:
        return pd.read_csv(fname)

    def create_df(self, df: DataFrame, label: str) -> pd.DataFrame:
        """
        DataFrame을 그대로 반환합니다.
        (Survived 컬럼을 학습/평가에 활용하기 위해 제거하지 않습니다.)
        """
        return df

    def create_label(self, df: DataFrame, label: str) -> pd.DataFrame:
        return df[[label]]

    def drop_feature(self, this, *feature: str) -> object:
        [i.drop(j, axis=1, inplace=True) for j in feature for i in [this.train,this.test ] ]

        # for i in [this.train, this.test]:
        #     for j in feature:
        #         i.drop(j, axis=1, inplace=True)
 
        return this

    def check_null(self, data) -> int:
        """
        데이터셋의 null 값 개수를 확인하고 반환
        Args:
            data: DataFrame 또는 TitanicDataSet 객체
        Returns:
            null 값의 총 개수
        """
        if isinstance(data, DataFrame):
            # DataFrame을 직접 받은 경우
            total_nulls = int(data.isnull().sum().sum())
            if total_nulls > 0:
                null_counts = data.isnull().sum()
                null_cols = null_counts[null_counts > 0]
                logger.info(f"[Null 값 확인] 총 {total_nulls}개")
                if len(null_cols) > 0:
                    logger.info(f"  Null이 있는 컬럼:\n{null_cols.to_string()}")
            return total_nulls
        else:
            # TitanicDataSet 객체를 받은 경우
            for dataset_name, dataset in [("Train", data.train), ("Test", data.test)]:
                null_counts = dataset.isnull().sum()
                total_nulls = null_counts.sum()
                logger.info(f"[{dataset_name} Null 값 확인]")
                logger.info(f"  총 Null 값 개수: {total_nulls}개")
                if total_nulls > 0:
                    null_cols = null_counts[null_counts > 0]
                    logger.info(f"  Null이 있는 컬럼:\n{null_cols.to_string()}")
            return int(data.train.isnull().sum().sum() + data.test.isnull().sum().sum())
    
    def extract_title_from_name(self, this):
        # for i in [this.train, this.test]:
        #     i['Title'] = i['Name'].str.extract('([A-Za-z]+)\.', expand=False) 

        [i.__setitem__('Title', i['Name'].str.extract('([A-Za-z]+)\.', expand=False)) 
         for i in [this.train, this.test]]
            # expand=False 는 시리즈 로 추출
        return this
    

    def remove_duplicate_title(self, this):
        a = []
        for i in [this.train, this.test]:
            # a.append(i['Title'].unique())
            a += list(set(i['Title'])) # train, test 두번을 누적해야 해서서
        a = list(set(a)) # train, test 각각은 중복이 아니지만, 합치면서 중복발생
        logger.info(f"[Title 목록] {sorted(a)}")
        # ['Mr', 'Miss', 'Dr', 'Major', 'Sir', 'Ms', 'Master', 'Capt', 'Mme', 'Mrs', 
        #  'Lady', 'Col', 'Rev', 'Countess', 'Don', 'Mlle', 'Dona', 'Jonkheer']
        '''
        ['Mr', 'Sir', 'Major', 'Don', 'Rev', 'Countess', 'Lady', 'Jonkheer', 'Dr',
        'Miss', 'Col', 'Ms', 'Dona', 'Mlle', 'Mme', 'Mrs', 'Master', 'Capt']
        Royal : ['Countess', 'Lady', 'Sir']
        Rare : ['Capt','Col','Don','Dr','Major','Rev','Jonkheer','Dona','Mme' ]
        Mr : ['Mlle']
        Ms : ['Miss']
        Master
        Mrs
        '''
        title_mapping = {'Mr': 1, 'Ms': 2, 'Mrs': 3, 'Master': 4, 'Royal': 5, 'Rare': 6}
        
        return title_mapping
    

    def title_nominal(self, this):
        # Title 매핑 정의
        title_mapping = {
            'Mr': 1,
            'Ms': 2,
            'Mrs': 3,
            'Master': 4,
            'Royal': 5,
            'Rare': 6
        }
        
        for i in [this.train, this.test]:
            i['Title'] = i['Title'].replace(['Countess', 'Lady', 'Sir'], 'Royal')
            i['Title'] = i['Title'].replace(['Capt','Col','Don','Dr','Major','Rev','Jonkheer','Dona','Mme'], 'Rare')
            i['Title'] = i['Title'].replace(['Mlle'], 'Mr')
            i['Title'] = i['Title'].replace(['Miss'], 'Ms')
            # Master 는 변화없음
            # Mrs 는 변화없음
            i['Title'] = i['Title'].fillna(0)
            i['Title'] = i['Title'].map(title_mapping)
            # 매핑되지 않은 값은 0으로 처리
            i['Title'] = i['Title'].fillna(0)
            
        return this      
        


    def pclass_ordinal(self, this):
        return this

    def gender_nominal(self, this):
        """Sex 컬럼을 Gender로 변경하고, male=0, female=1로 매핑한 후 Sex 컬럼 삭제"""
        gender_mapping = {'male': 0, 'female': 1}
        for i in [this.train, this.test]:
            i['Gender'] = i['Sex'].map(gender_mapping)
            i.drop(columns=['Sex'], inplace=True)
        return this

    def age_ratio(self, this):
        """Age 컬럼을 AgeGroup으로 변환한 후, Age 컬럼 삭제하고 AgeGroup을 Age로 이름 변경"""
        self.get_count_of_null(this,"Age")
        for i in [this.train, this.test]:
            i['Age'] = i['Age'].fillna(-0.5)
        self.get_count_of_null(this,"Age")
        train_max_age = max(this.train['Age'])
        test_max_age = max(this.test['Age'])
        max_age = max(train_max_age, test_max_age)
        logger.info(f"[Age 처리] 최고령자: {max_age}세")
        bins = [-1, 0, 5, 12, 18, 24, 35, 60, np.inf]
        labels = ['Unknown','Baby','Child','Teenager','Student','Young Adult','Adult', 'Senior']
        age_mapping = {'Unknown':0 , 'Baby': 1, 'Child': 2, 'Teenager' : 3, 'Student': 4,
                       'Young Adult': 5, 'Adult':6,  'Senior': 7}
        for i in [this.train, this.test]:
            i['AgeGroup'] = pd.cut(i['Age'], bins, labels=labels).map(age_mapping)
            # Age 컬럼 삭제하고 AgeGroup을 Age로 이름 변경
            i.drop(columns=['Age'], inplace=True)
            i.rename(columns={'AgeGroup': 'Age'}, inplace=True)
        
        return this
    
    def get_count_of_null( self, this , feature):
        for dataset_name, dataset in [("Train", this.train), ("Test", this.test)]:
            null_count = dataset[feature].isnull().sum()
            logger.info(f"[{dataset_name}] {feature} 컬럼의 Null 값 개수: {null_count}개")
    

    def fare_ordinal(self, this):
        """Fare 컬럼을 FareBand로 변환한 후, Fare 컬럼 삭제하고 FareBand를 Fare로 이름 변경"""
        for i in [this.train, this.test]:
            i['FareBand'] = pd.qcut(i['Fare'], 4, labels={1,2,3,4})
            # Fare 컬럼 삭제하고 FareBand를 Fare로 이름 변경
            i.drop(columns=['Fare'], inplace=True)
            i.rename(columns={'FareBand': 'Fare'}, inplace=True)

        this.train = this.train.fillna({'Fare': 1})
        this.test = this.test.fillna({'Fare': 1})
        
        return this


    def embarked_nominal(self, this):
        for i in [this.train, this.test]:
            i['Embarked'] = i['Embarked'].fillna('S')# 사우스햄튼이 가장 많으니까
        embarked_mapping = {'S':1, 'C':2, 'Q':3}
        this.train['Embarked'] = this.train['Embarked'].map(embarked_mapping)
        this.test['Embarked'] = this.test['Embarked'].map(embarked_mapping)
        return this

    def kwargs_sample(**kwargs) -> None:
        # for key, value in kwargs.items():
        #     print(f'키워드: {key} 값: {value}')
        {print(''.join(f'키워드: {key} 값: {value}')) for key, value in kwargs.items()}

    def create_k_fold(self):
        k_fold = KFold(n_splits=10, shuffle=True, random_state=0)
        return k_fold

    def accuracy_by_knn(self, model, dummy) -> str:
        clf = KNeighborsClassifier(n_neighbors=13)
        scoring = 'accuracy'
        k_fold = self.create_k_fold()
        score = cross_val_score(clf, model, dummy, cv=k_fold,
                                n_jobs=1, scoring=scoring)
        accuracy = round(np.mean(score) * 100, 2)
        return accuracy
    def accuracy_by_dtree(self, model, dummy) -> str:
        print('>>> 결정트리 방식 검증')  # 79.58
        k_fold = self.create_k_fold()
        clf = DecisionTreeClassifier()
        scoring = 'accuracy'
        score = cross_val_score(clf, model, dummy, cv=k_fold,
                                n_jobs=1, scoring=scoring)
        accuracy = round(np.mean(score) * 100, 2)
        return accuracy
    def accuracy_by_rforest(self, model, dummy) -> str:
        print('>>> 램덤포레스트 방식 검증')  # 82.15
        k_fold = self.create_k_fold()
        clf = RandomForestClassifier(n_estimators=13)  # 13개의 결정트리를 사용함
        scoring = 'accuracy'
        score = cross_val_score(clf, model, dummy, cv=k_fold,
                                n_jobs=1, scoring=scoring)
        accuracy = round(np.mean(score) * 100, 2)
        return accuracy
    def accuracy_by_nb(self, model, dummy) -> str:
        print('>>> 나이브베이즈 방식 검증')  # 79.57
        clf = GaussianNB()
        k_fold = self.create_k_fold()
        scoring = 'accuracy'
        score = cross_val_score(clf, model, dummy, cv=k_fold,
                                n_jobs=1, scoring=scoring)
        accuracy = round(np.mean(score) * 100, 2)
        return accuracy
    def accuracy_by_svm(self, model, dummy) -> str:
        k_fold = self.create_k_fold()
        print('>>> SVM 방식 검증')  # 83.05
        clf = SVC()
        scoring = 'accuracy'
        score = cross_val_score(clf, model, dummy, cv=k_fold,
                                n_jobs=1, scoring=scoring)
        accuracy = round(np.mean(score) * 100, 2)
        return accuracy

