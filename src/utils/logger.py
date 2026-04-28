import datetime
import os


def debug_log(msg):
    """Write a timestamped message to debug.log in the project root."""
    try:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        # Get project root (2 levels up from utils/)
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_path = os.path.join(root, "debug.log")
        with open(log_path, "a") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except Exception:
        pass
