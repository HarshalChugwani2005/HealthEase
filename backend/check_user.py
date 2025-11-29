import asyncio
from app.database import connect_to_mongo, close_mongo_connection
from app.models.user import User

async def main():
    await connect_to_mongo()
    
    email = "demo@healthease.local"
    user = await User.find_one(User.email == email)
    
    if user:
        print(f"User found: {user.email}")
        print(f"Role: {user.role}")
    else:
        print(f"User {email} not found.")
        
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())
