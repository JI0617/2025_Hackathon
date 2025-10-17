
import pandas as pd
import openai
import os

def load_api_key(file_path):
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    if key == 'OPENAI_API_KEY':
                        return value
    except FileNotFoundError:
        return None
    return None

# --- Configuration ---
api_key = load_api_key("C:\\Documents\\2025_Hackathon\\key.env")
if not api_key or api_key == 'your_api_key_here':
    raise ValueError("OpenAI API key not found or not set in key.env. Please create the file and add your key in the format OPENAI_API_KEY=your_key_here.")
openai.api_key = api_key

regions_list = [
  "강원특별자치도 강릉시", "강원특별자치도 동해시", "강원특별자치도 삼척시", "강원특별자치도 속초시", "강원특별자치도 양구군",
  "강원특별자치도 양양군", "강원특별자치도 영월군", "강원특별자치도 원주시", "강원특별자치도 인제군", "강원특별자치도 정선군",
  "강원특별자치도 철원군", "강원특별자치도 춘천시", "강원특별자치도 태백시", "강원특별자치도 평창군", "강원특별자치도 홍천군",
  "강원특별자치도 화천군", "강원특별자치도 횡성군", "경기도 가평군", "경기도 고양시", "경기도 과천시", "경기도 광명시",
  "경기도 광주시", "경기도 구리시", "경기도 군포시", "경기도 김포시", "경기도 남양주시", "경기도 동두천시", "경기도 부천시",
  "경기도 성남시", "경기도 수원시", "경기도 시흥시", "경기도 안산시", "경기도 안성시", "경기도 안양시", "경기도 양주시",
  "경기도 양평군", "경기도 여주시", "경기도 연천군", "경기도 오산시", "경기도 용인시", "경기도 의왕시", "경기도 의정부시",
  "경기도 이천시", "경기도 파주시", "경기도 평택시", "경기도 포천시", "경기도 하남시", "경기도 화성시", "경상남도 거제시",
  "경상남도 거창군", "경상남도 고성군", "경상남도 김해시", "경상남도 남해군", "경상남도 밀양시", "경상남도 사천시",
  "경상남도 산청군", "경상남도 양산시", "경상남도 의령군", "경상남도 진주시", "경상남도 창녕군", "경상남도 창원시",
  "경상남도 통영시", "경상남도 하동군", "경상남도 함안군", "경상남도 함양군", "경상남도 합천군", "경상북도 경산시",
  "경상북도 경주시", "경상북도 고령군", "경상북도 구미시", "경상북도 김천시", "경상북도 문경시", "경상북도 봉화군",
  "경상북도 상주시", "경상북도 성주군", "경상북도 안동시", "경상북도 영덕군", "경상북도 영양군", "경상북도 영주시",
  "경상북도 영천시", "경상북도 예천군", "경상북도 울릉군", "경상북도 울진군", "경상북도 의성군", "경상북도 청도군",
  "경상북도 청송군", "경상북도 칠곡군", "경상북도 포항시", "세종특별자치시", "전라남도 강진군", "전라남도 고흥군",
  "전라남도 곡성군", "전라남도 광양시", "전라남도 구례군", "전라남도 나주시", "전라남도 담양군", "전라남도 목포시",
  "전라남도 무안군", "전라남도 보성군", "전라남도 순천시", "전라남도 신안군", "전라남도 여수시", "전라남도 영광군",
  "전라남도 영암군", "전라남도 완도군", "전라남도 장성군", "전라남도 장흥군", "전라남도 진도군", "전라남도 함평군",
  "전라남도 해남군", "전라남도 화순군", "전북특별자치도 고창군", "전북특별자치도 군산시", "전북특별자치도 김제시",
  "전북특별자치도 남원시", "전북특별자치도 무주군", "전북특별자치도 부안군", "전북특별자치도 순창군", "전북특별자치도 완주군",
  "전북특별자치도 익산시", "전북특별자치도 임실군", "전북특별자치도 장수군", "전북특별자치도 전주시", "전북특별자치도 정읍시",
  "전북특별자치도 진안군", "제주특별자치도 서귀포시", "제주특별자치도 제주시", "충청남도 계룡시", "충청남도 공주시",
  "충청남도 금산군", "충청남도 논산시", "충청남도 당진시", "충청남도 보령시", "충청남도 부여군", "충청남도 서산시",
  "충청남도 서천군", "충청남도 아산시", "충청남도 예산군", "충청남도 천안시", "충청남도 청양군", "충청남도 태안군",
  "충청남도 홍성군", "충청북도 괴산군", "충청북도 단양군", "충청북도 보은군", "충청북도 영동군", "충청북도 옥천군",
  "충청북도 음성군", "충청북도 제천시", "충청북도 증평군", "충청북도 진천군", "충청북도 청주시", "충청북도 충주시"
]

def get_region_from_gpt(row_content):
    """
    Sends a request to the GPT model to classify the region of a policy.
    """
    prompt = f"""
    다음은 청년 정책에 대한 데이터입니다. 이 정책이 어느 지역에 해당하는지 아래의 지역 목록에서 찾아주세요.
    만약 목록에서 지역을 찾을 수 없다면 '전국'이라고 응답해주세요.
    응답은 지역 이름만 포함해야 합니다.

    ---
    정책 데이터:
    {row_content}
    ---
    지역 목록:
    {', '.join(regions_list)}
    ---
    지역:
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts region information from text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        region = response.choices[0].message.content.strip()
        return region
    except Exception as e:
        print(f"An error occurred: {e}")
        return "전국" # Default to '전국' on error

def process_csv(input_file, output_file):
    """
    Reads a CSV, gets region for each row using GPT, and saves to a new CSV.
    """
    df = pd.read_csv(input_file)
    
    # Apply the function to each row
    df['region'] = df.apply(lambda row: get_region_from_gpt(' '.join(row.astype(str))), axis=1)
    
    # Save the new dataframe to a csv file
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"Successfully created {output_file} with region classification from GPT.")

if __name__ == "__main__":
    input_csv_path = "C:\\Documents\\2025_Hackathon\\youth_policies_all1.csv"
    output_csv_path = "C:\\Documents\\2025_Hackathon\\youth_policies_with_gpt_region.csv"
    process_csv(input_csv_path, output_csv_path)
