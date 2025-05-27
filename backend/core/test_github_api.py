import os
import sys
from pathlib import Path

# Add backend/ to import path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from core.github_api import GitHubAPIClient

load_dotenv()

def main():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN not found in environment.")
        return

    client = GitHubAPIClient(token)
    result = client.fetch_user_contributions("bekarys2003")
    print(result)

if __name__ == "__main__":
    main()
