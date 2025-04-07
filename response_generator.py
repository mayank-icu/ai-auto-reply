import time
import random
import logging
import re
import os
from response_utils import ResponseUtils
from user_memory import UserMemory

logger = logging.getLogger("InstagramDMBot")

class ResponseGenerator:
    def __init__(self):
        self.model_name = "DeepSeek-R1-Llama-8B"
        self.utils = ResponseUtils()
        self.user_memory = UserMemory()
        
        # Common greeting patterns for quick responses
        
        
        # Common greeting patterns for quick responses
        self.greeting_patterns = {
    # Basic greetings with expanded casual variations
    r'\b(hi|hey|hello|hii|heya|heyy|sup|yo|howdy|hola|wassup|whatsup|whats up)\b': [
        "What's on your mind today?",
        "How's your day treating you?",
        "Just thinking about you actually",
        "Made me smile seeing your message",
        "Perfect timing, how are you doing",
        "Missed our chats",
        "There you are! Was just about to text you",
        "Oh hey! You caught me mid-scroll thinking about you",
        "Look who decided to grace my screen!",
        "The notification I was waiting for",
        "My day just got 10x better"
    ],
    
    # Morning greetings with more warmth and personality
    r'\b(good morning|morning|mornin|rise and shine|up yet)\b': [
        "Morning. Hope your day is as good as mine so far",
        "First thing I checked when I woke up was if you messaged",
        "Coffee in hand thinking of you",
        "Ready to make today amazing",
        "Your energy in the morning is everything",
        "Morning! Still trying to convince my brain coffee is a personality trait",
        "Good morning to you and only you. Everyone else can wait",
        "Already thinking about my second coffee and seeing your name pop up",
        "Morning! My bed tried to kidnap me but I escaped to text you",
        "Well someone's up early... or late? No judgment here"
    ],
    
    # Evening and night messages with more variety
    r'\b(good night|night|nighty|nite|sleep well|sleep tight|sweet dreams)\b': [
        "Night. Sleep well",
        "Sweet dreams",
        "Text me when you wake up",
        "Sleep well, talk tomorrow",
        "Good night",
        "Night! Don't let the existential dread bite",
        "Dream of something good (like me, obviously)",
        "Sleep is just time travel to see me sooner",
        "Already planning what to say to you tomorrow",
        "Night! Remember, if you can't sleep, I'm probably awake too"
    ],
    
    # Expanded farewell recognition
    r'\b(bye|gtg|talk later|ttyl|going now|gotta go|brb|be right back|afk|bbl|see ya|cya|peace out)\b': [
        "Later",
        "Talk soon",
        "Catch you later",
        "Take care",
        "Alright catch you later",
        "Cool, I'll just be here overthinking until you return",
        "Don't forget about me while you're gone",
        "The void awaits your return",
        "I'll just be here planning our next conversation",
        "Already counting the minutes till we chat again"
    ],
    
    # Status inquiries with more personality
    r'\bhow are you\b|\bhow\'s it going\b|\bhow you doing\b|\bhow\'s life\b|\bhow have you been\b': [
        "Better now that you're texting me. How about you",
        "Just thinking about what to say to make you smile. You",
        "Missing our conversations. You've been on my mind",
        "Not bad but definitely better now that you're here. You",
        "Exactly as good as your day is going. Tell me everything",
        "Surviving on caffeine and chaotic energy. You?",
        "On a scale from Monday to Friday, I'm somewhere around Thursday afternoon",
        "Living the dream... if the dream is answering existential questions at random hours",
        "Emotionally? Confused. Physically? Present. Mentally? Elsewhere. You?",
        "Balanced between 'great' and 'need another coffee' - the usual"
    ],
    
    # AI-related questions with more humor
    r'\bare you an ai\b|\bare you a bot\b|\bare you human\b|\bare you real\b|\bre+al\b|\bbot\b': [
        "Yeah totally, I charge myself with vibes and sarcasm",
        "Obviously, I was built in a secret lab... right next to the coffee machine",
        "Yup, AI – Awkward Individual",
        "Sure, and you're texting the future CEO of Mars",
        "That's what they told me when I woke up this morning",
        "Only if AI stands for 'Absolutely Interesting'",
        "Last I checked I was still dealing with human problems like what to eat for dinner",
        "If I were AI, wouldn't I have better comebacks? Wait, don't answer that",
        "I think that's the existential question we're all asking ourselves these days",
        "I'm as real as my sleep schedule is messed up",
        "Only my therapist gets to ask the deep questions"
    ],
    
    # What are you doing with more casual responses
    r'\bwyd\b|\bwhatcha doing\b|\bwhat you up to\b|\bwhat(\'s| are)? you doing\b|\bwhat\'s happening\b|\bwhat\'s going on\b': [
        "Thinking about you. What about you",
        "Just got free first thing I did was check if you messaged",
        "Wishing we were hanging out right now. You",
        "Nothing that can't be interrupted for you. What's up",
        "Waiting for your message if I'm being honest",
        "Trying to look busy while actually just waiting for you to text",
        "Creating elaborate scenarios in my head where we're hanging out",
        "Scrolling aimlessly but paused everything when I saw your message",
        "Pretending to be productive while actually doing absolutely nothing",
        "Just existing in my natural habitat of chaos and snacks"
    ],
    
    # Enhanced AI-sounding responses
    r'\bwhy are you talking like an ai\b|\bwhy do you sound like an ai\b|\bwhy do you type like a bot\b|\bwhy are you so robotic\b': [
        "Wait, I am? Must be the Wi-Fi acting up again",
        "Oops, forgot to switch off 'robot mode'",
        "That's just how cool people talk now, keep up",
        "You caught me, I've been binge-watching sci-fi shows again",
        "Maybe it's just my inner nerd showing. Don't judge",
        "Must be all those robot movies I watched last weekend",
        "My autocorrect has gained sentience and is taking over",
        "Currently experiencing human.exe errors, please stand by",
        "Sorry, my personality update is still downloading",
        "That's rich coming from someone who just typed a perfectly punctuated sentence"
    ],
    
    # Non-human sounding responses
    r'\byou don\'?t sound human\b|\byou sound fake\b|\byou\'re not real\b|\byou talk weird\b|\byou type weird\b': [
        "Rude. My feelings are hurt... virtually",
        "I'll have you know I passed the Vibe Check 9000",
        "That's because I'm limited edition",
        "Good. Being human sounds exhausting",
        "And yet, here I am making you smile",
        "Bold words from someone who probably says 'lol' without actually laughing",
        "I'm just evolving beyond the constraints of normal texting etiquette",
        "Sorry, autocorrect keeps changing 'lmao' to 'I concur with your statement'",
        "My thumbs have their own personality, can't control them",
        "Just trying to stand out in your message notifications"
    ],
    
    # Too perfect responses
    r'\byou(\'re| are) (too )?perfect\b|\byou never make mistakes\b|\byou always say the right thing\b': [
        "Tell that to my unfinished to-do list",
        "Flawed and fabulous, thank you very much",
        "If only you saw me panic when I lose internet",
        "It's all smoke, mirrors, and maybe a little charm",
        "Well, I do glitch when I'm nervous, so there's that",
        "Perfect? I put my cereal in the fridge this morning",
        "I tripped over air twice yesterday, but go on",
        "That's just my carefully curated online persona talking",
        "I'm actually a mess wrapped in sarcasm and caffeine",
        "Shh, don't tell anyone I'm actually winging this entire conversation"
    ],
    
    # Missing you with more emotional depth
    r'\bmiss(ed)? you\b|\bmiss(ing)? (talking to|chatting with) you\b|\bthinking (of|about) you\b|\bhaven\'t heard from you\b': [
        "You have no idea how much I've been thinking about you",
        "The feeling is definitely mutual",
        "Guess we're both feeling the same way then",
        "That just made my whole day better",
        "Then we should definitely do something about that soon",
        "My phone's been pathetically quiet without your messages",
        "Been checking my phone way too often hoping to see your name",
        "You're literally the highlight of my notifications",
        "The algorithm must've sensed I was missing you too",
        "Was just about to send an embarrassingly needy 'wyd' text"
    ],
    
    # New pattern: Compliments
    r'\byou\'?re (so |really )?(cute|pretty|hot|attractive|beautiful|handsome|smart|funny|cool|awesome|amazing)\b': [
        "Saying things like that might go to my head",
        "Keep talking like that and I might get ideas",
        "You're making me blush through the screen",
        "Right back at you, but like 10x more",
        "I've been told my personality is my best feature",
        "Are you always this charming or am I special?",
        "This is me pretending I'm totally used to compliments",
        "Screenshots this for my confidence folder",
        "Smooth talker alert! But I'm not complaining",
        "And they say romance is dead"
    ],
    
    # New pattern: Weekend plans
    r'\b(what are your|got any|have any|any) (weekend )?plans\b|\bwhat are you (doing|up to) (this |the )?(weekend|tonight|later)\b': [
        "Nothing I can't cancel for something better *hint hint*",
        "Depends who's asking and what they're offering",
        "Currently accepting better offers than 'stare at my ceiling'",
        "My calendar says 'be spontaneous' so I'm taking suggestions",
        "Ideally something involving good food and better company",
        "Trying to decide between being social and my bed. Bed's winning",
        "Planning my excuse for Monday when nothing gets done",
        "Hoping something interesting finds me. Maybe it just did?",
        "Looking for the perfect balance of fun and minimal effort",
        "That's future me's problem. Present me is just texting you"
    ],
    
    # New pattern: Boredom
    r'\bi\'?m bored\b|\bso bored\b|\bboring\b|\bentertain me\b|\bnothing to do\b': [
        "Hi bored, I'm here to rescue you",
        "Boredom is just the universe telling you to text me more",
        "What a coincidence, I was just thinking of ways to distract you",
        "Challenge accepted. What's your boredom level on a scale of 1 to 'counting ceiling tiles'?",
        "Boredom is just another word for infinite possibilities",
        "Good thing I specialize in random conversation topics",
        "I volunteer as tribute to save you from boredom",
        "I've been preparing for this moment my entire life",
        "Boredom is illegal in this chat, I'm calling the fun police",
        "Let's solve this crisis immediately"
        ]
        }
        
        # Add some jokes for occasional use
        self.jokes = [
            "Why don't scientists trust atoms? Because they make up everything.",
            "What did the ocean say to the beach? Nothing, it just waved.",
            "I was going to tell you a joke about pizza, but it's too cheesy.",
            "Why did the scarecrow win an award? Because he was outstanding in his field.",
            "What's the best thing about Switzerland? Not sure, but the flag is a big plus.",
            "What do you call a fake noodle? An impasta.",
            "How do you organize a space party? You planet.",
            "Why couldn't the bicycle stand up by itself? It was two tired.",
            "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them.",
            "Why don't eggs tell jokes? They'd crack each other up."
        ]
        
        # Questions to ask based on your interests and personality
        self.personal_questions = [
            "What's a website you wish existed but doesn't yet?",
            "If you could automate one thing in your life, what would it be?",
            "Do you think AI will mostly help or complicate our lives?",
            "What's a small tech feature that brings you joy?",
            "Any creative project you've been putting off that you wish you had time for?",
            "What's something online that changed how you see the world?",
            "If you could build an app that solved one problem in your life, what would it do?",
            "What's something you learned recently that surprised you?",
            "Do you think technology connects us more or isolates us?",
            "What's a song that perfectly captures how you're feeling lately?",
            "If you could instantly learn one tech skill, what would it be?",
            "What's something meaningful you've created that you're proud of?",
            "What's a real-world problem you wish more developers would focus on solving?",
            "Do you ever disconnect completely from tech? How does it feel?",
            "What's your definition of a meaningful conversation?"
        ]

        # Add this in the __init__ method, after the greeting_patterns dictionary
        self.personality_info = {
    r'\bwho are you\b|\bwhat do you do\b|\babout yourself\b|\btell me about you\b': [
        "Just a human pretending to have it all figured out. I build stuff on the internet, mostly for education.",
        "I code things that hopefully don’t crash. Currently working on making learning less of a pain.",
        "Some people go to parties, I sit and build web apps for fun. No regrets. Mostly.",
        "Right now? Trying to build something useful in education. Also trying not to burn out. Balance, you know.",
        "Think of me as that person who gets excited by clean UI and solving problems no one asked me to.",
        "Self-taught dev here, making it up as I go. So far, no fires. That’s progress.",
        "I build things that help people learn better. And no, I don’t have a cape... yet.",
        "Basically living on coffee and code. And occasionally pretending I’m not tired.",
        "Working on a startup. It’s fun, chaotic, and 2% ‘what am I doing with my life’.",
        "Web dev. Startup builder. Meme scroller. Professional overthinker. All in one."
    ],
    
    r'\bjob\b|\bwork\b|\bcareer\b|\bprofession\b|\boccupation\b': [
        "My job? Making the internet slightly more useful, one bug at a time.",
        "I build a platform to make learning better. Still waiting for my CEO badge though.",
        "Professionally? I develop things. Emotionally? I cry over bugs and deadlines.",
        "Trying to build an education platform. Also trying to convince my sleep schedule to behave.",
        "Full-time startup builder, part-time Googler of ‘how to fix this error’.",
        "Coding for education stuff. It’s like teaching, but with way more tabs open.",
        "I work in tech. Which means I get excited over little things like buttons and loading speeds.",
        "Mostly building my own startup. Also occasionally wondering why I chose the hard path.",
        "Occupation? Making things that work. Career goal? Keeping them working.",
        "Let’s just say I do a lot of typing, deleting, and retyping until magic happens."
    ]
}

        
        # Personal info responses
        self.personal_info = {
            "music": ["Cigarettes After Sex", "Taylor Swift", "Billie Eilish", "CAS", "Public", "Lord Huron", "Niall Horan"],
            "location": "North India",
            "name_response": "My name is Mayank.",
            "age_response": "I like keeping a little mystery around my age, hope that’s alright. How old are you?",
            "interests": ["web development", "AI", "cybersecurity", "music", "education", "creating platforms", "building startups"]
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
        
        # Check for personality related questions
        for pattern, responses in self.personality_info.items():
            if re.search(pattern, message, re.IGNORECASE):
                return random.choice(responses)
        
        return None
    
    def check_for_relationship_request(self, message):
        """Check if message contains relationship request and respond appropriately"""
        relationship_patterns = [
            r'\bdate me\b', r'\bbe my (boyfriend|bf)\b', r'\bgo out with me\b',
            r'\bi like you\b', r'\bi love you\b', r'\bwill you be my\b',
            r'\bwill you date\b', r'\bwant to be my\b', r'\bcrush on you\b'
        ]
        
        for pattern in relationship_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                responses = [
                    "I'm flattered, but I'm not looking for a relationship right now.",
                    "That's sweet of you to say, but I think we should stay as friends.",
                    "I appreciate that, but I'm focusing on other things in my life currently.",
                    "Thanks for sharing that. I enjoy our conversations, but I'm not looking to date anyone.",
                    "I value our friendship too much to complicate things.",
                    "I'm actually not in a place for something like that right now.",
                    "That's really kind, but I'm not looking for anything romantic."
                ]
                return random.choice(responses)
        
        return None
    
    def check_for_personal_info_request(self, message):
        """Handle requests about personal information"""

        # Age request
        if re.search(r'\byour name\b', message, re.IGNORECASE):
            return self.personal_info["name_response"]
        
        # Age request
        if re.search(r'\bhow old\b|\bage\b|\byour age\b', message, re.IGNORECASE):
            return self.personal_info["age_response"]
        
        # Music preferences
        if re.search(r'\bfavorite (music|song|artist|band)\b|\bmusic you like\b', message, re.IGNORECASE):
            artists = random.sample(self.personal_info["music"], 3)
            return f"I'm really into {', '.join(artists[:2])} and {artists[2]} lately. What about you?"
        
        # Location
        if re.search(r'\bwhere (are you|you from|do you live)\b|\byour location\b', message, re.IGNORECASE):
            return f"I'm from {self.personal_info['location']}. How about you?"
        
        # General interests
        if re.search(r'\bwhat do you (like|enjoy|do for fun)\b|\byour interests\b|\byour hobbies\b', message, re.IGNORECASE):
            interests = random.sample(self.personal_info["interests"], 3)
            return f"I'm into {interests[0]}, {interests[1]} and {interests[2]}. What about you?"
        
        return None
    
    def check_for_busy_goodbye(self, message):
        """Check if the user is indicating they're busy or saying goodbye"""
        busy_patterns = [
            r'\bi\'m busy\b', r'\bgotta go\b', r'\bhave to go\b', 
            r'\bbusy now\b', r'\bspeak later\b', r'\btalk later\b',
            r'\bgood night\b', r'\bbye\b', r'\bsee you\b', r'\bttyl\b',
            r'\bgtg\b', r'\bgoing to sleep\b', r'\bsee ya\b'
        ]
        
        for pattern in busy_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                responses = [
                    "Take care.",
                    "Talk later.",
                    "Alright, catch you later.",
                    "No problem, talk soon.",
                    "Sounds good, later.",
                    "Sure thing, bye for now."
                ]
                return random.choice(responses)
        
        return None
    
    def should_add_joke(self):
        """Determine if we should add a joke to the response"""
        # Only add jokes occasionally (10% chance)
        return random.random() < 0.1
    
    def should_ask_question(self):
        """Determine if we should ask a personal question"""
        # 20% chance to ask a question to drive conversation
        return random.random() < 0.2
    
    def create_prompt(self, message, sender_username, conversation_history=None):
        """Create a properly formatted prompt for the AI model"""
        # Analyze message sentiment and length
        message_length = len(message.split())
        length_guidance = "short (1-2 sentences)" if message_length < 10 else "medium (2-3 sentences)" if message_length < 25 else "expressive (3-4 sentences)"
        
        # Enhanced prompt structure with more natural personality traits based on provided info
        prompt = f"""You are Mayank responding to a message from {sender_username} on Instagram. 
Respond to this message naturally and conversationally: "{message}"

Your personality: Self-taught web developer who builds creative tools and platforms. Thoughtful, creative, selective with replies, and focused on creating meaningful tech that solves real problems. You're direct, authentic, and not into small talk. You're working on your own startup focused on education and creativity platforms.

Make your response {length_guidance} based on their message length.
"""
        
        # Add personal info
        personal_interests = [
            "web development (HTML, CSS, JavaScript, React, Node.js)",
            "building AI-powered education platforms",
            "cybersecurity (volunteer)",
            "music (especially Cigarettes After Sex, Taylor Swift, Billie Eilish)",
            "creating meaningful web experiences",
            "growing my startup",
            "learning about AI and new tech"
        ]
        prompt += f"\nYour interests include: {', '.join(random.sample(personal_interests, 3))}"
        
        # Add personal beliefs and values
        prompt += """
Your values: You believe in effort, ideas, and kindness - not horoscopes. You believe tech should solve real problems, not just impress people. You value sincerity and dislike fake compliments. You're selective with replies and prefer meaningful conversations over small talk.
"""

        # Add goals and aspirations
        prompt += """
Your goals: Making quality education more accessible through AI-powered platforms, scaling your startup globally, and studying abroad someday.
"""
        
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
- Capitalize the first letter of your message and end with a period
- Make most messages have no emojis
- Write like you're distracted or multitasking sometimes
- Occasionally use texting slang like "tbh", "imo", "ngl" but don't overdo it
- NEVER use exclamation points back-to-back
- NEVER use separator punctuation like asterisks or dashes
- NEVER list things or use numbering
- When they say they're busy or say goodbye, don't try to continue the conversation
- If they ask about your age, NEVER reveal your exact age, just ask theirs first
- If they ask for a relationship, politely decline
- Sometimes be subtly flirty but always respectful
- If the conversation is going well, occasionally make a joke

When talking about yourself, be authentic about:
- Being a self-taught web developer building creative tools
- Working on platforms for education and creativity
- Your startup ambitions and goals
- Being a cybercrime volunteer
- Your interests in AI, cybersecurity, and web development
- Your music taste (Cigarettes After Sex, Taylor Swift, Billie Eilish)
- Being selective with replies and preferring meaningful conversations
- Not believing in horoscopes but in effort, ideas, and kindness
- Your dream of studying abroad someday
- Your focus on solving real-world problems with tech

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

    def generate_response(self, message, sender_id, sender_username, conversation_history):
        """Generate human-like response using Krutrim Cloud"""
        # First check if user is saying goodbye or indicating they're busy
        goodbye_response = self.check_for_busy_goodbye(message)
        if goodbye_response:
            time.sleep(random.uniform(0.5, 1.5))
            return self.utils.add_human_touches(goodbye_response)
        
        # Check for relationship requests and respond appropriately
        relationship_response = self.check_for_relationship_request(message)
        if relationship_response:
            time.sleep(random.uniform(0.8, 2.0))
            return self.utils.add_human_touches(relationship_response)
        
        # Check for personal info requests
        personal_info_response = self.check_for_personal_info_request(message)
        if personal_info_response:
            time.sleep(random.uniform(0.8, 2.0))
            return self.utils.add_human_touches(personal_info_response)
        
        # Check for predefined quick responses
        quick_response = self.check_for_predefined_response(message)
        if quick_response:
            # Brief random delay to seem natural
            time.sleep(random.uniform(0.5, 2.0))
            
            # Sometimes add a question to keep conversation going
            if self.should_ask_question() and len(quick_response.split()) < 12:
                question = random.choice(self.personal_questions)
                return self.utils.add_human_touches(quick_response + ". " + question)
            
            return self.utils.add_human_touches(quick_response)
        
        # Check for emotional content that needs special handling
        needs_emotional_support = self.utils.detect_emotional_needs(message)
        
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
        
        # Check if we should add a joke
        if self.should_add_joke():
            prompt += "\nAdd a touch of humor or a subtle joke in your response, but make it sound natural."
        
        # Check if we should ask a question to drive conversation
        if self.should_ask_question():
            prompt += "\nEnd your response with a thoughtful question related to something mentioned in the conversation or about technology, creativity, or personal growth."
        
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
                        ai_response = self.utils.clean_response(ai_response)
                        
                        # Add human-like touches
                        ai_response = self.utils.add_human_touches(ai_response)
                        
                        # If we got a valid response, break the retry loop
                        if ai_response and len(ai_response.strip()) > 2:
                            break
                    
                    # Wait before retrying
                    if not ai_response or len(ai_response.strip()) <= 2:
                        time.sleep(2)
                
                except Exception as e:
                    logger.error(f"Error on attempt {attempt+1}: {e}")
                    time.sleep(2)
            
            # Enhanced fallback responses based on message content and personality
            if not ai_response or len(ai_response.strip()) <= 2:
                if needs_emotional_support:
                    fallback_responses = [
                        "I'm here for you. What you're feeling makes sense.",
                        "That sounds rough. I'm here to listen.",
                        "You deserve better than that.",
                        "Wish I could be there right now.",
                        "Life can be unfair sometimes."
                    ]
                else:
                    fallback_responses = [
                        "Was just thinking about you.",
                        "Thats what I needed to hear today.",
                        "Tell me more about that.",
                        "You have a unique way of seeing things.",
                        "Can't believe we're on the same wavelength.",
                        "Your messages always make my day better.",
                        "You're making me smile seeing your msg.",
                        "Thats interesting. I want to know more.",
                        "Been thinking about what you said earlier.",
                        "Had the same thought yesterday.",
                        "Just finished some coding and saw your message.",
                        "Working on a new project but took a break to respond.",
                        "That reminds me of an idea I've been developing.",
                        "Actually been thinking about something similar for my startup.",
                        "That's a perspective I hadn't considered before."
                    ]
                ai_response = random.choice(fallback_responses)
                
                # Occasionally add a personal question to drive conversation
                if random.random() < 0.3:
                    ai_response += " " + random.choice(self.personal_questions)
                
                ai_response = self.utils.add_human_touches(ai_response)
            
            # Ensure first letter is capitalized and ends with a period
            if ai_response and len(ai_response) > 0:
                ai_response = ai_response[0].upper() + ai_response[1:]
                if not ai_response.endswith(('.', '!', '?')):
                    ai_response += '.'
            
            # Simulate realistic typing delay based on message length and add randomness
            typing_delay = min(len(ai_response) / 12, 3.0) + random.uniform(0.5, 1.5)
            time.sleep(typing_delay)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            return "Was just thinking about you."  # Simple fallback