from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
import sqlite3
import random
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'hjuy_secret_2026'

# Google OAuth 설정
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID', 'default_client_id'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET', 'default_secret'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect('hjuy_chatbot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS conversations
                 (id INTEGER PRIMARY KEY, user_id INTEGER, message TEXT, reply TEXT, timestamp TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

init_db()

# 간단한 응답 목록
responses = [
    "안녕하세요! 무엇을 도와드릴까요?",
    "재미있는 이야기네요!",
    "더 자세히 말씀해주세요.",
    "알겠습니다. 계속 이야기해 보세요.",
    "좋은 하루 되세요!",
    "기분이 어떠신가요?"
]

def get_user_id(username):
    conn = sqlite3.connect('hjuy_chatbot.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username=?', (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def save_conversation(user_id, message, reply):
    conn = sqlite3.connect('hjuy_chatbot.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('INSERT INTO conversations (user_id, message, reply, timestamp) VALUES (?, ?, ?, ?)',
              (user_id, message, reply, timestamp))
    conn.commit()
    conn.close()

def get_user_conversations(user_id):
    conn = sqlite3.connect('hjuy_chatbot.db')
    c = conn.cursor()
    c.execute('SELECT message, reply, timestamp FROM conversations WHERE user_id=? ORDER BY timestamp DESC LIMIT 50',
              (user_id,))
    conversations = c.fetchall()
    conn.close()
    return list(reversed(conversations))

# 챗봇 응답 로직
def get_bot_reply(user_input):
    if '운세' in user_input:
        fortune_score = random.randint(1, 100)
        return f'오늘의 운세는 {fortune_score}점입니다. 좋은 하루 되세요!'
    elif '음식' in user_input or '추천' in user_input:
        foods = ['치킨', '피자', '킹크랩', '스테이크', '초밥', '라면', '떡볶이',
                 '비빔밥', '삼겹살', '갈비찜', '짜장면', '짬뽕', '김치찌개', '된장찌개',
                 '회', '샤브샤브', '파스타', '버거', '타코', '브런치']
        chosen = random.sample(foods, 5)
        return f'오늘 추천 메뉴: {", ".join(chosen)}. 이게 땡기네요!'
    elif '스포츠' in user_input or '근황' in user_input:
        return '무슨 종목이 궁금한가요? (예: 축구, 야구, 농구, 배구, 배드민턴, 탁구)'
    elif '축구' in user_input:
        return '최근 축구 소식\n- K리그: 현재 시즌 경쟁 중\n- 챔피언스리그: 톱클럽 경기 진행\n- 스타 선수: 메시, 호날두, 손흥민'
    elif (('시간' in user_input or '식 몇시' in user_input or '몇시' in user_input or '지금' in user_input) and '오류' not in user_input):
        from datetime import datetime
        now = datetime.now()
        return f'현재 시간은 {now.hour:02d}:{now.minute:02d} 입니다.'
    elif any(word in user_input for word in ['귀여워', '멋지다', '잘했어', '최고야', '대단해', '멋져']) and '!' in user_input:
        compliments = ['감사합니다! 😊', '부끄러워요~', '칭찬 감사해요!', '더 열심히 할게요!', '기분 좋네요!']
        return random.choice(compliments)
    elif any(word in user_input for word in ['고민', '힘들어', '지쳐', '슬퍼', '스트레스', '어려워', '힘들다', '괴로워']):
        comforts = ['힘내세요! 당신은 잘 해낼 수 있어요.',
                    '괜찮아요, 모두가 그런 순간이 있죠.',
                    '잘 될 거예요, 조금만 더 참아보세요.',
                    '당신의 노력이 헛되지 않을 거예요.',
                    '내가 도울 수 있는 게 있을까요?']
        return random.choice(comforts)
    elif any(word in user_input for word in ['일', '노력', '일할', '일하', '업무', '과제', '숙제']):
        return '노력은 곧 복이 된다! 💪 당신의 노력이 반드시 결과가 될 거예요. 화이팅!'
    elif '너는 누구야' in user_input or '너 누구야' in user_input or '자기소개' in user_input:
        return '안녕하세요! 저는 44채ㅅ 챗봇입니다. 😊\n운세, 추천, 스포츠 근황, 시간, 고민 상담 등 다양한 기능을 제공해요.\n궁금한 게 있으면 언제든 물어보세요!'
    elif '가 좋아' in user_input or ' vs ' in user_input or ' 아니면 ' in user_input:
        import re
        if '가 좋아' in user_input and '아니면' in user_input:
            match = re.search(r'(.+?)가 좋아\s*아니면\s*(.+?)가 좋아', user_input)
            if match:
                option1, option2 = match.group(1).strip(), match.group(2).strip()
                chosen = random.choice([option1, option2])
                return f'저는 {chosen}가 좋아요! 당신은 어떤 게 더 좋나요?'
        elif ' vs ' in user_input:
            options = user_input.split(' vs ')
            if len(options) == 2:
                chosen = random.choice([options[0].strip(), options[1].strip()])
                return f'저는 {chosen}를 선택할게요! 당신은 어떤 걸 고를래요?'
        elif ' 아니면 ' in user_input:
            options = user_input.split(' 아니면 ')
            if len(options) == 2:
                chosen = random.choice([options[0].strip(), options[1].strip()])
                return f'저는 {chosen}로 갈게요! 당신은 어느 쪽이에요?'
    elif '기분' in user_input or '어때' in user_input:
        return '저는 AI라서 기분은 없지만, 항상 최선을 다하고 있어요! 당신의 기분은 어떠신가요?'
    else:
        return random.choice(responses)

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('chatbot'))
    
    html = '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>44채ㅅ 챗봇 - 홈</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Malgun Gothic', Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; }
            .container { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 600px; text-align: center; }
            h1 { color: #667eea; margin-bottom: 20px; }
            p { color: #555; margin-bottom: 30px; line-height: 1.6; }
            .btn-group { display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; }
            a, button { padding: 12px 30px; border: none; border-radius: 10px; cursor: pointer; font-size: 16px; text-decoration: none; display: inline-flex; align-items: center; gap: 8px; }
            .btn-login { background: #667eea; color: white; }
            .btn-register { background: #764ba2; color: white; }
            .btn-google { background: white; color: #333; border: 1px solid #ddd; }
            .btn-login:hover { background: #5568d3; }
            .btn-register:hover { background: #6a3f91; }
            .btn-google:hover { background: #f5f5f5; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 44채ㅅ 챗봇</h1>
            <p>
                안녕하세요! 저는 44채ㅅ 챗봇입니다.<br/>
                운세, 추천, 스포츠 근황, 시간, 고민 상담 등 다양한 기능을 제공합니다.<br/>
                로그인 후 채팅을 시작하세요!
            </p>
            <div class="btn-group">
                <a href="/login" class="btn-login">로그인</a>
                <a href="/register" class="btn-register">회원가입</a>
                <a href="/login/google" class="btn-google">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                    </svg>
                    Google
                </a>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        conn = sqlite3.connect('hjuy_chatbot.db')
        c = conn.cursor()
        c.execute('SELECT id, password FROM users WHERE username=?', (username,))
        result = c.fetchone()
        conn.close()
        
        if result and check_password_hash(result[1], password):
            session['username'] = username
            session['user_id'] = result[0]
            return jsonify(success=True)
        else:
            return jsonify(success=False, error='사용자명 또는 비밀번호가 잘못되었습니다.')
    
    html = '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>로그인</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Malgun Gothic', Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; }
            .form-container { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 400px; width: 100%; }
            h2 { color: #667eea; margin-bottom: 30px; text-align: center; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 8px; color: #555; font-weight: bold; }
            input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
            input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.1); }
            button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; margin-bottom: 10px; }
            button:hover { background: #5568d3; }
            .divider { display: flex; align-items: center; margin: 20px 0; }
            .divider::before { content: ''; flex: 1; height: 1px; background: #ddd; }
            .divider::after { content: ''; flex: 1; height: 1px; background: #ddd; }
            .divider span { padding: 0 10px; color: #999; font-size: 12px; }
            .social-btn { display: flex; align-items: center; justify-content: center; gap: 8px; background: white; color: #333; border: 1px solid #ddd; }
            .social-btn:hover { background: #f5f5f5; }
            .error { color: #e74c3c; margin-top: 20px; text-align: center; }
            .link { text-align: center; margin-top: 20px; }
            .link a { color: #667eea; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="form-container">
            <h2>로그인</h2>
            <div class="form-group">
                <label>사용자명</label>
                <input type="text" id="username" placeholder="사용자명 입력"/>
            </div>
            <div class="form-group">
                <label>비밀번호</label>
                <input type="password" id="password" placeholder="비밀번호 입력"/>
            </div>
            <button onclick="login()">로그인</button>
            <div class="divider"><span>또는</span></div>
            <a href="/login/google" style="text-decoration: none;">
                <button type="button" class="social-btn">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                    </svg>
                    Google로 로그인
                </button>
            </a>
            <div id="error" class="error"></div>
            <div class="link"><a href="/">홈으로 돌아가기</a> | 계정이 없으신가요? <a href="/register">가입하기</a></div>
        </div>
        <script>
            function login() {
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                fetch('/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = '/chatbot';
                    } else {
                        document.getElementById('error').innerText = data.error;
                    }
                });
            }
            document.getElementById('password').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') login();
            });
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if len(username) < 3 or len(password) < 4:
            return jsonify(success=False, error='사용자명은 3자 이상, 비밀번호는 4자 이상이어야 합니다.')
        
        hashed_password = generate_password_hash(password)
        conn = sqlite3.connect('hjuy_chatbot.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            conn.close()
            return jsonify(success=True)
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify(success=False, error='이미 존재하는 사용자명입니다.')
    
    html = '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>회원가입</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Malgun Gothic', Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; }
            .form-container { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 400px; width: 100%; }
            h2 { color: #667eea; margin-bottom: 30px; text-align: center; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 8px; color: #555; font-weight: bold; }
            input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
            input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.1); }
            button { width: 100%; padding: 12px; background: #764ba2; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
            button:hover { background: #6a3f91; }
            .error { color: #e74c3c; margin-top: 20px; text-align: center; }
            .link { text-align: center; margin-top: 20px; }
            .link a { color: #667eea; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="form-container">
            <h2>회원가입</h2>
            <div class="form-group">
                <label>사용자명</label>
                <input type="text" id="username" placeholder="사용자명 입력"/>
            </div>
            <div class="form-group">
                <label>비밀번호</label>
                <input type="password" id="password" placeholder="비밀번호 입력"/>
            </div>
            <button onclick="register()">회원가입</button>
            <div id="error" class="error"></div>
            <div class="link"><a href="/">홈으로 돌아가기</a></div>
        </div>
        <script>
            function register() {
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                fetch('/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert('회원가입 완료! 로그인해주세요.');
                        window.location.href = '/login';
                    } else {
                        document.getElementById('error').innerText = data.error;
                    }
                });
            }
            document.getElementById('password').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') register();
            });
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/chatbot')
def chatbot():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    conversations = get_user_conversations(session['user_id'])
    conv_html = ''.join([f'<div class="conv-item"><p><strong>당신:</strong> {msg}</p><p><strong>44채ㅅ:</strong> {reply}</p><p style="color: #999; font-size: 12px;">{ts}</p></div>' 
                         for msg, reply, ts in conversations])
    
    html = f'''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>44채ㅅ 챗봇</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Malgun Gothic', Arial; background: #f5f7fa; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; display: flex; justify-content: space-between; align-items: center; }}
            .logout {{ background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 8px; cursor: pointer; color: white; text-decoration: none; }}
            .container {{ display: flex; max-width: 1200px; margin: 0 auto; gap: 20px; padding: 20px; height: calc(100vh - 80px); }}
            .menu {{ 
                width: 250px; 
                background: white; 
                border-radius: 12px; 
                padding: 20px; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                overflow-y: auto;
            }}
            .menu-title {{ font-weight: bold; color: #667eea; margin-bottom: 15px; }}
            .menu-item {{ padding: 10px; margin: 8px 0; background: #f0f2f5; border-radius: 8px; cursor: pointer; transition: all 0.3s; }}
            .menu-item:hover {{ background: #667eea; color: white; }}
            .chat-area {{ 
                flex: 1; 
                display: flex; 
                flex-direction: column; 
                background: white; 
                border-radius: 12px; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            #chatLog {{ 
                flex: 1; 
                overflow-y: auto; 
                padding: 20px; 
                background: #f9fafb;
            }}
            .conv-item {{ 
                margin-bottom: 15px; 
                padding: 12px; 
                background: white; 
                border-radius: 8px; 
                border-left: 4px solid #667eea;
            }}
            .input-area {{ 
                display: flex; 
                gap: 10px; 
                padding: 20px; 
                border-top: 1px solid #eee;
            }}
            #userInput {{ 
                flex: 1; 
                padding: 12px; 
                border: 1px solid #ddd; 
                border-radius: 8px; 
                font-size: 14px;
            }}
            button {{ 
                padding: 12px 24px; 
                background: #667eea; 
                color: white; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer;
            }}
            button:hover {{ background: #5568d3; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 44채ㅅ 챗봇</h1>
            <div>
                <span style="margin-right: 20px;">{{session['username']}}님</span>
                <a href="/logout" class="logout">로그아웃</a>
            </div>
        </div>
        <div class="container">
            <div class="menu">
                <div class="menu-title">기능</div>
                <div class="menu-item" onclick="insertText('운세')">🎲 운세</div>
                <div class="menu-item" onclick="insertText('음식 추천')">🍔 음식 추천</div>
                <div class="menu-item" onclick="insertText('요즘 스포츠 근황')">⚽ 스포츠</div>
                <div class="menu-item" onclick="insertText('지금 몇시?')">⏰ 시간</div>
                <div class="menu-item" onclick="insertText('너는 누구야')">🤖 자기소개</div>
                <div class="menu-item" onclick="insertText('사이다 vs 콜라')">🎮 밸런스게임</div>
                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd;"></div>
                <div class="menu-title">대화 기록</div>
                <div style="font-size: 12px; color: #999;">최근 50개 대화가 저장됩니다.</div>
            </div>
            <div class="chat-area">
                <div id="chatLog">
                    {conv_html if conv_html else '<p style="color: #999; text-align: center; padding: 40px; margin-top: auto; margin-bottom: auto;">아직 대화 기록이 없습니다. 시작하세요!</p>'}
                </div>
                <div class="input-area">
                    <input type="text" id="userInput" placeholder="메시지를 입력하세요..."/>
                    <button onclick="sendMessage()">전송</button>
                </div>
            </div>
        </div>
        <script>
            function insertText(text) {{
                document.getElementById('userInput').value = text;
                document.getElementById('userInput').focus();
            }}
            function sendMessage() {{
                const text = document.getElementById('userInput').value.trim();
                if (!text) return;
                
                const log = document.getElementById('chatLog');
                const userDiv = document.createElement('div');
                userDiv.className = 'conv-item';
                userDiv.innerHTML = '<p><strong>당신:</strong> ' + text + '</p>';
                log.appendChild(userDiv);
                
                fetch('/chat', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ message: text }})
                }})
                .then(res => res.json())
                .then(data => {{
                    const replyDiv = document.createElement('div');
                    replyDiv.className = 'conv-item';
                    const now = new Date().toLocaleString('ko-KR');
                    replyDiv.innerHTML = '<p><strong>44채ㅅ:</strong> ' + data.reply + '</p><p style="color: #999; font-size: 12px;">' + now + '</p>';
                    log.appendChild(replyDiv);
                    log.scrollTop = log.scrollHeight;
                }});
                
                document.getElementById('userInput').value = '';
            }}
            document.getElementById('userInput').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') sendMessage();
            }});
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify(reply='로그인이 필요합니다.'), 401
    
    data = request.get_json() or {}
    user_input = data.get('message', '').strip()
    
    if not user_input:
        return jsonify(reply='메시지를 입력해주세요.'), 400
    
    reply = get_bot_reply(user_input)
    save_conversation(session['user_id'], user_input, reply)
    
    return jsonify(reply=reply)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/login/google')
def login_google():
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/callback')
def google_callback():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0])
        
        # 이메일로 사용자 확인
        conn = sqlite3.connect('hjuy_chatbot.db')
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username=?', (email,))
        user = c.fetchone()
        
        if not user:
            # 새로운 사용자 생성 (임시 비밀번호 사용)
            temp_password = generate_password_hash('google_oauth_user')
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (email, temp_password))
            conn.commit()
            c.execute('SELECT id FROM users WHERE username=?', (email,))
            user = c.fetchone()
        
        conn.close()
        
        # 세션 설정
        session['username'] = email
        session['user_id'] = user[0]
        
        return redirect(url_for('chatbot'))
    except Exception as e:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
