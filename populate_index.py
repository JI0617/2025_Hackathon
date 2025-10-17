

import os
import pandas as pd
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
import time

# --- 1. 환경 변수 및 기본 설정 ---

# .env 파일에서 환경 변수 로드
load_dotenv("key.env")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 

# Pinecone 설정
INDEX_NAME = "region-index"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536 # "text-embedding-3-small"의 차원

# Pinecone 클라이언트 초기화
# 참고: PINECONE_API_KEY는 자동으로 환경변수에서 읽어오므로 명시적으로 전달할 필요가 없을 수 있습니다.
pc = Pinecone(api_key=PINECONE_API_KEY)

# --- 2. Pinecone 인덱스 생성 ---

# 현재 활성화된 인덱스 목록 확인
active_indexes = [index_info["name"] for index_info in pc.list_indexes()]

# 인덱스가 존재하지 않으면 새로 생성
if INDEX_NAME not in active_indexes:
    print(f"'{INDEX_NAME}' 인덱스를 찾을 수 없습니다. 새로 생성합니다.")
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIMENSION,
        metric="cosine", # 코사인 유사도 사용
        spec=ServerlessSpec(
            cloud="aws", # 또는 "gcp"
            region="us-east-1" # 무료 티어에서 사용 가능한 리전으로 변경
        )
    )
    # 인덱스가 준비될 때까지 잠시 대기
    while not pc.describe_index(INDEX_NAME).status['ready']:
        print("인덱스 생성 중...")
        time.sleep(5)
    print("인덱스 생성이 완료되었습니다.")
else:
    print(f"'{INDEX_NAME}' 인덱스가 이미 존재합니다.")

# 생성된 인덱스에 연결
pinecone_index = pc.Index(INDEX_NAME)

# --- 3. 데이터 로드 및 준비 ---

try:
    # CSV 파일 로드
    df = pd.read_csv("Data/통합_테이블.csv")

    # 필수 컬럼 확인
    required_columns = ['지역명', 'summary', '의료 등급', '교육 인프라 등급', '월세등급', '보증금(만원)', '월세금(만원)']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"CSV 파일에 필수 컬럼({required_columns})이 모두 존재하지 않습니다.")

    # summary가 비어있는 행 제거
    df.dropna(subset=['summary'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    print(f"'{INDEX_NAME}'에 업로드할 데이터를 로드했습니다. 총 {len(df)}개의 지역 데이터.")
    print("데이터 샘플:")
    print(df.head())

except FileNotFoundError:
    print("오류: 'Data/통합_테이블.csv' 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
except Exception as e:
    print(f"데이터 로드 중 오류가 발생했습니다: {e}")

# --- 4. 임베딩 및 Pinecone 업로드 ---

print("\n데이터 임베딩 및 Pinecone 업로드를 시작합니다...")

# OpenAI 임베딩 모델 초기화
try:
    embedder = OpenAIEmbeddings(model=EMBEDDING_MODEL, openai_api_key=OPENAI_API_KEY)
    print("OpenAI 임베딩 모델을 초기화했습니다.")
except Exception as e:
    print(f"OpenAI 임베딩 모델 초기화 중 오류 발생: {e}")
    # 임베딩 모델 없이는 진행 불가하므로 종료
    exit()

# 데이터를 배치 단위로 처리
batch_size = 100
vectors_to_upsert = []

for i, row in df.iterrows():
    # 1. 임베딩할 텍스트
    text_to_embed = row['summary']
    
    # 2. 메타데이터 생성
    metadata = {
        'region_name': row['지역명'],
        'medical_grade': row['의료 등급'],
        'education_grade': row['교육 인프라 등급'],
        'rent_grade': row['월세등급'],
        'deposit': float(row['보증금(만원)']),
        'monthly_rent': float(row['월세금(만원)']),
        'text': text_to_embed # 원본 요약 텍스트도 메타데이터에 포함
    }
    
    # 3. 벡터 ID 생성 (고유해야 함)
    vector_id = f"region_{i}"
    
    # 4. 임베딩 생성 (개별 처리)
    try:
        embedding = embedder.embed_query(text_to_embed)
    except Exception as e:
        print(f"ID {vector_id} ({row['지역명']}) 임베딩 중 오류 발생: {e}")
        continue

    vectors_to_upsert.append({
        "id": vector_id,
        "values": embedding,
        "metadata": metadata
    })

    # 배치가 꽉 차거나 마지막 데이터일 경우 업로드
    if len(vectors_to_upsert) >= batch_size or i == len(df) - 1:
        if vectors_to_upsert:
            print(f"{i+1}/{len(df)} 지점까지의 데이터 업로드 중...")
            try:
                pinecone_index.upsert(vectors=vectors_to_upsert)
                vectors_to_upsert = [] # 리스트 비우기
            except Exception as e:
                print(f"Pinecone 업로드 중 오류 발생: {e}")

print("\n모든 데이터의 임베딩 및 Pinecone 업로드가 완료되었습니다.")
print(f"Pinecone 인덱스 '{INDEX_NAME}' 상태:")
print(pinecone_index.describe_index_stats())


