import os
import httpx # Library สำหรับส่ง HTTP Request ไปยัง n8n
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel # สำหรับกำหนดรูปแบบข้อมูล (Schema)
from dotenv import load_dotenv # สำหรับอ่านค่าจากไฟล์ .env

# โหลดตัวแปรสภาพแวดล้อมจากไฟล์ .env (N8N_SCORER_WEBHOOK และ N8N_SUMMARY_WEBHOOK)
load_dotenv()

# สร้าง Instance ของ FastAPI Application
app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (safe for localhost development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# 1. การตั้งค่า n8n Webhook URLs
# ค่าเหล่านี้จะถูกอ่านจากไฟล์ .env
# ----------------------------------------------------
# ใช้ os.getenv เพื่อดึงค่าจากไฟล์ .env หรือใช้ค่า Default ถ้าไม่พบ (ใช้ค่า Default ตามที่เรากำหนดใน .env)
N8N_SCORER_WEBHOOK = os.getenv("N8N_SCORER_WEBHOOK")
N8N_SUMMARY_WEBHOOK = os.getenv("N8N_SUMMARY_WEBHOOK")

# ตรวจสอบว่า URL ถูกโหลดมาถูกต้องหรือไม่
if not N8N_SCORER_WEBHOOK or not N8N_SUMMARY_WEBHOOK:
    print("WARNING: Webhook URLs not found in .env. Check your .env file.")

# ----------------------------------------------------
# 2. Pydantic Models (รูปแบบข้อมูลเข้า-ออก)
# ----------------------------------------------------

# รูปแบบข้อมูลที่รับเข้าเมื่อผู้ใช้กด Submit จาก Frontend
class SentenceSubmission(BaseModel):
    word: str
    sentence: str

# รูปแบบข้อมูลที่คาดว่าจะได้รับจาก n8n (AI Scoring Output)
class AIResponse(BaseModel):
    score: float
    level: str
    suggestion: str
    corrected_sentence: str

# ----------------------------------------------------
# 3. API Endpoints หลักของ Worddee.ai
# ----------------------------------------------------

# (A) Endpoint สำหรับสุ่มคำศัพท์ (Word of the Day)
@app.get("/api/word")
def get_random_word():
    """
    สุ่มคำศัพท์เพื่อใช้เป็นโจทย์ในหน้า Challenge
    """
    # ตัวอย่างคำศัพท์ที่เตรียมไว้
    words = [
        {"word": "Serendipity", "definition": "The occurrence of events by chance in a happy or beneficial way"},
        {"word": "Ephemeral", "definition": "Lasting for a very short time; transient"},
        {"word": "Eloquent", "definition": "Fluent or persuasive in speaking or writing"},
        {"word": "Pragmatic", "definition": "Dealing with things in a realistic and practical way"},
        {"word": "Melancholy", "definition": "A feeling of pensive sadness, typically with no obvious cause"},
        {"word": "Innovation", "definition": "A new method, idea, product, etc."},
        {"word": "Resilience", "definition": "The ability to recover quickly from difficulties"},
    ]
    import random
    return random.choice(words)

# (B) Endpoint สำหรับตรวจสอบประโยคและให้คะแนน AI (เชื่อมต่อไป n8n Workflow A)
@app.post("/api/score", response_model=AIResponse)
async def validate_sentence(data: SentenceSubmission):
    """
    รับประโยคผู้ใช้ ส่งไป n8n เพื่อเรียก AI ตรวจสอบ/บันทึก DB และรับผลลัพธ์กลับ
    """
    print(f"Received submission: Word='{data.word}'")
    
    # First try real n8n webhook
    if N8N_SCORER_WEBHOOK:
        try:
            # ส่ง POST Request ไปยัง Webhook ของ n8n (AI Scorer Workflow)
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(N8N_SCORER_WEBHOOK, json=data.dict())
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"n8n Webhook Error: {e}, falling back to mock")
    
    # Fallback to mock if n8n is not available
    return await mock_scorer_webhook(data)

# (C) Endpoint สำหรับดึงข้อมูลสรุป Dashboard (เชื่อมต่อไป n8n Workflow B)
@app.get("/api/summary")
async def get_dashboard_summary():
    """
    ดึงข้อมูลสถิติและประวัติการเล่นสำหรับแสดงบน Dashboard จาก n8n
    """
    try:
        # ส่ง GET Request ไปยัง Webhook ของ n8n (Dashboard Summary Workflow)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(N8N_SUMMARY_WEBHOOK)
            response.raise_for_status()
            
            # n8n จะส่ง JSON Summary กลับมา (สถิติ + ประวัติ)
            return response.json()
    except Exception as e:
        print(f"Summary Service Error: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch dashboard summary from external service.")

# ============================================================
# TEMPORARY: Mock n8n Webhooks (ใช้ชั่วคราวแทน n8n workflows)
# ============================================================
# สำหรับการพัฒนา เราจะสร้าง mock endpoints ที่ทำหน้าที่เป็น n8n webhooks
# ในอนาคต สามารถแทนที่ด้วย real n8n workflows ได้

