import pandas as pd

# Define file paths
medical_file = 'Data/의료 인프라_수정.csv'
edu_file = 'Data/교육 인프라.csv'
house_file = 'Data/집값.csv'
output_file = 'Data/통합_테이블.csv'

# Read CSV files into pandas DataFrames
df_medical = pd.read_csv(medical_file, encoding='utf-8-sig')
df_edu = pd.read_csv(edu_file, encoding='utf-8-sig')
df_house = pd.read_csv(house_file, encoding='utf-8-sig')

# Merge DataFrames
merged_df = pd.merge(df_medical, df_edu, on='지역명')
merged_df = pd.merge(merged_df, df_house, on='지역명')

# Reorder columns
grade_cols = ['의료 등급', '교육 인프라 등급', '월세등급']
other_cols = [col for col in merged_df.columns if col not in grade_cols]
new_order = other_cols + grade_cols
merged_df = merged_df[new_order]

# Save the merged DataFrame to a new CSV
merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"Successfully created '{output_file}'")
