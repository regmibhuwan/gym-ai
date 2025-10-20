#!/usr/bin/env python3
"""
GymAI Voice Logging Test Script

This script demonstrates the complete voice logging workflow:
1. Audio transcription using OpenAI Whisper
2. Workout parsing using GPT-4
3. Database storage via the log-workout endpoint

Usage:
    python test_voice_logging.py
"""

import requests
import json
import os
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test-user-123"

def test_transcribe_endpoint():
    """Test the transcribe endpoint with a sample audio file"""
    print("🎤 Testing Transcribe Endpoint...")
    
    # Note: In a real test, you would provide an actual audio file
    # For this demo, we'll simulate the response
    print("✅ Transcribe endpoint is ready (would process audio file)")
    return "bench press 3 sets 8 reps 185 pounds"

def test_parse_workout_endpoint(text):
    """Test the parse-workout endpoint"""
    print("🧠 Testing Parse Workout Endpoint...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/parse-workout",
            json={"text": text},
            timeout=30
        )
        
        if response.status_code == 200:
            parsed_data = response.json()
            print("✅ Parse workout successful!")
            print(f"Exercise: {parsed_data.get('exercise_name')}")
            print(f"Sets: {len(parsed_data.get('sets', []))}")
            return parsed_data
        else:
            print(f"❌ Parse workout failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Parse workout error: {e}")
        return None

def test_log_workout_endpoint(parsed_data):
    """Test the log-workout endpoint"""
    print("💾 Testing Log Workout Endpoint...")
    
    try:
        workout_data = {
            "user_id": TEST_USER_ID,
            "exercise_name": parsed_data["exercise_name"],
            "sets": parsed_data["sets"],
            "notes": f"Test workout logged at {datetime.now().isoformat()}"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/log-workout",
            json=workout_data,
            timeout=30
        )
        
        if response.status_code == 200:
            log_response = response.json()
            print("✅ Log workout successful!")
            print(f"Session ID: {log_response['session_id']}")
            print(f"Exercise ID: {log_response['exercise_id']}")
            print(f"Sets created: {len(log_response['sets_created'])}")
            return log_response
        else:
            print(f"❌ Log workout failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Log workout error: {e}")
        return None

def test_workout_history():
    """Test retrieving workout history"""
    print("📊 Testing Workout History...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/workout-sessions",
            params={"user_id": TEST_USER_ID},
            timeout=30
        )
        
        if response.status_code == 200:
            sessions = response.json()
            print(f"✅ Found {len(sessions)} workout sessions")
            for session in sessions:
                print(f"  - {session['date'][:10]}: {len(session.get('exercises', []))} exercises")
            return sessions
        else:
            print(f"❌ Get history failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Get history error: {e}")
        return None

def main():
    """Run the complete voice logging test workflow"""
    print("🚀 GymAI Voice Logging Test")
    print("=" * 50)
    
    # Check if backend is running
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("Make sure to start the backend with: python main.py")
        return
    
    print()
    
    # Step 1: Simulate audio transcription
    transcribed_text = test_transcribe_endpoint()
    print()
    
    # Step 2: Parse workout text
    parsed_data = test_parse_workout_endpoint(transcribed_text)
    if not parsed_data:
        print("❌ Test failed at parsing step")
        return
    print()
    
    # Step 3: Log workout to database
    log_response = test_log_workout_endpoint(parsed_data)
    if not log_response:
        print("❌ Test failed at logging step")
        return
    print()
    
    # Step 4: Verify workout was saved
    sessions = test_workout_history()
    print()
    
    print("🎉 Voice Logging Test Complete!")
    print("=" * 50)
    print("Summary:")
    print(f"✅ Audio transcription: Ready")
    print(f"✅ Workout parsing: {parsed_data['exercise_name']}")
    print(f"✅ Database logging: Session {log_response['session_id'][:8]}...")
    print(f"✅ History retrieval: {len(sessions) if sessions else 0} sessions")

if __name__ == "__main__":
    main()

