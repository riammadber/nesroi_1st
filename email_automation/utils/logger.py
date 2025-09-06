import structlog
import logging
import sys
from config.settings import settings

def setup_logger():
    """Configure structured logging"""
        structlog.configure(
                processors=[
                            structlog.stdlib.filter_by_level,
                                        structlog.stdlib.add_logger_name,
                                                    structlog.stdlib.add_log_level,
                                                                structlog.stdlib.PositionalArgumentsFormatter(),
                                                                            structlog.processors.TimeStamper(fmt="iso"),
                                                                                        structlog.processors.StackInfoRenderer(),
                                                                                                    structlog.processors.format_exc_info,
                                                                                                                structlog.processors.UnicodeDecoder(),
                                                                                                                            structlog.processors.JSONRenderer()
                                                                                                                                    ],
                                                                                                                                            wrapper_class=structlog.stdlib.BoundLogger,
                                                                                                                                                    logger_factory=structlog.stdlib.LoggerFactory(),
                                                                                                                                                            cache_logger_on_first_use=True,
                                                                                                                                                                )

                                                                                                                                                                    logging.basicConfig(
                                                                                                                                                                            format="%(message)s",
                                                                                                                                                                                    stream=sys.stdout,
                                                                                                                                                                                            level=getattr(logging, settings.log_level.upper()),
                                                                                                                                                                                                )

                                                                                                                                                                                                # Initialize logger
                                                                                                                                                                                                setup_logger()
                                                                                                                                                                                                logger = structlog.get_logger()