import requests
import time
import random
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Set, Optional, Any, Tuple

logger = logging.getLogger("InstagramDMBot")

class MessageHandler:
    def __init__(self, instagram_token: str, user_memory, response_generator):
        self.instagram_token = instagram_token
        self.user_memory = user_memory
        self.response_generator = response_generator
        self.user_id = "17841457439366144"
        self.last_check = datetime.now(timezone.utc) - timedelta(minutes=5)  # Look back 5 minutes on first run
        self.base_url = "https://graph.instagram.com/v17.0"
        self.headers = {"Authorization": f"Bearer {self.instagram_token}"}
        self.retry_count = 3  # Number of API call retries
        
    def get_messages(self) -> Dict[str, List[Dict]]:
        """Fetch recent messages from Instagram API with retry logic"""
        url = f"{self.base_url}/{self.user_id}/conversations"
        # Increase limit to catch more messages that might have been missed
        params = {"fields": "participants,messages{message,from,created_time,id}", "limit": 50}
        
        # Implement retry logic
        for attempt in range(self.retry_count):
            try:
                logger.debug(f"Fetching messages (attempt {attempt+1}/{self.retry_count})")
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Successfully retrieved {len(data.get('data', []))} conversations")
                return data
            except requests.RequestException as e:
                if attempt < self.retry_count - 1:
                    wait = (2 ** attempt) * 1.5  # Exponential backoff
                    logger.warning(f"Error getting messages (attempt {attempt+1}): {e}. Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    logger.error(f"Failed to get messages after {self.retry_count} attempts: {e}")
        
        # If all retries failed
        return {"data": []}
            
    def send_message(self, recipient_id: str, message: str) -> bool:
        """Send message to Instagram user with optional delay"""
        # Don't send empty messages
        if not message.strip():
            logger.warning("Attempted to send empty message, skipping")
            return False
        
        # Random chance to add a small delay before sending
        if random.random() < 0.4:
            delay = random.uniform(1.5, 5.0)
            logger.info(f"Adding a {delay:.1f}s delay before sending message")
            time.sleep(delay)
            
        url = f"{self.base_url}/me/messages"
        data = {"recipient": {"id": recipient_id}, "message": {"text": message}}
        
        # Implement retry logic for sending messages
        for attempt in range(self.retry_count):
            try:
                response = requests.post(url, json=data, headers=self.headers, timeout=10)
                response.raise_for_status()
                logger.info(f"Message sent: {message[:50]}..." if len(message) > 50 else f"Message sent: {message}")
                return True
            except requests.RequestException as e:
                if attempt < self.retry_count - 1:
                    wait = (2 ** attempt) * 1.5  # Exponential backoff
                    logger.warning(f"Error sending message (attempt {attempt+1}): {e}. Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    logger.error(f"Failed to send message after {self.retry_count} attempts: {e}")
        
        return False
    
    def _parse_message_time(self, time_string: str) -> datetime:
        """Parse Instagram API datetime formats with error handling"""
        formats = [
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%S+0000',
            '%Y-%m-%dT%H:%M:%S.%f%z'  # Added format with milliseconds
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(time_string, fmt)
                # Ensure timezone info is present
                return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
                
        logger.error(f"Could not parse date: {time_string}")
        return datetime.now(timezone.utc)
    
    def _create_response_with_delay(self, sender_id: str, sender_username: str, message_content: str) -> str:
        """Generate response with human-like delay"""
        # Variable response delay (feels more human)
        response_delay = random.uniform(2, 6) if random.random() < 0.8 else random.uniform(10, 20)
        time.sleep(response_delay)
        
        # Generate response with sender username for context
        return self.response_generator.generate_response(
            message_content, 
            sender_id,
            sender_username,
            self.user_memory.get_conversation_history(sender_id)
        )
    
    def process_messages(self) -> int:
        """Get and respond to new messages. Returns count of processed messages."""
        data = self.get_messages()
        messages_processed = 0
        
        # Set a buffer time to avoid edge cases with timestamps
        # This helps catch messages that might have been missed
        buffer_time = timedelta(minutes=10)
        check_time = self.last_check - buffer_time
        logger.info(f"Checking for messages after {check_time.isoformat()}")
        
        for conv in data.get('data', []):
            messages = conv.get('messages', {}).get('data', [])
            
            # Get participant info
            participants = conv.get('participants', {}).get('data', [])
            participant_map = {p['id']: p.get('username', 'user') for p in participants}

            # Sort messages by time for proper ordering
            sorted_messages = sorted(
                messages, 
                key=lambda m: self._parse_message_time(m['created_time'])
            )

            for msg in sorted_messages:
                # Skip already processed messages
                if msg['id'] in self.user_memory.processed_messages:
                    logger.debug(f"Skipping already processed message: {msg['id']}")
                    continue

                # Parse message time
                msg_time = self._parse_message_time(msg['created_time'])

                # Process new messages from others (with buffer time to catch missed messages)
                if msg_time > check_time and msg['from'].get('id') != self.user_id:
                    # Get sender info
                    sender_id = msg['from']['id']
                    sender_username = participant_map.get(sender_id, 'Unknown')
                    message_content = msg.get('message', '')
                    
                    logger.info(f"Received message from {sender_username} at {msg_time.isoformat()}: '{message_content}'")
                    
                    # Store message in history
                    self.user_memory.add_message_to_history(sender_id, "user", message_content)
                    
                    # Generate and send response
                    response = self._create_response_with_delay(sender_id, sender_username, message_content)

                    if self.send_message(sender_id, response):
                        logger.info(f"Sent response to {sender_username}: '{response[:50]}...'" if len(response) > 50 else f"Sent response to {sender_username}: '{response}'")
                        # Mark message as processed AFTER successful response
                        self.user_memory.processed_messages.add(msg['id'])
                        self.user_memory.add_message_to_history(sender_id, "assistant", response)
                        messages_processed += 1
                    else:
                        logger.error(f"Failed to send response for message {msg['id']}")

        # Update last check time
        self.last_check = datetime.now(timezone.utc)
        
        if messages_processed:
            logger.info(f"Processed {messages_processed} new messages")
        else:
            logger.debug("No new messages to process")
            
        return messages_processed