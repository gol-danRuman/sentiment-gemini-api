import google.generativeai as genai
from app.core.config import GEMINI_API_KEY

genai.configure(api_key=str(GEMINI_API_KEY))

# For safety ratings, if needed. For now, we'll keep it simple.
# generation_config = {
#     "temperature": 0.9,
#     "top_p": 1,
#     "top_k": 1,
#     "max_output_tokens": 2048,
# }

# safety_settings = [
#     {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
#     {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
#     {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
#     {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
# ]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    # generation_config=generation_config,
    # safety_settings=safety_settings
)

async def get_sentiment_from_gemini(text: str) -> tuple[str, float | None]:
    """Gets sentiment from Gemini model. Returns (sentiment_label, score)."""
    prompt = f"""Analyze the sentiment of the following text and return the sentiment label (Positive, Negative, or Neutral) and a confidence score if available. 
    If a confidence score is available, append it after a colon. For example: Positive:0.95. If not, just return the label. 
    Text: {text}
    Sentiment:"""
    
    try:
        response = await model.generate_content_async(prompt)
        result_text = response.text.strip()
        
        parts = result_text.split(':')
        sentiment_label = parts[0].strip()
        score = None
        if len(parts) > 1:
            try:
                score = float(parts[1].strip())
            except ValueError:
                pass # Score is not a float, ignore
        
        return sentiment_label, score
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # Fallback or re-raise as a custom exception
        return "Error", None 