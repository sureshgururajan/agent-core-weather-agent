import os
from strands import Agent, tool
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Environment variables from AgentCore Runtime
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")

# Create the BedrockAgentCore app
app = BedrockAgentCoreApp()

@tool
def get_weather(location: str) -> dict:
    """
    Get weather information for a specific location.
    
    Args:
        location: The city or location to get weather for
        
    Returns:
        Dictionary containing weather information including temperature, condition, and humidity
    """
    # TODO: Replace with actual weather API integration
    weather_data = {
        "location": location,
        "temperature": "72°F",
        "condition": "Sunny",
        "humidity": "45%",
    }
    
    return weather_data

# Create the Strands agent with the weather tool
agent = Agent(name="WeatherAgent", tools=[get_weather])

@app.entrypoint
def invoke(payload):
    """Process user input and return a response"""
    user_message = payload.get("prompt", "")
    
    # Handle direct action calls
    if "action" in payload and payload["action"] == "get_weather":
        location = payload.get("parameters", {}).get("location", "")
        if location:
            result = get_weather(location)
            return result
    
    # Handle conversational prompts
    if user_message:
        response = agent(user_message)
        return {"response": str(response)}
    
    return {"error": "No prompt or action provided"}

if __name__ == "__main__":
    app.run()
