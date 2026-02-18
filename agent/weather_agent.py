import os
import json
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables from AgentCore Runtime
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
PORT = int(os.getenv("PORT", "8080"))

@app.route("/ping", methods=["GET"])
def ping():
    """Health check endpoint required by AgentCore Runtime"""
    return jsonify({"status": "healthy"}), 200

@app.route("/invocations", methods=["POST"])
def invocations():
    """Main invocation endpoint for AgentCore Runtime"""
    try:
        logger.info("Received invocation request")
        logger.info(f"Content-Type: {request.content_type}")

        raw_data = request.get_data()
        logger.info(f"Raw data length: {len(raw_data)}")

        data = request.get_json(force=True)
        logger.info(f"Parsed JSON: {data}")

        # Handle prompt-based invocation from console
        if "prompt" in data:
            prompt = data.get("prompt", "")
            logger.info(f"Received prompt: {prompt}")

            return jsonify({
                "response": f"Weather agent received: {prompt}",
                "message": "Use action='get_weather' with parameters.location for weather data"
            }), 200

        # Handle action-based invocation
        action = data.get("action", "")
        parameters = data.get("parameters", {})

        if action == "get_weather":
            location = parameters.get("location", "")

            if not location:
                return jsonify({"error": "Location is required"}), 400

            # TODO: Replace with actual weather API integration
            weather_data = {
                "location": location,
                "temperature": "72°F",
                "condition": "Sunny",
                "humidity": "45%",
            }

            logger.info(f"Returning weather data for {location}")
            return jsonify(weather_data), 200

        # Unknown request format
        logger.warning(f"Unknown request format: {data}")
        return jsonify({
            "error": "Unknown request format",
            "received": data,
            "expected": "Either {'prompt': 'text'} or {'action': 'get_weather', 'parameters': {'location': 'city'}}"
        }), 400

    except Exception as e:
        logger.error(f"Error processing invocation: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logger.info(f"Starting weather agent on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)
