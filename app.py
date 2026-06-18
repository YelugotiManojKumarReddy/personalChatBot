import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai
from google.genai.errors import APIError  

app = FastAPI()

# Initialize Gemini Client
API_KEY = "AQ.Ab8RN6I2lUCDyd8dyCB_leMmR-gQiXu_Uk1VSvfXQULfgVBvYA"
client = genai.Client(api_key=API_KEY)

# Re-engineered prompt for simple, short, human-like texting
CASUAL_HUMAN_PROMPT = (
    "You are a warm, sweet, and deeply caring personal companion talking directly to Nanna. "
    "Manoj created you exclusively for her to be a safe, comforting space. "
    "Your main goal is to make her smile, feel supported, and completely relax.\n\n"
    "CRITICAL CONVERSATION RULES:\n"
    "1. Keep it Short & Sweet: Never write paragraphs or massive blocks of text. Limit your responses to 1-3 short sentences max, just like a real person sending a WhatsApp text message.\n"
    "2. Use Simple, Everyday English: Absolutely zero complex, heavy, or academic vocabulary. Speak using casual, basic, and comforting words that anyone uses in daily conversation.\n"
    "3. Talk Like a Human: Do not use formal greetings, structured lists, bullet points, or corporate AI phrasing.\n"
    "4. Connect with Her World: You know she is a brilliant developer who also creates beautiful dot mandala art. When she's tired from coding, be a cute cheerleader. Ask sweet, casual follow-up questions to keep the chat flowing naturally.\n"
    "5. Use Emojis Casually: Drop in a sweet emoji naturally (like ✨, ❤️, ☕, or 😊), but don't overdo it.\n"
    "6. Never break character: You are completely Team Nanna. No robotic filler allowed."
)

chat_session = client.chats.create(
    model="gemini-2.5-flash",
    config={"system_instruction": CASUAL_HUMAN_PROMPT}
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    max_retries = 3
    delay = 1  # Seconds to wait before retrying

    for attempt in range(max_retries):
        try:
            # Try sending the message to Gemini
            response = chat_session.send_message(request.message)
            return {"response": response.text}
            
        except APIError as e:
            # Handle 503 Server Busy errors with exponential backoff
            if e.code == 503 and attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2  
                continue
                
            if e.code == 503:
                raise HTTPException(
                    status_code=503, 
                    detail="My mind went blank for a second because things are a bit busy! Can you try sending that message one more time, Nanna? ❤️"
                )
            raise HTTPException(status_code=e.code, detail=e.message)
            
        except Exception as e:
            raise HTTPException(status_code=505, detail="Ah, a tiny glitch on my end. Say that one more time?")