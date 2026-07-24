import os
import asyncio
from pyrogram import Client
from pyrogram.raw import types as raw_types

API_ID   = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION  = os.getenv("SESSION_STRING")

TARGET_CHATS = {-1002866597350, -1003984885147}

TRIGGER_WORDS = {
    "گزارش", "report", "@admin",
    "صیک", "سیک", "اخطار", "بن", "سکوت",
    "ban", "mute"
}

def full_id(channel_id: int) -> int:
    return -(1_000_000_000_000 + channel_id)

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

async def delete_msg(client: Client, chat_id: int, msg_id: int):
    try:
        await client.delete_messages(chat_id, msg_id)
    except:
        pass
    my_messages.get(chat_id, set()).discard(msg_id)


@app.on_raw_update()
async def raw_handler(client, update, users, chats):

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

        reply = getattr(msg, "reply_to", None)
        if not reply:
            return

        replied_id = getattr(reply, "reply_to_msg_id", None)
        if not replied_id or replied_id not in my_messages.get(chat_id, set()):
            return

        text = (getattr(msg, "message", "") or "").lower()
        if any(word in text for word in TRIGGER_WORDS):
            asyncio.create_task(delete_msg(client, chat_id, replied_id))


app.run()
