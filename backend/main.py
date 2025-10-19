from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
import os
import json
import logging
from datetime import datetime, timedelta
import openai
from pydantic import BaseModel
import uuid

from database import get_db, create_tables, test_connection
from models import WorkoutSession, Exercise, Set

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GymAI API",
    description="AI-powered workout tracking API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Pydantic models for request/response
class WorkoutSessionCreate(BaseModel):
    user_id: str
    notes: Optional[str] = None

class WorkoutSessionResponse(BaseModel):
    id: str
    user_id: str
    date: datetime
    notes: Optional[str]
    created_at: datetime
    exercises: List[dict] = []

    class Config:
        from_attributes = True

class ExerciseCreate(BaseModel):
    session_id: str
    exercise_name: str

class ExerciseResponse(BaseModel):
    id: str
    session_id: str
    exercise_name: str
    created_at: datetime
    sets: List[dict] = []

    class Config:
        from_attributes = True

class SetCreate(BaseModel):
    exercise_id: str
    set_number: int
    reps: Optional[int] = None
    weight: Optional[float] = None
    notes: Optional[str] = None

class SetResponse(BaseModel):
    id: str
    exercise_id: str
    set_number: int
    reps: Optional[int]
    weight: Optional[float]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class TranscribeRequest(BaseModel):
    audio_data: str  # Base64 encoded audio

class ParseWorkoutRequest(BaseModel):
    text: str

class AICoachRequest(BaseModel):
    message: str
    user_id: str
    context: Optional[str] = None

class LogWorkoutRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    exercise_name: str
    sets: List[dict]
    notes: Optional[str] = None

class LogWorkoutResponse(BaseModel):
    session_id: str
    exercise_id: str
    sets_created: List[str]
    message: str

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and test connection on startup"""
    try:
        create_tables()
        if test_connection():
            logger.info("GymAI API started successfully")
        else:
            logger.error("Failed to connect to database")
    except Exception as e:
        logger.error(f"Startup error: {e}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Workout Session endpoints
@app.post("/workout-sessions", response_model=WorkoutSessionResponse)
async def create_workout_session(
    session_data: WorkoutSessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new workout session"""
    try:
        workout_session = WorkoutSession(
            user_id=session_data.user_id,
            notes=session_data.notes
        )
        db.add(workout_session)
        db.commit()
        db.refresh(workout_session)
        
        return WorkoutSessionResponse(
            id=workout_session.id,
            user_id=workout_session.user_id,
            date=workout_session.date,
            notes=workout_session.notes,
            created_at=workout_session.created_at,
            exercises=[]
        )
    except Exception as e:
        logger.error(f"Error creating workout session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create workout session")

