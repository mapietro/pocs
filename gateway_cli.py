"""
 Requisitos: pip install requests
 Variáveis de ambiente:

 WHATSAPP_GATEWAY_API_KEY (obrigatório)

GATEWAY_BASE_URL (opcional, default http://localhost:8000)
"""


from dotenv import load_dotenv  # <--- Adicione isto
import os
import sys
import time
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

import requests

# ----------------------------
# Config
# ----------------------------
load_dotenv()

BASE_URL = os.getenv("GATEWAY_BASE_URL", "http://localhost:8000").rstrip("/")
API_KEY = os.getenv("WHATSAPP_GATEWAY_API_KEY")

if not API_KEY:
    print("ERRO: defina a variável WHATSAPP_GATEWAY_API_KEY no ambiente.")
    sys.exit(1)

HEADERS = {"X-API-Key": API_KEY}


# ----------------------------
# HTTP helpers
# ----------------------------
def http_get(path: str, params: dict | None = None) -> dict:
    url = f"{BASE_URL}{path}"
    r = requests.get(url, headers=HEADERS, params=params or {}, timeout=30)
    r.raise_for_status()
    return r.json()


def http_post_json(path: str, payload: dict) -> dict:
    url = f"{BASE_URL}{path}"
    r = requests.post(
        url,
        headers={**HEADERS, "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def iso_now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


# ----------------------------
# Gateway: Conversations & Messages
# ----------------------------
def list_conversations(limit: int = 20) -> dict:
    return http_get("/gateway/conversations", params={"limit": limit})


def list_messages(conversation_id: str, limit: int = 50, cursor: str | None = None) -> dict:
    params = {"limit": limit}
    if cursor:
        params["cursor"] = cursor
    return http_get(f"/gateway/conversations/{conversation_id}/messages", params=params)


def get_delta(conversation_id: str, since_cursor: str | None, updated_since: str | None, limit: int = 200) -> dict:
    params = {"limit": limit}
    if since_cursor:
        params["since_cursor"] = since_cursor
    if updated_since:
        params["updated_since"] = updated_since
    return http_get(f"/gateway/conversations/{conversation_id}/messages/delta", params=params)


def upsert(local_by_id: dict[str, dict], item: dict) -> None:
    msg_id = item.get("id")
    if not msg_id:
        return

    if msg_id in local_by_id:
        # Atualiza campos mutáveis
        for k in ["status", "updated_at", "error_message", "content", "provider_message_id", "metadata"]:
            if k in item:
                local_by_id[msg_id][k] = item[k]
    else:
        local_by_id[msg_id] = item


def format_msg(m: dict) -> str:
    direction = m.get("direction", "?")
    mtype = m.get("message_type", "?")
    status = m.get("status", "?")
    created_at = (m.get("created_at") or "")[:19].replace("T", " ")
    updated_at = (m.get("updated_at") or "")[:19].replace("T", " ")
    content = m.get("content") or {}

    # Texto
    if isinstance(content, dict) and "text" in content:
        body = content.get("text", "")

    # Placeholder de mídia
    elif isinstance(content, dict) and content.get("media_asset_id"):
        fname = content.get("file_name") or "media"
        body = f"[MEDIA {mtype}] {fname} (media_asset_id={content.get('media_asset_id')})"

    else:
        body = str(content)[:120]

    return f"{created_at} [{direction}] {mtype} {status} | {body} | upd={updated_at}"


def run_poll(conversation_id: str, history_limit: int, poll_interval: float, delta_limit: int, max_render: int):
    # 1) Cold start: histórico
    hist = list_messages(conversation_id, limit=history_limit)
    local: dict[str, dict] = {}
    for it in hist.get("items", []):
        upsert(local, it)

    ordered = sorted(local.values(), key=lambda x: (x.get("created_at", ""), x.get("id", "")))

    # Inicialização pragmática de since_cursor (o delta devolverá next_since_cursor oficial)
    since_cursor = None
    if ordered:
        last = ordered[-1]
        since_cursor = f"{last.get('created_at')}|{last.get('id')}"

    # updated_since inicial: agora; depois vira server_time do gateway
    updated_since = iso_now_utc()

    print(f"Polling conversation_id={conversation_id}")
    print("Ctrl+C para sair.\n")

    while True:
        try:
            # Renderiza
            ordered = sorted(local.values(), key=lambda x: (x.get("created_at", ""), x.get("id", "")))
            os.system("cls" if os.name == "nt" else "clear")

            print(f"Gateway: {BASE_URL}")
            print(f"Conversation: {conversation_id}")
            print(f"since_cursor: {since_cursor}")
            print(f"updated_since: {updated_since}")
            print("-" * 110)

            tail = ordered[-max_render:] if len(ordered) > max_render else ordered
            for m in tail:
                print(format_msg(m))

            print("-" * 110)
            print(f"Polling a cada {poll_interval}s | delta_limit={delta_limit}")

            # 2) Delta
            delta = get_delta(conversation_id, since_cursor=since_cursor, updated_since=updated_since, limit=delta_limit)

            for it in delta.get("items", []):
                upsert(local, it)

            if delta.get("next_since_cursor"):
                since_cursor = delta["next_since_cursor"]

            updated_since = delta.get("server_time") or updated_since

            time.sleep(poll_interval)

        except requests.HTTPError as e:
            print(f"HTTPError: {e}")
            time.sleep(poll_interval)
        except requests.RequestException as e:
            print(f"RequestException: {e}")
            time.sleep(poll_interval)


# ----------------------------
# Gateway: Media
# ----------------------------
def media_upload(file_path: str, idempotency_key: str | None = None) -> dict:
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    url = f"{BASE_URL}/gateway/media/upload"
    headers = dict(HEADERS)
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key

    with p.open("rb") as f:
        files = {"file": (p.name, f)}
        r = requests.post(url, headers=headers, files=files, timeout=120)
        r.raise_for_status()
        return r.json()


def media_download_info(media_asset_id: str) -> dict:
    return http_get(f"/gateway/media/{media_asset_id}/download")


def media_download_file(media_asset_id: str, out_dir: str = ".") -> Path:
    info = media_download_info(media_asset_id)
    download_url = info.get("download_url")
    if not download_url:
        raise RuntimeError(f"Resposta sem download_url: {info}")

    filename = info.get("file_name") or f"{media_asset_id}.bin"
    out_path = Path(out_dir) / filename

    # baixa o binário direto da signed URL
    r = requests.get(download_url, stream=True, timeout=180)
    r.raise_for_status()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as w:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                w.write(chunk)

    return out_path


# ----------------------------
# Gateway: Send media message (requires conversation_id in your API)
# ----------------------------
def send_media(to: str, conversation_id: str, media_asset_id: str, msg_type: str, message_id: str | None = None) -> dict:
    payload = {
        "to": to,
        "conversation_id": conversation_id,
        "type": msg_type,  # "audio" ou "document"
        "media_asset_id": media_asset_id,
        "message_id": message_id or f"cli-{int(time.time())}",
    }    
    return http_post_json("/gateway/send", payload)


# ----------------------------
# CLI Entrypoint
# ----------------------------
def main():
    parser = argparse.ArgumentParser(
        description="CLI pseudo-front para testar Polling (Chat Read APIs) + Mídia (upload/download/send) no WhatsApp Gateway"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_conv = sub.add_parser("conversations", help="Listar conversas do tenant")
    p_conv.add_argument("--limit", type=int, default=20)

    p_hist = sub.add_parser("messages", help="Listar histórico de mensagens de uma conversa (1 página)")
    p_hist.add_argument("conversation_id")
    p_hist.add_argument("--limit", type=int, default=50)
    p_hist.add_argument("--cursor", default=None)

    p_poll = sub.add_parser("poll", help="Rodar polling/delta para uma conversa")
    p_poll.add_argument("conversation_id")
    p_poll.add_argument("--history", type=int, default=50)
    p_poll.add_argument("--interval", type=float, default=2.5)
    p_poll.add_argument("--delta-limit", type=int, default=200)
    p_poll.add_argument("--render", type=int, default=30)

    p_up = sub.add_parser("media-upload", help="Upload de mídia (multipart) e retorna media_asset_id")
    p_up.add_argument("file")
    p_up.add_argument("--idem", help="Idempotency-Key", default=None)

    p_info = sub.add_parser("media-info", help="Obter JSON de download (download_url etc.)")
    p_info.add_argument("media_asset_id")

    p_dl = sub.add_parser("media-download", help="Baixar o binário via signed URL retornada pelo gateway")
    p_dl.add_argument("media_asset_id")
    p_dl.add_argument("--out", default=".", help="Diretório de saída")

    p_send = sub.add_parser("send-media", help="Enviar mensagem com mídia usando conversation_id + media_asset_id")
    p_send.add_argument("--to", required=True, help="Destinatário (wa_id/telefone), ex: 5511999999999")
    p_send.add_argument("--conversation-id", required=True, help="UUID da conversa (você disse que vai pegar do banco)")
    p_send.add_argument("--media-asset-id", required=True)
    p_send.add_argument("--type", required=True, choices=["audio", "document"])
    p_send.add_argument("--message-id", default=None)

    args = parser.parse_args()

    if args.cmd == "conversations":
        data = list_conversations(limit=args.limit)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    if args.cmd == "messages":
        data = list_messages(args.conversation_id, limit=args.limit, cursor=args.cursor)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    if args.cmd == "poll":
        print(args.conversation_id)
        run_poll(args.conversation_id, args.history, args.interval, args.delta_limit, args.render)
        return

    if args.cmd == "media-upload":
        resp = media_upload(args.file, idempotency_key=args.idem)
        print(json.dumps(resp, indent=2, ensure_ascii=False))
        return

    if args.cmd == "media-info":
        resp = media_download_info(args.media_asset_id)
        print(json.dumps(resp, indent=2, ensure_ascii=False))
        return

    if args.cmd == "media-download":
        out = media_download_file(args.media_asset_id, out_dir=args.out)
        print(f"OK: baixado em {out}")
        return

    if args.cmd == "send-media":
        resp = send_media(
            to=args.to,
            conversation_id=args.conversation_id,
            media_asset_id=args.media_asset_id,
            msg_type=args.type,
            message_id=args.message_id,
        )
        print(json.dumps(resp, indent=2, ensure_ascii=False))
        return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSaindo.")
