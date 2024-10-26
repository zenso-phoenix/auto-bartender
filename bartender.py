"""IMPORT LIBRARIES"""
import RPi.GPIO as GPIO  # Required for controlling GPIO pins
import time  # Required to manage delays and wait times
from flask import Flask, request, jsonify
import os
import openai

""" OPENAI SETUP """
# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define available drinks for ChatGPT to choose from
drinks = [
    "Sex on the Beach",
    "Gin and Tonic",
    "Tom Collins",
    "Gin Sunrise",
    "Negroni",
    "Margarita",
    "Rum Punch or Mai Tai",
    "Daiquiri",
    "Mojito",
    "Vodka Cranberry or Cape Codder",
    "Sea Breeze",
    "Vodka Tonic",
    "Screwdriver",
    "Cosmopolitan or Cosmo",
    "Lemon Drop",
    "Tequila Sunrise",
    "Shirley Temple",
    "Squirtini"
]

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
            max_tokens=20
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
            
            # Mood intents
            if intent_name == "ProvideMoodIntent":
                user_mood = alexa_request['request']['intent']['slots']['mood']['value']
                return handle_mood_input(user_mood)
            elif intent_name == "UnsureIntent":
                return ask_for_mood_response()
            
            # Drink intents
            elif intent_name == "SexOnTheBeachIntent":
                return make_sex_on_the_beach_response()
            elif intent_name == "GinAndTonicIntent":
                return make_gin_and_tonic_response()
            elif intent_name == "TomCollinsIntent":
                return make_tom_collins_response()
            elif intent_name == "GinSunriseIntent":
                return make_gin_sunrise_response()
            elif intent_name == "NegroniIntent":
                return make_negroni_response()
            elif intent_name == "MargaritaIntent":
                return make_margarita_response()
            elif intent_name == "RumPunchIntent": # Rum Punch and Mai Tai utterances
                return make_rum_punch_response()
            elif intent_name == "DaquiriIntent":
                return make_daiquiri_response()
            elif intent_name == "MojitoIntent":
                return make_mojito_response()
            elif intent_name == "VodkaCranberryIntent": # Vodka Cranberry and Cape Codder utterances
                return make_vodka_cranberry_response()
            elif intent_name == "SeaBreezeIntent":
                return make_sea_breeze_response()
            elif intent_name == "VodkaTonicIntent":
                return make_vodka_tonic_response()
            elif intent_name == "ScrewdriverIntent":
                return make_screwdriver_response()
            elif intent_name == "CosmopolitanIntent": # Cosmopolitan and Cosmo utterances
                return make_cosmo_response()
            elif intent_name == "LemonDropIntent":
                return make_lemon_drop_response()
            elif intent_name == "TequilaSunriseIntent":
                return make_tequila_sunrise_response()
            elif intent_name == "ShirleyTempleIntent":
                return make_shirley_temple_response()
            elif intent_name == "SquirtiniIntent":
                return make_squirtini_response()
            else:
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
                "text": "Unknown drink."
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

    if recommended_drink in drinks:
        # Trigger the drink-making function based on the recommendation
        if recommended_drink == "Margarita":
            make_margarita()
        elif recommended_drink == "Sex on the Beach":
            make_sex_on_the_beach()
        elif recommended_drink == "Gin and Tonic":
            make_gin_and_tonic()
        elif recommended_drink == "Tom Collins":
            make_tom_collins()
        elif recommended_drink == "Gin Sunrise":
            make_gin_sunrise()
        elif recommended_drink == "Negroni":
            make_negroni()
        elif recommended_drink == "Rum Punch or Mai Tai":
            make_rum_punch()
        elif recommended_drink == "Daiquiri":
            make_daiquiri()
        elif recommended_drink == "Mojito":
            make_mojito()
        elif recommended_drink == "Vodka Cranberry or Cape Codder":
            make_vodka_cranberry()
        elif recommended_drink == "Sea Breeze":
            make_sea_breeze()
        elif recommended_drink == "Vodka Tonic":
            make_vodka_tonic()
        elif recommended_drink == "Screwdriver":
            make_screwdriver()
        elif recommended_drink == "Cosmopolitan or Cosmo":
            make_cosmo()
        elif recommended_drink == "Lemon Drop":
            make_lemon_drop()
        elif recommended_drink == "Tequila Sunrise":
            make_tequila_sunrise()
        elif recommended_drink == "Shirley Temple":
            make_shirley_temple()
        elif recommended_drink == "Squirtini":
            make_squirtini()
        else:
            # Fallback if drink not found
            make_margarita()
            recommended_drink = "Margarita"

        return jsonify({
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": f"Based on how you're feeling, I'll make a {recommended_drink}."
                },
                "shouldEndSession": True
            }
        })
    else:
        # Fallback if no drink is found
        make_margarita()
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
                "text": "No problem! How are you feeling today? Your mood can help me recommend the perfect drink."
            },
            "shouldEndSession": False
        }
    })

