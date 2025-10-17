

import os
import re
import json
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableMap, RunnablePassthrough

# --- 1. 환경 변수 및 기본 설정 ---

load_dotenv("key.env")

# LangSmith 연결 설정
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "Card-Recommand" # 프로젝트 이름을 설정할 수 있습니다.

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

INDEX_NAME = "region-index"
EMBEDDING_MODEL = "text-embedding-3-small"

# --- 2. 서비스 초기화 ---

try:
    # Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)
    pinecone_index = pc.Index(INDEX_NAME)
    print(f"Pinecone 인덱스 '{INDEX_NAME}'에 연결되었습니다.")
    print(pinecone_index.describe_index_stats())

    # LangChain
    embedder = OpenAIEmbeddings(model=EMBEDDING_MODEL, openai_api_key=OPENAI_API_KEY)
    llm = ChatOpenAI(model_name="gpt-4o", openai_api_key=OPENAI_API_KEY, temperature=0)
    parser = StrOutputParser()
    print("LangChain 및 OpenAI 모델을 초기화했습니다.")

except Exception as e:
    print(f"서비스 초기화 중 오류 발생: {e}")
    exit()

# --- 3. RAG 체인 로직 ---

def get_filter_json_via_llm(query: str) -> dict:
    prompt = f'''
    아래 "질문"에서 명시적으로 드러난 지역 조건만 JSON으로 추출해줘.
    '의료 등급', '교육 인프라 등급', '월세등급'은 '상', '중', '하' 중에서만 선택해.
    '보증금'이나 '월세금'은 숫자 범위로 추출해줘 (예: 50만원 이하 -> lte: 50).
    질문에 등장하지 않은 항목은 null로 남겨.
    추정이나 예시 추가 절대 금지. 반드시 하나의 딕셔너리(JSON)만 출력.

    예시:
    질문: 의료 시설 좋고 월세 싼 곳 추천해줘
    →
    {{
      "medical_grade": "상",
      "education_grade": null,
      "rent_grade": "하",
      "deposit": null,
      "monthly_rent": null
    }}

    질문: 보증금 1000만원 이하, 월세 50만원 이하이면서 교육 환경 좋은 곳 있을까?
    →
    {{
      "medical_grade": null,
      "education_grade": "상",
      "rent_grade": null,
      "deposit": {{"op": "lte", "value": 1000}},
      "monthly_rent": {{"op": "lte", "value": 50}}
    }}

    질문: {query}
    반드시 위 예시 포맷을 따르고, JSON 외 다른 출력 절대 금지.
    '''
    response = llm.invoke(prompt)
    raw = response.content.strip()

    if raw.startswith("```json") or raw.startswith("```"):
        raw = re.sub(r"```(?:json)?", "", raw).strip()
        raw = raw.rstrip("`").strip()
    try:
        return json.loads(raw)
    except Exception as e:
        print(f"LLM JSON 파싱 실패: {e}, 응답 내용: {response.content}")
        return {}

def build_metadata_filter(parsed: dict) -> dict:
    filter_dict = {"$and": []}
    
    for key, pinecone_key in [("medical_grade", "medical_grade"), ("education_grade", "education_grade"), ("rent_grade", "rent_grade")]:
        if parsed.get(key) and parsed[key] in ["상", "중", "하"]:
            filter_dict["$and"].append({pinecone_key: {"$eq": parsed[key]}})

    for key, pinecone_key in [("deposit", "deposit"), ("monthly_rent", "monthly_rent")]:
        if isinstance(parsed.get(key), dict):
            op = parsed[key].get("op")
            val = parsed[key].get("value")
            if op in ["lte", "gte", "eq"] and isinstance(val, (int, float)):
                filter_dict["$and"].append({pinecone_key: {f"${op}": val}})

    return filter_dict if filter_dict["$and"] else {}

def search_similar_regions(input_dict: dict, k=10):
    query = input_dict["query"]
    vector = input_dict["vector"]
    
    parsed = get_filter_json_via_llm(query)
    metadata_filter = build_metadata_filter(parsed)
    
    print(f"생성된 메타데이터 필터: {metadata_filter}")

    if metadata_filter:
        resp = pinecone_index.query(vector=vector, top_k=k, include_metadata=True, filter=metadata_filter)
    else:
        resp = pinecone_index.query(vector=vector, top_k=k, include_metadata=True)
        
    return [match["metadata"] for match in resp["matches"]]

