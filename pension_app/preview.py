import pandas as pd

df = pd.read_csv("data/pension_raw.csv", encoding="cp949")

# 첫 다섯 행
print(df.head())

# 컬럼 이름 목록
print(df.columns.tolist())

# 각 컬럼의 데이터 타입
print(df.dtypes)

# 전체 행 수와 컬럼 수
print(df.shape)  # (행 수, 컬럼 수)

# 각 컬럼별 결측값(NaN) 개수
print(df.isna().sum())