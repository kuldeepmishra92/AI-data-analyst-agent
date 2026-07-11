from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import GEMINI_API_KEY

def get_llm(temperature: float = 0.0) -> ChatGoogleGenerativeAI:
    """Initialize and return the Gemini 2.5 Flash LLM client."""
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set. "
            "Please configure it in the .env file in the root directory."
        )
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=temperature
    )
