from flask import Flask, request, jsonify, render_template_string
import random

app = Flask(__name__)

# 간단한 응답 목록
responses = [
    "안녕하세요! 무엇을 도와드릴까요?",
    "재미있는 이야기네요!",
    "더 자세히 말씀해주세요.",
    "알겠습니다. 계속 이야기해 보세요.",
    "좋은 하루 되세요!",
    "기분이 어떠신가요?"
]

@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>44채ㅅ 챗봇</title>
        <style>
            body { font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', Arial, sans-serif; background: #f1f5f9; color: #1e293b; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin:0; }
            .chat-container { width: min(720px, 95vw); background: #ffffff; padding: 20px; border-radius: 16px; box-shadow: 0 12px 30px rgba(15,23,42,0.12); }
            h1 { margin: 0 0 18px 0; color: #0f172a; }
            #chatLog { background: #e2e8f0; border-radius: 12px; min-height: 260px; padding: 12px; overflow-y: auto; white-space: pre-wrap; line-height: 1.6; font-size: 15px; }
            .user-input { display: flex; gap: 10px; margin-top: 14px; }
            #userInput { flex: 1; padding: 12px 14px; border: 1px solid #cbd5e1; border-radius: 10px; font-size: 15px; }
            #userInput:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.18); }
            button { background: linear-gradient(120deg, #2563eb, #4f46e5); color: white; border: none; border-radius: 10px; padding: 0 20px; font-size: 15px; cursor: pointer; }
            button:hover { filter: brightness(1.05); }
            .meta { color: #64748b; font-size: 13px; margin-top: 8px; }
            .chat-entry-user { color: #1d4ed8; }
            .chat-entry-ai { color: #0f172a; }
        </style>
    </head>
    <body>
        <section class="chat-container">
            <h1>44채ㅅ 챗봇</h1>
            <div id="chatLog"></div>
            <div class="meta">AI 이름: 44채ㅅ (말걸어보세요)</div>
            <div class="user-input">
                <input id="userInput" type="text" placeholder="메시지를 입력하세요..." />
                <button onclick="sendMessage()">전송</button>
            </div>

        <script>
            function appendLog(msg, cls) {
                const log = document.getElementById('chatLog');
                const wrapped = document.createElement('div');
                wrapped.textContent = msg;
                wrapped.className = cls;
                log.appendChild(wrapped);
                log.scrollTop = log.scrollHeight;
            }

            function sendMessage() {
                const input = document.getElementById('userInput');
                const text = input.value.trim();
                if (!text) return;
                appendLog('당신: ' + text, 'chat-entry-user');
                input.value = '';

                fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                })
                .then(res => res.json())
                .then(data => appendLog('44채ㅅ: ' + data.reply, 'chat-entry-ai'))
                .catch(err => appendLog('44채ㅅ: 오류가 발생했습니다.', 'chat-entry-ai'));
            }

            document.getElementById('userInput').addEventListener('keypress', function(e){
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_input = data.get('message', '').strip()

    if not user_input:
        return jsonify(reply='메시지를 입력해주세요.'), 400

    if '운세' in user_input:
        fortune_score = random.randint(1, 100)
        reply = f'오늘의 운세는 {fortune_score}점입니다. 좋은 하루 되세요!'
    elif '음식' in user_input or '추천' in user_input:
        # 카테고리별 추천 리스트
        foods = [
            '치킨', '피자', '킹크랩', '스테이크', '초밥', '라면', '떡볶이',
            '비빔밥', '삼겹살', '갈비찜', '짜장면', '짬뽕', '김치찌개', '된장찌개',
            '회', '샤브샤브', '파스타', '버거', '타코', '브런치'
        ]
        juices = [
            '오렌지 주스', '사과 주스', '포도 주스', '토마토 주스', '망고 주스',
            '파인애플 주스', '키위 주스', '블루베리 주스', '딸기 주스', '레몬 주스',
            '자몽 주스', '바나나 주스', '수박 주스', '멜론 주스', '복숭아 주스'
        ]
        desserts = [
            '케이크', '쿠키', '아이스크림', '와플', '마카롱', '타르트', '브라우니',
            '푸딩', '젤리', '도넛', '크로와상', '티라미수', '초콜릿', '머핀', '파이'
        ]
        coffees = [
            '아메리카노', '카페라떼', '카푸치노', '에스프레소', '카페모카',
            '바닐라 라떼', '카라멜 마키아토', '콜드브루', '아이스 아메리카노', '프라푸치노'
        ]
        teas = [
            '녹차', '홍차', '페퍼민트 티', '캐모마일 티', '잉글리시 브렉퍼스트',
            '얼그레이', '자스민 티', '히비스커스 티', '루이보스 티', '민트 티'
        ]
        salads = [
            '시저 샐러드', '그릭 샐러드', '카프레제 샐러드', '코울슬로', '퀴노아 샐러드',
            '아보카도 샐러드', '치킨 샐러드', '연어 샐러드', '비트 샐러드', '토마토 샐러드'
        ]

        # 카테고리 선택
        if '주스' in user_input:
            category = juices
            category_name = '주스'
        elif '디저트' in user_input:
            category = desserts
            category_name = '디저트'
        elif '커피' in user_input:
            category = coffees
            category_name = '커피'
        elif '차' in user_input or '티' in user_input:
            category = teas
            category_name = '차'
        elif '샐러드' in user_input:
            category = salads
            category_name = '샐러드'
        else:
            category = foods
            category_name = '메뉴'

        chosen = random.sample(category, min(5, len(category)))
        reply = f'오늘 추천 {category_name}: {", ".join(chosen)}. 이게 땡기네요!'
    elif '스포츠' in user_input or '근황' in user_input:
        reply = '무슨 종목이 궁금한가요? (예: 축구, 야구, 농구, 배구, 배드민턴, 탁구)'
    elif '프리미어 리그' in user_input:
        reply = ('최근 프리미어 리그 소식\n'
                 '- 맨시티, 리버풀, 아스널 경쟁 치열\n'
                 '- 하드웨어: 케인, 살라, 데 브라위너\n'
                 '- 다음 경기: 토트넘 vs 첼시')
    elif '축구' in user_input:
        reply = ('최근 축구 소식\n'
                 '- K리그: 현재 시즌 경쟁 중\n'
                 '- 챔피언스리그: 톱클럽 경기 진행\n'
                 '- 스타 선수: 메시, 호날두, 손흥민')
    elif '야구' in user_input:
        reply = ('최근 야구 소식\n'
                 '- KBO: 순위 경쟁 치열\n'
                 '- MLB: 포스트시즌 돌입\n'
                 '- 주목 선수: 류현진, 김광현')
    elif '농구' in user_input:
        reply = ('최근 농구 소식\n'
                 '- KBL: 플레이오프 준비\n'
                 '- NBA: 스타 선수 활약 중 (르브론, 커리)')
    elif '배구' in user_input:
        reply = ('최근 배구 소식\n'
                 '- V리그: 시즌 마무리 단계\n'
                 '- 국제대회: 올림픽 준비 중\n'
                 '- 주목 선수: 김연경, 황택의')
    elif '배드민턴' in user_input:
        reply = ('최근 배드민턴 소식\n'
                 '- 올림픽: 한국 선수 메달 경쟁\n'
                 '- 세계랭킹: 안세영, 송지현 상위권\n'
                 '- 대회: 코리아오픈 진행 중')
    elif '탁구' in user_input:
        reply = ('최근 탁구 소식\n'
                 '- 국제대회: 중국 선수 우세\n'
                 '- 한국 대표: 장우진, 신유빈\n'
                 '- 올림픽: 메달 기대')
    elif (('시간' in user_input or '식 몇시' in user_input or '몇시' in user_input or '지금' in user_input) and '오류' not in user_input):
        from datetime import datetime
        now = datetime.now()
        reply = f'현재 시간은 {now.hour:02d}:{now.minute:02d} 입니다.'
    elif any(word in user_input for word in ['귀여워', '멋지다', '잘했어', '최고야', '대단해', '멋져']) and '!' in user_input:
        compliments = [
            '감사합니다! 😊',
            '부끄러워요~',
            '칭찬 감사해요!',
            '더 열심히 할게요!',
            '기분 좋네요!'
        ]
        reply = random.choice(compliments)
    elif any(word in user_input for word in ['고민', '힘들어', '지쳐', '슬퍼', '스트레스', '어려워', '힘들다', '괴로워']):
        comforts = [
            '힘내세요! 당신은 잘 해낼 수 있어요.',
            '괜찮아요, 모두가 그런 순간이 있죠.',
            '잘 될 거예요, 조금만 더 참아보세요.',
            '당신의 노력이 헛되지 않을 거예요.',
            '내가 도울 수 있는 게 있을까요?'
        ]
        reply = random.choice(comforts)
    elif any(word in user_input for word in ['일', '노력', '일할', '일하', '업무', '과제', '숙제']):
        reply = '노력은 곧 복이 된다! 💪 당신의 노력이 반드시 결과가 될 거예요. 화이팅!'
    elif '너는 누구야' in user_input or '너 누구야' in user_input or '자기소개' in user_input:
        reply = ('안녕하세요! 저는 44채ㅅ 챗봇입니다. 😊\n'
                 '운세, 추천, 스포츠 근황, 시간, 고민 상담 등 다양한 기능을 제공해요.\n'
                 '궁금한 게 있으면 언제든 물어보세요!')
    elif '가 좋아' in user_input or ' vs ' in user_input or ' 아니면 ' in user_input:
        # 밸런스 게임: 두 옵션 중 랜덤 선택
        import re
        if '가 좋아' in user_input and '아니면' in user_input:
            # "A가 좋아 아니면 B가 좋아" 패턴
            match = re.search(r'(.+?)가 좋아\s*아니면\s*(.+?)가 좋아', user_input)
            if match:
                option1 = match.group(1).strip()
                option2 = match.group(2).strip()
                chosen = random.choice([option1, option2])
                reply = f'저는 {chosen}가 좋아요! 당신은 어떤 게 더 좋나요?'
            else:
                reply = '밸런스 게임을 하려면 "A가 좋아 아니면 B가 좋아" 형식으로 물어봐 주세요!'
        elif '가 좋아' in user_input:
            # "A가 좋아 B가 좋아" 패턴
            match = re.search(r'(.+?)가 좋아\s*(.+?)가 좋아', user_input)
            if match:
                option1 = match.group(1).strip()
                option2 = match.group(2).strip()
                chosen = random.choice([option1, option2])
                reply = f'저는 {chosen}가 좋아요! 당신은 어떤 게 더 좋나요?'
            else:
                reply = '밸런스 게임을 하려면 "A가 좋아 B가 좋아" 형식으로 물어봐 주세요!'
        elif ' vs ' in user_input:
            options = user_input.split(' vs ')
            if len(options) == 2:
                option1 = options[0].strip()
                option2 = options[1].strip()
                chosen = random.choice([option1, option2])
                reply = f'저는 {chosen}를 선택할게요! 당신은 어떤 걸 고를래요?'
            else:
                reply = '밸런스 게임을 하려면 "A vs B" 형식으로 물어봐 주세요!'
        elif ' 아니면 ' in user_input:
            options = user_input.split(' 아니면 ')
            if len(options) == 2:
                option1 = options[0].strip()
                option2 = options[1].strip()
                chosen = random.choice([option1, option2])
                reply = f'저는 {chosen}로 갈게요! 당신은 어느 쪽이에요?'
            else:
                reply = '밸런스 게임을 하려면 "A 아니면 B" 형식으로 물어봐 주세요!'
        else:
            reply = '밸런스 게임을 시작하려면 "A가 좋아 B가 좋아"나 "A vs B" 형식으로 물어봐 주세요!'
    elif '기분' in user_input or '어때' in user_input:
        reply = '저는 AI라서 기분은 없지만, 항상 최선을 다하고 있어요! 당신의 기분은 어떠신가요?'
    
    else:
        reply = random.choice(responses)

    return jsonify(reply=reply)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
