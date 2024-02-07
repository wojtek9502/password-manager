import logging
import os
from pathlib import Path

from sqlalchemy import create_engine
from dotenv import load_dotenv

#db
from src.common.Database import Database
from src.user.models import UserModel

PROJECT_DIR = Path(__file__).parent
LOGS_DIR = Path(PROJECT_DIR, 'logs')
logger = logging.getLogger()

load_dotenv()


engine = create_engine(os.environ['DB_URI'])
Base = Database