@app.post("/webhook/scorer")
async def mock_scorer_webhook(data: SentenceSubmission):
    """
    Mock n8n Scorer Webhook - ให้คะแนนประโยคตามคุณภาพ
    ตรวจสอบ: ความยาว, คำศัพท์, ไวยากรณ์, ความชัดเจน
    (ในการใช้จริง จะเป็น n8n workflow ที่เรียก Gemini API)
    """
    try:
        sentence = data.sentence.strip()
        word = data.word.lower()
        
        # ===== การให้คะแนนแบบจริง =====
        score = 50.0  # เริ่มจาก 50
        feedback = []
        
        # 1. ตรวจสอบความยาวประโยค (ต้องมีอย่างน้อย 6 คำ)
        word_count = len(sentence.split())
        if word_count < 6:
            feedback.append("❌ ประโยคสั้นเกินไป - ใช้อย่างน้อย 6 คำ")
        elif word_count < 10:
            score += 10
            feedback.append("✓ ความยาวโอเค")
        else:
            score += 15
            feedback.append("✓ ประโยคมีความยาวที่ดี")
        
        # 2. ตรวจสอบว่ามีคำศัพท์หรือไม่ (case-insensitive)
        if word in sentence.lower():
            score += 20
            feedback.append(f"✓ ใช้คำศัพท์ '{word}' ได้ถูกต้อง")
        else:
            feedback.append(f"❌ ไม่เห็นคำศัพท์ '{word}' ในประโยค")
        
        # 3. ตรวจสอบการใช้ตัวพิมพ์ใหญ่ในตำแหน่งแรก
        if sentence[0].isupper():
            score += 5
            feedback.append("✓ ตัวพิมพ์ใหญ่ที่ต้นประโยค")
        else:
            feedback.append("❌ ต้องขึ้นต้นด้วยตัวพิมพ์ใหญ่")
        
        # 4. ตรวจสอบการใช้ลงท้ายด้วยจุด
        if sentence.endswith(('.', '!', '?')):
            score += 5
            feedback.append("✓ ลงท้ายด้วยวรรคตอนที่ถูกต้อง")
        else:
            feedback.append("❌ ต้องลงท้ายด้วยจุด, อัศเจรีย์, หรือเครื่องหมายคำถาม")
        
        # 5. ตรวจสอบความหลากหลายไวยากรณ์ (ตรวจสอบคำกริยา)
        common_verbs = ['is', 'are', 'was', 'were', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'can', 'could', 'will', 'would', 'should', 'must', 'may', 'might']
        has_verb = any(verb in sentence.lower().split() for verb in common_verbs)
        if has_verb:
            score += 15
            feedback.append("✓ ใช้กริยาได้ถูกต้อง")
        else:
            feedback.append("⚠️  ไม่มีกริยาในประโยค - ตรวจสอบไวยากรณ์")
        
        # 6. ตรวจสอบว่ามีบุพบท (Prepositions) - เพิ่มคะแนน
        prepositions = ['in', 'on', 'at', 'by', 'with', 'for', 'to', 'from', 'of', 'about', 'through', 'during']
        has_prep = any(prep in sentence.lower().split() for prep in prepositions)
        if has_prep:
            score += 10
            feedback.append("✓ ใช้บุพบทได้")
        
        # ปรับให้คะแนนไม่เกิน 100
        score = min(score, 100.0)
        score = max(score, 0.0)  # ไม่น้อยกว่า 0
        
        # กำหนด Level ตามคะแนน
        if score >= 85:
            level = "Advanced"
            suggestion = "Excellent work! Your sentence demonstrates strong command of English. " + " ".join(feedback)
        elif score >= 70:
            level = "Intermediate"
            suggestion = "Good job! You're on the right track. " + " ".join(feedback)
        else:
            level = "Beginner"
            suggestion = "Keep practicing! Review the feedback below to improve. " + " ".join(feedback)
        
        # สร้างประโยคแบบดีขึ้น (เพื่อแสดงตัวอย่าง)
        corrected_sentence = sentence
        if not word in sentence.lower():
            # ถ้าไม่มีคำศัพท์ให้สร้างตัวอย่าง
            corrected_sentence = f"I believe the {word.lower()} aspect of this is very important. {sentence}"
        
        response = {
            "score": round(score, 1),
            "level": level,
            "suggestion": suggestion,
            "corrected_sentence": corrected_sentence
        }
        
        print(f"Mock Scorer: Word='{data.word}' Sentence='{data.sentence}' Score={score:.1f} Level='{level}'")
        return response
        
    except Exception as e:
        print(f"Mock Scorer Error: {e}")
        raise HTTPException(status_code=500, detail="Scorer service error")

@app.get("/webhook/summary")
async def mock_summary_webhook():
    """
    Mock n8n Summary Webhook - ดึงสถิติและประวัติ
    (ในการใช้จริง จะเป็น n8n workflow ที่ query PostgreSQL)
    """
    try:
        # Mock Response
        summary = {
            "statistics": {
                "total_submissions": 42,
                "avg_score": 78.5,
                "max_score": 98.0,
                "min_score": 65.0
            },
            "recent_submissions": [
                {
                    "word": "Innovation",
                    "sentence": "The team showed great innovation.",
                    "score": 85.0,
                    "level": "Intermediate",
                    "timestamp": "2025-12-13T10:30:00Z"
                },
                {
                    "word": "Resilience",
                    "sentence": "She showed resilience in face of challenges.",
                    "score": 92.0,
                    "level": "Advanced",
                    "timestamp": "2025-12-13T10:25:00Z"
                }
            ]
        }
        
        print("Mock Summary: Returning dashboard statistics")
        return summary
        
    except Exception as e:
        print(f"Mock Summary Error: {e}")
        raise HTTPException(status_code=500, detail="Summary service error")

# ----------------------------------------------------
# 4. วิธีรัน FastAPI
# (รันใน Terminal เมื่ออยู่ในโฟลเดอร์ backend/ และเปิดใช้งาน venv แล้ว)
# uvicorn main:app --reload --port 8000
# ----------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
