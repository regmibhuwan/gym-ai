# GymAI Backend

This is the FastAPI backend for the GymAI workout tracking application.

## Features

- RESTful API for workout session management
- PostgreSQL database with SQLAlchemy ORM
- OpenAI integration for voice transcription and AI coaching
- Automatic database table creation
- Health check endpoint
- CORS support for frontend integration

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your actual values
```

3. Run the application:
```bash
python main.py
```

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for Whisper and GPT-4
- `PORT`: Server port (default: 8000)

## API Endpoints

### Workout Sessions
- `POST /workout-sessions` - Create new session
- `GET /workout-sessions` - List sessions (with filters)
- `DELETE /workout-sessions/{id}` - Delete session

### Exercises
- `POST /exercises` - Add exercise to session
- `DELETE /exercises/{id}` - Delete exercise

### Sets
- `POST /sets` - Add set to exercise
- `DELETE /sets/{id}` - Delete set

### AI Features
- `POST /transcribe` - Transcribe audio to text
- `POST /parse-workout` - Parse workout text to structured data
- `POST /ai-coach` - AI coaching assistant

### Health
- `GET /health` - Health check

## Database Schema

- `workout_sessions`: Main workout sessions
- `exercises`: Exercises within sessions
- `sets`: Individual sets for exercises

## Development

The application uses SQLite for local development if no DATABASE_URL is provided.
For production, use PostgreSQL with proper connection pooling.

