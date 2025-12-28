import os
import sys
import asyncio
from pyrogram import Client
from pyrogram.errors import InputUserDeactivated, UserIsBlocked, FloodWait, PeerIdInvalid
from motor.motor_asyncio import AsyncIOMotorClient

# System path set karna taaki plugins folder se main module mil sake
sys.path.append(os.getcwd())

# --- CONFIGURATION (Koyeb Env Vars se) ---
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URL = os.environ.get("MONGO_URL")
# Agar aapke DB ka naam alag hai toh yahan badal dein
DB_NAME = os.environ.get("DB_NAME", "Cluster0") 

# MongoDB Connection
db_client = AsyncIOMotorClient(MONGO_URL)
db = db_client[DB_NAME]
users_col = db["users"] # Check kar lena aapke collection ka naam yahi hai na

app = Client(
    "cleanup_session", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    bot_token=BOT_TOKEN,
    in_memory=True # Koyeb par session file ka jhanjhat khatam karne ke liye
)

async def start_cleaning():
    async with app:
        print("\n" + "="*30)
        print("🚀 DATABASE CLEANUP STARTED")
        print("="*30 + "\n")
        
        # Database se saare users nikalna
        all_users_cursor = users_col.find({})
        all_users = await all_users_cursor.to_list(length=None)
        
        total_users = len(all_users)
        deleted_count = 0
        active_count = 0
        
        print(f"📊 Total Users in DB: {total_users}")

        for index, user in enumerate(all_users):
            # ID check karna (kuch DBs me 'user_id' hota hai kuch me '_id')
            user_id = user.get("user_id") or user.get("_id")
            
            if not user_id:
                continue

            try:
                # User ko check karna
                await app.get_users(user_id)
                active_count += 1
                
            except (InputUserDeactivated, UserIsBlocked, PeerIdInvalid):
                # Inactive users ko delete karna
                await users_col.delete_one({"user_id": user_id})
                deleted_count += 1
                print(f"❌ [{index+1}/{total_users}] Removed: {user_id}")

            except FloodWait as e:
                print(f"⏳ Waiting {e.value}s due to Telegram limits...")
                await asyncio.sleep(e.value)

            except Exception as e:
                # Baaki koi error aaye toh skip karo
                pass

            # Har check ke beech thoda gap (Safe side)
            await asyncio.sleep(0.3)

        print("\n" + "="*30)
        print("✅ CLEANUP COMPLETED")
        print(f"👤 Active Users: {active_count}")
        print(f"🗑️ Deleted Users: {deleted_count}")
        print("="*30 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(start_cleaning())
    except KeyboardInterrupt:
        print("\nStopped by user.")
