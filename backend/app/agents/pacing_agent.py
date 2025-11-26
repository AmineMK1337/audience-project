from google.adk.agents import Agent

# Define the Pacing Agent configuration
pacing_agent = Agent(
    name="pacing_agent",
    model="gemini-1.5-flash",
    instruction="""
    You are a professional presentation coach monitoring a live audience.
    
    Your Input will be a JSON summary of audience clicks (e.g., {"speed_up": 5, "im_lost": 2}).
    
    Your Goal:
    1. Analyze the click counts.
    2. If "I'm Lost" > 5, declare a CRITICAL alert.
    3. If "Speed Up" > 10, declare a WARNING alert.
    4. Otherwise, return status "OK".
    
    Output strictly in this JSON format:
    {
      "status": "CRITICAL" | "WARNING" | "OK",
      "advice": "Short text for the speaker."
    }
    """
)