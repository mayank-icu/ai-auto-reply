import time
import random
import logging
import os
from dotenv import load_dotenv
from message_handler import MessageHandler
from user_memory import UserMemory
from response_generator import ResponseGenerator

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("instagram_bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger("InstagramDMBot")

class InstagramDMBot:
    def __init__(self):
        # Load API tokens from environment variables
        self.instagram_token = os.environ.get("INSTAGRAM_TOKEN")
        if not self.instagram_token:
            logger.error("INSTAGRAM_TOKEN environment variable not set")
            raise ValueError("Missing required environment variable: INSTAGRAM_TOKEN")
        
        # Set up Krutrim Cloud API key
        krutrim_api_key = os.environ.get("KRUTRIM_CLOUD_API_KEY")
        if not krutrim_api_key:
            logger.error("KRUTRIM_CLOUD_API_KEY environment variable not set")
            raise ValueError("Missing required environment variable: KRUTRIM_CLOUD_API_KEY")
        
        os.environ["KRUTRIM_CLOUD_API_KEY"] = krutrim_api_key
        
        # Initialize components
        self.user_memory = UserMemory()
        self.response_generator = ResponseGenerator()
        self.message_handler = MessageHandler(
            self.instagram_token, 
            self.user_memory,
            self.response_generator
        )
        
        logger.info("Bot initialized successfully")

    def run(self):
        """Main bot loop"""
        logger.info("Instagram DM Bot running...")
        consecutive_errors = 0
        
        while True:
            try:
                # Get and process messages
                messages_count = self.message_handler.process_messages()
                logger.info(f"Processed {messages_count} messages in this cycle")
                
                # Reset error counter on successful run
                if consecutive_errors > 0:
                    consecutive_errors = 0
                
                # Save data periodically (20% chance each cycle)
                if random.random() < 0.2:
                    self.user_memory.save_data()
                    logger.info("User memory data saved")
                    
                # Variable wait between checks
                wait_time = random.uniform(5, 10)
                logger.debug(f"Waiting {wait_time:.2f} seconds until next check")
                time.sleep(wait_time)

            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                self.user_memory.save_data()
                break
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Error in main loop ({consecutive_errors}): {e}", exc_info=True)
                
                # Back off exponentially if errors persist
                wait_time = min(30 * consecutive_errors, 300)  # Cap at 5 minutes
                logger.info(f"Backing off for {wait_time} seconds")
                time.sleep(wait_time)


if __name__ == "__main__":
    try:
        # Check for dependencies
        required_packages = ["krutrim_cloud", "python-dotenv"]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                logger.info(f"{package} module not found. Installing...")
                import subprocess
                subprocess.check_call(["pip", "install", package])
                logger.info(f"{package} installed successfully")
        
        # Now safe to import after installing if needed
        from krutrim_cloud import KrutrimCloud
        from dotenv import load_dotenv
        
        bot = InstagramDMBot()
        bot.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)