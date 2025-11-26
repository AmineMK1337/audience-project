# backend-fastapi/app/services/gemini_client.py
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

class GeminiClient:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
            
        genai.configure(api_key=api_key)
        # Use one of the available models
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    async def analyze(self, prompt: str):
        try:
            response = await self.model.generate_content_async(prompt)
            # Simple cleanup to ensure we get a dict back
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            print(f"Gemini Error: {e}")
            return None

    def analyze_sync(self, prompt: str):
        """Synchronous version for testing"""
        try:
            response = self.model.generate_content(prompt)
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            print(f"Gemini Error: {e}")
            return None

    def list_available_models(self):
        """List all available models"""
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"Available model: {model.name}")