import logging
from datetime import datetime
from models.config import Config


class Logger:
    def __init__(self, config: Config):
        self.config = config
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        log_file = (
            self.config.logs_path / f"assistant_{datetime.now().strftime('%Y%m%d')}.log"
        )
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )
