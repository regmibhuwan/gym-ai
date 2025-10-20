# 🎤 GymAI Voice Logging Feature

## Overview

The voice logging feature allows users to record their workouts using audio and have them automatically transcribed and parsed into structured data using AI. This creates a seamless, hands-free workout logging experience.

## 🚀 Features Implemented

### Backend Enhancements

#### 1. Enhanced Transcribe Endpoint (`POST /transcribe`)
- **File Validation**: Checks file type and size (max 25MB)
- **Error Handling**: Comprehensive error messages for invalid files
- **Response Format**: Returns `{"text": "transcribed_text"}` instead of `{"transcript": "..."}`
- **Timeout Protection**: Handles API timeouts gracefully

#### 2. Improved Parse Workout Endpoint (`POST /parse-workout`)
- **Better GPT Prompt**: More specific instructions for workout parsing
- **Data Validation**: Validates parsed data structure and values
- **Error Handling**: Returns structured error messages
- **Response Format**: Returns single exercise with sets array
- **Weight Unit Support**: Includes weight_unit field

#### 3. New Log Workout Endpoint (`POST /log-workout`)
- **Transactional Safety**: All-or-nothing database operations
- **Session Management**: Creates new session or uses existing one
- **Complete Workflow**: Handles session → exercise → sets creation
- **User Validation**: Ensures session belongs to correct user
- **Rollback Support**: Automatic rollback on errors

### Frontend Enhancements

#### 1. Complete Voice Logging Workflow
- **Session Management**: Start/End workout sessions
- **Audio Upload**: Support for multiple audio formats (MP3, WAV, M4A, MP4, WebM)
- **Text Fallback**: Manual text input option
- **Real-time Processing**: Step-by-step workflow with progress indicators
- **Error Handling**: User-friendly error messages with retry options

#### 2. Enhanced User Experience
- **Current Session Tracking**: Shows active workout session
- **Exercise Summary**: Real-time display of logged exercises
- **Volume Calculations**: Automatic total volume computation
- **Tips Section**: Helpful guidance for better results
- **Mobile Responsive**: Works on all device sizes

#### 3. Session State Management
- **Persistent Sessions**: Maintains workout state across page refreshes
- **Exercise Tracking**: Lists all exercises in current session
- **Session Controls**: Start, end, and clear workout sessions
- **Data Validation**: Prevents invalid submissions

## 🔧 Technical Implementation

### API Endpoints

```python
# Transcribe audio to text
POST /transcribe
Content-Type: multipart/form-data
Body: audio_file (file)

Response: {"text": "bench press 3 sets 8 reps 185 pounds"}

# Parse workout text to structured data
POST /parse-workout
Content-Type: application/json
Body: {"text": "workout description"}

Response: {
  "exercise_name": "Bench Press",
  "sets": [
    {"set_number": 1, "reps": 8, "weight": 185, "weight_unit": "lbs"},
    {"set_number": 2, "reps": 7, "weight": 185, "weight_unit": "lbs"},
    {"set_number": 3, "reps": 6, "weight": 185, "weight_unit": "lbs"}
  ]
}

# Log complete workout to database
POST /log-workout
Content-Type: application/json
Body: {
  "user_id": "user123",
  "session_id": "optional_session_id",
  "exercise_name": "Bench Press",
  "sets": [...],
  "notes": "optional notes"
}

Response: {
  "session_id": "session_uuid",
  "exercise_id": "exercise_uuid",
  "sets_created": ["set_uuid1", "set_uuid2"],
  "message": "Workout logged successfully"
}
```

### GPT Prompt Template

```
You are a workout data parser. Extract exercise information from natural language.

Input: "{transcribed_text}"

Extract:
1. Exercise name (standardize: "Bench Press", "Squats", "Deadlifts", etc.)
2. Number of sets and reps for each set
3. Weight used (convert to pounds if needed)

Return ONLY valid JSON in this exact format:
{
  "exercise_name": "Exercise Name",
  "sets": [
    {"set_number": 1, "reps": 8, "weight": 185, "weight_unit": "lbs"},
    {"set_number": 2, "reps": 7, "weight": 185, "weight_unit": "lbs"}
  ]
}

If you cannot parse the input, return:
{"error": "Could not parse workout data"}
```

### Frontend Workflow

1. **Start Workout Session**
   - User clicks "Start Workout" button
   - Creates new workout session in database
   - Stores session ID in Streamlit session state

2. **Record/Input Workout**
   - User uploads audio file OR types workout description
   - Audio is transcribed using OpenAI Whisper API
   - Text is parsed using GPT-4 with structured prompt

3. **Review Parsed Data**
   - Display parsed exercise and sets in formatted table
   - Show total volume calculation
   - Allow user to confirm or retry

