import os
from openai import OpenAI
import threading

""" OPENAI SETUP """
# Set up OpenAI API key
client = OpenAI(
    api_key=

# List of all drinks for GPT
drinks = [
    "SexOnTheBeach", "GinAndTonic", "TomCollins", "GinSunrise", "Negroni",
    "Margarita", "RumPunch", "Daiquiri", "Mojito", "VodkaCranberry",
    "SeaBreeze", "VodkaTonic", "Screwdriver", "Cosmopolitan", "LemonDrop",
    "TequilaSunrise", "ShirleyTemple", "Squirtini"
]

def get_drink_recommendation(mood):
    """
    Get a drink recommendation based on user's mood.
    
    Args:
        mood (str): The user's current mood
        
    Returns:
        str: Recommended drink name from the drinks list
    """
    if not isinstance(mood, str):
        raise ValueError("Mood must be a string")
        
    if not mood.strip():
        raise ValueError("Mood cannot be empty")
        
    try:
        if not client.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
            
        prompt = (
            f"The user is feeling {mood}. Based on their mood, suggest one drink from this list:\n"
            f"{', '.join(drinks)}.\nChoose one drink name from the list that best suits their mood in the following format:\ndrink name"
        )
        
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=20,
            temperature=0.7  # Added for more consistent outputs
        )
        
        suggested_drink = completion.choices[0].message.content.strip()
        
        # Validate that the suggested drink is in our list
        if suggested_drink not in drinks:
            print(f"Warning: GPT suggested '{suggested_drink}' which is not in our drinks list")
            return "Margarita"  # Default fallback
            
        return suggested_drink
        
    except Exception as e:
        print(f"Error during OpenAI request: {e}")
        return "Margarita"  # Default fallback

# Example usage
if __name__ == "__main__":
    try:
        mood = "Squirtle"
        recommendation = get_drink_recommendation(mood)
        print(f"Recommended drink for {mood} mood: {recommendation}")
    except Exception as e:
        print(f"Error: {e}")