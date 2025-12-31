"""
서울시 범죄 발생 건수와 CCTV 상관관계 지도 시각화 스크립트
crime_processed.csv와 cctv_processed.csv 데이터를 기반으로 지도에 시각화합니다.
"""
import pandas as pd
import numpy as np
import folium
from folium import plugins
from pathlib import Path
import json

def load_and_merge_data(crime_csv_path: str, cctv_csv_path: str, locations_csv_path: str):
    """
    범죄, CCTV, 위치 데이터를 로드하고 통합합니다.
    
    Args:
        crime_csv_path: crime_processed.csv 파일 경로
        cctv_csv_path: cctv_processed.csv 파일 경로
        locations_csv_path: locations.csv 파일 경로
        
    Returns:
        통합된 데이터프레임
    """
    # 범죄 데이터 로드
    crime_df = pd.read_csv(crime_csv_path)
    
    # 숫자 컬럼의 쉼표 제거 및 변환
    numeric_columns = ['살인 발생', '강도 발생', '강간 발생', '절도 발생', '폭력 발생']
    
    for col in numeric_columns:
        if col in crime_df.columns:
            crime_df[col] = crime_df[col].astype(str).str.replace(',', '').astype(float)
    
    # 자치구별로 범죄 발생 건수 집계
    crime_grouped = crime_df.groupby('자치구')[numeric_columns].sum().reset_index()
    crime_grouped['총 범죄 발생'] = crime_grouped[numeric_columns].sum(axis=1)
    
    # CCTV 데이터 로드
    cctv_df = pd.read_csv(cctv_csv_path)
    cctv_df = cctv_df.rename(columns={'기관명': '자치구', '소계': 'CCTV 개수'})
    
    # 위치 데이터 로드 (자치구별 중심 좌표)
    locations_df = pd.read_csv(locations_csv_path)
    locations_grouped = locations_df.groupby('자치구').agg({
        '위도': 'mean',
        '경도': 'mean'
    }).reset_index()
    
    # 데이터 병합
    merged_df = crime_grouped.merge(cctv_df, on='자치구', how='outer')
    merged_df = merged_df.merge(locations_grouped, on='자치구', how='left')
    
    # 결측치 처리
    merged_df['CCTV 개수'] = merged_df['CCTV 개수'].fillna(0)
    merged_df['총 범죄 발생'] = merged_df['총 범죄 발생'].fillna(0)
    
    # 상관관계 계산을 위한 정규화
    merged_df['범죄 정규화'] = (merged_df['총 범죄 발생'] - merged_df['총 범죄 발생'].min()) / \
                              (merged_df['총 범죄 발생'].max() - merged_df['총 범죄 발생'].min() + 1e-10)
    merged_df['CCTV 정규화'] = (merged_df['CCTV 개수'] - merged_df['CCTV 개수'].min()) / \
                              (merged_df['CCTV 개수'].max() - merged_df['CCTV 개수'].min() + 1e-10)
    
    # 상관관계 점수 계산 (범죄 대비 CCTV 비율)
    # CCTV가 많고 범죄가 적으면 좋은 점수, 범죄가 많고 CCTV가 적으면 나쁜 점수
    merged_df['CCTV_범죄_비율'] = merged_df['CCTV 개수'] / (merged_df['총 범죄 발생'] + 1)
    merged_df['상관관계 점수'] = merged_df['CCTV 정규화'] - merged_df['범죄 정규화']
    
    return merged_df

