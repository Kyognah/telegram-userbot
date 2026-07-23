from pyrogram import Client, raw
from pyrogram.raw.types import (
    UpdateNewChannelMessage,
    UpdateChannelUserTyping,
    UpdateUserTyping
)
import os

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_string = os.getenv("SESSION_STRING")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

TARGET_CHATS = {-1002866597350, -1003984885147}

app = Client(
    "userbot",
    api_id=api_id,
    api_hash=api_hash,
    session_string=session_string,
    sleep_threshold=0,
    workers=4
)

my_messages = set()

@app.on_raw_update()
async def ultra_fast(client, update, users, chats):
    # === تشخیص ریپلای (کانال) ===
    if isinstance(update, UpdateNewChannelMessage):
        msg = update.message
        if msg.reply_to and msg.reply_to.reply_to_msg_id in my_messages:
            try:
                await client.delete_messages(msg.chat_id, msg.reply_to.reply_to_msg_id)
                my_messages.discard(msg.reply_to.reply_to_msg_id)
            except:
                pass

    # === تشخیص typing در کانال ===
    elif isinstance(update, UpdateChannelUserTyping):
        user_id = None
        if update.from_id and hasattr(update.from_id, "user_id"):
            user_id = update.from_id.user_id

        chat_id = None
        if update.channel_id:
            chat_id = -1000000000000 + update.channel_id

        if user_id == ADMIN_ID and chat_id in TARGET_CHATS:
            if my_messages:
                msg_id = my_messages.pop()
                try:
                    await client.delete_messages(chat_id, msg_id)
                except:
                    pass

    elif isinstance(update, UpdateUserTyping):
        pass

@app.on_message()
async def save_my_message(_, message):
    if message.chat.id in TARGET_CHATS and message.from_user and message.from_user.is_self:
        my_messages.add(message.id)

app.run()