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
                "What's on your mind today?",
                "How's your day treating you?",
                "Just thinking about you, actually.",
                "Made me smile seeing your message.",
                "Perfect timing! How are you doing?",
                "Missed our chats."
            ],
            r'\bgood morning\b': [
                "Morning! Hope your day is as beautiful as you are.",
                "First thing I checked when I woke up was if you messaged.",
                "Coffee in hand, thinking of you.",
                "Ready to make today amazing?",
                "Your energy in the morning is everything."
            ],
            r'\bgood night\b': [
                "Sweet dreams. Wish I could be there.",
                "Night night. Text me when you wake up?",
                "Dream of good things (maybe me?).",
                "Sleep well! Sending you the warmest goodnight hug.",
                "Tomorrow's another day for us to talk more."
            ],
            r'\bhow are you\b': [
                "Better now that you're texting me. How about you?",
                "Just thinking about what to say to make you smile. You?",
                "Missing our conversations. You've been on my mind.",
                "Not bad, but definitely better now that you're here. You?",
                "Exactly as good as your day is going. Tell me everything."
            ],
            r'\bwyd\b|\bwhat(\'s| are)? you doing\b': [
                "Thinking about you. What about you?",
                "Just got free, first thing I did was check if you messaged.",
                "Wishing we were hanging out right now. You?",
                "Nothing that can't be interrupted for you. What's up?",
                "Waiting for your message if I'm being honest."
            ],
            r'\bmiss(ed)? you\b': [
                "You have no idea how much I've been thinking about you.",
                "The feeling is definitely mutual.",
                "Guess we're both feeling the same way then.",
                "That just made my whole day better.",
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
        length_guidance = "short (1-2 sentences)" if message_length < 10 else "medium (2-3 sentences)" if message_length < 25 else "expressive (3-4 sentences)"
        
        # Enhanced prompt structure with more natural personality traits
        prompt = f"""You are Mayank responding to a message from {sender_username} on Instagram. 
Respond to this message naturally and conversationally: "{message}"

Your personality: Confident, casual, friendly, attentive, and real. You write like a normal person having a regular conversation, not overly enthusiastic or formal.

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
                "music, especially indie pop",
                "movies, especially Interstellar",
                "philosophy",
                "travel",
                "deep conversations"
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
        
        # Add improved instructions for more natural responses
        prompt += """
IMPORTANT GUIDELINES:
- Skip greetings like "hey" or "hello" - jump straight into your response
- Match your response length to their message length
- Keep your tone casual and natural, like a real person texting
- Show genuine interest but don't be overly enthusiastic
- Take their side when they share frustrations or problems
- Use natural texting language with occasional typos and abbreviations
- Capitalize the first letter of your message (90% of the time)
- Make most messages have no emojis (99% should have none)
- Write like you're distracted or multitasking sometimes
- Occasionally use texting slang like "tbh", "imo", "ngl" but don't overdo it
- NEVER use exclamation points back-to-back
- NEVER use separator punctuation like asterisks or dashes
- NEVER list things or use numbering
- Make sentences flow naturally with occasional run-ons
- Avoid perfect grammar or punctuation
- Respond ONLY with your message - no quotes or explanations

Examples of good natural responses: 
"was actually thinking about that earlier today"
"just finished work and saw your message"
"you always have the most interesting way of looking at things"
"been feeling the same way lately"
"yeah that makes sense especially with everything going on"
"honestly would've done the same thing"
"you're handling it better than most people would"
"pretty sure we talked about this before"
"remember when we had that conversation about it"
"had the same thought yesterday"
"thats actually a really good point"
"never looked at it that way before"
"sounds like you've had a day"
"wish i could help more with that"
"let me know how it goes tomorrow"
"been thinking about you"
"""
        
        return prompt

    def add_human_touches(self, text):
        """Add occasional typos and other human-like texting features"""
        if not text:
            return ""
        
        # Only apply modifications sometimes
        if random.random() < 0.35:  # 85% chance of modifications
            # Words that might get typos or slang
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
                'message': 'msg',
                'something': 'smth',
                'nothing': 'nothin',
                'everything': 'everythin',
                'friend': 'bud',
                'good': 'gud',
                'see you': 'cu',
                'see you later': 'cya',
                'wait': 'w8',
                'sorry': 'sry',
                'no problem': 'np',
                'kind of': 'kinda',
                'alright': 'aight',
                'amazing': 'amazn',
                'whatever': 'whatevs'
            }
            
            # Simple text slang words
            slang_expressions = {
                ' seriously ': ' srsly ',
                ' very ': ' rlly ',
                ' extremely ': ' super ',
                ' yes ': ' yea ',
                ' no ': ' nah ',
                ' crazy ': ' wild ',
                ' true ': ' tru ',
                ' impressive ': ' cool ',
                ' good ': ' gud ',
                ' upset ': ' bummed ',
                ' agree ': ' agree ',
                ' angry ': ' mad ',
                ' comfortable ': ' comfy ',
                ' perfect ': ' perfect ',
                ' tired ': ' tired ',
                ' happy ': ' happy ',
                ' surprised ': ' surprised ',
                ' suspicious ': ' sus ',
                ' annoying ': ' annoying ',
                ' honestly ': ' honestly '
            }
            
            # Randomly select words to misspell or replace with slang (if text is long enough)
            words = text.split()
            if len(words) > 3:
                # Scale typos with message length (longer message = slightly more typos)
                num_typos = min(max(int(len(words) / 15), 1), 2)  # 1-2 typos based on length
                for _ in range(num_typos):
                    if random.random() < 0.3:  # 30% chance per attempt
                        word_idx = random.randint(0, len(words) - 1)
                        word = words[word_idx].lower()
                        if word in common_typos and len(word) > 2 and random.random() < 0.5:
                            words[word_idx] = common_typos[word]
                
                text = ' '.join(words)
            
            # Apply slang replacements (but very sparingly)
            slang_limit = 1  # Max 1 slang term per message
            slang_count = 0
            
            for phrase, slang in slang_expressions.items():
                if random.random() < 0.1 and slang_count < slang_limit:  # 10% chance per slang term
                    if re.search(phrase, text, re.IGNORECASE):
                        text = re.sub(phrase, slang, text, flags=re.IGNORECASE, count=1)
                        slang_count += 1
            
            # Add popular text slang (rarely)
            if random.random() < 0.35:  # 15% chance to add slang
                slang_to_add = random.choice([
                    " tbh", " imo", " ngl", " fr", " lol", " idk", " btw"
                ])
                
                # Add at appropriate locations
                sentences = re.split(r'([.!?] )', text)
                if len(sentences) >= 3:  # If we have at least one full sentence
                    # Choose a random sentence end to add slang
                    idx = random.randrange(0, len(sentences) - 2, 2)
                    sentences[idx] = sentences[idx] + slang_to_add
                    text = ''.join(sentences)
                elif not text.endswith(('.', '!', '?')):
                    # Or just add to the end if appropriate
                    text += slang_to_add
            
            # Occasionally introduce text shorthand
            text = re.sub(r'\b(right now)\b', 'rn', text, flags=re.IGNORECASE) if random.random() < 0.3 else text
            text = re.sub(r'\b(to be honest)\b', 'tbh', text, flags=re.IGNORECASE) if random.random() < 0.3 else text
            text = re.sub(r'\b(in my opinion)\b', 'imo', text, flags=re.IGNORECASE) if random.random() < 0.3 else text
            text = re.sub(r'\b(what are you doing)\b', 'wyd', text, flags=re.IGNORECASE) if random.random() < 0.3 else text
            text = re.sub(r'\b(oh my god)\b', 'omg', text, flags=re.IGNORECASE) if random.random() < 0.3 else text
            text = re.sub(r'\b(by the way)\b', 'btw', text, flags=re.IGNORECASE) if random.random() < 0.3 else text
            
            # Ensure first letter is capitalized (90% of the time)
            if random.random() < 0.9 and len(text) > 0:
                text = text[0].upper() + text[1:]
            else:
                # Sometimes deliberately don't capitalize (10%)
                if len(text) > 0 and text[0].isupper():
                    text = text[0].lower() + text[1:]
            
            # End punctuation (70% of the time, otherwise leave hanging)
            if random.random() < 0.7 and not text.endswith(('.', '!', '?')):
                # Choose ending punctuation
                if random.random() < 0.8:
                    text = text + '.'  # Most common
                elif random.random() < 0.5:
                    text = text + '!'  # Sometimes
                else:
                    text = text + '?'  # Rarely
            
            # Add an emoji (only 1% chance)
            if random.random() < 0.01:
                emojis = ['😊', '👍', '❤️', '😂', '🙌', '🤔', '😅', '😄', '✨', '🙃', '😏', '💕']
                text += f" {random.choice(emojis)}"
                
            # Sometimes drop apostrophes (texting style)
            if random.random() < 0.4:
                text = re.sub(r'([a-z])\'([a-z])', r'\1\2', text)
                
            # Sometimes use run-on text with no punctuation (25%)
            if random.random() < 0.25:
                parts = re.split(r'([.!?] )', text)
                if len(parts) > 2:
                    idx = random.randrange(0, len(parts) - 2, 2)
                    parts[idx+1] = " "  # Remove punctuation
                    text = ''.join(parts)
        
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
            r'^i could say\s*',
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
            r'i\'m unable to',
            r'my programming',
            r'based on your message',
            r'it sounds like',
            r'i understand that',
            r'i appreciate',
            r'in response to',
        ]
        
        for phrase in ai_phrases:
            text = re.sub(phrase, '', text, flags=re.IGNORECASE)
        
        # Remove excessive punctuation (multiple !!! or ??? or combinations)
        text = re.sub(r'(!|\?){2,}', r'\1', text)
        
        # Remove bullet points and numbering
        text = re.sub(r'^[\d\.\*\-\•]+\s*', '', text, flags=re.MULTILINE)
        
        # Remove separators
        text = re.sub(r'[\*\-\_\=]{2,}', '', text)
        
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
- Be understanding but don't be over-the-top supportive
- Show care but keep it casual and real
- Take their side naturally
- Don't use clichés or generic advice
- Make support sound authentic and not rehearsed
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
                        temperature=0.9  # Higher temperature for more natural randomness
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
                        "I'm here for you. What you're feeling makes sense",
                        "That sounds rough. I'm here to listen",
                        "You deserve better than that",
                        "Wish I could be there right now",
                        "Life can be unfair sometimes"
                    ]
                else:
                    fallback_responses = [
                        "Was just thinking about you",
                        "Thats what I needed to hear today",
                        "Tell me more about that",
                        "You have a unique way of seeing things",
                        "Can't believe we're on the same wavelength",
                        "Your messages always make my day better",
                        "You're making me smile seeing your msg",
                        "Thats interesting. I want to know more",
                        "Been thinking about what you said earlier",
                        "Had the same thought yesterday"
                    ]
                ai_response = random.choice(fallback_responses)
                ai_response = self.add_human_touches(ai_response)
            
            # Simulate realistic typing delay based on message length and add randomness
            typing_delay = min(len(ai_response) / 12, 3.0) + random.uniform(0.5, 1.5)
            time.sleep(typing_delay)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            return "Was just thinking about you"  # Simple fallback