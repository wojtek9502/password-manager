import logging
from pathlib import Path

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).parent
LOGS_DIR = Path(PROJECT_DIR, 'logs')
logger = logging.getLogger()

load_dotenv()
