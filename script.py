import requests
import time
import random
import json
import re
from datetime import datetime, timezone
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("instagram_bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger("InstagramDMBot")

class InstagramDMBot:
    def __init__(self):
        # API tokens
        self.instagram_token = "IGAAPxtpkJxy5BZAE9TWngwY0wzSUM4ZAW16QWE2YjBTaTloYWdaNDRVY2VIN2MzOFBlNExmNFZATUm8yVUFHY3Fkc1VJbGlza202eVFOaEdxb1BpUDlMZA09tNFRxOEpQQ2NpWmtaY0w1T29qRlNFNnB0WDJoNEZAkSFp1QllfQlhIZAwZDZD"
        
        # Set up Krutrim Cloud
        os.environ["KRUTRIM_CLOUD_API_KEY"] = "uVMUHtDBaSjAkfUmHvhYwDoOoF"
        try:
            from krutrim_cloud import KrutrimCloud
            self.krutrim_client = KrutrimCloud(api_key=os.environ["KRUTRIM_CLOUD_API_KEY"])
            self.model_name = "DeepSeek-R1-Llama-8B"
        except ImportError:
            logger.error("krutrim_cloud module not found, will install when needed")
            self.krutrim_client = None
        
        # User and message tracking
        self.user_id = "17841457439366144"
        self.last_check = datetime.now(timezone.utc)
        self.processed_messages = set()
        self.conversation_history = {}
        
        # Personal information as context for responses
        self.personal_info = {
            "name": "Mayank",
            "interests": [
                "technology and AI, especially in education",
                "web development (React, Node.js)",
                "music, especially Cigarettes After Sex and indie pop (Taylor Swift, Ariana Grande)",
                "movies, especially Interstellar"
            ]
        }
        
        # Special user information
        self.special_users = {
    "h.dr0zd": {
        "interests": [
            "reading (non-fiction, horror, crime, historical fiction)",
            "baking, owns a small home bakery",
            "learning languages",
            "Gilmore Girls, admires Lorelai",
            "music (hasn't listened to Cigarettes After Sex)",
            "prefers physical books over ebooks/audiobooks",
            "buys second-hand books on Vinted",
            "shares book recommendations on Goodreads",
            "2000s series and movies",
            "supports LGBTQ+ rights",
            "deep and casual talks",
            "strong political views, dislikes Trump",
            "likely supported Kamala Harris",
            "possibly dislikes Putin, supports Ukraine",
            "loves traveling but hasn't traveled much",
            "curious about different cultures",
            "wants to learn about India and Holi"
        ],
        "relationship": "bestfriend"
    },
    "tutelio.in": {
        "relationship": "girlfriend",
        "notes": "she is your lover"
    },
    "mustbepranav": {
        "relationship": "bestfriend",
        "notes": "my bestfriend from 8 years and he's from Katihar, Bihar, India. He is 16 years old and other stuffs"
    },
    "jeffer_2869": {
        "relationship": "online friend",
        "notes": "he's from Alaska, USA and is in boarding school"
    },
    "rishu._198": {
        "relationship": "friend",
        "notes": "we met in Allen Career Institute and he's currently in Kota"
    }
}

        
        # Initialize data file if needed and load saved data
        self.initialize_data_file()
        self.load_data()

    def initialize_data_file(self):
        """Create an empty data file if it doesn't exist"""
        try:
            with open('instagram_bot_data.json', 'r') as f:
                pass  # File exists, do nothing
        except FileNotFoundError:
            # Create empty data structure
            data = {
                "conversation_history": {},
                "processed_messages": []
            }
            # Write to file
            with open('instagram_bot_data.json', 'w') as f:
                json.dump(data, f)
            logger.info("Created new data file")

    def get_messages(self):
        """Fetch recent messages from Instagram API"""
        url = f"https://graph.instagram.com/v17.0/{self.user_id}/conversations"
        headers = {"Authorization": f"Bearer {self.instagram_token}"}
        params = {"fields": "participants,messages{message,from,created_time,id}", "limit": 20}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting messages. Status code: {response.status_code}, Response: {response.text}")
                return {"data": []}
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return {"data": []}

    def create_prompt(self, message, sender_username, conversation_history=None):
        """Create a properly formatted prompt for the AI model"""
        is_special_user = sender_username in self.special_users
        
        # Basic prompt structure
        prompt = f"""You are Mayank responding to a message from {sender_username} on Instagram. 
Respond to this message naturally and conversationally: "{message}"
"""
        
        # Add relationship context for special users
        if is_special_user:
            relationship = self.special_users[sender_username].get("relationship", "friend")
            prompt += f"\nThis person is your {relationship}. "
            
            # Add specific user interests if available
            if "interests" in self.special_users[sender_username]:
                interests = self.special_users[sender_username]["interests"]
                prompt += f"\nTheir interests include: {', '.join(random.sample(interests, min(3, len(interests))))}"
        else:
            # Add your personal info for regular users
            prompt += f"\nYour interests include: {', '.join(random.sample(self.personal_info['interests'], 2))}"
        
        # Add conversation context if available
        if conversation_history and len(conversation_history) > 1:
            prompt += "\n\nRecent messages (most recent at bottom):"
            recent_msgs = conversation_history[-3:]  # Last 3 messages
            for entry in recent_msgs:
                if entry["role"] == "user":
                    prompt += f"\n{sender_username}: {entry['content']}"
                else:
                    prompt += f"\nYou: {entry['content']}"
        
        # Add instructions for human-like response
        prompt += """
IMPORTANT: 
- Keep your response very short (1-2 sentences usually)
- Be casual like texting a friend
- Occasionally make small typos or grammar errors
- Use lowercase, casual punctuation, and occasional emojis
- Respond ONLY with your message - no quotes or explanations
- Use simple, direct language like real texting

Examples of good responses: 
"yeah that sounds good"
"i was thinking about that movie yesterday"
"definitely gonna check that out"
"omg i totally forgot about that 😂"
"haha ya thats so true"
"""
        
        return prompt

    def add_human_touches(self, text):
        """Add occasional typos and other human-like texting features"""
        if not text:
            return ""
        
        # Only apply modifications sometimes
        if random.random() < 0.6:  # 60% chance of modifications
            # Words that might get typos
            common_typos = {
                'the': 'teh',
                'and': 'adn',
                'you': 'u',
                'your': 'ur',
                'are': 'r',
                'to': '2',
                'for': '4',
                'really': 'rly',
                'with': 'w',
                'want': 'wanna',
                'going to': 'gonna',
                'though': 'tho',
                'what': 'wat',
                'that': 'dat',
                'yes': 'yea',
                'okay': 'ok',
                'right': 'rite',
                'about': 'abt',
                'love': 'luv',
                'please': 'plz',
                'because': 'cuz',
                'today': '2day'
            }
            
            # Randomly select a word to misspell (if text is long enough)
            words = text.split()
            if len(words) > 3:
                for i in range(1):  # Just one typo per message
                    if random.random() < 0.3:  # 30% chance per attempt
                        word_idx = random.randint(0, len(words) - 1)
                        word = words[word_idx].lower()
                        if word in common_typos:
                            words[word_idx] = common_typos[word]
                
                text = ' '.join(words)
            
            # Sometimes remove punctuation or make it lowercase
            if random.random() < 0.5:
                text = text.lower()
            
            # Sometimes remove the first period
            if text.endswith('.') and random.random() < 0.7:
                text = text[:-1]
            
            # Sometimes add an emoji
            if random.random() < 0.2:
                emojis = ['😊', '👍', '❤️', '😂', '😊', '🙌', '🤔', '😅', '😄']
                text += f" {random.choice(emojis)}"
        
        return text

    def generate_response(self, message, sender_id, sender_username):
        """Generate human-like response using Krutrim Cloud"""
        # Initialize conversation history if needed
        if sender_id not in self.conversation_history:
            self.conversation_history[sender_id] = []
        
        # Add user message to history
        self.conversation_history[sender_id].append({"role": "user", "content": message})
        
        # Get relevant conversation history
        conversation_context = self.conversation_history[sender_id][-5:]
        
        # Create prompt for AI with sender info
        prompt = self.create_prompt(message, sender_username, conversation_context)
        
        # Brief random delay
        time.sleep(random.uniform(0.5, 2.0))
        
        try:
            # Ensure Krutrim client is available
            if self.krutrim_client is None:
                try:
                    from krutrim_cloud import KrutrimCloud
                    self.krutrim_client = KrutrimCloud(api_key=os.environ["KRUTRIM_CLOUD_API_KEY"])
                except ImportError:
                    logger.error("Failed to import krutrim_cloud, installing...")
                    import subprocess
                    subprocess.check_call(["pip", "install", "krutrim_cloud"])
                    from krutrim_cloud import KrutrimCloud
                    self.krutrim_client = KrutrimCloud(api_key=os.environ["KRUTRIM_CLOUD_API_KEY"])
                    logger.info("krutrim_cloud installed successfully")
            
            # Log attempt to call AI
            logger.info(f"Calling Krutrim API with prompt: {prompt[:100]}...")
            
            # Send request to model API with retry logic
            max_retries = 3
            ai_response = ""
            
            for attempt in range(max_retries):
                try:
                    # Prepare Krutrim messages
                    messages = [{"role": "user", "content": prompt}]
                    
                    # Call Krutrim API
                    response = self.krutrim_client.chat.completions.create(
                        model=self.model_name,
                        messages=messages
                    )
                    
                    if response and hasattr(response, "choices") and response.choices:
                        ai_response = response.choices[0].message.content
                        logger.info(f"Raw AI response: {ai_response}")
                        
                        # Clean up the response
                        ai_response = self.clean_response(ai_response)
                        
                        # Add human-like touches
                        ai_response = self.add_human_touches(ai_response)
                        
                        # If we got a valid response, break the retry loop
                        if ai_response and len(ai_response.strip()) > 2:
                            break
                    
                    # Wait before retrying
                    if not ai_response or len(ai_response.strip()) <= 2:
                        time.sleep(2)
                
                except Exception as e:
                    logger.error(f"Error on attempt {attempt+1}: {e}")
                    time.sleep(2)
            
            # Fallback responses if needed
            if not ai_response or len(ai_response.strip()) <= 2:
                fallback_responses = [
                    "hey, what's up?",
                    "yeah I get that",
                    "that makes sense",
                    "cool! tell me more",
                    "sounds good",
                    "totally agree",
                    "lol yeah",
                    "sorry I was busy, what's new?",
                    "interesting! how's your day going?"
                ]
                ai_response = random.choice(fallback_responses)
            
            # Simulate realistic typing delay based on message length
            typing_delay = min(len(ai_response) / 15, 3.0)
            time.sleep(typing_delay)
            
            # Add to conversation history
            self.conversation_history[sender_id].append({"role": "assistant", "content": ai_response})
            
            # Keep conversation history manageable
            self.conversation_history[sender_id] = self.conversation_history[sender_id][-15:]
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            return "hey, what's up?"  # Simple fallback

    def clean_response(self, text):
        """Clean up AI responses to appear natural"""
        if not text:
            return ""
        
        # Remove any thinking sections
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL|re.IGNORECASE)
        
        # Remove any markdown, XML tags, etc.
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'<.*?>', '', text, flags=re.DOTALL)
        
        # Extract the actual message from common patterns
        patterns = [
            r'"(.*?)"',
            r'(?:response|reply|message):\s*["\'](.*?)["\']',
            r'(?:You|Mayank):\s*(.*?)(?:\n|$)',
        ]
        
        for pattern in patterns:
            matches = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                extracted = matches.group(1).strip()
                if len(extracted) > 2:
                    text = extracted
                    break
        
        # Remove common prefixes/suffixes
        prefixes = [
            r'^mayank:?\s*',
            r'^you:?\s*',
            r'^response:?\s*', 
            r'^i would say\s*',
            r'^i\'d say\s*',
            r'^i\'d respond with\s*',
        ]
        
        for prefix_pattern in prefixes:
            text = re.sub(prefix_pattern, '', text, flags=re.IGNORECASE)
        
        # Remove formal greetings (if they stand alone)
        text = re.sub(r"^(hello|hi|hey)( there)?,?\s+", "", text, flags=re.IGNORECASE)
        
        # Remove any AI-like phrases
        ai_phrases = [
            r'as an ai',
            r'as a language model',
            r'i\'m not actually',
            r'i cannot',
            r'i\'m an ai'
        ]
        
        for phrase in ai_phrases:
            text = re.sub(phrase, '', text, flags=re.IGNORECASE)
        
        # Clean up any double spaces and limit length
        text = re.sub(r'\s+', ' ', text).strip()
        
        # If the response is too long, truncate it
        words = text.split()
        if len(words) > 15:  # Shorter messages are more realistic
            text = " ".join(words[:15]) + "..."
        
        logger.info(f"Cleaned response: '{text}'")
        return text.strip()

    def send_message(self, recipient_id, message):
        """Send message to Instagram user"""
        # Don't send empty messages
        if not message.strip():
            logger.warning("Attempted to send empty message, skipping")
            return False
        
        # Random chance to add a small delay before sending
        if random.random() < 0.4:
            delay = random.uniform(1.5, 5.0)
            logger.info(f"Adding a {delay:.1f}s delay before sending message")
            time.sleep(delay)
            
        url = "https://graph.instagram.com/v17.0/me/messages"
        data = {"recipient": {"id": recipient_id}, "message": {"text": message}}
        
        try:
            response = requests.post(
                url,
                json=data,
                headers={"Authorization": f"Bearer {self.instagram_token}"}
            )
            
            if response.status_code == 200:
                logger.info(f"Message sent: {message}")
                return True
            else:
                logger.error(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
            
    def save_data(self):
        """Save conversation history and processed messages to disk"""
        try:
            data = {
                "conversation_history": self.conversation_history,
                "processed_messages": list(self.processed_messages)
            }
            
            with open('instagram_bot_data.json', 'w') as f:
                json.dump(data, f)
                
            logger.info("Saved data to disk")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def load_data(self):
        """Load conversation history and processed messages from disk"""
        try:
            with open('instagram_bot_data.json', 'r') as f:
                data = json.load(f)
                
            self.conversation_history = data.get("conversation_history", {})
            self.processed_messages = set(data.get("processed_messages", []))
            
            logger.info("Loaded saved data")
        except FileNotFoundError:
            logger.warning("No saved data found, starting fresh")
            self.save_data()  # Create an initial data file
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            # If error occurs, reset to empty data
            self.conversation_history = {}
            self.processed_messages = set()
            self.save_data()  # Create a fresh data file

    def run(self):
        """Main bot loop"""
        logger.info("Instagram DM Bot running...")
        
        while True:
            try:
                # Get messages with occasional variation in timing
                time.sleep(random.uniform(4, 11))  # More random timing
                data = self.get_messages()
                
                for conv in data.get('data', []):
                    messages = conv.get('messages', {}).get('data', [])
                    
                    # Get participant info
                    participants = conv.get('participants', {}).get('data', [])
                    participant_map = {p['id']: p.get('username', 'user') for p in participants}

                    for msg in messages:
                        # Skip already processed messages
                        if msg['id'] in self.processed_messages:
                            continue

                        # Parse message time
                        try:
                            msg_time = datetime.strptime(
                                msg['created_time'],
                                '%Y-%m-%dT%H:%M:%S%z'
                            )
                        except ValueError:
                            try:
                                msg_time = datetime.strptime(
                                    msg['created_time'],
                                    '%Y-%m-%dT%H:%M:%S+0000'
                                ).replace(tzinfo=timezone.utc)
                            except ValueError:
                                logger.error(f"Could not parse date: {msg['created_time']}")
                                msg_time = datetime.now(timezone.utc)

                        # Process new messages from others
                        if msg_time > self.last_check and msg['from'].get('id') != self.user_id:
                            # Get sender info
                            sender_id = msg['from']['id']
                            sender_username = participant_map.get(sender_id, 'Unknown')
                            message_content = msg.get('message', '')
                            
                            # Variable response delay (feels more human)
                            response_delay = random.uniform(2, 6) if random.random() < 0.8 else random.uniform(10, 20)
                            time.sleep(response_delay)
                            
                            logger.info(f"Received message from {sender_username}: '{message_content}'")
                            
                            # Generate response with sender username for context
                            response = self.generate_response(message_content, sender_id, sender_username)

                            # Send message
                            if self.send_message(sender_id, response):
                                logger.info(f"Sent response to {sender_username}: '{response}'")
                                self.processed_messages.add(msg['id'])

                # Update last check time
                self.last_check = datetime.now(timezone.utc)
                
                # Save data periodically (20% chance each cycle)
                if random.random() < 0.2:
                    self.save_data()
                    
                # Variable wait between checks (more random timing)
                time.sleep(random.uniform(5, 12))

            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                self.save_data()
                break
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(30)  # Longer wait after error


if __name__ == "__main__":
    try:
        # Check for dependencies
        try:
            from krutrim_cloud import KrutrimCloud
        except ImportError:
            logger.info("krutrim_cloud module not found. Installing...")
            import subprocess
            subprocess.check_call(["pip", "install", "krutrim_cloud"])
            from krutrim_cloud import KrutrimCloud
            logger.info("krutrim_cloud installed successfully")
        
        bot = InstagramDMBot()
        bot.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)