import random

# 간단한 응답 목록
responses = [
    "안녕하세요! 무엇을 도와드릴까요?",
    "재미있는 이야기네요!",
    "더 자세히 말씀해주세요.",
    "알겠습니다. 계속 이야기해 보세요.",
    "좋은 하루 되세요!",
    "기분이 어떠신가요?"
]

print("챗봇: 안녕하세요! 대화를 시작합니다. 'exit'를 입력하면 종료됩니다.")

while True:
    user_input = input("당신: ")
    if user_input.lower() == 'exit':
        print("챗봇: 안녕히 가세요!")
        break
    
    # 특정 키워드에 대한 응답
    if "기분" in user_input or "어때" in user_input:
        print("챗봇: 저는 AI라서 기분은 없지만, 항상 최선을 다하고 있어요! 당신의 기분은 어떠신가요?")
    else:
        # 랜덤 응답 선택
        response = random.choice(responses)
        print(f"챗봇: {response}")