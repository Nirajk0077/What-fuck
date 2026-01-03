from pyrogram import Client, filters
from pyrogram.types import Message
from info import ADMINS

@Client.on_message(
    filters.group &
    (
        filters.regex(r"(@|#)") |
        filters.regex(r"^/")
    ) &
    ~filters.user(ADMINS),
    group=-1
)
async def group_cleaner(client: Client, message: Message):
    try:
        await message.delete()
        message.stop_propagation()
    except Exception:
        # If deletion fails (e.g. no permissions), we still stop propagation
        # to ensure the bot ignores the message (no search results/replies).
        message.stop_propagation()
