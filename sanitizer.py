import re
import logging

# ---------------------------------------------------------
# SECURITY: SANITIZE USER INPUT FOR MALICIOUS CODE
# ---------------------------------------------------------

class InputSanitizer:
    @staticmethod
    def sanitize_city_name(city_name):
        """Sanitize city name input"""
        if not city_name or not isinstance(city_name, str):
            return None
            
        # Strip whitespace
        city_name = city_name.strip()
        
        # Check length
        if len(city_name) > 50:
            return None
            
        # Only allow letters, spaces, hyphens, apostrophes, and periods
        if re.match("^[a-zA-Z\s\-'\.]+$", city_name):
            return city_name.title()
        return None
    
    @staticmethod
    def sanitize_text_input(text, max_length=100):
        """Sanitize general text input"""
        if not text or not isinstance(text, str):
            return None
            
        text = text.strip()
        
        if len(text) > max_length:
            return None
            
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '&', '"', "'", '`', ';', '|', '$', '(', ')']
        for char in dangerous_chars:
            text = text.replace(char, '')
            
        return text
    
    @staticmethod
    def validate_day_request(user_text):
        """Validate day request input"""
        if not user_text:
            return None
            
        # Sanitize first
        sanitized = InputSanitizer.sanitize_text_input(user_text, 50)
        if not sanitized:
            return None
            
        # Check for valid day names
        valid_days = ['today', 'tomorrow', 'monday', 'tuesday', 'wednesday', 
                     'thursday', 'friday', 'saturday', 'sunday']
        
        return sanitized.lower() if sanitized.lower() in valid_days else None

# Simple functions for easy use
def sanitize_city(city_input):
    return InputSanitizer.sanitize_city_name(city_input)

def validate_text(text_input):
    return InputSanitizer.sanitize_text_input(text_input)

def validate_day(day_input):
    return InputSanitizer.validate_day_request(day_input)