@app.get("/workout-sessions", response_model=List[WorkoutSessionResponse])
async def get_workout_sessions(
    user_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get workout sessions with optional filtering"""
    try:
        query = db.query(WorkoutSession)
        
        if user_id:
            query = query.filter(WorkoutSession.user_id == user_id)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(WorkoutSession.date >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(WorkoutSession.date <= end_dt)
        
        sessions = query.order_by(desc(WorkoutSession.date)).all()
        
        result = []
        for session in sessions:
            exercises_data = []
            for exercise in session.exercises:
                sets_data = [
                    {
                        "id": s.id,
                        "set_number": s.set_number,
                        "reps": s.reps,
                        "weight": s.weight,
                        "notes": s.notes,
                        "created_at": s.created_at
                    }
                    for s in exercise.sets
                ]
                exercises_data.append({
                    "id": exercise.id,
                    "exercise_name": exercise.exercise_name,
                    "created_at": exercise.created_at,
                    "sets": sets_data
                })
            
            result.append(WorkoutSessionResponse(
                id=session.id,
                user_id=session.user_id,
                date=session.date,
                notes=session.notes,
                created_at=session.created_at,
                exercises=exercises_data
            ))
        
        return result
    except Exception as e:
        logger.error(f"Error fetching workout sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch workout sessions")

@app.delete("/workout-sessions/{session_id}")
async def delete_workout_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Delete a workout session"""
    try:
        session = db.query(WorkoutSession).filter(WorkoutSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Workout session not found")
        
        db.delete(session)
        db.commit()
        return {"message": "Workout session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting workout session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete workout session")

# Exercise endpoints
@app.post("/exercises", response_model=ExerciseResponse)
async def create_exercise(
    exercise_data: ExerciseCreate,
    db: Session = Depends(get_db)
):
    """Create a new exercise"""
    try:
        # Verify session exists
        session = db.query(WorkoutSession).filter(WorkoutSession.id == exercise_data.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Workout session not found")
        
        exercise = Exercise(
            session_id=exercise_data.session_id,
            exercise_name=exercise_data.exercise_name
        )
        db.add(exercise)
        db.commit()
        db.refresh(exercise)
        
        return ExerciseResponse(
            id=exercise.id,
            session_id=exercise.session_id,
            exercise_name=exercise.exercise_name,
            created_at=exercise.created_at,
            sets=[]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating exercise: {e}")
        raise HTTPException(status_code=500, detail="Failed to create exercise")

@app.delete("/exercises/{exercise_id}")
async def delete_exercise(
    exercise_id: str,
    db: Session = Depends(get_db)
):
    """Delete an exercise"""
    try:
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")
        
        db.delete(exercise)
        db.commit()
        return {"message": "Exercise deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting exercise: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete exercise")

# Set endpoints
@app.post("/sets", response_model=SetResponse)
async def create_set(
    set_data: SetCreate,
    db: Session = Depends(get_db)
):
    """Create a new set"""
    try:
        # Verify exercise exists
        exercise = db.query(Exercise).filter(Exercise.id == set_data.exercise_id).first()
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")
        
        set_obj = Set(
            exercise_id=set_data.exercise_id,
            set_number=set_data.set_number,
            reps=set_data.reps,
            weight=set_data.weight,
            notes=set_data.notes
        )
        db.add(set_obj)
        db.commit()
        db.refresh(set_obj)
        
        return SetResponse(
            id=set_obj.id,
            exercise_id=set_obj.exercise_id,
            set_number=set_obj.set_number,
            reps=set_obj.reps,
            weight=set_obj.weight,
            notes=set_obj.notes,
            created_at=set_obj.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating set: {e}")
        raise HTTPException(status_code=500, detail="Failed to create set")

@app.delete("/sets/{set_id}")
async def delete_set(
    set_id: str,
    db: Session = Depends(get_db)
):
    """Delete a set"""
    try:
        set_obj = db.query(Set).filter(Set.id == set_id).first()
        if not set_obj:
            raise HTTPException(status_code=404, detail="Set not found")
        
        db.delete(set_obj)
        db.commit()
        return {"message": "Set deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting set: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete set")

# AI endpoints
@app.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...)
):
    """Transcribe audio to text using OpenAI Whisper"""
    try:
        if not openai.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")
        
        # Check file size (max 25MB for Whisper)
        audio_content = await audio_file.read()
        if len(audio_content) > 25 * 1024 * 1024:  # 25MB
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 25MB.")
        
        # Transcribe using OpenAI Whisper
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_content,
            response_format="text"
        )
        
        if not transcript or not transcript.strip():
            raise HTTPException(status_code=400, detail="No speech detected in audio file.")
        
        return {"text": transcript.strip()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise HTTPException(status_code=500, detail="Failed to transcribe audio")

@app.post("/parse-workout")
async def parse_workout(
    request: ParseWorkoutRequest
):
    """Parse workout text into structured data using GPT-4"""
    try:
        if not openai.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="No text provided for parsing")
        
        prompt = f"""You are a workout data parser. Extract exercise information from natural language.

Input: "{request.text}"

Extract:
1. Exercise name (standardize: "Bench Press", "Squats", "Deadlifts", etc.)
2. Number of sets and reps for each set
3. Weight used (convert to pounds if needed)

Return ONLY valid JSON in this exact format:
{{
  "exercise_name": "Exercise Name",
  "sets": [
    {{"set_number": 1, "reps": 8, "weight": 185, "weight_unit": "lbs"}},
    {{"set_number": 2, "reps": 7, "weight": 185, "weight_unit": "lbs"}}
  ]
}}

If you cannot parse the input, return:
{{"error": "Could not parse workout data"}}"""
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a workout parsing assistant. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1000
        )
        
        parsed_data = json.loads(response.choices[0].message.content)
        
        # Validate parsed data
        if "error" in parsed_data:
            raise HTTPException(status_code=400, detail=parsed_data["error"])
        
        if "exercise_name" not in parsed_data or "sets" not in parsed_data:
            raise HTTPException(status_code=400, detail="Invalid workout data format")
        
        # Validate sets data
        for i, set_data in enumerate(parsed_data["sets"]):
            if not isinstance(set_data.get("set_number"), int) or set_data.get("set_number") < 1:
                parsed_data["sets"][i]["set_number"] = i + 1
            
            if not isinstance(set_data.get("reps"), int) or set_data.get("reps") < 0:
                raise HTTPException(status_code=400, detail=f"Invalid reps in set {i+1}")
            
            if not isinstance(set_data.get("weight"), (int, float)) or set_data.get("weight") < 0:
                raise HTTPException(status_code=400, detail=f"Invalid weight in set {i+1}")
        
        return parsed_data
    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse AI response")
    except Exception as e:
        logger.error(f"Error parsing workout: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse workout")

@app.post("/log-workout", response_model=LogWorkoutResponse)
async def log_workout(
    request: LogWorkoutRequest,
    db: Session = Depends(get_db)
):
    """Log a complete workout with transactional safety"""
    try:
        # Start transaction
        session_id = request.session_id
        
        # Create new session if not provided
        if not session_id:
            workout_session = WorkoutSession(
                user_id=request.user_id,
                notes=request.notes
            )
            db.add(workout_session)
            db.commit()
            db.refresh(workout_session)
            session_id = workout_session.id
        else:
            # Verify existing session belongs to user
            existing_session = db.query(WorkoutSession).filter(
                WorkoutSession.id == session_id,
                WorkoutSession.user_id == request.user_id
            ).first()
            if not existing_session:
                raise HTTPException(status_code=404, detail="Workout session not found")
        
        # Create exercise
        exercise = Exercise(
            session_id=session_id,
            exercise_name=request.exercise_name
        )
        db.add(exercise)
        db.commit()
        db.refresh(exercise)
        
        # Create sets
        sets_created = []
        for set_data in request.sets:
            set_obj = Set(
                exercise_id=exercise.id,
                set_number=set_data.get("set_number", 1),
                reps=set_data.get("reps"),
                weight=set_data.get("weight"),
                notes=set_data.get("notes")
            )
            db.add(set_obj)
            db.commit()
            db.refresh(set_obj)
            sets_created.append(set_obj.id)
        
        return LogWorkoutResponse(
            session_id=session_id,
            exercise_id=exercise.id,
            sets_created=sets_created,
            message="Workout logged successfully"
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error logging workout: {e}")
        raise HTTPException(status_code=500, detail="Failed to log workout")

@app.post("/ai-coach")
async def ai_coach(
    request: AICoachRequest,
    db: Session = Depends(get_db)
):
    """AI coaching assistant"""
    try:
        if not openai.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Get recent workout context
        recent_sessions = db.query(WorkoutSession).filter(
            WorkoutSession.user_id == request.user_id
        ).order_by(desc(WorkoutSession.date)).limit(3).all()
        
        context = ""
        if recent_sessions:
            context = "Recent workouts:\n"
            for session in recent_sessions:
                context += f"- {session.date.strftime('%Y-%m-%d')}: {len(session.exercises)} exercises\n"
        
        prompt = f"""
        You are an AI fitness coach. Provide helpful, encouraging, and scientifically-backed advice.
        
        {context}
        
        User question: {request.message}
        
        Keep responses concise but helpful. Focus on form, progression, and motivation.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a knowledgeable and encouraging fitness coach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return {"response": response.choices[0].message.content}
    except Exception as e:
        logger.error(f"Error with AI coach: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AI coach response")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
