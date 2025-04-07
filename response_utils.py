import re
import random
import logging

logger = logging.getLogger("InstagramDMBot")

class ResponseUtils:
    def __init__(self):
        # Common typos and text slang for human-like responses
        self.common_typos = {
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
            'wait': 'w8',
            'sorry': 'sry',
            'no problem': 'np',
            'kind of': 'kinda',
            'whatever': 'whatevs'
        }
        
        # Simple text slang
        self.slang_expressions = {
            ' seriously ': ' srsly ',
            ' very ': ' rlly ',
            ' extremely ': ' super ',
            ' yes ': ' yea ',
            ' no ': ' nah ',
            ' crazy ': ' wild ',
            ' true ': ' tru ',
            ' impressive ': ' cool ',
            ' upset ': ' bummed ',
            ' agree ': ' agree ',
            ' angry ': ' mad ',
            ' comfortable ': ' comfy ',
            ' tired ': ' tired ',
            ' happy ': ' happy ',
            ' surprised ': ' surprised ',
            ' suspicious ': ' sus ',
            ' annoying ': ' annoying ',
            ' honestly ': ' honestly '
        }
    
    def add_human_touches(self, text):
        """Add occasional typos and other human-like texting features"""
        if not text:
            return ""
        
        # Only apply modifications sometimes (35% chance)
        if random.random() < 0.35:
            words = text.split()
            if len(words) > 3:
                # Scale typos with message length (longer message = slightly more typos)
                num_typos = min(max(int(len(words) / 15), 1), 2)  # 1-2 typos based on length
                for _ in range(num_typos):
                    if random.random() < 0.3:  # 30% chance per attempt
                        word_idx = random.randint(0, len(words) - 1)
                        word = words[word_idx].lower()
                        if word in self.common_typos and len(word) > 2 and random.random() < 0.5:
                            words[word_idx] = self.common_typos[word]
                
                text = ' '.join(words)
            
            # Apply slang replacements (but very sparingly)
            slang_limit = 1  # Max 1 slang term per message
            slang_count = 0
            
            for phrase, slang in self.slang_expressions.items():
                if random.random() < 0.1 and slang_count < slang_limit:  # 10% chance per slang term
                    if re.search(phrase, text, re.IGNORECASE):
                        text = re.sub(phrase, slang, text, flags=re.IGNORECASE, count=1)
                        slang_count += 1
            
            # Add popular text slang (rarely)
            if random.random() < 0.25:  # 25% chance to add slang
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
            
            # Occasionally introduce text shorthand (30% chance each)
            text = re.sub(r'\b(right now)\b', 'rn', text, flags=re.IGNORECASE) if random.random() < 0.3 else text
            text = re.sub(r'\b(to be honest)\b', 'tbh', text, flags=re.IGNORECASE) if random.random() < 0.3 else text
            text = re.sub(r'\b(in my opinion)\b', 'imo', text, flags=re.IGNORECASE) if random.random() < 0.3 else text
            text = re.sub(r'\b(what are you doing)\b', 'wyd', text, flags=re.IGNORECASE) if random.random() < 0.3 else text
            text = re.sub(r'\b(oh my god)\b', 'omg', text, flags=re.IGNORECASE) if random.random() < 0.3 else text
            text = re.sub(r'\b(by the way)\b', 'btw', text, flags=re.IGNORECASE) if random.random() < 0.3 else text
            
            # Sometimes drop apostrophes (texting style) - 40% chance
            if random.random() < 0.4:
                text = re.sub(r'([a-z])\'([a-z])', r'\1\2', text)
            
            # Sometimes use run-on text with no punctuation (25% chance)
            if random.random() < 0.25:
                parts = re.split(r'([.!?] )', text)
                if len(parts) > 2:
                    idx = random.randrange(0, len(parts) - 2, 2)
                    parts[idx+1] = " "  # Remove punctuation
                    text = ''.join(parts)
        
        # Always ensure first letter is capitalized
        if text and len(text) > 0:
            text = text[0].upper() + text[1:]
            
        # Ensure text ends with punctuation
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
            
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