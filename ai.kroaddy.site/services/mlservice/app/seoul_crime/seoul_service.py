import sys
from pathlib import Path
import pandas as pd
import numpy as np
from app.seoul_crime.seoul_method import SeoulMethod
from app.seoul_crime.seoul_data import SeoulData
from app.seoul_crime.kakao_map_singleton import KakaoMapSingleton
import logging

# 로깅 설정 (터미널에 출력되도록)
logger = logging.getLogger("seoul_service")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
class SeoulService:
    
    def __init__(self):
        self.data = SeoulData()
        self.method = SeoulMethod()
        self.crime_rate_columns = ['살인검거율', '강도검거율', '강간검거율', '절도검거율', '폭력검거율']
        self.crime_columns = ['살인', '강도', '강간', '절도', '폭력']

    def preprocess(self):
        data_dir = Path(self.data.dname)
        cctv_path = data_dir / "cctv.csv"
        crime_path = data_dir / "crime.csv"
        pop_path = data_dir / "pop.xls"
        
        # 데이터 로드
        cctv = self.method.csv_to_df(str(cctv_path))
        # 존재하는 컬럼만 삭제 (에러 방지)
        # 2013년도 이전, 2014년, 2015년, 2016년 컬럼 삭제
        cols_to_drop = ['2013년도 이전', '2014년', '2015년', '2016년']
        existing_cols_to_drop = [col for col in cols_to_drop if col in cctv.columns]
        if existing_cols_to_drop:
            cctv = cctv.drop(existing_cols_to_drop, axis=1)
            logger.info(f"CCTV 컬럼 삭제 완료: {existing_cols_to_drop}")
        crime = self.method.csv_to_df(str(crime_path))
        pop = self.method.xlsx_to_df(str(pop_path))
        
        # pop 컬럼 편집
        # axis = 1 방향으로 자치구와 왼쪽부터 4번째 컬럼만 남기고 모두 삭제
        if '자치구' in pop.columns:
            # 자치구 컬럼의 인덱스 찾기
            gu_idx = pop.columns.get_loc('자치구')
            # 왼쪽부터 4번째 컬럼 인덱스 (0-based이므로 3)
            fourth_idx = 3
            # 유지할 컬럼 인덱스 리스트
            cols_to_keep = [gu_idx, fourth_idx]
            # 중복 제거 및 정렬
            cols_to_keep = sorted(set(cols_to_keep))
            # 해당 컬럼만 선택
            pop = pop.iloc[:, cols_to_keep]
            logger.info(f"pop 컬럼 편집 완료: {pop.columns.tolist()}")
        else:
            logger.warning("'자치구' 컬럼을 찾을 수 없습니다. 컬럼 편집을 건너뜁니다.")
        
        # axis = 0 방향으로 위로부터 2,3,4번째 행을 제거 (인덱스 1, 2, 3)
        pop = pop.drop(pop.index[1:4], axis=0).reset_index(drop=True)
        logger.info(f"pop 행 편집 완료: {len(pop)}행 남음")
        
    
        # 관서명에 따른 경찰서 주소 찾기
        station_names = [] # 경찰서 관서명 리스트
        for name in crime['관서명']:
            station_names.append('서울' + str(name[:-1]) + '경찰서')
        print(f"🔥💧경찰서 관서명 리스트: {station_names}")
        station_addrs = []
        station_lats = []
        station_lngs = []
        gmaps1 = KakaoMapSingleton()
        gmaps2 = KakaoMapSingleton()
        if gmaps1 is gmaps2:
            print("동일한 객체 입니다.")
        else:
            print("다른 객체 입니다.")
        gmaps = KakaoMapSingleton()  # 카카오맵 객체 생성
        for name in station_names:
            try:
                tmp = gmaps.geocode(name, language='ko')
                if tmp and len(tmp) > 0:
                    print(f"""{name}의 검색 결과: {tmp[0].get("formatted_address")}""")
                    station_addrs.append(tmp[0].get("formatted_address"))
                    tmp_loc = tmp[0].get("geometry")
                    station_lats.append(tmp_loc['location']['lat'])
                    station_lngs.append(tmp_loc['location']['lng'])
                else:
                    logger.warning(f"'{name}'에 대한 검색 결과가 없습니다.")
                    station_addrs.append("")
                    station_lats.append(0.0)
                    station_lngs.append(0.0)
            except Exception as e:
                logger.error(f"'{name}' 지오코딩 실패: {str(e)}")
                station_addrs.append("")
                station_lats.append(0.0)
                station_lngs.append(0.0)
        print(f"🔥💧자치구 리스트: {station_addrs}")
        gu_names = []
        for addr in station_addrs:
            if not addr or addr.strip() == "":
                logger.warning(f"빈 주소입니다. 기본값 '알수없음'을 사용합니다.")
                gu_names.append("알수없음")
                continue
            
            tmp = addr.split()
            tmp_gu_list = [gu for gu in tmp if gu and len(gu) > 0 and gu[-1] == '구']
            
            if tmp_gu_list:
                gu_names.append(tmp_gu_list[0])
            else:
                logger.warning(f"주소 '{addr}'에서 자치구를 찾을 수 없습니다. 기본값 '알수없음'을 사용합니다.")
                gu_names.append("알수없음")
        
        print(f"🔥💧자치구 리스트 2: {gu_names}")
        
        # gu_names 길이가 crime 행 수와 일치하는지 확인
        if len(gu_names) != len(crime):
            logger.error(f"자치구 리스트 길이({len(gu_names)})와 범죄 데이터 행 수({len(crime)})가 일치하지 않습니다.")
            raise ValueError(f"자치구 리스트 길이({len(gu_names)})와 범죄 데이터 행 수({len(crime)})가 일치하지 않습니다.")
        
        # 위도, 경도 길이 확인
        if len(station_lats) != len(crime) or len(station_lngs) != len(crime):
            logger.warning(f"위도/경도 리스트 길이가 범죄 데이터와 일치하지 않습니다. 기본값(0.0)으로 채웁니다.")
            while len(station_lats) < len(crime):
                station_lats.append(0.0)
            while len(station_lngs) < len(crime):
                station_lngs.append(0.0)
        
        crime['자치구'] = gu_names
        crime['위도'] = station_lats
        crime['경도'] = station_lngs
        crime['주소'] = station_addrs
        
        print(f"🔥💧위도 리스트: {station_lats[:5]}... (총 {len(station_lats)}개)")
        print(f"🔥💧경도 리스트: {station_lngs[:5]}... (총 {len(station_lngs)}개)")

        # 데이터 로드 확인 로그 (터미널에 출력)
        print("\n" + "="*80)
        print("서울시 범죄 데이터 전처리 시작")
        print("="*80)
        logger.info("데이터 로드 완료")
        print(f"\n[CCTV 데이터]")
        print(f"  행 수: {len(cctv)}")
        print(f"  컬럼: {cctv.columns.tolist()}")
        print(f"  탑 5:\n{cctv.head(5).to_string()}")
        logger.info(f"cctv 데이터: {len(cctv)}행, {len(cctv.columns)}컬럼")
        
        print(f"\n[범죄 데이터]")
        print(f"  행 수: {len(crime)}")
        print(f"  컬럼: {crime.columns.tolist()}")
        print(f"  탑 5:\n{crime.head(5).to_string()}")
        logger.info(f"crime 데이터: {len(crime)}행, {len(crime.columns)}컬럼")
        
        print(f"\n[인구 데이터]")
        print(f"  행 수: {len(pop)}")
        print(f"  컬럼: {pop.columns.tolist()}")
        print(f"  탑 5:\n{pop.head(5).to_string()}")
        logger.info(f"pop 데이터: {len(pop)}행, {len(pop.columns)}컬럼")
        
        # cctv와 pop 머지 전략
        # - cctv의 "기관명"과 pop의 "자치구"를 키로 사용
        # - 중복된 feature가 없도록 처리
        # - "기관명"과 "자치구"는 같은 값이지만 컬럼명이 다르므로 left_on, right_on 사용
        
        # 머지 전에 컬럼명 확인 및 중복 컬럼 체크
        print(f"\n[머지 전 컬럼 확인]")
        print(f"  CCTV 컬럼: {cctv.columns.tolist()}")
        print(f"  인구 컬럼: {pop.columns.tolist()}")
        logger.info(f"cctv 컬럼: {cctv.columns.tolist()}")
        logger.info(f"pop 컬럼: {pop.columns.tolist()}")
        
        # 중복되는 컬럼 확인 (키 컬럼 제외)
        cctv_cols = set(cctv.columns) - {'기관명'}
        pop_cols = set(pop.columns) - {'자치구'}
        duplicate_cols = cctv_cols & pop_cols
        
        if duplicate_cols:
            print(f"  ⚠️ 중복되는 컬럼 발견: {duplicate_cols}")
            logger.warning(f"중복되는 컬럼이 발견되었습니다: {duplicate_cols}")
            logger.info("머지 시 suffixes를 사용하여 중복 컬럼을 구분합니다.")
        else:
            print(f"  ✅ 중복 컬럼 없음")
        
        # cctv의 "기관명"과 pop의 "자치구"를 키로 머지
        print(f"\n[데이터 머지 중...]")
        print(f"  CCTV 키: '기관명'")
        print(f"  인구 키: '자치구'")
        cctv_pop = self.method.df_merge(
            left=cctv,
            right=pop,
            left_on='기관명',
            right_on='자치구',
            how='inner'
        )
        
        # 머지 후 "자치구" 컬럼 제거 (기관명과 동일한 값이므로)
        if '자치구' in cctv_pop.columns and '기관명' in cctv_pop.columns:
            # 두 컬럼의 값이 동일한지 확인
            if cctv_pop['기관명'].equals(cctv_pop['자치구']):
                cctv_pop = cctv_pop.drop(columns=['자치구'])
                print(f"  ✅ '자치구' 컬럼 제거 완료 (기관명과 동일한 값)")
                logger.info("'자치구' 컬럼을 제거했습니다 (기관명과 동일한 값).")
            else:
                print(f"  ⚠️ '기관명'과 '자치구'의 값이 다릅니다. 두 컬럼 모두 유지합니다.")
                logger.warning("'기관명'과 '자치구'의 값이 다릅니다. 두 컬럼 모두 유지합니다.")
        
        print(f"\n[머지 완료]")
        print(f"  Shape: {cctv_pop.shape}")
        print(f"  컬럼: {cctv_pop.columns.tolist()}")
        print(f"  탑 5:\n{cctv_pop.head(5).to_string()}")
        logger.info(f"머지 완료: cctv_pop shape = {cctv_pop.shape}")
        logger.info(f"cctv_pop 컬럼: {cctv_pop.columns.tolist()}")

        # 구별 고령자 비율과 CCTV 의 상관계수
        # 구별 외국인 비율과 CCTV 의 상관계수

        print("\n" + "="*80)
        print("서울시 범죄 데이터 전처리 완료")
        print("="*80)
        logger.info("데이터 전처리 완료")
        
        # 위도, 경도 정보 준비
        location_data = []
        for i in range(len(station_names)):
            location_data.append({
                "관서명": crime['관서명'].iloc[i] if i < len(crime) else "",
                "경찰서명": station_names[i],
                "주소": station_addrs[i] if i < len(station_addrs) else "",
                "자치구": gu_names[i] if i < len(gu_names) else "",
                "위도": float(station_lats[i]) if i < len(station_lats) else 0.0,
                "경도": float(station_lngs[i]) if i < len(station_lngs) else 0.0
            })
        
        # CSV 파일 저장
        save_dir = Path(self.data.sname)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. CCTV 데이터 저장
        cctv_save_path = save_dir / "cctv_processed.csv"
        cctv.to_csv(cctv_save_path, index=False, encoding='utf-8-sig')
        logger.info(f"CCTV 데이터 저장 완료: {cctv_save_path}")
        print(f"💾 CCTV 데이터 저장: {cctv_save_path}")
        
        # 2. 범죄 데이터 저장 (위도, 경도 포함)
        crime_save_path = save_dir / "crime_processed.csv"
        crime.to_csv(crime_save_path, index=False, encoding='utf-8-sig')
        logger.info(f"범죄 데이터 저장 완료: {crime_save_path}")
        print(f"💾 범죄 데이터 저장: {crime_save_path}")
        
        # 3. 인구 데이터 저장
        pop_save_path = save_dir / "pop_processed.csv"
        pop.to_csv(pop_save_path, index=False, encoding='utf-8-sig')
        logger.info(f"인구 데이터 저장 완료: {pop_save_path}")
        print(f"💾 인구 데이터 저장: {pop_save_path}")
        
        # 4. 머지된 데이터 저장
        merged_save_path = save_dir / "merged_processed.csv"
        cctv_pop.to_csv(merged_save_path, index=False, encoding='utf-8-sig')
        logger.info(f"머지된 데이터 저장 완료: {merged_save_path}")
        print(f"💾 머지된 데이터 저장: {merged_save_path}")
        
        # 5. 위치 정보 데이터 저장 (위도, 경도 포함)
        location_df = pd.DataFrame(location_data)
        location_save_path = save_dir / "locations.csv"
        location_df.to_csv(location_save_path, index=False, encoding='utf-8-sig')
        logger.info(f"위치 정보 데이터 저장 완료: {location_save_path}")
        print(f"💾 위치 정보 데이터 저장: {location_save_path}")
        
        print(f"\n✅ 모든 데이터가 {save_dir} 폴더에 저장되었습니다.")
        logger.info(f"모든 CSV 파일 저장 완료: {save_dir}")
        
        # 표 형식 데이터 준비 (Postman 응답용)
        cctv_table = cctv.head(10).to_dict(orient='records')
        crime_table = crime.head(10).to_dict(orient='records')
        pop_table = pop.head(10).to_dict(orient='records')
        merged_table = cctv_pop.head(10).to_dict(orient='records')
        
        # 표 형식 문자열 (터미널 출력용)
        cctv_table_str = cctv.head(10).to_string()
        crime_table_str = crime.head(10).to_string()
        pop_table_str = pop.head(10).to_string()
        merged_table_str = cctv_pop.head(10).to_string()
        
        return {
            "status": "success",
            "cctv_rows": len(cctv),
            "crime_rows": len(crime),
            "pop_rows": len(pop),
            "merged_rows": len(cctv_pop),
            "merged_columns": len(cctv_pop.columns),
            "message": "데이터 전처리가 완료되었습니다",
            "data": {
                "cctv": {
                    "columns": cctv.columns.tolist(),
                    "sample_data": cctv_table,
                    "sample_table": cctv_table_str
                },
                "crime": {
                    "columns": crime.columns.tolist(),
                    "sample_data": crime_table,
                    "sample_table": crime_table_str
                },
                "pop": {
                    "columns": pop.columns.tolist(),
                    "sample_data": pop_table,
                    "sample_table": pop_table_str
                },
                "merged": {
                    "columns": cctv_pop.columns.tolist(),
                    "sample_data": merged_table,
                    "sample_table": merged_table_str
                },
                "locations": {
                    "total_count": len(location_data),
                    "locations": location_data,
                    "summary": {
                        "위도_범위": {
                            "min": float(min(station_lats)) if station_lats else 0.0,
                            "max": float(max(station_lats)) if station_lats else 0.0,
                            "mean": float(np.mean(station_lats)) if station_lats else 0.0
                        },
                        "경도_범위": {
                            "min": float(min(station_lngs)) if station_lngs else 0.0,
                            "max": float(max(station_lngs)) if station_lngs else 0.0,
                            "mean": float(np.mean(station_lngs)) if station_lngs else 0.0
                        }
                    }
                }
            }
        }
        