/* =====================================================================
   Minecraft PvP 2.0 — 온라인 대전 중계 서버 (Cloudflare Workers)
   Durable Object 로 방(room)을 만들고 두 명을 이어 준다.
   배포:  npm i -g wrangler && wrangler deploy
   접속 주소:  wss://<이름>.<계정>.workers.dev/ws
   ===================================================================== */

export class Room {
  constructor(state) {
    this.state = state;
    this.peers = [];          // [{ws, name, host}]
  }

  async fetch(request) {
    if (request.headers.get('Upgrade') !== 'websocket')
      return new Response('websocket only', { status: 426 });

    const pair = new WebSocketPair();
    const [client, server] = Object.values(pair);
    server.accept();

    if (this.peers.length >= 2) {
      server.send(JSON.stringify({ t: 'full' }));
      server.close(1000, 'room full');
      return new Response(null, { status: 101, webSocket: client });
    }

    const peer = { ws: server, name: '플레이어', host: this.peers.length === 0 };
    this.peers.push(peer);

    server.addEventListener('message', (ev) => {
      let m = null;
      try { m = JSON.parse(ev.data); } catch (e) { }
      if (m && m.t === 'join') {
        peer.name = String(m.name || '플레이어').slice(0, 12);
        server.send(JSON.stringify({ t: 'joined', host: peer.host }));
        if (this.peers.length === 2) {
          for (const p of this.peers) {
            try { p.ws.send(JSON.stringify({ t: 'peer', host: p.host })); } catch (e) { }
          }
        }
        return;
      }
      /* 그 외 모든 패킷은 상대에게 그대로 중계 */
      for (const p of this.peers) {
        if (p === peer) continue;
        try { p.ws.send(ev.data); } catch (e) { }
      }
    });

    const bye = () => {
      this.peers = this.peers.filter((p) => p !== peer);
      for (const p of this.peers) {
        try { p.ws.send(JSON.stringify({ t: 'left' })); } catch (e) { }
      }
    };
    server.addEventListener('close', bye);
    server.addEventListener('error', bye);

    return new Response(null, { status: 101, webSocket: client });
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === '/' || url.pathname === '/health') {
      return new Response('Minecraft PvP 2.0 relay OK', {
        headers: { 'content-type': 'text/plain; charset=utf-8' }
      });
    }
    if (url.pathname !== '/ws') return new Response('not found', { status: 404 });

    const room = (url.searchParams.get('room') || 'LOBBY').toUpperCase().slice(0, 8);
    const id = env.ROOM.idFromName(room);
    return env.ROOM.get(id).fetch(request);
  }
};