def format_regions(regions: list) -> str:
    if not regions:
        return "추천할 만한 지역을 찾지 못했습니다. 다른 조건으로 질문해주세요."
    
    info_strs = []
    for region in regions:
        info_strs.append(
            f"지역명: {region.get('region_name', '정보 없음')}\n"
            f"요약: {region.get('text', '정보 없음')}"
        )
    return "\n---\n".join(info_strs)

def format_context_for_prompt(input_dict: dict):
    """검색된 지역 목록을 LLM 프롬프트에 넣기 좋은 형태의 단일 문자열로 변환합니다."""
    context_block = "\n---\n".join([
        f"지역명: {r.get('region_name')}\n"
        f"의료 등급: {r.get('medical_grade')}\n"
        f"교육 인프라 등급: {r.get('education_grade')}\n"
        f"월세 등급: {r.get('rent_grade')}\n"
        f"평균 보증금: {r.get('deposit')}\n"
        f"평균 월세금: {r.get('monthly_rent')}\n"
        f"요약: {r.get('text')}"
        for r in input_dict["regions"]
    ])
    # 다음 단계에서 query와 context_block을 모두 사용할 수 있도록 딕셔너리로 반환
    return {"query": input_dict["query"], "context_block": context_block}

def create_final_prompt(input_dict: dict) -> str:
    """최종 LLM 프롬프트를 생성합니다."""
    return f'''
    당신은 대한민국 지역 추천 전문가입니다.
    
    [사용자 질문]
    {input_dict['query']}

    [검색된 지역 정보]
    {input_dict['context_block']}

    [지시사항]
    1. 위 '검색된 지역 정보'만을 참고하여 '사용자 질문'에 가장 적합한 **상위 3곳의 지역**을 추천해 주세요.
    2. 각 지역의 추천 순위를 매기고, 추천하는 이유를 '검색된 지역 정보'의 '요약' 내용을 바탕으로 각각 설명해주세요.
    3. 답변은 아래 [답변 형식]을 반드시 지켜서 3곳 모두에 대해 작성해주세요. 만약 추천할 지역이 3곳 미만이면 있는 만큼만 추천해주세요.
    4. 각 추천 지역의 [상세 정보]는 '검색된 지역 정보'에서 정확히 가져와 채워주세요.

    [답변 형식]
    **1. [지역명]**
    
    [추천 이유]
    [여기에 1순위 지역의 추천 이유를 서술]
    
    [상세 정보]
    - 의료 등급: [의료 등급]
    - 교육 인프라 등급: [교육 인프라 등급]
    - 월세 등급: [월세 등급]
    - 평균 보증금: [보증금]만원
    - 평균 월세금: [월세금]만원
    ---
    **2. [지역명]**
    
    [추천 이유]
    [여기에 2순위 지역의 추천 이유를 서술]
    
    [상세 정보]
    - 의료 등급: [의료 등급]
    - 교육 인프라 등급: [교육 인프라 등급]
    - 월세 등급: [월세 등급]
    - 평균 보증금: [보증금]만원
    - 평균 월세금: [월세금]만원
    ---
    **3. [지역명]**
    
    [추천 이유]
    [여기에 3순위 지역의 추천 이유를 서술]
    
    [상세 정보]
    - 의료 등급: [의료 등급]
    - 교육 인프라 등급: [교육 인프라 등급]
    - 월세 등급: [월세 등급]
    - 평균 보증금: [보증금]만원
    - 평균 월세금: [월세금]만원
    '''

recommend_chain = (
    {
        "query": RunnablePassthrough(),
        "vector": RunnableLambda(lambda q: embedder.embed_query(q))
    }
    | RunnableMap({
        "query": lambda x: x["query"],
        "regions": search_similar_regions
    })
    | RunnableLambda(format_context_for_prompt)
    | RunnableLambda(create_final_prompt)
    | llm
    | parser
)

# --- 4. 메인 실행 루프 ---

def main():
    print("\n=== 지역 추천 챗봇 ===")
    print("의료, 교육, 월세, 보증금 등 원하는 조건을 자유롭게 질문하세요. (종료: q)")
    
    while True:
        user_query = input("\n추천 받고 싶은 지역을 설명해 주세요: ").strip()
        if user_query.lower() in ("q", "quit", "exit"):
            print("\n프로그램을 종료합니다.")
            break
        
        if not user_query:
            continue
            
        try:
            answer = recommend_chain.invoke(user_query)
            print(f"\n[Gemini의 추천]\n{answer}")
        except Exception as e:
            print(f"\n[오류] 추천 결과 생성에 실패했습니다: {e}")

if __name__ == "__main__":
    main()
