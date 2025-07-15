import httpx

import google.genai as genai
from google.genai import types
from src.common.config import settings
from src.common.logger import get_logger


logger = get_logger(__name__)

GEMINI_API_KEY = settings.GEMINI_API_KEY


class Gemini:
    """ Service class for interacting with Gemini Pro API."""
    def __init__(self,client: genai.Client):
        self.client = client
        logger.info("Gemini client initialized")

    async def generate_website_code(self,user_input: str) -> str:
        """Generate static website code from Gemini Pro."""
        get_prompt_template = self.generate_prompt_from_payload(user_input)
        try: 
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=get_prompt_template,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=128) # Disables thinking
                    
                ),
            )
            # logger.info("Gemini response received: %s", model_text)
            return response.text
        except Exception as e:
            logger.exception("Error calling Gemini: %s", e)
            return f"Error calling Gemini: {str(e)}"

    def generate_prompt_from_payload(self, user_input: str) -> str:
        """Generate prompt from the payload."""
        return f"""
            You are an expert AI web developer.
            Your task is to generate a simple but complete static website based on the following requirements:
            {user_input}
            Please provide the HTML, CSS, and JavaScript code strictly in the output format below.
            ---
                ✅ Instructions:
                - Create a single-page responsive website.
                - Use only HTML, CSS, and minimal JavaScript if needed.
                - Include clear structure: header, main, footer.
                - Add placeholder text and cloud images if details are missing.
                - Use clean, readable indentation.
                - Write all code inline in one file.
                - Do NOT include explanations — only the final code.
                - Return the code block fenced in triple backticks with `html`, `css`, and `javascript` tags.
            ---
            Example output format:
            ```html
            <!-- Your generated HTML goes here -->
            ```css
            <!-- Your generated CSS goes here -->
            ```javascript
            <!--Your generated JavaScript goes here -->
            ```
            
        """
