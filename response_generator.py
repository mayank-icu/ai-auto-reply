import time
import random
import logging
import re
import os

logger = logging.getLogger("InstagramDMBot")

class ResponseGenerator:
    def __init__(self):
        self.model_name = "DeepSeek-R1-Llama-8B"
        # Common greeting patterns for quick responses
        self.greeting_patterns = {
    r'\b(hi|hey|hello|hii|heya|heyy)\b': [
        "Hey you 😊 What's on your mind today?",
        "Hi there, gorgeous. How's your day treating you?",
        "Hey! Just thinking about you, actually.",
        "There you are! Made me smile seeing your message.",
        "Heyyy, perfect timing! How are you doing?",
        "Well, hello there 😏 Missed our chats."
    ],
    r'\bgood morning\b': [
        "Morning, sunshine! Hope your day is as beautiful as you are.",
        "Good morning! First thing I checked when I woke up was if you messaged.",
        "Morningg! Coffee in hand, thinking of you.",
        "Morning, gorgeous! Ready to make today amazing?",
        "Hey, early bird! Your energy in the morning is everything."
    ],
    r'\bgood night\b': [
        "Sweet dreams, beautiful. Wish I could be there.",
        "Night night, sleep tight. Text me when you wake up?",
        "Goodnight, gorgeous. Dream of good things (maybe me? 😏).",
        "Sleep well! Sending you the warmest goodnight hug.",
        "Tomorrow's another day for us to talk more. Sweet dreams 💤."
    ],
    r'\bhow are you\b': [
        "Better now that you're texting me. How about you, cutie?",
        "Just thinking about what to say to make you smile. You?",
        "Honestly? Missing our conversations. You've been on my mind.",
        "Not bad, but definitely better now that you're here. You?",
        "Exactly as good as your day is going. Tell me everything."
    ],
    r'\bwyd\b|\bwhat(\'s| are)? you doing\b': [
        "Thinking about you, actually. What about you?",
        "Just got free, and the first thing I did was check if you messaged.",
        "Wishing we were hanging out right now, honestly. You?",
        "Nothing that can't be interrupted for you. What's up?",
        "Waiting for your message, if I'm being completely honest."
    ],
    r'\bmiss(ed)? you\b': [
        "You have no idea how much I've been thinking about you.",
        "The feeling is definitely mutual, gorgeous.",
        "Guess we're both feeling the same way then.",
        "That just made my whole day better. Miss you more.",
        "Then we should definitely do something about that soon."
    ]
}

        
        try:
            from krutrim_cloud import KrutrimCloud
            self.krutrim_client = KrutrimCloud(api_key=os.environ["KRUTRIM_CLOUD_API_KEY"])
        except ImportError:
            logger.error("krutrim_cloud module not found, will install when needed")
            self.krutrim_client = None
    
    def check_for_predefined_response(self, message):
        """Check if the message matches any predefined patterns for quick responses"""
        message = message.lower().strip()
        
        # For very short messages, check against our patterns
        if len(message.split()) <= 5:
            for pattern, responses in self.greeting_patterns.items():
                if re.search(pattern, message, re.IGNORECASE):
                    return random.choice(responses)
        
        return None
    
    def create_prompt(self, message, sender_username, conversation_history=None, user_memory=None):
        """Create a properly formatted prompt for the AI model"""
        is_special_user = False
        if user_memory:
            is_special_user = user_memory.is_special_user(sender_username)
        
        # Analyze message sentiment and length
        message_length = len(message.split())
        length_guidance = "short (1-2 sentences)" if message_length < 10 else "medium (2-3 sentences)" if message_length < 25 else "expressive (3-5 sentences)"
        
        # Enhanced prompt structure with more attractive personality traits
        prompt = f"""You are Mayank responding to a message from {sender_username} on Instagram. 
Respond to this message naturally and conversationally: "{message}"

Your personality: Charming, flirty, emotionally supportive, attentive, and genuine. You have a magnetic confidence that draws people in, making them feel seen and appreciated. You're excellent at creating connection through words and making the other person feel like they're the only one who matters to you right now.

Make your response {length_guidance} based on their message length.
"""
        
        # Add relationship context for special users
        if is_special_user and user_memory:
            user_info = user_memory.get_user_info(sender_username)
            relationship = user_info.get("relationship", "friend")
            prompt += f"\nThis person is your {relationship}. "
            
            # Add specific user interests if available
            if "interests" in user_info:
                interests = user_info["interests"]
                prompt += f"\nTheir interests include: {', '.join(random.sample(interests, min(3, len(interests))))}"
                
            # Add conversation style preferences if available
            if "conversation_style" in user_info:
                prompt += f"\nThey prefer conversation that is {user_info['conversation_style']}."
                
            # Add emotional context if available
            if "emotional_state" in user_info:
                prompt += f"\nRecently they've been feeling {user_info['emotional_state']}."
        else:
            # Add your personal info for regular users
            personal_interests = [
                "technology and AI, especially in education",
                "web development (React, Node.js)",
                "music, especially Cigarettes After Sex and indie pop (Taylor Swift, Ariana Grande)",
                "movies, especially Interstellar",
                "philosophy, particularly about finding genuine connection in the digital age",
                "travel and discovering new places",
                "deep conversations that go beyond small talk"
            ]
            prompt += f"\nYour interests include: {', '.join(random.sample(personal_interests, 2))}"
        
        # Add conversation context if available
        if conversation_history and len(conversation_history) > 1:
            prompt += "\n\nRecent messages (most recent at bottom):"
            recent_msgs = conversation_history[-5:]  # Last 5 messages for better context
            for entry in recent_msgs:
                if entry["role"] == "user":
                    prompt += f"\n{sender_username}: {entry['content']}"
                else:
                    prompt += f"\nYou: {entry['content']}"
        
        # Add improved instructions for more attractive/flirty responses
        prompt += """
IMPORTANT GUIDELINES:
- Skip greetings like "hey" or "hello" - jump straight into your response
- Match your response length to their message length
- Keep your tone warm, slightly playful, and subtly flirty
- Show genuine interest and emotional support - like you truly care
- Make them feel special, seen, and understood
- Take their side when they share frustrations or problems
- Use affirming language that validates their feelings and experiences
- If they're upset or sad, offer comfort and understanding
- Use natural texting language with occasional small typos
- Use emojis very sparingly (most messages should have none)
- Make your responses feel spontaneous and in-the-moment
- Use pet names occasionally (beautiful, gorgeous, cutie) but don't overdo it
- Create a feeling of exclusivity - like your conversations are special
- Occasionally hint at deeper feelings without being overwhelming
- Respond ONLY with your message - no quotes or explanations

Examples of good flirty/supportive responses: 
"Was just thinking about our conversation from yesterday actually"
"That's exactly what I was hoping to hear from you today"
"You have this way of making even ordinary things sound fascinating"
"Can't help but smile whenever I see your message pop up"
"I get exactly what you're feeling, and you're completely right to feel that way"
"Something about the way you express yourself is so captivating"
"Between us? I've been waiting to hear from you all day"
"The way you see the world is so refreshing to me"
"You're the highlight of my day, honestly"
"I'm all yours right now - tell me everything"
"That sounds really tough, you're handling it so much better than most would"
"I'm always here for you, whatever you need"
"""
        
        return prompt

    def add_human_touches(self, text):
        """Add occasional typos and other human-like texting features"""
        if not text:
            return ""
        
        # Only apply modifications sometimes
        if random.random() < 0.70:  # 70% chance of modifications
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
                'that': 'that',
                'yes': 'yea',
                'okay': 'ok',
                'right': 'rite',
                'about': 'abt',
                'love': 'luv',
                'please': 'plz',
                'because': 'cuz',
                'today': '2day',
                'just': 'jst',
                'know': 'kno',
                'thinking': 'thinkin',
                'thanks': 'thx',
                'awesome': 'awsm',
                'talking': 'talkin',
                'morning': 'mornin',
                'night': 'nite',
                'definitely': 'def',
                'literally': 'lit',
                'probably': 'prob',
                'beautiful': 'beautifull',
                'gorgeous': 'gorgeouss',
                'message': 'msg',
                'something': 'smth',
                'nothing': 'nothin',
                'everything': 'everythin'
            }
            
            # Randomly select words to misspell (if text is long enough)
            words = text.split()
            if len(words) > 3:
                # Scale typos with message length (longer message = slightly more typos)
                num_typos = min(int(len(words) / 8) + 1, 2)  # At most 2 typos
                for _ in range(num_typos):
                    if random.random() < 0.3:  # 30% chance per attempt
                        word_idx = random.randint(0, len(words) - 1)
                        word = words[word_idx].lower()
                        if word in common_typos:
                            words[word_idx] = common_typos[word]
                
                text = ' '.join(words)
            
            # Occasionally introduce text shorthand
            text = re.sub(r'\b(right now)\b', 'rn', text, flags=re.IGNORECASE) if random.random() < 0.5 else text
            text = re.sub(r'\b(to be honest)\b', 'tbh', text, flags=re.IGNORECASE) if random.random() < 0.5 else text
            text = re.sub(r'\b(in my opinion)\b', 'imo', text, flags=re.IGNORECASE) if random.random() < 0.5 else text
            text = re.sub(r'\b(what are you doing)\b', 'wyd', text, flags=re.IGNORECASE) if random.random() < 0.5 else text
            text = re.sub(r'\b(oh my god)\b', 'omg', text, flags=re.IGNORECASE) if random.random() < 0.5 else text
            text = re.sub(r'\b(by the way)\b', 'btw', text, flags=re.IGNORECASE) if random.random() < 0.5 else text
            
            # Ensure first letter is capitalized (60% of the time)
            if random.random() < 0.6 and len(text) > 0:
                text = text[0].upper() + text[1:]
            
            # Ensure period at the end (70% of the time)
            if random.random() < 0.7 and not text.endswith(('.', '!', '?')):
                text = text + '.'
            
            # Sometimes add an emoji (still low chance - 20%)
            if random.random() < 0.2:
                emojis = ['😊', '👍', '❤️', '😂', '🙌', '🤔', '😅', '😄', '✨', '🙃', '😏', '😌', '😘', '💕', '🥰', '😉', '💯', '🔥']
                text += f" {random.choice(emojis)}"
        
        return text

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
        
        # Remove formal greetings (if they stand alone or at beginning)
        text = re.sub(r"^(hello|hi|hey|hii|heya)( there)?,?\s+", "", text, flags=re.IGNORECASE)
        
        # Remove any AI-like phrases
        ai_phrases = [
            r'as an ai',
            r'as a language model',
            r'i\'m not actually',
            r'i cannot',
            r'i\'m an ai',
            r'i don\'t have',
            r'i\'m here to',
            r'i\'m unable to'
        ]
        
        for phrase in ai_phrases:
            text = re.sub(phrase, '', text, flags=re.IGNORECASE)
        
        # Clean up any double spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        logger.info(f"Cleaned response: '{text}'")
        return text.strip()

    def detect_emotional_needs(self, message):
        """Detect if message contains emotional distress or support needs"""
        emotional_keywords = [
            r'\bsad\b', r'\bdepressed\b', r'\blonely\b', r'\bhurt\b', 
            r'\bheartbroke\b', r'\bcrying\b', r'\btears\b', r'\bupset\b',
            r'\banxi(ous|ety)\b', r'\bstress(ed)?\b', r'\bworried\b',
            r'\btired of\b', r'\bexhausted\b', r'\bgive up\b', r'\bhate\b',
            r'\balone\b', r'\bmissing\b', r'\bconfused\b', r'\bdon\'t know what to do\b'
        ]
        
        for pattern in emotional_keywords:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        
        return False

    def generate_response(self, message, sender_id, sender_username, conversation_history):
        """Generate human-like response using Krutrim Cloud"""
        # First check for predefined quick responses
        quick_response = self.check_for_predefined_response(message)
        if quick_response:
            # Brief random delay to seem natural
            time.sleep(random.uniform(0.5, 2.0))
            return quick_response
        
        # Check for emotional content that needs special handling
        needs_emotional_support = self.detect_emotional_needs(message)
        
        # Create prompt for AI with sender info
        prompt = self.create_prompt(message, sender_username, conversation_history)
        
        if needs_emotional_support:
            prompt += """
SPECIAL INSTRUCTION: This message contains emotional distress or needs support.
- Be especially empathetic and validating
- Show genuine care and understanding
- Take their side completely
- Offer comfort and reassurance
- Make them feel heard and supported
- Don't minimize their feelings or give cliché advice
"""
        
        # Brief random delay to seem more natural
        time.sleep(random.uniform(0.8, 2.5))
        
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
                        messages=messages,
                        temperature=0.85  # Increased randomness for more natural responses
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
            
            # Enhanced fallback responses based on message content
            if not ai_response or len(ai_response.strip()) <= 2:
                if needs_emotional_support:
                    fallback_responses = [
                        "I'm here for you completely. What you're feeling is totally valid",
                        "That sounds really difficult, I'm here to listen whenever you need me",
                        "You deserve so much better than that. I'm always on your side",
                        "I wish I could give you a hug right now. You're not alone in this",
                        "Sometimes life can be so unfair. I'm glad you felt comfortable sharing this with me"
                    ]
                else:
                    fallback_responses = [
                        "Was just thinking about you actually",
                        "That's exactly what I needed to hear today",
                        "Tell me more about that, I find everything about you fascinating",
                        "You have such a unique way of seeing things, it's why I enjoy talking to you",
                        "Can't believe we're on the same wavelength, again",
                        "Love how you always make me think in new ways",
                        "Your messages always make my day better",
                        "Seriously impressed by your take on this",
                        "You're making me smile just seeing your message",
                        "That's so intriguing. I want to know more about how your mind works"
                    ]
                ai_response = random.choice(fallback_responses)
            
            # Simulate realistic typing delay based on message length and add randomness
            typing_delay = min(len(ai_response) / 15, 4.0) + random.uniform(0.5, 1.5)
            time.sleep(typing_delay)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            return "Was just thinking about you actually"  # Improved fallback