import logging
from pythonjsonlogger import jsonlogger
from typing import Dict, Any
from datetime import datetime
import sys

class StructuredLogFormatter(jsonlogger.JsonFormatter):
    """Custom JSON log formatter with additional fields"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.utcnow().isoformat()
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Configure and return a structured logger
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
        
    handler = logging.StreamHandler(sys.stdout)
    formatter = StructuredLogFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level.upper())
    logger.propagate = False
    
    # Add exception logging hook
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        logger.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_exception
    
    return logger