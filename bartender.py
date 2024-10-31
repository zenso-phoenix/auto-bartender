""" IMPORT LIBRARIES """
import RPi.GPIO as GPIO  # Required for controlling GPIO pins
import time  # Required to manage delays and wait times
from flask import Flask, request, jsonify
import os
import openai

""" OPENAI SETUP """
# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# List of all drinks for GPT
drinks = [
    "Sex on the Beach", "Gin and Tonic", "Tom Collins", "Gin Sunrise", "Negroni",
    "Margarita", "Rum Punch", "Daiquiri", "Mojito", "Vodka Cranberry",
    "Sea Breeze", "Vodka Tonic", "Screwdriver", "Cosmopolitan", "Lemon Drop",
    "Tequila Sunrise", "Shirley Temple", "Squirtini"
]

# Function for GPT to recommend a drink based on mood
def get_drink_recommendation(mood):
    try:
        prompt = (
            f"The user is feeling {mood}. Based on their mood, suggest one drink from this list: "
            f"{', '.join(drinks)}. Choose one drink name from the list that best suits their mood in the following format:\ndrink name"
        )
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=20
        )
        suggested_drink = response.choices[0].text.strip()
        return suggested_drink
    except Exception as e:
        print(f"Error during OpenAI request: {e}")
        return "Margarita"

""" GPIO SETUP """
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
GPIO.setwarnings(False)  # Disable warnings

# Assign GPIO pins for liquids
liquids = {
    "gin": 4, "rum": 5, "vodka": 6, "oj": 7, "cran": 8,
    "tonic": 9, "grenadine": 10, "lemonime": 11
}

# Initialize each pin as OUTPUT and set to HIGH (off state)
for pin in liquids.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
print("GPIO setup complete.")

""" FLASK APP FOR ALEXA """
app = Flask(__name__)

# Route for handling Alexa requests
@app.route('/', methods=['POST'])
def alexa_handler():
    try:
        alexa_request = request.get_json()
        request_type = alexa_request['request']['type']
        
        if request_type == "LaunchRequest":
            return launch_response()
        
        elif request_type == "IntentRequest":
            intent_name = alexa_request['request']['intent']['name']
            
            # Handle mood-based intent
            if intent_name == "ProvideMoodIntent":
                user_mood = alexa_request['request']['intent']['slots']['mood']['value']
                return handle_mood_input(user_mood)
            elif intent_name == "UnsureIntent":
                return ask_for_mood_response()
            
            # Handle drink-specific intents
            if intent_name in drink_handlers:
                return drink_handlers[intent_name]()
            
            return unknown_drink_response()  # Unknown intent fallback
            
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "version": "1.0",
            "response": {
                "outputSpeech": {"type": "PlainText", "text": "Error"},
                "shouldEndSession": True
            }
        }), 500

# Default response when Alexa launches the skill
def launch_response():
    return jsonify({
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "What would you like to drink?"
            },
            "shouldEndSession": False
        }
    })

# Response for unknown drinks
def unknown_drink_response():
    return jsonify({
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Unknown drink."
            },
            "shouldEndSession": True
        }
    })

""" BASIC FUNCTIONS """
shot = 2.2  # Duration for a standard shot (1.5 oz per 2.2 seconds)

# Function to dispense liquids
def dispense(liquid_name, seconds):
    if liquid_name in liquids:
        try:
            print(f"Dispensing {liquid_name} for {seconds} seconds.")
            GPIO.output(liquids[liquid_name], GPIO.LOW)  # Turn on pump
            time.sleep(seconds)  # Pump runs
            GPIO.output(liquids[liquid_name], GPIO.HIGH)  # Turn off pump
        except Exception as e:
            print(f"Error dispensing {liquid_name}: {e}")
    else:
        print(f"Error: {liquid_name} not found.")

""" MOOD FUNCTIONS """
# If user says "idk," system asks for mood
def ask_for_mood_response():
    return jsonify({
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "How are you feeling today? I'll make the perfect drink for your mood."
            },
            "shouldEndSession": False
        }
    })

# Input mood --> GPT recommends drink --> System makes the drink
def handle_mood_input(mood):
    recommended_drink = get_drink_recommendation(mood)

    if recommended_drink in drink_handlers:
        drink_handlers[recommended_drink]()  # Call the recommended drink function
        return jsonify({
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": f"Based on your mood, I'll make you a {recommended_drink}."
                },
                "shouldEndSession": True
            }
        })
    else:
        make_margarita()  # Fallback to Margarita
        return jsonify({
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "I'm not sure what to make based on that mood, but I'll make a Margarita!"
                },
                "shouldEndSession": True
            }
        })

""" DRINK FUNCTIONS """
def make_margarita():
    try:
        dispense("rum", shot)
        dispense("lemonime", 5)
        dispense("tonic", 2)
        dispense("oj", 2)
    except Exception as e:
        print(f"Error making Margarita: {e}")
    return jsonify({
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Your Margarita is ready!"
            },
            "shouldEndSession": True
        }
    })

def make_sex_on_the_beach():
    try:
        dispense("vodka", 3)
        dispense("rum", 3)
        dispense("gin", 3)
        dispense("oj", 10)
        dispense("cran", 5)
    except Exception as e:
        print(f"Error making Sex on the Beach: {e}")

