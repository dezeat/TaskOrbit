"""Configure a module-level logger for the application.

Sets up a simple formatting and exposes `logger` for import.
"""

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)