def create_interactive_map(data: pd.DataFrame, geojson_path: str, output_path: str = None):
    """
    범죄와 CCTV 상관관계를 지도에 시각화합니다.
    Choropleth 맵과 비례 기호를 함께 사용합니다.
    
    Args:
        data: 통합된 데이터프레임
        geojson_path: 서울시 자치구 GeoJSON 파일 경로
        output_path: 저장할 HTML 파일 경로
    """
    # GeoJSON 파일 로드
    with open(geojson_path, 'r', encoding='utf-8') as f:
        seoul_geojson = json.load(f)
    
    # 서울시 중심 좌표
    seoul_center = [37.5665, 126.9780]
    
    # 지도 생성
    m = folium.Map(
        location=seoul_center,
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # 데이터에 CCTV/범죄 비율을 정규화 (0-1 사이)
    data['CCTV_범죄_비율_정규화'] = (data['CCTV_범죄_비율'] - data['CCTV_범죄_비율'].min()) / \
                                   (data['CCTV_범죄_비율'].max() - data['CCTV_범죄_비율'].min() + 1e-10)
    
    # Choropleth 맵을 위한 데이터 준비 (GeoJSON의 id와 매칭)
    choropleth_df_data = []
    for idx, row in data.iterrows():
        gu_name = row['자치구']
        # GeoJSON에서 해당 자치구 찾기
        for feature in seoul_geojson['features']:
            if feature['properties']['name'] == gu_name:
                choropleth_df_data.append({
                    '자치구': feature['id'],  # GeoJSON의 id 사용
                    '값': row['CCTV_범죄_비율_정규화']
                })
                break
    
    choropleth_df = pd.DataFrame(choropleth_df_data)
    
    # Choropleth 레이어 추가 (CCTV/범죄 비율을 색상으로 표시)
    if len(choropleth_df) > 0:
        folium.Choropleth(
            geo_data=seoul_geojson,
            data=choropleth_df,
            columns=['자치구', '값'],
            key_on='feature.id',
            fill_color='RdPu',  # Red-Purple 색상맵 (연한 핑크에서 진한 보라색)
            fill_opacity=0.7,
            line_opacity=0.8,
            line_weight=1,
            line_color='white',
            legend_name='CCTV/범죄 비율 (정규화)',
            smooth_factor=0
        ).add_to(m)
    
    # CCTV/범죄 비율을 색상으로 매핑하기 위한 정규화
    min_ratio = data['CCTV_범죄_비율'].min()
    max_ratio = data['CCTV_범죄_비율'].max()
    
    # 색상맵 함수 (RdYlGn: 빨강-노랑-초록)
    def get_color_by_ratio(ratio, min_val, max_val):
        """CCTV/범죄 비율에 따라 색상을 반환 (낮을수록 빨강, 높을수록 초록)"""
        if max_val == min_val:
            normalized = 0.5
        else:
            normalized = (ratio - min_val) / (max_val - min_val)
        
        # RdYlGn 색상맵 (빨강 -> 노랑 -> 초록)
        if normalized < 0.2:
            return '#d73027'  # 빨강 (낮은 비율)
        elif normalized < 0.4:
            return '#f46d43'  # 주황-빨강
        elif normalized < 0.6:
            return '#fee08b'  # 노랑
        elif normalized < 0.8:
            return '#abdda4'  # 연두
        else:
            return '#66bd63'  # 초록 (높은 비율)
    
    # 비례 기호 추가 (CCTV 비율에 따라 색상 구분, 크기는 CCTV 개수에 비례)
    for idx, row in data.iterrows():
        if pd.isna(row['위도']) or pd.isna(row['경도']):
            continue
            
        crime_total = row['총 범죄 발생']
        cctv_count = row['CCTV 개수']
        cctv_crime_ratio = row['CCTV_범죄_비율']
        
        # 마커 크기 결정 (CCTV 개수에 비례, 지역 경계에 맞게 크게 설정)
        # 최소 40, 최대 120으로 설정하여 자치구 영역을 더 잘 덮도록 함
        marker_size = max(40, min(120, int(cctv_count / 25)))
        
        # CCTV/범죄 비율에 따른 색상 결정
        marker_color = get_color_by_ratio(cctv_crime_ratio, min_ratio, max_ratio)
        
        # 팝업 내용 생성
        popup_html = f"""
        <div style="font-family: Malgun Gothic; width: 250px;">
            <h3 style="margin: 5px 0;">{row['자치구']}</h3>
            <hr style="margin: 5px 0;">
            <p style="margin: 3px 0;"><b>총 범죄 발생:</b> {int(crime_total):,}건</p>
            <p style="margin: 3px 0;"><b>CCTV 개수:</b> {int(cctv_count):,}대</p>
            <p style="margin: 3px 0;"><b>CCTV/범죄 비율:</b> {cctv_crime_ratio:.2f}</p>
            <hr style="margin: 5px 0;">
            <p style="margin: 3px 0; font-size: 11px;">
                <b>범죄 상세:</b><br>
                살인: {int(row['살인 발생'])}건 | 
                강도: {int(row['강도 발생'])}건<br>
                강간: {int(row['강간 발생'])}건 | 
                절도: {int(row['절도 발생'])}건<br>
                폭력: {int(row['폭력 발생'])}건
            </p>
        </div>
        """
        
        # 원형 마커 추가 (CCTV 비율에 따라 색상 구분)
        folium.CircleMarker(
            location=[row['위도'], row['경도']],
            radius=marker_size,
            popup=folium.Popup(popup_html, max_width=300),
            color='#333333',  # 어두운 회색 테두리
            weight=3,
            fill=True,
            fillColor=marker_color,  # CCTV/범죄 비율에 따른 색상
            fillOpacity=0.7,
            tooltip=f"{row['자치구']}: CCTV {int(cctv_count):,}대 (비율: {cctv_crime_ratio:.2f})"
        ).add_to(m)
    
    # 상단 컬러 범례 추가 (실제 CCTV/범죄 비율 값 사용)
    # 범례 값 계산 (6단계)
    legend_values = []
    for i in range(6):
        val = min_ratio + (max_ratio - min_ratio) * i / 5
        legend_values.append(val)
    
    legend_html = f'''
    <div style="position: fixed; 
                top: 10px; left: 50%; transform: translateX(-50%);
                width: 500px; height: 90px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:12px; padding: 10px;
                font-family: Malgun Gothic;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
    <div style="text-align: center; margin-bottom: 5px;">
        <strong>지역 색상: CCTV/범죄 비율</strong>
    </div>
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <span style="font-size: 10px;">{legend_values[0]:.2f}</span>
        <div style="flex: 1; height: 20px; background: linear-gradient(to right, 
            #d73027, #f46d43, #fee08b, #abdda4, #66bd63); 
            margin: 0 10px; border: 1px solid #ccc;"></div>
        <span style="font-size: 10px;">▲{legend_values[5]:.2f}</span>
    </div>
    <div style="text-align: center; margin-top: 5px; font-size: 10px; color: #666;">
        원 크기 = CCTV 개수 | 원 색상 = CCTV/범죄 비율 (빨강: 낮음, 초록: 높음)
    </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # 저장
    if output_path:
        m.save(output_path)
        print(f"지도가 저장되었습니다: {output_path}")
    else:
        m.save('crime_cctv_map.html')
        print("지도가 저장되었습니다: crime_cctv_map.html")
    
    return m

def create_correlation_chart(data: pd.DataFrame, output_path: str = None):
    """
    범죄와 CCTV의 상관관계를 산점도로 시각화합니다.
    
    Args:
        data: 통합된 데이터프레임
        output_path: 저장할 이미지 파일 경로
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # 한글 폰트 설정
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 산점도 그리기
    scatter = ax.scatter(
        data['총 범죄 발생'],
        data['CCTV 개수'],
        s=data['총 범죄 발생'] * 2,  # 크기는 범죄 발생 건수에 비례
        c=data['상관관계 점수'],
        cmap='RdYlGn',
        alpha=0.6,
        edgecolors='black',
        linewidth=1
    )
    
    # 각 점에 자치구명 표시
    for idx, row in data.iterrows():
        ax.annotate(
            row['자치구'],
            (row['총 범죄 발생'], row['CCTV 개수']),
            fontsize=8,
            ha='center',
            va='bottom'
        )
    
    # 상관계수 계산 및 표시
    correlation = data['총 범죄 발생'].corr(data['CCTV 개수'])
    ax.text(0.05, 0.95, f'상관계수: {correlation:.3f}', 
            transform=ax.transAxes, fontsize=12,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 추세선 추가
    z = np.polyfit(data['총 범죄 발생'], data['CCTV 개수'], 1)
    p = np.poly1d(z)
    ax.plot(data['총 범죄 발생'], p(data['총 범죄 발생']), 
            "r--", alpha=0.5, linewidth=2, label='추세선')
    
    ax.set_xlabel('총 범죄 발생 건수', fontsize=12)
    ax.set_ylabel('CCTV 개수', fontsize=12)
    ax.set_title('서울시 자치구별 범죄 발생 건수와 CCTV 개수 상관관계', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # 컬러바 추가
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('상관관계 점수 (높을수록 CCTV가 충분)', fontsize=10)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"산점도가 저장되었습니다: {output_path}")
    else:
        plt.savefig('crime_cctv_correlation.png', dpi=300, bbox_inches='tight')
        print("산점도가 저장되었습니다: crime_cctv_correlation.png")
    
    plt.close()

def main():
    """메인 함수"""
    # 파일 경로 설정
    script_dir = Path(__file__).parent
    crime_csv_path = script_dir / 'save' / 'crime_processed.csv'
    cctv_csv_path = script_dir / 'save' / 'cctv_processed.csv'
    locations_csv_path = script_dir / 'save' / 'locations.csv'
    geojson_path = script_dir / 'resources' / 'crime' / 'kr-state.json'
    
    # 파일 존재 확인
    for path in [crime_csv_path, cctv_csv_path, locations_csv_path, geojson_path]:
        if not path.exists():
            print(f"오류: {path} 파일을 찾을 수 없습니다.")
            return
    
    print("데이터 로딩 및 통합 중...")
    # 데이터 로드 및 통합
    merged_data = load_and_merge_data(
        str(crime_csv_path),
        str(cctv_csv_path),
        str(locations_csv_path)
    )
    
    print("\n통합된 데이터 미리보기:")
    print(merged_data[['자치구', '총 범죄 발생', 'CCTV 개수', 'CCTV_범죄_비율', '상관관계 점수']].head(10))
    
    print("\n상관계수 계산 중...")
    correlation = merged_data['총 범죄 발생'].corr(merged_data['CCTV 개수'])
    print(f"범죄 발생 건수와 CCTV 개수의 상관계수: {correlation:.3f}")
    
    print("\n지도 생성 중...")
    # 인터랙티브 지도 생성
    map_output_path = script_dir / 'save' / 'crime_cctv_map.html'
    create_interactive_map(merged_data, str(geojson_path), str(map_output_path))
    
    print("\n산점도 생성 중...")
    # 상관관계 산점도 생성
    chart_output_path = script_dir / 'save' / 'crime_cctv_correlation.png'
    create_correlation_chart(merged_data, str(chart_output_path))
    
    print("\n모든 시각화가 완료되었습니다!")
    print(f"- 인터랙티브 지도: {map_output_path}")
    print(f"- 상관관계 산점도: {chart_output_path}")

if __name__ == "__main__":
    main()

