"""
서울시 구별 범죄 발생 히트맵 생성 스크립트
crime_processed.csv 데이터를 기반으로 정규화된 범죄 발생 히트맵을 생성합니다.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

def load_and_process_data(crime_csv_path: str, pop_csv_path: str = None, use_population: bool = True):
    """
    CSV 파일을 로드하고 자치구별로 집계하여 정규화합니다.
    인구수를 반영하여 범죄율(인구 대비 범죄 발생률)을 계산할 수 있습니다.
    
    Args:
        crime_csv_path: crime_processed.csv 파일 경로
        pop_csv_path: pop_processed.csv 파일 경로 (인구수 데이터)
        use_population: 인구수를 반영할지 여부 (기본값: True)
        
    Returns:
        정규화된 범죄 데이터프레임
    """
    # 범죄 데이터 읽기
    df = pd.read_csv(crime_csv_path)
    
    # 숫자 컬럼의 쉼표 제거 및 변환
    numeric_columns = ['살인 발생', '강도 발생', '강간 발생', '절도 발생', '폭력 발생']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '').astype(float)
    
    # 자치구별로 집계 (합산)
    grouped = df.groupby('자치구')[numeric_columns].sum().reset_index()
    
    # 인구수 데이터 로드 및 병합
    if use_population and pop_csv_path:
        pop_path = Path(pop_csv_path)
        if pop_path.exists():
            try:
                # 첫 번째 줄이 헤더인 경우와 두 번째 줄이 헤더인 경우 모두 처리
                pop_df = pd.read_csv(pop_path, skiprows=1)  # 첫 번째 줄(잘못된 헤더) 건너뛰기
                
                # 인구수 컬럼명 확인 및 정리
                if '인구' in pop_df.columns:
                    pop_df = pop_df.rename(columns={'인구': '인구수'})
                elif '합계' in pop_df.columns:
                    pop_df = pop_df.rename(columns={'합계': '인구수'})
                
                # 인구수 컬럼이 숫자가 아닌 경우 처리
                if '인구수' in pop_df.columns:
                    pop_df['인구수'] = pd.to_numeric(pop_df['인구수'], errors='coerce')
                
                # 자치구명으로 병합
                grouped = grouped.merge(pop_df[['자치구', '인구수']], on='자치구', how='left')
                
                # 결측치가 있는 경우 경고
                if grouped['인구수'].isna().any():
                    missing_gu = grouped[grouped['인구수'].isna()]['자치구'].tolist()
                    print(f"경고: 다음 자치구의 인구수 데이터가 없습니다: {missing_gu}")
                    # 결측치를 평균값으로 채우기
                    grouped['인구수'] = grouped['인구수'].fillna(grouped['인구수'].mean())
                
                # 인구수로 나누어 범죄율 계산 (인구 10만명당 범죄 발생 건수)
                for col in numeric_columns:
                    grouped[f'{col}_범죄율'] = (grouped[col] / grouped['인구수']) * 100000
                
                # 범죄율 컬럼으로 교체
                crime_rate_columns = [f'{col}_범죄율' for col in numeric_columns]
                # 범죄율 데이터로 정규화
                normalized_data = grouped[['자치구'] + crime_rate_columns].copy()
                normalized_data.columns = ['자치구'] + numeric_columns
                
                print("인구수를 반영하여 범죄율(인구 10만명당)을 계산했습니다.")
            except Exception as e:
                print(f"경고: 인구수 데이터 처리 중 오류 발생: {e}")
                print("범죄 발생 건수만 사용합니다.")
                use_population = False
        else:
            print(f"경고: 인구수 파일을 찾을 수 없습니다. 범죄 발생 건수만 사용합니다.")
            use_population = False
    
    # 인구수를 사용하지 않는 경우 원래 방식 사용
    if not use_population or '인구수' not in grouped.columns:
        normalized_data = grouped.copy()
    
    # 각 범죄 유형별로 정규화 (0-1 사이)
    for col in numeric_columns:
        min_val = normalized_data[col].min()
        max_val = normalized_data[col].max()
        if max_val > min_val:
            normalized_data[col] = (normalized_data[col] - min_val) / (max_val - min_val)
        else:
            normalized_data[col] = 0.0
    
    # 전체 범죄 합계 계산 (정규화된 값들의 평균)
    normalized_data['범죄'] = normalized_data[numeric_columns].mean(axis=1)
    
    # 전체 범죄 기준으로 내림차순 정렬
    normalized_data = normalized_data.sort_values('범죄', ascending=False)
    
    return normalized_data

def create_heatmap(data: pd.DataFrame, output_path: str = None):
    """
    범죄 데이터를 히트맵으로 시각화합니다.
    
    Args:
        data: 정규화된 범죄 데이터프레임
        output_path: 저장할 파일 경로 (None이면 화면에 표시)
    """
    # 히트맵용 데이터 준비
    # 컬럼 순서: 강간, 강도, 살인, 절도, 폭력, 범죄
    heatmap_data = data[['강간 발생', '강도 발생', '살인 발생', '절도 발생', '폭력 발생', '범죄']].copy()
    heatmap_data.columns = ['강간', '강도', '살인', '절도', '폭력', '범죄']
    
    # 행 인덱스를 자치구명으로 설정
    heatmap_data.index = data['자치구'].values
    
    # 그림 크기 설정 (이미지와 유사한 비율)
    fig, ax = plt.subplots(figsize=(10, 14))
    
    # 히트맵 생성 (magma 또는 viridis 색상맵 사용)
    sns.heatmap(
        heatmap_data,
        annot=True,  # 숫자 표시
        fmt='.6f',  # 소수점 6자리까지 표시
        cmap='magma_r',  # 보라색-핑크 계열 (역순으로 높은 값이 어둡게)
        cbar_kws={'label': '정규화된 값'},
        linewidths=0.5,
        linecolor='gray',
        ax=ax
    )
    
    # 제목 설정
    ax.set_title('구별 범죄 발생 (정규화된 발생 건수의 값으로 정렬)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # 축 레이블 설정
    ax.set_xlabel('범죄 유형', fontsize=12)
    ax.set_ylabel('자치구', fontsize=12)
    
    # y축 레이블 회전 (가독성 향상)
    plt.yticks(rotation=0)
    plt.xticks(rotation=0)
    
    # 레이아웃 조정
    plt.tight_layout()
    
    # 저장 또는 표시
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"히트맵이 저장되었습니다: {output_path}")
    else:
        plt.show()
    
    plt.close()

def main():
    """메인 함수"""
    # 파일 경로 설정
    script_dir = Path(__file__).parent
    crime_csv_path = script_dir / 'save' / 'crime_processed.csv'
    pop_csv_path = script_dir / 'save' / 'pop_processed.csv'
    output_path = script_dir / 'save' / 'crime_heatmap.png'
    
    # 파일 존재 확인
    if not crime_csv_path.exists():
        print(f"오류: {crime_csv_path} 파일을 찾을 수 없습니다.")
        return
    
    print("데이터 로딩 중...")
    # 데이터 로드 및 처리 (인구수 반영)
    normalized_data = load_and_process_data(
        str(crime_csv_path),
        str(pop_csv_path) if pop_csv_path.exists() else None,
        use_population=True
    )
    
    print("히트맵 생성 중...")
    # 히트맵 생성
    create_heatmap(normalized_data, str(output_path))
    
    print("\n처리된 데이터 미리보기:")
    print(normalized_data.head(10))
    
    print(f"\n히트맵 생성 완료: {output_path}")

if __name__ == "__main__":
    main()