def make_gin_and_tonic():
    try:
        dispense("gin", shot)
        dispense("tonic", 6)
    except Exception as e:
        print(f"Error making Gin and Tonic: {e}")

def make_tom_collins():
    try:
        dispense("gin", shot)
        dispense("lemonime", 5)
        dispense("tonic", 4)
    except Exception as e:
        print(f"Error making Tom Collins: {e}")

def make_gin_sunrise():
    try:
        dispense("gin", shot)
        dispense("oj", 6)
        dispense("grenadine", 2)
    except Exception as e:
        print(f"Error making Gin Sunrise: {e}")

def make_negroni():
    try:
        dispense("gin", shot)
        dispense("rum", shot)
        dispense("tonic", 3)
    except Exception as e:
        print(f"Error making Negroni: {e}")

def make_rum_punch():
    try:
        dispense("rum", 3)
        dispense("oj", 5)
        dispense("cran", 3)
        dispense("grenadine", 2)
    except Exception as e:
        print(f"Error making Rum Punch: {e}")

def make_daiquiri():
    try:
        dispense("rum", shot)
        dispense("lemonime", 5)
        dispense("tonic", 2)  # A splash of tonic to mimic club soda
    except Exception as e:
        print(f"Error making Daiquiri: {e}")

def make_mojito():
    try:
        dispense("rum", shot)
        dispense("lemonime", 5)
        dispense("tonic", 5)  # Tonic acts as a fizzy element like soda water
    except Exception as e:
        print(f"Error making Mojito: {e}")

def make_vodka_cranberry():
    try:
        dispense("vodka", shot)
        dispense("cran", 5)
    except Exception as e:
        print(f"Error making Vodka Cranberry: {e}")

def make_sea_breeze():
    try:
        dispense("vodka", shot)
        dispense("cran", 4)
        dispense("oj", 4)
    except Exception as e:
        print(f"Error making Sea Breeze: {e}")

def make_vodka_tonic():
    try:
        dispense("vodka", shot)
        dispense("tonic", 6)
    except Exception as e:
        print(f"Error making Vodka Tonic: {e}")

def make_screwdriver():
    try:
        dispense("vodka", shot)
        dispense("oj", 6)
    except Exception as e:
        print(f"Error making Screwdriver: {e}")

def make_cosmo():
    try:
        dispense("vodka", shot)
        dispense("oj", 1)
        dispense("cran", 4)
        dispense("lemonime", 3)
        dispense("grenadine", 1)  # Adds sweetness and a touch of color
    except Exception as e:
        print(f"Error making Cosmopolitan: {e}")

def make_lemon_drop():
    try:
        dispense("vodka", shot)
        dispense("lemonime", 5)
        dispense("tonic", 2)  # Adds a bit of fizz, similar to soda water
    except Exception as e:
        print(f"Error making Lemon Drop: {e}")

def make_tequila_sunrise():
    try:
        dispense("rum", shot)
        dispense("oj", 6)
        dispense("grenadine", 2)
    except Exception as e:
        print(f"Error making Tequila Sunrise: {e}")

def make_shirley_temple():
    try:
        dispense("tonic", 6)
        dispense("grenadine", 2)
    except Exception as e:
        print(f"Error making Shirley Temple: {e}")

def make_squirtini():
    try:
        for liquid in liquids.keys():
            dispense(liquid, 1)  # Dispense each for 1 second
    except Exception as e:
        print(f"Error making Squirtini: {e}")

""" ROUTE HANDLERS FOR DRINK FUNCTIONS """
# Map drink names and intents to their corresponding functions
drink_handlers = {
    "MargaritaIntent": make_margarita,
    "SexOnTheBeachIntent": make_sex_on_the_beach,
    "GinAndTonicIntent": make_gin_and_tonic,
    "TomCollinsIntent": make_tom_collins,
    "GinSunriseIntent": make_gin_sunrise,
    "NegroniIntent": make_negroni,
    "RumPunchIntent": make_rum_punch,
    "DaiquiriIntent": make_daiquiri,
    "MojitoIntent": make_mojito,
    "VodkaCranberryIntent": make_vodka_cranberry,
    "SeaBreezeIntent": make_sea_breeze,
    "VodkaTonicIntent": make_vodka_tonic,
    "ScrewdriverIntent": make_screwdriver,
    "CosmopolitanIntent": make_cosmo,
    "LemonDropIntent": make_lemon_drop,
    "TequilaSunriseIntent": make_tequila_sunrise,
    "ShirleyTempleIntent": make_shirley_temple,
    "SquirtiniIntent": make_squirtini
}

# Flask dynamic drink routing
@app.route('/make_drink/<drink_name>', methods=['POST'])
def make_drink(drink_name):
    # Make the drink name case-insensitive and replace underscores with spaces
    drink_name = drink_name

    if drink_name in drink_handlers:
        drink_handlers[drink_name]()  # Call the function
        return jsonify({"status": f"{drink_name} is ready!"})
    else:
        return jsonify({"error": "Drink not found"}), 404

""" START FLASK """
# Start the Flask server
if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        # Cleanup GPIO pins on shutdown
        print("Cleaning up GPIO pins...")
        GPIO.cleanup()
