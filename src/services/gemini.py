import httpx

import google.genai as genai
from google.genai import types
from src.common.config import settings
from src.common.logger import get_logger


logger = get_logger(__name__)

GEMINI_API_KEY = settings.GEMINI_API_KEY
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"


GENAI_CLIENT = genai.Client(
    api_key=GEMINI_API_KEY
)


async def generate_website_code(user_input: str) -> str:
    """Generate static website code from Gemini Pro."""
    get_prompt_template = generate_prompt_from_payload(user_input)
    # payload = {
    #     "contents": [{"parts": [{"text": get_prompt_template}]}]
    # }
    
    try: 
        response = GENAI_CLIENT.models.generate_content(
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

    # async with httpx.AsyncClient() as client:
    #     try:
    #         response = await client.post(
    #             GEMINI_API_URL,
    #             params=params,
    #             json=payload,
    #             timeout=60
    #         )
    #         response.raise_for_status()

    #         data = response.json()
    #         # Extract generated text from the Gemini response:
    #         model_text = (
    #             data["candidates"][0]["content"]["parts"][0]["text"]
    #             if "candidates" in data and len(data["candidates"]) > 0
    #             else ""
    #         )

    #         logger.info("Gemini response received: %s", model_text)
    #         return model_text
    #     except Exception as e:
    #         logger.exception("Error calling Gemini: %s", e)
    #         return f"Error calling Gemini: {str(e)}"
def generate_prompt_from_payload(user_input: str) -> str:
    """Generate prompt from the payload."""
    return f"""
        You are an expert AI web developer.
        Your task is to generate a simple but complete static website based on the following requirements:
        {user_input}
        Please provide the HTML, CSS, and JavaScript code.
        ---
            ✅ Instructions:
            - Create a single-page responsive website.
            - Use only HTML, CSS, and minimal JavaScript if needed.
            - Include clear structure: header, main, footer.
            - Add placeholder text and images if details are missing.
            - Use clean, readable indentation.
            - Write all code inline in one file.
            - Do NOT include explanations — only the final code.
            - Return the code block fenced in triple backticks with `html`.
        ---
        Example output format:
        ```html
        <!-- Your generated HTML goes here -->
    """
