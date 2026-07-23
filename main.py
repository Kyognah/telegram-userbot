import os
import asyncio
from pyrogram import Client
from pyrogram.raw import types as raw_types

API_ID   = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION  = os.getenv("SESSION_STRING")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

TARGET_CHATS: set[int] = {-1002866597350, -1003984885147}

def raw_id(chat_id: int) -> int:
    return abs(chat_id) - 1_000_000_000_000

def full_id(channel_id: int) -> int:
    return -(1_000_000_000_000 + channel_id)

TARGET_RAW_IDS: set[int] = {raw_id(c) for c in TARGET_CHATS}

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION,
    sleep_threshold=0,
    workers=8,
)

my_messages: dict[int, set[int]] = {}

def store_msg(chat_id: int, msg_id: int):
    my_messages.setdefault(chat_id, set()).add(msg_id)

async def nuke(client: Client, chat_id: int, msg_id: int):
    try:
        await client.delete_messages(chat_id, msg_id)
    except Exception:
        pass
    my_messages.get(chat_id, set()).discard(msg_id)

async def nuke_all(client: Client, chat_id: int):
    ids = list(my_messages.get(chat_id, set()))
    if not ids:
        return
    my_messages[chat_id].clear()
    try:
        for i in range(0, len(ids), 100):
            await client.delete_messages(chat_id, ids[i:i+100])
    except Exception:
        pass


# ─── ذخیره پیام‌های ارسالی ─────────────────────────────────────────────────
@app.on_raw_update()
async def raw_handler(client, update, users, chats):

    # ══ ذخیره پیام‌های خودمون (هم معمولی، هم ناشناس) ════════════════════════
    if isinstance(update, raw_types.UpdateNewChannelMessage):
        msg = update.message
        if not isinstance(msg, raw_types.Message):
            return

        peer = getattr(msg, "peer_id", None)
        if not isinstance(peer, raw_types.PeerChannel):
            return

        chat_id = full_id(peer.channel_id)
        if chat_id not in TARGET_CHATS:
            return

        # ✅ تشخیص پیام خودمون — هم حالت معمولی هم ناشناس
        from_id = getattr(msg, "from_id", None)
        is_mine = False

        if isinstance(from_id, raw_types.PeerUser):
            me = await client.get_me()
            is_mine = (from_id.user_id == me.id)

        elif isinstance(from_id, raw_types.PeerChannel):
            is_mine = (from_id.channel_id == peer.channel_id)

        if is_mine:
            store_msg(chat_id, msg.id)
            return

        # ══ ریپلای به پیام ما ════════════════════════════════════════════════
        reply = getattr(msg, "reply_to", None)
        if not reply:
            return

        replied_id = getattr(reply, "reply_to_msg_id", None)
        if replied_id and replied_id in my_messages.get(chat_id, set()):
            asyncio.create_task(nuke(client, chat_id, replied_id))

    # ══ تایپینگ در سوپرگروپ ══════════════════════════════════════════════════
    elif isinstance(update, raw_types.UpdateChannelUserTyping):
        if update.channel_id not in TARGET_RAW_IDS:
            return

        chat_id = full_id(update.channel_id)
        from_id = getattr(update, "from_id", None)
        triggered = False

        if isinstance(from_id, raw_types.PeerUser):
            triggered = (from_id.user_id == ADMIN_ID)

        elif isinstance(from_id, raw_types.PeerChannel):
            triggered = (from_id.channel_id == update.channel_id)

        if triggered:
            asyncio.create_task(nuke_all(client, chat_id))


app.run()
