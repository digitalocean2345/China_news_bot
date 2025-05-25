import subprocess
import logging
from datetime import datetime

class GitManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _run_command(self, command):
        """Run a git command and return the result"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git command failed: {e.stderr}")
            raise

    def push_changes(self):
        """Push changes to GitHub"""
        try:
            # Get current timestamp for commit message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add changes
            self._run_command(['git', 'add', 'docs/*'])
            
            # Create commit
            commit_message = f"Update news pages - {timestamp}"
            self._run_command(['git', 'commit', '-m', commit_message])
            
            # Push changes
            self._run_command(['git', 'push'])
            
            self.logger.info("Successfully pushed changes to GitHub")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to push changes to GitHub: {e}")
            return False 