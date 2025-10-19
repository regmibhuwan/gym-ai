import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import uuid
import json
import os
from typing import Dict, List, Optional

# Page configuration
st.set_page_config(
    page_title="GymAI - AI Workout Tracker",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

if "current_session" not in st.session_state:
    st.session_state.current_session = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Helper functions
def make_api_request(endpoint: str, method: str = "GET", data: Dict = None) -> Optional[Dict]:
    """Make API request to backend"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, params=data)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

def get_workout_stats(user_id: str) -> Dict:
    """Get workout statistics for user"""
    sessions = make_api_request("/workout-sessions", data={"user_id": user_id})
    if not sessions:
        return {"total_sessions": 0, "this_week": 0, "total_volume": 0}
    
    total_sessions = len(sessions)
    
    # Calculate this week's sessions
    week_ago = datetime.now() - timedelta(days=7)
    this_week = len([s for s in sessions if datetime.fromisoformat(s["date"].replace("Z", "+00:00")) > week_ago])
    
    # Calculate total volume
    total_volume = 0
    for session in sessions:
        for exercise in session.get("exercises", []):
            for set_data in exercise.get("sets", []):
                if set_data.get("reps") and set_data.get("weight"):
                    total_volume += set_data["reps"] * set_data["weight"]
    
    return {
        "total_sessions": total_sessions,
        "this_week": this_week,
        "total_volume": total_volume
    }

# Sidebar navigation
st.sidebar.title("💪 GymAI")
st.sidebar.markdown("AI-Powered Workout Tracker")

page = st.sidebar.selectbox(
    "Navigate",
    ["Home", "Log Workout", "History", "AI Coach", "Stats"]
)

# Home Page
if page == "Home":
    st.title("Welcome to GymAI! 🏋️‍♂️")
    st.markdown("Your AI-powered workout tracking companion")
    
    # Quick stats
    stats = get_workout_stats(st.session_state.user_id)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sessions", stats["total_sessions"])
    with col2:
        st.metric("This Week", stats["this_week"])
    with col3:
        st.metric("Total Volume (lbs)", f"{stats['total_volume']:.0f}")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏋️ Log New Workout", use_container_width=True):
            st.session_state.page = "Log Workout"
            st.rerun()
    
    with col2:
        if st.button("🤖 Ask AI Coach", use_container_width=True):
            st.session_state.page = "AI Coach"
            st.rerun()
    
    # Recent workouts preview
    st.subheader("Recent Workouts")
    sessions = make_api_request("/workout-sessions", data={"user_id": st.session_state.user_id})
    
    if sessions:
        for session in sessions[:3]:  # Show last 3
            with st.expander(f"Workout - {session['date'][:10]}"):
                if session.get("notes"):
                    st.write(f"**Notes:** {session['notes']}")
                
                for exercise in session.get("exercises", []):
                    st.write(f"**{exercise['exercise_name']}**")
                    if exercise.get("sets"):
                        sets_df = pd.DataFrame(exercise["sets"])
                        st.dataframe(sets_df[["set_number", "reps", "weight"]], hide_index=True)
    else:
        st.info("No workouts yet. Start by logging your first workout!")

# Log Workout Page
elif page == "Log Workout":
    st.title("Log Your Workout 🏋️‍♂️")
    
    # Session management
    if "current_workout_session" not in st.session_state:
        st.session_state.current_workout_session = None
    
    if "current_workout_exercises" not in st.session_state:
        st.session_state.current_workout_exercises = []
    
    # Session controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.session_state.current_workout_session:
            st.success(f"✅ Active workout session started")
        else:
            st.info("No active workout session")
    
    with col2:
        if not st.session_state.current_workout_session:
            if st.button("🏋️ Start Workout", type="primary"):
                # Create new workout session
                session_data = {
                    "user_id": st.session_state.user_id,
                    "notes": f"Workout started at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }
                session_response = make_api_request("/workout-sessions", "POST", session_data)
                if session_response:
                    st.session_state.current_workout_session = session_response["id"]
                    st.session_state.current_workout_exercises = []
                    st.rerun()
    
    with col3:
        if st.session_state.current_workout_session:
            if st.button("🏁 End Workout"):
                st.session_state.current_workout_session = None
                st.session_state.current_workout_exercises = []
                st.success("Workout session ended!")
                st.rerun()
    
    st.markdown("---")
    
    # Voice recording section
    st.subheader("🎤 Voice Recording")
    st.markdown("Record yourself describing your workout, then upload the audio file.")
    
    audio_file = st.file_uploader(
        "Upload Audio File",
        type=["mp3", "wav", "m4a", "mp4", "webm"],
        help="Supported formats: MP3, WAV, M4A, MP4, WebM (max 25MB)"
    )
    
    # Text input fallback
    st.subheader("📝 Or Type Your Workout")
    workout_text = st.text_area(
        "Describe your workout in natural language",
        placeholder="Example: 'Did 3 sets of bench press, 8 reps at 185 pounds, then 3 sets of squats, 12 reps at 225 pounds'",
        height=120,
        help="Be as specific as possible: exercise name, number of sets, reps, and weight"
    )
    
    # Process workout button
    col1, col2 = st.columns([1, 1])
    
    with col1:
        process_workout = st.button("🤖 Process Workout", type="primary", use_container_width=True)
    
    with col2:
        if st.button("🔄 Clear All", use_container_width=True):
            st.session_state.current_workout_session = None
            st.session_state.current_workout_exercises = []
            st.rerun()
    
    # Process workout workflow
    if process_workout:
        if not audio_file and not workout_text.strip():
            st.error("Please provide either an audio file or text description")
        else:
            processed_text = ""
            
            # Step 1: Transcribe audio if provided
            if audio_file:
                with st.spinner("🎤 Transcribing audio..."):
                    try:
                        files = {"audio_file": audio_file}
                        response = requests.post(f"{API_BASE_URL}/transcribe", files=files, timeout=30)
                        
                        if response.status_code == 200:
                            transcript_data = response.json()
                            processed_text = transcript_data["text"]
                            st.success("✅ Audio transcribed successfully!")
                            
                            # Show transcription
                            with st.expander("📝 Transcription", expanded=True):
                                st.write(processed_text)
                        else:
                            st.error(f"❌ Transcription failed: {response.text}")
                            return
                    except requests.exceptions.RequestException as e:
                        st.error(f"❌ Transcription error: {e}")
                        return
            
            # Use text input if no audio or transcription failed
            if not processed_text:
                processed_text = workout_text.strip()
            
            # Step 2: Parse workout text
            if processed_text:
                with st.spinner("🧠 Parsing workout data..."):
                    try:
                        parsed_data = make_api_request("/parse-workout", "POST", {"text": processed_text})
                        
                        if parsed_data and "error" not in parsed_data:
                            st.success("✅ Workout parsed successfully!")
                            
                            # Display parsed data
                            st.subheader("📊 Parsed Workout Data")
                            
                            exercise_name = parsed_data.get("exercise_name", "Unknown Exercise")
                            sets_data = parsed_data.get("sets", [])
                            
                            # Create formatted table
                            if sets_data:
                                sets_df = pd.DataFrame(sets_data)
                                sets_df = sets_df[["set_number", "reps", "weight", "weight_unit"]]
                                sets_df.columns = ["Set", "Reps", "Weight", "Unit"]
                                
                                st.write(f"**Exercise:** {exercise_name}")
                                st.dataframe(sets_df, hide_index=True, use_container_width=True)
                                
                                # Calculate total volume
                                total_volume = sum(row["reps"] * row["weight"] for _, row in sets_df.iterrows())
                                st.metric("Total Volume", f"{total_volume:.0f} lbs")
                                
                                # Confirm and save button
                                col1, col2 = st.columns([1, 1])
                                
                                with col1:
                                    if st.button("💾 Save Exercise", type="primary", use_container_width=True):
                                        # Save to current session
                                        if st.session_state.current_workout_session:
                                            session_id = st.session_state.current_workout_session
                                        else:
                                            # Create new session
                                            session_data = {
                                                "user_id": st.session_state.user_id,
                                                "notes": f"Workout started at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                                            }
                                            session_response = make_api_request("/workout-sessions", "POST", session_data)
                                            if session_response:
                                                session_id = session_response["id"]
                                                st.session_state.current_workout_session = session_id
                                            else:
                                                st.error("Failed to create workout session")
                                                return
                                        
                                        # Log workout using new endpoint
                                        workout_data = {
                                            "user_id": st.session_state.user_id,
                                            "session_id": session_id,
                                            "exercise_name": exercise_name,
                                            "sets": sets_data,
                                            "notes": f"Processed from: {processed_text[:100]}..."
                                        }
                                        
                                        log_response = make_api_request("/log-workout", "POST", workout_data)
                                        
                                        if log_response:
                                            st.success("🎉 Exercise saved successfully!")
                                            
                                            # Add to current session exercises
                                            exercise_summary = {
                                                "exercise_name": exercise_name,
                                                "sets": len(sets_data),
                                                "total_volume": total_volume,
                                                "timestamp": datetime.now().strftime("%H:%M")
                                            }
                                            st.session_state.current_workout_exercises.append(exercise_summary)
                                            
                                            # Clear inputs
                                            st.rerun()
                                        else:
                                            st.error("Failed to save exercise")
                                
                                with col2:
                                    if st.button("✏️ Edit Data", use_container_width=True):
                                        st.info("Edit functionality coming soon!")
                            else:
                                st.warning("No sets data found in parsed workout")
                        else:
                            error_msg = parsed_data.get("error", "Failed to parse workout") if parsed_data else "No response from server"
                            st.error(f"❌ Parsing failed: {error_msg}")
                            
                            # Show retry option
                            if st.button("🔄 Try Again"):
                                st.rerun()
                    except Exception as e:
                        st.error(f"❌ Parsing error: {e}")
    
    # Current workout session summary
    if st.session_state.current_workout_exercises:
        st.markdown("---")
        st.subheader("📋 Current Workout Session")
        
        # Calculate session totals
        total_exercises = len(st.session_state.current_workout_exercises)
        total_volume = sum(ex["total_volume"] for ex in st.session_state.current_workout_exercises)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Exercises", total_exercises)
        with col2:
            st.metric("Total Volume", f"{total_volume:.0f} lbs")
        with col3:
            st.metric("Session ID", st.session_state.current_workout_session[:8] + "...")
        
        # Show exercises in current session
        for i, exercise in enumerate(st.session_state.current_workout_exercises):
            with st.expander(f"💪 {exercise['exercise_name']} - {exercise['timestamp']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Sets:** {exercise['sets']}")
                with col2:
                    st.write(f"**Volume:** {exercise['total_volume']:.0f} lbs")
                with col3:
                    if st.button("🗑️ Remove", key=f"remove_{i}"):
                        st.session_state.current_workout_exercises.pop(i)
                        st.rerun()
    
    # Tips section
    with st.expander("💡 Tips for Better Results"):
        st.markdown("""
        **For Voice Recording:**
        - Speak clearly and at normal pace
        - Include exercise name, sets, reps, and weight
        - Example: "Bench press, 3 sets, 8 reps each, 185 pounds"
        
        **For Text Input:**
        - Be specific about exercise names
        - Include all sets and reps
        - Mention weights clearly
        - Example: "Squats: 3 sets x 12 reps @ 225 lbs"
        
        **Supported Exercise Names:**
        - Bench Press, Squats, Deadlifts
        - Pull-ups, Push-ups, Rows
        - Overhead Press, Bicep Curls
        - And many more!
        """)

# History Page
elif page == "History":
    st.title("Workout History 📊")
    
    # Date filters
    col1, col2 = st.columns(2)
    with col1:
        date_filter = st.selectbox(
            "Filter by period",
            ["All", "This Week", "Last Week", "This Month", "Custom"]
        )
    
    with col2:
        if date_filter == "Custom":
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
    
    # Get sessions
    params = {"user_id": st.session_state.user_id}
    
    if date_filter == "This Week":
        week_ago = datetime.now() - timedelta(days=7)
        params["start_date"] = week_ago.isoformat()
    elif date_filter == "Last Week":
        two_weeks_ago = datetime.now() - timedelta(days=14)
        week_ago = datetime.now() - timedelta(days=7)
        params["start_date"] = two_weeks_ago.isoformat()
        params["end_date"] = week_ago.isoformat()
    elif date_filter == "This Month":
        month_ago = datetime.now() - timedelta(days=30)
        params["start_date"] = month_ago.isoformat()
    elif date_filter == "Custom":
        params["start_date"] = start_date.isoformat()
        params["end_date"] = end_date.isoformat()
    
    sessions = make_api_request("/workout-sessions", data=params)
    
    if sessions:
        st.subheader(f"Found {len(sessions)} workout sessions")
        
        # Export button
        if st.button("Export to CSV"):
            # Prepare data for export
            export_data = []
            for session in sessions:
                for exercise in session.get("exercises", []):
                    for set_data in exercise.get("sets", []):
                        export_data.append({
                            "Date": session["date"][:10],
                            "Exercise": exercise["exercise_name"],
                            "Set": set_data.get("set_number"),
                            "Reps": set_data.get("reps"),
                            "Weight": set_data.get("weight"),
                            "Notes": set_data.get("notes")
                        })
            
            df = pd.DataFrame(export_data)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"workout_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        # Display sessions
        for session in sessions:
            with st.expander(f"Workout - {session['date'][:10]} {session['date'][11:16]}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if session.get("notes"):
                        st.write(f"**Notes:** {session['notes']}")
                    
                    # Calculate session volume
                    session_volume = 0
                    for exercise in session.get("exercises", []):
                        exercise_volume = 0
                        st.write(f"**{exercise['exercise_name']}**")
                        
                        if exercise.get("sets"):
                            sets_data = []
                            for set_data in exercise["sets"]:
                                reps = set_data.get("reps", 0)
                                weight = set_data.get("weight", 0)
                                volume = reps * weight
                                exercise_volume += volume
                                
                                sets_data.append({
                                    "Set": set_data.get("set_number"),
                                    "Reps": reps,
                                    "Weight": weight,
                                    "Volume": volume,
                                    "Notes": set_data.get("notes", "")
                                })
                            
                            sets_df = pd.DataFrame(sets_data)
                            st.dataframe(sets_df, hide_index=True)
                            st.write(f"*Exercise Volume: {exercise_volume:.0f} lbs*")
                            session_volume += exercise_volume
                    
                    st.write(f"**Total Session Volume: {session_volume:.0f} lbs**")
                
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{session['id']}"):
                        if make_api_request(f"/workout-sessions/{session['id']}", "DELETE"):
                            st.success("Session deleted!")
                            st.rerun()
    else:
        st.info("No workout sessions found for the selected period.")

# AI Coach Page
elif page == "AI Coach":
    st.title("AI Fitness Coach 🤖")
    st.markdown("Ask me anything about your workouts, form, nutrition, or fitness goals!")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Ask your fitness question...")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("AI Coach is thinking..."):
                # Get recent workout context
                recent_sessions = make_api_request("/workout-sessions", data={"user_id": st.session_state.user_id})
                context = ""
                if recent_sessions:
                    context = f"User has {len(recent_sessions)} total workout sessions. "
                    if recent_sessions:
                        latest = recent_sessions[0]
                        context += f"Latest workout was on {latest['date'][:10]} with {len(latest.get('exercises', []))} exercises."
                
                response = make_api_request("/ai-coach", "POST", {
                    "message": user_input,
                    "user_id": st.session_state.user_id,
                    "context": context
                })
                
                if response:
                    ai_response = response["response"]
                    st.write(ai_response)
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                else:
                    st.error("Failed to get AI response")
    
    # Quick question buttons
    st.subheader("Quick Questions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💪 How's my progress?"):
            st.session_state.chat_history.append({"role": "user", "content": "How's my progress?"})
            st.rerun()
        
        if st.button("🏋️ Form tips"):
            st.session_state.chat_history.append({"role": "user", "content": "Give me some form tips"})
            st.rerun()
    
    with col2:
        if st.button("🍎 Nutrition advice"):
            st.session_state.chat_history.append({"role": "user", "content": "Give me nutrition advice"})
            st.rerun()
        
        if st.button("🎯 Goal setting"):
            st.session_state.chat_history.append({"role": "user", "content": "Help me set fitness goals"})
            st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# Stats Page
elif page == "Stats":
    st.title("Workout Statistics 📈")
    
    sessions = make_api_request("/workout-sessions", data={"user_id": st.session_state.user_id})
    
    if sessions:
        # Prepare data
        workout_data = []
        exercise_frequency = {}
        personal_records = {}
        
        for session in sessions:
            date = datetime.fromisoformat(session["date"].replace("Z", "+00:00"))
            daily_volume = 0
            
            for exercise in session.get("exercises", []):
                exercise_name = exercise["exercise_name"]
                exercise_frequency[exercise_name] = exercise_frequency.get(exercise_name, 0) + 1
                
                for set_data in exercise.get("sets", []):
                    reps = set_data.get("reps", 0)
                    weight = set_data.get("weight", 0)
                    volume = reps * weight
                    daily_volume += volume
                    
                    # Track personal records
                    if exercise_name not in personal_records:
                        personal_records[exercise_name] = {"max_weight": 0, "max_volume": 0}
                    
                    if weight > personal_records[exercise_name]["max_weight"]:
                        personal_records[exercise_name]["max_weight"] = weight
                    
                    if volume > personal_records[exercise_name]["max_volume"]:
                        personal_records[exercise_name]["max_volume"] = volume
            
            workout_data.append({
                "date": date,
                "volume": daily_volume,
                "exercises": len(session.get("exercises", []))
            })
        
        # Weekly volume chart
        st.subheader("Weekly Volume Trend")
        df = pd.DataFrame(workout_data)
        df["week"] = df["date"].dt.isocalendar().week
        df["year"] = df["date"].dt.year
        df["year_week"] = df["year"].astype(str) + "-W" + df["week"].astype(str).str.zfill(2)
        
        weekly_volume = df.groupby("year_week")["volume"].sum().reset_index()
        
        fig = px.line(weekly_volume, x="year_week", y="volume", 
                     title="Weekly Training Volume")
        fig.update_layout(xaxis_title="Week", yaxis_title="Volume (lbs)")
        st.plotly_chart(fig, use_container_width=True)
        
        # Exercise frequency
        st.subheader("Exercise Frequency")
        freq_df = pd.DataFrame(list(exercise_frequency.items()), 
                              columns=["Exercise", "Frequency"])
        freq_df = freq_df.sort_values("Frequency", ascending=True)
        
        fig = px.bar(freq_df, x="Frequency", y="Exercise", 
                    orientation="h", title="Most Performed Exercises")
        st.plotly_chart(fig, use_container_width=True)
        
        # Personal Records
        st.subheader("Personal Records")
        pr_data = []
        for exercise, records in personal_records.items():
            pr_data.append({
                "Exercise": exercise,
                "Max Weight": records["max_weight"],
                "Max Volume": records["max_volume"]
            })
        
        if pr_data:
            pr_df = pd.DataFrame(pr_data)
            pr_df = pr_df.sort_values("Max Weight", ascending=False)
            st.dataframe(pr_df, hide_index=True)
        
        # Monthly summary
        st.subheader("Monthly Summary")
        df["month"] = df["date"].dt.to_period("M")
        monthly_stats = df.groupby("month").agg({
            "volume": ["sum", "mean"],
            "exercises": "sum"
        }).round(0)
        
        monthly_stats.columns = ["Total Volume", "Avg Volume", "Total Exercises"]
        st.dataframe(monthly_stats, use_container_width=True)
    
    else:
        st.info("No workout data available. Start logging workouts to see your statistics!")

# Footer
st.markdown("---")
st.markdown("💪 **GymAI** - AI-Powered Workout Tracking | Built with Streamlit & FastAPI")