"""IMPORT LIBRARIES"""
import RPi.GPIO as GPIO  # Required for controlling GPIO pins
import time  # Required to manage delays and wait times
from flask import Flask, request, jsonify
import os
import openai

""" OPENAI SETUP """
# Set up OpenAI API key

"""
Bash: echo 'export OPENAI_API_KEY="your-openai-api-key"' >> ~/.bashrc
Note: it may be ~/.bash_profile on some systems
Bash: source ~/.bashrc
"""
openai.api_key = os.getenv("OPENAI_API_KEY")

# Unified dictionary mapping drink names and intents to their corresponding functions
drink_handlers = {
    "Margarita": make_margarita_response,
    "Sex on the Beach": make_sex_on_the_beach_response,
    "Gin and Tonic": make_gin_and_tonic_response,
    "Tom Collins": make_tom_collins_response,
    "Gin Sunrise": make_gin_sunrise_response,
    "Negroni": make_negroni_response,
    "Rum Punch or Mai Tai": make_rum_punch_response,
    "Daiquiri": make_daiquiri_response,
    "Mojito": make_mojito_response,
    "Vodka Cranberry or Cape Codder": make_vodka_cranberry_response,
    "Sea Breeze": make_sea_breeze_response,
    "Vodka Tonic": make_vodka_tonic_response,
    "Screwdriver": make_screwdriver_response,
    "Cosmopolitan or Cosmo": make_cosmo_response,
    "Lemon Drop": make_lemon_drop_response,
    "Tequila Sunrise": make_tequila_sunrise_response,
    "Shirley Temple": make_shirley_temple_response,
    "Squirtini": make_squirtini_response,
    # Additional mappings for Alexa intents directly
    "ProvideMoodIntent": handle_mood_input,
    "UnsureIntent": ask_for_mood_response
}
# Filter `drink_handlers` to extract only drink names (exclude "Intent" entries)
drinks = [name for name in drink_handlers.keys() if "Intent" not in name]

# Drink recommendation function based on mood parameter
def get_drink_recommendation(mood):
    try:
        prompt = (
            f"The user is feeling {mood}. Based on their mood, suggest one drink from this list: "
            f"{', '.join(drinks)}. Provide the name of the one drink that best suits their mood in the following format:\n[drink]"
        )
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=30,
            temperature=0.7
        )
        suggested_drink = response.choices[0].text.strip()
        return suggested_drink
    except Exception as e:
        print(f"Error during OpenAI request: {e}")
        return "Margarita"

""" GPIO SETUP """
# Setup GPIO mode and warnings
GPIO.setmode(GPIO.BCM)  # Use BCM numbering (GPIO numbers)
GPIO.setwarnings(False)  # Disable warnings

# Assign liquids and pumps
liquids = {
    "gin": 4,
    "rum": 5, # Swap out for tequila for margaritas
    "vodka": 6,
    "oj": 7,  # Pineapple-orange action
    "cran": 8,
    "tonic": 9, # Can replace with sprite if ur fat
    "grenadine": 10,  # Grenadine = (cran + grenadine) = pomegranate, right?
    "lemonime": 11  # Lemon-lime mix for sinful bartending
}

# Set each pump pin as OUTPUT
for pin in liquids.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

print("GPIO setup complete.")

""" ALEXA SETUP """
# Flask app to listen for Alexa requests
app = Flask(__name__)

# Test code for Alexa
@app.route('/', methods=['POST'])
def alexa_handler():
    try:
        alexa_request = request.get_json()
        request_type = alexa_request['request']['type']
        
        if request_type == "LaunchRequest":
            return launch_response()
        
        elif request_type == "IntentRequest":
            intent_name = alexa_request['request']['intent']['name']
            
            # Check if the intent name exists in the unified dictionary
            if intent_name in drink_handlers:
                # Handle mood-based intent separately to pass the mood parameter
                if intent_name == "ProvideMoodIntent":
                    user_mood = alexa_request['request']['intent']['slots']['mood']['value']
                    return drink_handlers[intent_name](user_mood)  # Pass mood to handle_mood_input
                else:
                    return drink_handlers[intent_name]()  # Call function directly for drink intents
            
            # Unknown intent fallback
            return unknown_drink_response()
            
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Error"
                },
                "shouldEndSession": True
            }
        }), 500
            
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

def unknown_drink_response():
    return jsonify({
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Squirtle. Squirtiddy, squirt, squirt!"
                },
                "shouldEndSession": True
            }
        })

""" BASIC FUNCTIONS + VARIABLES """
# Function to dispense liquids
def dispense(liquid_name, seconds):
    if liquid_name in liquids:
        try:
            print(f"Dispensing {liquid_name} for {seconds} seconds.")
            GPIO.output(liquids[liquid_name], GPIO.LOW)  # Turn on liquid pump
            time.sleep(seconds)  # Pump flows for assigned seconds
            GPIO.output(liquids[liquid_name], GPIO.HIGH)  # Turn off liquid pump
        except Exception as e:
            print(f"Error while dispensing {liquid_name}: {e}")
    else:
        print(f"Error: {liquid_name} not found.")

# Shot variable
shot = 2.2 # 1.5 oz. every 2.2 sec according to math

# Mood response function
def handle_mood_input(mood):
    recommended_drink = get_drink_recommendation(mood)
    
    if recommended_drink in drink_handlers:
        # Call the function associated with the recommended drink
        drink_handlers[recommended_drink]()  # Calls the function
        return jsonify({
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": f"Based on how you're feeling, I'll make you {recommended_drink}."
                },
                "shouldEndSession": True
            }
        })
    else:
        # Fallback if no valid drink is found
        return jsonify({
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "I'm not sure what to make based on that mood, but how about a Margarita instead?"
                },
                "shouldEndSession": True
            }
        })

