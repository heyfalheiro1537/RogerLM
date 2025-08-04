import logging
from datetime import datetime
from config import Config


class Logger:
    def __init__(self, config: Config):
        self.config = config
        self.setup_logging(config)

    def setup_logging(config: Config):
        """Setup logging configuration"""
        log_file = (
            config.logs_path / f"assistant_{datetime.now().strftime('%Y%m%d')}.log"
        )
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )
