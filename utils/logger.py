import logging
import os
import sys
from datetime import datetime

# Ensure outputs directory exists
os.makedirs('outputs', exist_ok=True)

class UnicodeSafeFormatter(logging.Formatter):
    """Custom formatter that handles Unicode characters safely on Windows console"""
    def format(self, record):
        msg = super().format(record)
        try:
            # Try to encode/decode safely for Windows console
            return msg.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
        except Exception:
            # Fallback: replace problematic characters
            return msg

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outputs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Apply Unicode-safe formatter to all handlers
for handler in logger.handlers:
    handler.setFormatter(UnicodeSafeFormatter('%(asctime)s - %(levelname)s - %(message)s'))

def log_info(message):
    """Log info message"""
    logger.info(message)

def log_error(message):
    """Log error message"""
    logger.error(message)

def log_warning(message):
    """Log warning message"""
    logger.warning(message)

def log_debug(message):
    """Log debug message"""
    logger.debug(message)

def log_success(message):
    """Log success message"""
    logger.info(f"✅ {message}")

def log_step(step_name):
    """Log step separator"""
    logger.info("=" * 60)
    logger.info(f"🚀 {step_name}")
    logger.info("=" * 60)
