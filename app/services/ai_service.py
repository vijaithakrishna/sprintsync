from datetime import datetime, timezone
from app.config import settings

STUB_RESPONSE = {
    "suggestion": (
        "Implement and test the described feature following "
        "existing code conventions. Add input validation, "
        "error handling, and relevant unit tests."
    ),
    "model": "stub",
    "generated_at": None,
}


async def generate_suggestion(title: str) -> dict:
    now = datetime.now(timezone.utc)

    print(f"DEBUG: AI_MODE = {settings.AI_MODE}")

    if settings.AI_MODE == "stub":
        return {**STUB_RESPONSE, "generated_at": now}

    try:
        from groq import Groq

        client = Groq(api_key=settings.GROQ_API_KEY)

        print(f"DEBUG: Calling Groq API...")
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior software engineer writing sprint card descriptions. "
                        "Given a short task title, return a clear, actionable 2-3 sentence "
                        "engineering description. Be specific and use technical language. "
                        "Do not repeat the title in your response."
                    )
                },
                {
                    "role": "user",
                    "content": f"Task title: {title}"
                }
            ],
            max_tokens=150,
            temperature=0.4,
        )

        suggestion = response.choices[0].message.content.strip()
        print(f"DEBUG: Got response: {suggestion[:80]}")

        return {
            "suggestion": suggestion,
            "model": "llama-3.1-8b-instant",
            "generated_at": now,
        }

    except Exception as exc:
        print(f"DEBUG: Groq error = {type(exc).__name__}: {str(exc)}")
        return {
            "suggestion": "AI unavailable. Please describe this task manually.",
            "model": "fallback",
            "generated_at": now,
        }