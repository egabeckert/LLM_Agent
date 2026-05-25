
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Look for the env variable
env_path = os.getenv("PROJECT_ROOT")

# 2. If it's not in the .env, use your known good path
if not env_path:
    env_path = "/home/elliot/chudnelius2.0"

# 3. Always absolute-ify it to be safe
SANDBOX_ROOT = os.path.abspath(env_path)

print(f"BOOTS DEBUG: Sandbox is locked to: {SANDBOX_ROOT}")


MAX_CHARS = 10000
