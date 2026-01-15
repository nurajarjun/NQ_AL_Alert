import sys
import os
import logging

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Mock environment variables to prevent main.py from failing on missing unrelated env vars
os.environ["TELEGRAM_BOT_TOKEN"] = "mock_token"
os.environ["TELEGRAM_CHAT_ID"] = "mock_id"

try:
    print("Attempting to import main...")
    from backend import main
    print("✅ main imported successfully")
    
    if hasattr(main, 'global_manager') and main.global_manager is not None:
        print(f"✅ global_manager is initialized: {main.global_manager}")
        session = main.global_manager.get_current_session()
        print(f"   Current Session: {session}")
    else:
        print("❌ global_manager is NOT initialized in main.py")
        sys.exit(1)

except ImportError as e:
    print(f"❌ Failed to import main: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ An error occurred: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
