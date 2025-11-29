import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import certifi
import ssl

# Connection string from .env
MONGODB_URL = "mongodb+srv://harshalchugwani:harshal1230@cluster0.a4dssr7.mongodb.net/healthease?appName=Cluster0"

async def test_connect(name, kwargs):
    print(f"Testing {name} with kwargs: {kwargs}")
    try:
        client = AsyncIOMotorClient(MONGODB_URL, **kwargs)
        # Force a connection
        await client.admin.command('ping')
        print(f"SUCCESS: {name}")
        return True
    except Exception as e:
        print(f"FAILURE: {name} - {e}")
        return False

async def main():
    # Test 1: Standard with certifi
    await test_connect("Standard+Certifi", {
        "tls": True,
        "tlsCAFile": certifi.where(),
        "serverSelectionTimeoutMS": 5000
    })

    # Test 2: tlsInsecure
    await test_connect("tlsInsecure", {
        "tls": True,
        "tlsInsecure": True,
        "serverSelectionTimeoutMS": 5000
    })

    # Test 3: AllowInvalidCertificates
    await test_connect("AllowInvalidCertificates", {
        "tls": True,
        "tlsAllowInvalidCertificates": True,
        "tlsAllowInvalidHostnames": True,
        "serverSelectionTimeoutMS": 5000
    })
    
    # Test 4: No explicit TLS args (rely on SRV)
    await test_connect("NoExplicitTLS", {
        "serverSelectionTimeoutMS": 5000
    })

if __name__ == "__main__":
    asyncio.run(main())
