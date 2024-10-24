import RPi.GPIO as GPIO  # Required for controlling GPIO pins
import time  # Required to manage delays and wait times
from flask import Flask, request, jsonify

# Setup GPIO mode and warnings
GPIO.setmode(GPIO.BCM)  # Use BCM numbering (GPIO numbers)
GPIO.setwarnings(False)  # Disable warnings

# Assign liquids and pumps
liquids = {
    "gin": 4,
    "rum": 5,
    "vodka": 6,
    "oj": 7,  # Pineapple-orange action
    "cran": 8,
    "sprite": 9,  # Simple syrup alternative
    "grenadine": 10,  # Grenadine = (cran + grenadine) = pomegranate
    "lemonime": 11  # Lemon-lime mix for sinful bartending
}

# Set each pump pin as OUTPUT
for pin in liquids.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

print("GPIO setup complete.")

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
            
            if intent_name == "MargaritaIntent":
                return make_margarita_response()
            elif intent_name == "SexOnTheBeachIntent":
                return make_sex_on_the_beach_response()
            elif intent_name == "VodkaCranberryIntent":
                return make_vodka_cranberry_response()
            elif intent_name == "GinAndTonicIntent":
                return make_gin_and_tonic_response()
            elif intent_name == "MaiTaiIntent":
                return make_mai_tai_response()
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
                "text": "Welcome! Ask me for drink!!!"
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
                "text": "I'm sorry"
                },
                "shouldEndSession": True
            }
        })

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
shot = 2.2 # 1.5 oz. every 2.2 sec

# Test route for Margarita
@app.route('/make_margarita', methods=['POST'])
def make_margarita_response():
    try:
        dispense("rum", shot)
        dispense("lemonime", 5)
        dispense("sprite", 2)
        dispense("oj", 2)
        return jsonify({"status": "Margarita is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return 500 error if something goes wrong

# Test route for Sex on the Beach
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

# Test route for Vodka Cranberry
@app.route('/make_vodka_cranberry', methods=['POST'])
def make_vodka_cranberry_response():
    try:
        dispense("vodka", shot)
        dispense("cran", 5)
        return jsonify({"status": "Vodka cranberry is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return 500 error if something goes wrong

# Test route for Gin and Tonic
@app.route('/make_gin_and_tonic', methods=['POST'])
def make_gin_and_tonic():
    try:
        dispense("gin", shot)
        dispense("tonic", 6)
        return jsonify({"status": "Gin and tonic is ready!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return 500 error if something goes wrong

# Start the Flask server
if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        # Cleanup GPIO pins on shutdown
        print("Cleaning up GPIO pins...")
        GPIO.cleanup()