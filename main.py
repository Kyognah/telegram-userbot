import os
import asyncio
from pyrogram import Client, raw

API_ID   = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION  = os.getenv("SESSION_STRING")

TARGET_CHATS = {-1002866597350, -1003984885147}
TRIGGER_WORDS = {"گزارش", "report", "@admin", "صیک", "سیک", "اخطار", "بن", "سکوت", "ban", "mute"}

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION,
    sleep_threshold=0,
    workers=12
)

my_messages = {}
peer_cache = {}


@app.on_raw_update()
async def ultra_fast(client, update, users, chats):

    if isinstance(update, raw.types.UpdateNewChannelMessage):
        msg = update.message
        if not isinstance(msg, raw.types.Message):
            return

        peer = getattr(msg, "peer_id", None)
        if not isinstance(peer, raw.types.PeerChannel):
            return

        chat_id = -(1_000_000_000_000 + peer.channel_id)
        if chat_id not in TARGET_CHATS:
            return

        if getattr(msg, "out", False):
            my_messages.setdefault(chat_id, set()).add(msg.id)
            return

        reply = getattr(msg, "reply_to", None)
        if not reply:
            return

        replied_id = getattr(reply, "reply_to_msg_id", None)
        if not replied_id or replied_id not in my_messages.get(chat_id, set()):
            return

        text = (getattr(msg, "message", "") or "").lower()
        if any(w in text for w in TRIGGER_WORDS):
            try:
                if chat_id not in peer_cache:
                    peer_cache[chat_id] = await client.resolve_peer(chat_id)
                await client.invoke(raw.functions.messages.DeleteMessages(
                    peer=peer_cache[chat_id],
                    id=[replied_id],
                    revoke=True
                ))
                my_messages[chat_id].discard(replied_id)
            except:
                pass


app.run()