4. **Save Exercise**
   - Use log-workout endpoint to save complete exercise
   - Add exercise to current session summary
   - Clear inputs for next exercise

5. **End Workout Session**
   - User can end session when complete
   - Session remains in database for history viewing

## 🎯 Usage Examples

### Voice Recording Examples

**Good Examples:**
- "Bench press, 3 sets, 8 reps each, 185 pounds"
- "Squats: 4 sets x 12 reps @ 225 lbs"
- "Deadlifts, set 1: 5 reps 315, set 2: 5 reps 315, set 3: 3 reps 315"

**Text Input Examples:**
- "Did 3 sets of bench press, 10 reps at 135 lbs"
- "Squats: 3 sets x 12 reps @ 185 pounds"
- "Overhead press, 4 sets, 8 reps each, 95 pounds"

### Supported Exercise Names

The AI can recognize and standardize many exercise names:
- **Chest**: Bench Press, Push-ups, Incline Press
- **Back**: Deadlifts, Pull-ups, Rows, Lat Pulldowns
- **Legs**: Squats, Lunges, Leg Press, Calf Raises
- **Arms**: Bicep Curls, Tricep Extensions, Hammer Curls
- **Shoulders**: Overhead Press, Lateral Raises, Rear Delt Flyes

## 🚀 Getting Started

### Prerequisites

1. **OpenAI API Key**: Required for Whisper and GPT-4
2. **Backend Running**: FastAPI server on port 8000
3. **Database**: PostgreSQL or SQLite for local development

### Setup

1. **Backend Setup**:
```bash
cd gym-ai/backend
pip install -r requirements.txt
cp env.example .env
# Add your OpenAI API key to .env
python main.py
```

2. **Frontend Setup**:
```bash
cd gym-ai/frontend
pip install -r requirements.txt
streamlit run app.py
```

3. **Test Voice Logging**:
```bash
python test_voice_logging.py
```

### Environment Variables

```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@host:port/db
OPENAI_API_KEY=sk-your-openai-api-key
PORT=8000

# Frontend
API_BASE_URL=http://localhost:8000
```

## 🔍 Testing

### Manual Testing

1. **Start Backend**: `python main.py`
2. **Start Frontend**: `streamlit run app.py`
3. **Navigate to Log Workout page**
4. **Test Voice Recording**:
   - Record yourself saying: "Bench press, 3 sets, 8 reps each, 185 pounds"
   - Upload the audio file
   - Verify transcription and parsing
   - Save the exercise
5. **Test Text Input**:
   - Type: "Squats: 4 sets x 12 reps @ 225 lbs"
   - Process and verify parsing
   - Save the exercise

### Automated Testing

Run the test script:
```bash
python test_voice_logging.py
```

This will test all endpoints and verify the complete workflow.

## 🐛 Troubleshooting

### Common Issues

1. **Transcription Fails**:
   - Check audio file format (MP3, WAV, M4A supported)
   - Ensure file size < 25MB
   - Verify OpenAI API key is valid

2. **Parsing Fails**:
   - Be more specific in workout description
   - Include exercise name, sets, reps, and weight
   - Check OpenAI API credits

3. **Database Errors**:
   - Verify DATABASE_URL is correct
   - Ensure database is running
   - Check database permissions

4. **Frontend Not Loading**:
   - Verify backend is running on port 8000
   - Check API_BASE_URL environment variable
   - Look for CORS errors in browser console

### Error Messages

- `"Invalid file type"`: Upload a supported audio format
- `"File too large"`: Reduce audio file size to < 25MB
- `"No speech detected"`: Ensure audio contains clear speech
- `"Could not parse workout data"`: Try rephrasing your workout description
- `"Failed to create workout session"`: Check database connection

## 🔮 Future Enhancements

1. **Real-time Audio Recording**: Browser-based audio recording
2. **Multiple Exercise Support**: Parse multiple exercises in one input
3. **Exercise Templates**: Pre-defined workout templates
4. **Voice Commands**: "Add set", "Next exercise", etc.
5. **Offline Support**: Cache transcriptions for offline use
6. **Multi-language Support**: Support for non-English languages

## 📊 Performance

- **Transcription**: ~2-5 seconds for 30-second audio
- **Parsing**: ~1-3 seconds for workout text
- **Database**: ~100-500ms for workout logging
- **Total Workflow**: ~5-10 seconds end-to-end

## 🔒 Security

- **File Validation**: Strict file type and size limits
- **User Isolation**: Users can only access their own data
- **API Rate Limiting**: Built-in OpenAI rate limiting
- **Input Sanitization**: All inputs are validated and sanitized

---

**Built with ❤️ for the fitness community**