# Ask for mood if user says "idk"
def ask_for_mood_response():
    return jsonify({
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "No problem! How are you feeling today?"
            },
            "shouldEndSession": False
        }
    })

""" DRINKS """
# Sex on the Beach
@app.route('/make_sex_on_the_beach', methods=['POST'])
def make_sex_on_the_beach_response():
    try:
        dispense("vodka", 3)
        dispense("rum", 3)
        dispense("gin", 3)
        dispense("oj", 10)
        dispense("cran", 5)
        return jsonify({"status": "Sex on the Beach is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return 500 error if something goes wrong

# Gin and Tonic
@app.route('/make_gin_and_tonic', methods=['POST'])
def make_gin_and_tonic_response():
    try:
        dispense("gin", shot)
        dispense("tonic", 6)
        return jsonify({"status": "Gin and tonic is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return 500 error if something goes wrong
    
# Tom Collins
@app.route('/make_tom_collins', methods=['POST'])
def make_tom_collins_response():
    try:
        dispense("gin", shot)
        dispense("lemonime", 5)
        dispense("tonic", 4)
        return jsonify({"status": "Tom Collins is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Gin Sunrise
@app.route('/make_gin_sunrise', methods=['POST'])
def make_gin_sunrise_response():
    try:
        dispense("gin", shot)
        dispense("oj", 6)
        dispense("grenadine", 2)
        return jsonify({"status": "Gin Sunrise is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Negroni
@app.route('/make_negroni', methods=['POST'])
def make_negroni_response():
    try:
        dispense("gin", shot)
        dispense("rum", shot)
        dispense("tonic", 3)
        return jsonify({"status": "Negroni is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Margarita
@app.route('/make_margarita', methods=['POST'])
def make_margarita_response():
    try:
        dispense("rum", shot)
        dispense("lemonime", 5)
        dispense("tonic", 2)
        dispense("oj", 2)
        return jsonify({"status": "Margarita is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return 500 error if something goes wrong

# Rum Punch or Mai Tai
@app.route('/make_rum_punch', methods=['POST'])
def make_rum_punch_response():
    try:
        dispense("rum", 3)
        dispense("oj", 5)
        dispense("cran", 3)
        dispense("grenadine", 2)
        return jsonify({"status": "Rum Punch is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Daiquiri (better w sprite)
@app.route('/make_daiquiri', methods=['POST'])
def make_daiquiri_response():
    try:
        dispense("rum", shot)
        dispense("lemonime", 5)
        dispense("tonic", 2)  # A splash of tonic to mimic club soda
        return jsonify({"status": "Daiquiri is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Mojito (add mint)
@app.route('/make_mojito', methods=['POST'])
def make_mojito_response():
    try:
        dispense("rum", shot)
        dispense("lemonime", 5)
        dispense("tonic", 5)  # Tonic acts as a fizzy element like soda water
        return jsonify({"status": "Mojito is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vodka Cranberry or Cape Codder
@app.route('/make_vodka_cranberry', methods=['POST'])
def make_vodka_cranberry_response():
    try:
        dispense("vodka", shot)
        dispense("cran", 5)
        return jsonify({"status": "Vodka cranberry is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return 500 error if something goes wrong

# Sea Breeze
@app.route('/make_sea_breeze', methods=['POST'])
def make_sea_breeze_response():
    try:
        dispense("vodka", shot)
        dispense("cran", 4)
        dispense("oj", 4)
        return jsonify({"status": "Sea Breeze is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vodka Tonic
@app.route('/make_vodka_tonic', methods=['POST'])
def make_vodka_tonic_response():
    try:
        dispense("vodka", shot)
        dispense("tonic", 6)
        return jsonify({"status": "Vodka Tonic is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Screwdriver
@app.route('/make_screwdriver', methods=['POST'])
def make_screwdriver_response():
    try:
        dispense("vodka", shot)
        dispense("oj", 6)
        return jsonify({"status": "Screwdriver is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Cosmopolitan or Cosmo
@app.route('/make_cosmo', methods=['POST'])
def make_cosmo_response():
    try:
        dispense("vodka", shot)
        dispense("cran", 4)
        dispense("lemonime", 3)
        dispense("grenadine", 1)  # Adds sweetness and a touch of color
        return jsonify({"status": "Cosmopolitan is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Lemon Drop
@app.route('/make_lemon_drop', methods=['POST'])
def make_lemon_drop_response():
    try:
        dispense("vodka", shot)
        dispense("lemonime", 5)
        dispense("tonic", 2)  # Adds a bit of fizz, similar to soda water
        return jsonify({"status": "Lemon Drop is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Tequila Sunrise (with rum substitute)
@app.route('/make_tequila_sunrise', methods=['POST'])
def make_tequila_sunrise_response():
    try:
        dispense("rum", shot)
        dispense("oj", 6)
        dispense("grenadine", 2)
        return jsonify({"status": "Tequila Sunrise is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Shirley Temple
@app.route('/make_shirley_temple', methods=['POST'])
def make_shirley_temple_response():
    try:
        dispense("tonic", 6)
        dispense("grenadine", 2)
        return jsonify({"status": "Shirley Temple is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Squirtini (everything)
@app.route('/make_squirtini', methods=['POST'])
def make_squirtini_response():
    try:
        for liquid in liquids.keys():
            dispense(liquid, 1)  # Dispense each for 1 second
        return jsonify({"status": "Squirtini is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

""" START FLASK """
# Start the Flask server
if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        # Cleanup GPIO pins on shutdown
        print("Cleaning up GPIO pins...")
        GPIO.cleanup()