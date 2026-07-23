from pyrogram import Client
from pyrogram.raw.types import (
    UpdateNewChannelMessage,
    UpdateChannelUserTyping,
    PeerUser,
    PeerChannel,
)
import os

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_string = os.getenv("SESSION_STRING")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

TARGET_CHATS = {-1002866597350, -1003984885147}
TARGET_CHANNEL_IDS = {abs(cid) - 1000000000000 for cid in TARGET_CHATS}


def to_chat_id(channel_id: int) -> int:
    return -(1000000000000 + channel_id)


app = Client(
    "userbot",
    api_id=api_id,
    api_hash=api_hash,
    session_string=session_string,
    sleep_threshold=0,
    workers=4,
)

my_messages: set[int] = set()


@app.on_raw_update()
async def ultra_fast(client, update, users, chats):

    # === ریپلای به پیام ما ===
    if isinstance(update, UpdateNewChannelMessage):
        msg = update.message

        if not hasattr(msg, "peer_id") or not hasattr(msg.peer_id, "channel_id"):
            return

        chat_id = to_chat_id(msg.peer_id.channel_id)
        if chat_id not in TARGET_CHATS:
            return

        reply = getattr(msg, "reply_to", None)
        if reply and getattr(reply, "reply_to_msg_id", None) in my_messages:
            target_id = reply.reply_to_msg_id
            try:
                await client.delete_messages(chat_id, target_id)
                my_messages.discard(target_id)
            except:
                pass

    # === تشخیص typing ===
    elif isinstance(update, UpdateChannelUserTyping):
        if update.channel_id not in TARGET_CHANNEL_IDS:
            return

        chat_id = to_chat_id(update.channel_id)
        from_id = getattr(update, "from_id", None)

        is_target = False

        if isinstance(from_id, PeerUser):
            is_target = (from_id.user_id == ADMIN_ID)

        elif isinstance(from_id, PeerChannel):
            is_target = (from_id.channel_id == update.channel_id)

        elif from_id is None:
            is_target = True

        if is_target and my_messages:
            msg_id = my_messages.pop()
            try:
                await client.delete_messages(chat_id, msg_id)
            except:
                pass


@app.on_message()
async def save_my_message(_, message):
    if message.chat.id not in TARGET_CHATS:
        return

    if message.from_user and message.from_user.is_self:
        my_messages.add(message.id)
        return

    if message.sender_chat and message.sender_chat.id == message.chat.id:
        my_messages.add(message.id)


app.run()
