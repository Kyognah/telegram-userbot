from pyrogram import Client, raw
from pyrogram.raw.types import UpdateNewMessage, UpdateChatUserTyping, UpdateUserTyping
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
    print(f"[RAW] Type: {type(update).__name__}")

    # === تشخیص ریپلای ===
    if isinstance(update, UpdateNewMessage):
        msg = update.message
        if msg.reply_to and msg.reply_to.reply_to_msg_id in my_messages:
            print(f"[REPLY DETECTED] Deleting message {msg.reply_to.reply_to_msg_id}")
            try:
                await client.delete_messages(msg.chat_id, msg.reply_to.reply_to_msg_id)
                my_messages.discard(msg.reply_to.reply_to_msg_id)
            except Exception as e:
                print(f"[ERROR DELETE REPLY] {e}")

    # === تشخیص typing ===
    elif isinstance(update, UpdateChatUserTyping):
        user_id = None
        chat_id = None

        if hasattr(update, 'from_id') and update.from_id:
            user_id = update.from_id.user_id if hasattr(update.from_id, 'user_id') else update.from_id
        if hasattr(update, 'peer') and update.peer:
            chat_id = update.peer.channel_id if hasattr(update.peer, 'channel_id') else update.peer

        print(f"[TYPING] user_id={user_id}, chat_id={chat_id}, ADMIN_ID={ADMIN_ID}")

        if user_id == ADMIN_ID and chat_id in TARGET_CHATS:
            if my_messages:
                msg_id = my_messages.pop()
                print(f"[TYPING DETECTED] Deleting my message {msg_id}")
                try:
                    await client.delete_messages(chat_id, msg_id)
                except Exception as e:
                    print(f"[ERROR DELETE TYPING] {e}")

    elif isinstance(update, UpdateUserTyping):
        print(f"[TYPING USER] user_id={getattr(update, 'user_id', None)}")

@app.on_message()
async def save_my_message(_, message):
    if message.chat.id in TARGET_CHATS and message.from_user and message.from_user.is_self:
        my_messages.add(message.id)
        print(f"[MY MESSAGE SAVED] {message.id}")

app.run()