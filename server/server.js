/* =====================================================================
   Minecraft PvP 2.0 — 온라인 대전 중계 서버 (Node.js 버전)
   Render / Railway / Fly.io / 집 PC 어디서나 동작한다.
     npm init -y && npm i ws && node server.js
   접속 주소:  ws://localhost:8787/ws   또는  wss://<배포주소>/ws
   ===================================================================== */
const http = require('http');
const { WebSocketServer } = require('ws');

const PORT = process.env.PORT || 8787;
const rooms = new Map();          // room -> [ws, ws]

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'content-type': 'text/plain; charset=utf-8' });
  res.end('Minecraft PvP 2.0 relay OK');
});

const wss = new WebSocketServer({ server, path: '/ws' });

wss.on('connection', (ws, req) => {
  let room = null;

  ws.on('message', (data) => {
    let m = null;
    try { m = JSON.parse(data); } catch (e) { }

    if (m && m.t === 'join') {
      room = String(m.room || 'LOBBY').toUpperCase().slice(0, 8);
      let list = rooms.get(room);
      if (!list) { list = []; rooms.set(room, list); }
      if (list.length >= 2) {
        ws.send(JSON.stringify({ t: 'full' }));
        ws.close();
        return;
      }
      ws._host = list.length === 0;
      ws._room = room;
      list.push(ws);
      ws.send(JSON.stringify({ t: 'joined', host: ws._host }));
      if (list.length === 2) {
        for (const p of list) {
          try { p.send(JSON.stringify({ t: 'peer', host: p._host })); } catch (e) { }
        }
      }
      return;
    }

    /* 상대에게 그대로 중계 */
    const list = rooms.get(ws._room) || [];
    for (const p of list) {
      if (p !== ws && p.readyState === 1) { try { p.send(data.toString()); } catch (e) { } }
    }
  });

  const bye = () => {
    const list = rooms.get(ws._room);
    if (!list) return;
    const i = list.indexOf(ws);
    if (i >= 0) list.splice(i, 1);
    for (const p of list) { try { p.send(JSON.stringify({ t: 'left' })); } catch (e) { } }
    if (!list.length) rooms.delete(ws._room);
  };
  ws.on('close', bye);
  ws.on('error', bye);
});

server.listen(PORT, () => console.log('relay listening on :' + PORT + ' (path /ws)'));
