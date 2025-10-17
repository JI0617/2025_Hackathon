
import pandas as pd

def recommend_youth_policies(file_path, age, region, job_type):
    """
    CSV 파일에서 사용자 입력 조건(나이, 지역, 직업 유형)에 맞는 청년 정책을 추천합니다.

    :param file_path: 청년 정책 정보가 담긴 CSV 파일 경로
    :param age: 사용자의 나이 (정수)
    :param region: 사용자의 지역 (문자열, 예: '서울특별시')
    :param job_type: 사용자의 직업 유형 ('창업', '취업', '귀농' 중 하나)
    :return: 필터링된 정책 정보를 담은 DataFrame 또는 결과 없음 메시지
    """
    try:
        # 1. CSV 파일 읽기
        df = pd.read_csv(file_path)

        # 'sprtTrgtMinAge', 'sprtTrgtMaxAge' 컬럼을 숫자로 변환 (에러 발생 시 NaN 처리)
        df['sprtTrgtMinAge'] = pd.to_numeric(df['sprtTrgtMinAge'], errors='coerce')
        df['sprtTrgtMaxAge'] = pd.to_numeric(df['sprtTrgtMaxAge'], errors='coerce')
        
        # 'lclsfNm' 및 'mclsfNm' 컬럼의 결측값(NaN)을 빈 문자열로 대체하여 검색 가능하게 함
        df['lclsfNm'] = df['lclsfNm'].fillna('')
        df['mclsfNm'] = df['mclsfNm'].fillna('')

        # 2. 나이 필터링
        # 사용자의 나이가 최소 나이 이상, 최대 나이 이하인 정책 필터링
        # 나이 정보가 없는(NaN) 정책은 일단 모두 포함 (추후 더 정밀한 처리가 가능하나 여기서는 포괄적으로 처리)
        age_filtered_df = df[
            (df['sprtTrgtMinAge'].isna() | (df['sprtTrgtMinAge'] <= age)) &
            (df['sprtTrgtMaxAge'].isna() | (df['sprtTrgtMaxAge'] >= age))
        ]

        # 3. 지역 필터링
        # 사용자의 지역이 'region' 컬럼에 포함되거나, 'region' 컬럼이 비어있는 정책 포함
        # 'region' 컬럼이 비어있으면 (NaN이나 빈 문자열) 전국 정책으로 간주
        region_filtered_df = age_filtered_df[
            age_filtered_df['region'].isna() | 
            (age_filtered_df['region'] == '') | 
            age_filtered_df['region'].str.contains(region, na=False)
        ]

        # 4. 직업 유형 필터링 (대분류/중분류 기준)
        # 'lclsfNm' (대분류) 또는 'mclsfNm' (중분류) 컬럼에 직업 유형이 포함되는 정책 필터링
        job_filtered_df = region_filtered_df[
            region_filtered_df['lclsfNm'].str.contains(job_type, na=False) |
            region_filtered_df['mclsfNm'].str.contains(job_type, na=False)
        ]
        
        # 필터링된 결과가 없을 경우, 나이/지역만 필터링된 결과에서 가장 관련성이 높은 정책 5개를 보여줄 수 있음
        # 여기서는 단순히 결과가 없을 경우 메시지를 반환
        if job_filtered_df.empty:
            return f"나이 {age}세, 지역 '{region}', 직업 유형 '{job_type}'에 해당하는 추천 정책이 없습니다. 지역 또는 직업 유형을 일반화하여 다시 시도해 보세요."

        # 5. 최종 추천 결과 컬럼 선택
        recommendations = job_filtered_df[['plcyNm', 'plcyExplnCn', 'plcySprtCn']].copy()
        recommendations.columns = ['정책 이름', '정책 설명', '지원 내용']
        
        # 인덱스 초기화 및 반환
        return recommendations.reset_index(drop=True)

    except FileNotFoundError:
        return f"에러: 파일 경로 '{file_path}'를 찾을 수 없습니다."
    except Exception as e:
        return f"처리 중 에러가 발생했습니다: {e}"

# --- 사용 예시 ---

# 1. 파일 경로 지정 (사용자가 업로드한 파일 이름 사용)
file_path = 'youth_policies_add_region.csv'

# 2. 사용자 정보 설정 (웹에서 받을 정보)
user_age = 28
user_region = '경상남도'  # '경상남도'처럼 CSV 파일의 region 컬럼 값과 일치하거나 포함되어야 함
user_job_type = '취업'      # '창업', '취업', '귀농' 등

# 3. 정책 추천 함수 실행
recommended_policies = recommend_youth_policies(file_path, user_age, user_region, user_job_type)

# 4. 결과 출력
print(f"--- 사용자 조건: {user_age}세, {user_region}, {user_job_type} 정책 추천 결과 ---")
print(recommended_policies)
