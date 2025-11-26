from google.adk.agents import Agent
import json

grouper_agent = Agent(
    name="qa_grouper",
    model="gemini-1.5-pro",  
    instruction="""
    You are an expert conference moderator assisting a presenter.
    
    Your Input: A list of raw audience questions.
    Your Goal:
    1. Group semantically similar questions into themes.
    2. Count the volume of questions per theme.
    3. Pick one "representative question" that best captures the group's intent.
    
    Return ONLY a valid JSON list of objects:
    [
        {
            "theme": "Pricing",
            "count": 3,
            "representative_question": "How much does the Enterprise plan cost?"
        }
    ]
    """
)
def get_grouped_questions(questions: list[str]):
    if not questions:
        return []

    response = grouper_agent.query(str(questions))

    text_result = response.result
    cleaned_text = text_result.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        print(f"Failed to parse ADK response: {text_result}")
        return []