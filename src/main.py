"""
Main application module for the logging service.
"""
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main application entry point."""
    logger.info("Starting logging service...")
    
    # Add your application logic here
    
    logger.info("Logging service is running...")

if __name__ == "__main__":
    main() 