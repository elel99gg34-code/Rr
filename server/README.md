# 온라인 대전 중계 서버

Minecraft PvP 2.0 의 온라인 1대1은 **두 가지 방식**을 지원합니다.

| 방식 | 서버 필요 | 사용법 |
|---|---|---|
| **직접 연결 (P2P)** | ❌ 없음 | 코드를 카톡/디스코드로 주고받기 |
| **서버 방코드** | ⭕ 필요 | 서버 주소 + 4자리 방코드 입력 |

P2P 는 아무 준비 없이 바로 됩니다. 아래는 "방코드" 방식을 쓰고 싶을 때만 보세요.

---

## 왜 Vercel 이 아니라 Cloudflare 인가

- **Vercel** : 서버리스 함수라 WebSocket 같은 **지속 연결을 유지할 수 없습니다**. 게임 HTML(정적 파일) 호스팅은 되지만 중계 서버는 못 돌립니다.
- **GitHub Pages** : 정적 파일만. 게임 배포용으로는 좋지만 서버는 불가.
- **Cloudflare Workers + Durable Objects** : WebSocket 을 정식 지원하고 무료 플랜으로 충분합니다. ✅

## Cloudflare Workers 배포 (권장, 5분)

```bash
npm i -g wrangler
wrangler login
cd server
wrangler deploy
```

배포가 끝나면 `https://mcpvp-relay.<계정>.workers.dev` 주소가 나옵니다.
게임의 **온라인 → 서버 방코드** 탭에 이렇게 넣으세요:

```
wss://mcpvp-relay.<계정>.workers.dev/ws
```

## Node 서버 (Render / Railway / 집 PC)

```bash
cd server
npm install
npm start          # ws://localhost:8787/ws
```

Render 에 올릴 때: Build `npm install`, Start `npm start`, 접속 주소는 `wss://<앱>.onrender.com/ws`.

## 프로토콜

방(room)에 최대 2명. 서버는 **아무 검증 없이 그대로 중계만** 합니다.
전투 판정(무적시간·방어구·넉백)은 전부 클라이언트에서 바닐라 규칙으로 계산하며,
피격 판정의 최종 결정권은 **맞은 쪽**에 있습니다. 친구와 하는 사설 대전용 구조입니다.
