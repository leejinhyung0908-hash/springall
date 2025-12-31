from openai import OpenAI
import os

# 환경 변수에서 API 키 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("오류: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

res = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "안녕, 잘 작동하니?"}]
)

print(res.choices[0].message.content)