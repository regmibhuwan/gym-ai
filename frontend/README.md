# GymAI Frontend

This is the Streamlit frontend for the GymAI workout tracking application.

## Features

- **Home Dashboard**: Quick stats and recent workouts overview
- **Voice Workout Logging**: Record workouts via audio and AI transcription
- **Text Workout Logging**: Type workout descriptions for AI parsing
- **Workout History**: View, filter, and export workout sessions
- **AI Coach**: Conversational AI assistant for fitness advice
- **Statistics**: Visual charts and personal records tracking

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export API_BASE_URL=http://localhost:8000  # Backend API URL
```

3. Run the application:
```bash
streamlit run app.py
```

## Environment Variables

- `API_BASE_URL`: Backend API URL (default: http://localhost:8000)

## Pages

### Home
- Welcome dashboard with quick stats
- Recent workouts preview
- Quick action buttons

### Log Workout
- Audio file upload for voice recording
- Text input for workout descriptions
- AI-powered workout parsing
- Real-time session tracking

### History
- Date range filtering
- Collapsible workout sessions
- Volume calculations
- CSV export functionality
- Session deletion

### AI Coach
- Chat interface with AI assistant
- Context-aware responses
- Quick question buttons
- Chat history management

### Stats
- Weekly volume trends
- Exercise frequency charts
- Personal records tracking
- Monthly summaries

## Features

- **Mobile Responsive**: Works on all device sizes
- **Dark Theme**: Modern dark UI design
- **Real-time Updates**: Live data synchronization
- **Error Handling**: Graceful error management
- **Loading States**: User-friendly loading indicators

## Development

The frontend communicates with the FastAPI backend via REST API calls.
All user data is stored in the backend database with automatic user ID generation.
