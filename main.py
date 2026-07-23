import uvloop
uvloop.install()

from pyrogram import Client, raw
from pyrogram.raw.types import UpdateNewMessage, UpdateUserTyping, UpdateChatUserTyping

import os

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_string = os.getenv("SESSION_STRING")
admin_id = int(os.getenv("ADMIN_ID"))

TARGET_CHATS = {-1002866597350, -1003984885147}

app = Client("userbot", api_id=api_id, api_hash=api_hash, session_string=session_string)

my_messages = set()

@app.on_raw_update()
async def ultra_fast(client, update, users, chats):
    if isinstance(update, UpdateNewMessage):
        msg = update.message
        if msg.reply_to and msg.reply_to.reply_to_msg_id in my_messages:
            try:
                await client.invoke(raw.functions.messages.DeleteMessages(
                    peer=await client.resolve_peer(msg.chat_id),
                    id=[msg.reply_to.reply_to_msg_id],
                    revoke=True
                ))
                my_messages.discard(msg.reply_to.reply_to_msg_id)
            except:
                pass

    elif isinstance(update, (UpdateUserTyping, UpdateChatUserTyping)):
        user_id = getattr(update, 'user_id', None)
        if user_id == admin_id:
            chat_id = getattr(update, 'peer', None)
            if chat_id in TARGET_CHATS and my_messages:
                msg_id = my_messages.pop()
                try:
                    await client.invoke(raw.functions.messages.DeleteMessages(
                        peer=await client.resolve_peer(chat_id),
                        id=[msg_id],
                        revoke=True
                    ))
                except:
                    pass

@app.on_message()
async def save_my_message(_, message):
    if message.chat.id in TARGET_CHATS and message.from_user and message.from_user.is_self:
        my_messages.add(message.id)

app.run()