""" DRINKS """
# Non-route functions to make drinks

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

def make_margarita():
    try:
        dispense("rum", shot)
        dispense("lemonime", 5)
        dispense("tonic", 2)
        dispense("oj", 2)
    except Exception as e:
        print(f"Error making Margarita: {e}")

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

# Flask route handlers for drinks

@app.route('/make_sex_on_the_beach', methods=['POST'])
def make_sex_on_the_beach_response():
    make_sex_on_the_beach()
    return jsonify({"status": "Sex on the Beach is ready!"})

@app.route('/make_gin_and_tonic', methods=['POST'])
def make_gin_and_tonic_response():
    make_gin_and_tonic()
    return jsonify({"status": "Gin and Tonic is ready!"})

@app.route('/make_tom_collins', methods=['POST'])
def make_tom_collins_response():
    make_tom_collins()
    return jsonify({"status": "Tom Collins is ready!"})

@app.route('/make_gin_sunrise', methods=['POST'])
def make_gin_sunrise_response():
    make_gin_sunrise()
    return jsonify({"status": "Gin Sunrise is ready!"})

@app.route('/make_negroni', methods=['POST'])
def make_negroni_response():
    make_negroni()
    return jsonify({"status": "Negroni is ready!"})

@app.route('/make_margarita', methods=['POST'])
def make_margarita_response():
    make_margarita()
    return jsonify({"status": "Margarita is ready!"})

@app.route('/make_rum_punch', methods=['POST'])
def make_rum_punch_response():
    make_rum_punch()
    return jsonify({"status": "Rum Punch is ready!"})

@app.route('/make_daiquiri', methods=['POST'])
def make_daiquiri_response():
    make_daiquiri()
    return jsonify({"status": "Daiquiri is ready!"})

@app.route('/make_mojito', methods=['POST'])
def make_mojito_response():
    make_mojito()
    return jsonify({"status": "Mojito is ready!"})

@app.route('/make_vodka_cranberry', methods=['POST'])
def make_vodka_cranberry_response():
    make_vodka_cranberry()
    return jsonify({"status": "Vodka Cranberry is ready!"})

@app.route('/make_sea_breeze', methods=['POST'])
def make_sea_breeze_response():
    make_sea_breeze()
    return jsonify({"status": "Sea Breeze is ready!"})

@app.route('/make_vodka_tonic', methods=['POST'])
def make_vodka_tonic_response():
    make_vodka_tonic()
    return jsonify({"status": "Vodka Tonic is ready!"})

@app.route('/make_screwdriver', methods=['POST'])
def make_screwdriver_response():
    make_screwdriver()
    return jsonify({"status": "Screwdriver is ready!"})

@app.route('/make_cosmo', methods=['POST'])
def make_cosmo_response():
    make_cosmo()
    return jsonify({"status": "Cosmopolitan is ready!"})

@app.route('/make_lemon_drop', methods=['POST'])
def make_lemon_drop_response():
    make_lemon_drop()
    return jsonify({"status": "Lemon Drop is ready!"})

@app.route('/make_tequila_sunrise', methods=['POST'])
def make_tequila_sunrise_response():
    make_tequila_sunrise()
    return jsonify({"status": "Tequila Sunrise is ready!"})

@app.route('/make_shirley_temple', methods=['POST'])
def make_shirley_temple_response():
    make_shirley_temple()
    return jsonify({"status": "Shirley Temple is ready!"})

@app.route('/make_squirtini', methods=['POST'])
def make_squirtini_response():
    make_squirtini()
    return jsonify({"status": "Squirtini is ready!"})

""" START FLASK """
# Start the Flask server
if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        # Cleanup GPIO pins on shutdown
        print("Cleaning up GPIO pins...")
        GPIO.cleanup()