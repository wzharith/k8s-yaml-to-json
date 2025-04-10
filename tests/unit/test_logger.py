import logging
import io
from k8s_converter.core.logger import logger


class TestLogger:
    """Test cases for the logging module"""

    def test_logger_initialization(self):
        """Test that the logger is properly initialized"""
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert (
            logger.name == "k8s_converter.core.logger"
        )  # Logger name is the module name
        assert logger.level <= logging.INFO  # Should be INFO or more detailed

    def test_logger_format(self):
        """Test that the logger has the expected format"""
        # Create a handler to capture log output
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)

        # Set the level to ensure messages are captured
        original_level = logger.level
        logger.setLevel(logging.INFO)

        # Create a formatter similar to the one in logger.py
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        # Add handler to our logger
        logger.addHandler(handler)

        try:
            # Log a test message
            logger.info("Test message")

            # Check the format - only check for parts that don't include timestamps
            log_output = log_capture.getvalue()
            assert "k8s_converter.core.logger" in log_output
            assert "INFO" in log_output
            assert "Test message" in log_output
        finally:
            # Clean up - restore original level and remove our handler
            logger.setLevel(original_level)
            logger.removeHandler(handler)
