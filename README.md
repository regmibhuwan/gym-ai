# GymAI - AI-Powered Workout Tracker 💪

A comprehensive workout tracking application that combines voice recognition, AI parsing, and intelligent coaching to revolutionize your fitness journey.

## 🚀 Features

### Core Functionality
- **Voice Workout Logging**: Record workouts via audio and get AI transcription
- **Text Workout Logging**: Type workout descriptions for intelligent parsing
- **Workout History**: View, filter, and export your training sessions
- **AI Fitness Coach**: Get personalized advice and motivation
- **Statistics & Analytics**: Track progress with visual charts and personal records

### Technical Highlights
- **Pure Python Stack**: No JavaScript/React complexity
- **AI Integration**: OpenAI Whisper for transcription, GPT-4 for parsing and coaching
- **Modern UI**: Dark theme with mobile-responsive design
- **Real-time Updates**: Live data synchronization
- **Export Capabilities**: CSV export for data portability

## 🏗️ Architecture

```
gym-ai/
├── backend/          # FastAPI REST API
│   ├── main.py      # API endpoints & AI integration
│   ├── models.py    # Database models (SQLAlchemy)
│   ├── database.py  # Database configuration
│   └── requirements.txt
├── frontend/        # Streamlit web app
│   ├── app.py       # Main application
│   ├── .streamlit/  # Configuration
│   └── requirements.txt
└── render.yaml      # Deployment configuration
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Python-based UI)
- **Backend**: FastAPI (REST API)
- **Database**: PostgreSQL (via Render)
- **AI Services**: OpenAI (Whisper + GPT-4)
- **Deployment**: Render (both frontend and backend)

## 🚀 Quick Start

### Local Development

1. **Clone and Setup**
```bash
git clone <repository-url>
cd gym-ai
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
cp env.example .env
# Edit .env with your OpenAI API key
python main.py
```

3. **Frontend Setup**
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

4. **Access the App**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Production Deployment (Render)

1. **Database Setup**
   - Create PostgreSQL database on Render
   - Note the DATABASE_URL

2. **Backend Deployment**
   - Connect GitHub repository
   - Set environment variables:
     - `DATABASE_URL`: Your PostgreSQL URL
     - `OPENAI_API_KEY`: Your OpenAI API key
   - Deploy from `backend/` directory

3. **Frontend Deployment**
   - Deploy from `frontend/` directory
   - Set environment variable:
     - `API_BASE_URL`: Your backend URL

## 📱 Usage

### Logging Workouts
1. **Voice Method**: Record yourself describing your workout, upload the audio file
2. **Text Method**: Type your workout description in natural language
3. **AI Processing**: The app transcribes/parses your input into structured data
4. **Review & Save**: Confirm the parsed data and save to your history

### AI Coach
- Ask questions about form, nutrition, progress, or goal setting
- Get context-aware responses based on your workout history
- Use quick question buttons for common topics

### Statistics
- View weekly volume trends
- Track exercise frequency
- Monitor personal records
- Export data for external analysis

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
OPENAI_API_KEY=sk-your-openai-key
PORT=8000
```

**Frontend**
```bash
API_BASE_URL=http://localhost:8000  # Backend URL
```

### OpenAI Setup
1. Get API key from https://platform.openai.com/
2. Add to environment variables
3. Ensure sufficient credits for Whisper and GPT-4 usage

## 📊 Database Schema

- **workout_sessions**: Main workout sessions with notes and timestamps
- **exercises**: Individual exercises within sessions
- **sets**: Sets with reps, weight, and notes for each exercise

## 🎯 Why This Architecture?

### Streamlit Benefits
- **Pure Python**: No frontend framework complexity
- **Built-in Components**: File upload, audio recording, charts
- **Rapid Development**: Fast prototyping and iteration
- **Mobile Responsive**: Works on all devices
- **Easy Deployment**: One-click deployment to cloud platforms

### FastAPI Benefits
- **High Performance**: Async support and automatic validation
- **Auto Documentation**: Interactive API docs
- **Type Safety**: Pydantic models for data validation
- **Modern Python**: Uses latest Python features

## 🔮 Future Enhancements

- **User Authentication**: Multi-user support with accounts
- **Social Features**: Share workouts and compete with friends
- **Advanced Analytics**: Machine learning insights
- **Mobile App**: Native mobile application
- **Integration**: Connect with fitness trackers and wearables
- **Nutrition Tracking**: Meal planning and macro tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for Whisper and GPT-4 APIs
- Streamlit team for the amazing framework
- FastAPI for the high-performance backend
- Render for easy deployment platform

---

**Built with ❤️ for the fitness community**
