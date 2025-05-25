from git_manager import GitManager
import logging

logging.basicConfig(level=logging.INFO)

def test_git_push():
    git_manager = GitManager()
    result = git_manager.push_changes()
    print(f"Push successful: {result}")

if __name__ == "__main__":
    test_git_push() 