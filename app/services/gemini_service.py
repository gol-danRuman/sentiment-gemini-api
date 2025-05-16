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
    generation_config={
        "temperature": 0.3,  # Lower temperature for more consistent outputs
        "top_p": 0.8,
        "top_k": 40,
    }
)

async def get_sentiment_from_gemini(text: str) -> tuple[str, float | None]:
    """Gets sentiment from Gemini model. Returns (sentiment_label, score)."""
    prompt = f"""Analyze the sentiment of the following text and provide a response in this exact format:
    SENTIMENT: [Positive/Negative/Neutral]
    SCORE: [0.0 to 1.0]

    Text: {text}
    """
    
    try:
        response = await model.generate_content_async(prompt)
        result_text = response.text.strip()
        
        # Parse the response
        sentiment_label = None
        score = None
        
        for line in result_text.split('\n'):
            line = line.strip()
            if line.startswith('SENTIMENT:'):
                sentiment_label = line.replace('SENTIMENT:', '').strip()
            elif line.startswith('SCORE:'):
                try:
                    score = float(line.replace('SCORE:', '').strip())
                except ValueError:
                    score = None
        
        if not sentiment_label:
            sentiment_label = "Neutral"  # Default if parsing fails
            
        return sentiment_label, score
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "Error", None 