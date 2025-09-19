import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('key.env')

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

file_path = 'Data/통합_테이블.csv'
df = pd.read_csv(file_path, encoding='utf-8-sig')

# Get column names
cols = df.columns

def generate_summary(row):
    prompt = f"""다음은 대한민국의 한 지역에 대한 정보입니다.

- 지역명: {row[cols[0]]}
- 의료 평균접근성: {row[cols[1]]}
- 학생수: {row[cols[2]]}
- 교원수: {row[cols[3]]}
- 교원 1인당 학생수: {row[cols[4]]}
- 보증금(만원): {row[cols[5]]}
- 월세금(만원): {row[cols[6]]}
- 종합월부담: {row[cols[7]]}
- 의료_등급: {row[cols[8]]}
- 교육 인프라 등급: {row[cols[9]]}
- 종합부담등급: {row[cols[10]]}
- 월세등급: {row[cols[11]]}

이 지역의 특성을 2문장으로 요약해주세요."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes regional data."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Process all rows
df['summary'] = df.apply(generate_summary, axis=1)

df.to_csv(file_path, index=False, encoding='utf-8-sig')

print("Summaries added for all rows.")
