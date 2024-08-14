import os
import logging


def setup_logger(log_file="climate_trace.log"):
    # Create a logger
    logger = logging.getLogger("climate_trace")
    logger.setLevel(logging.DEBUG)

    # Create handlers
    c_handler = logging.StreamHandler()  # Console handler
    f_handler = logging.FileHandler(log_file)
    c_handler.setLevel(logging.INFO)  # Less detailed for console
    f_handler.setLevel(logging.DEBUG)  # More detailed for file

    # Create formatters and add it to handlers
    c_format = logging.Formatter("%(levelname)s - %(message)s")
    f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger


# Create the logger
logger = setup_logger()
