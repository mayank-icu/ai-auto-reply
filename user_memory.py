import json
import logging

logger = logging.getLogger("InstagramDMBot")

class UserMemory:
    def __init__(self):
        # User and message tracking
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
        
        # Load saved data
        self.load_data()
        
    def add_message_to_history(self, user_id, role, content):
        """Add a message to the conversation history"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
            
        self.conversation_history[user_id].append({"role": role, "content": content})
        
        # Keep conversation history manageable
        self.conversation_history[user_id] = self.conversation_history[user_id][-15:]
        
    def get_conversation_history(self, user_id):
        """Get conversation history for a user"""
        return self.conversation_history.get(user_id, [])
        
    def get_user_info(self, username):
        """Get information about a specific user"""
        return self.special_users.get(username, {})
        
    def is_special_user(self, username):
        """Check if user is in the special users list"""
        return username in self.special_users
            
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
            self.initialize_data_file()
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            # If error occurs, reset to empty data
            self.conversation_history = {}
            self.processed_messages = set()
            self.initialize_data_file()
            
    def initialize_data_file(self):
        """Create an empty data file if it doesn't exist"""
        try:
            data = {
                "conversation_history": {},
                "processed_messages": []
            }
            # Write to file
            with open('instagram_bot_data.json', 'w') as f:
                json.dump(data, f)
            logger.info("Created new data file")
        except Exception as e:
            logger.error(f"Error creating data file: {e}")