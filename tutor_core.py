import os
import json
import csv
import time
import datetime
import threading
from google import genai
from google.genai import types

class ConfigManager:
    def __init__(self, config_path='API_KEY.txt'):
        self.config_path = config_path
        self.api_key = self._load_api_key()

    def _load_api_key(self):
        try:
            with open(self.config_path, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"\n[ERROR] Could not find '{self.config_path}'")
            return None

class ProgressTracker:
    def __init__(self, db_path='progress_db.csv'):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        if not os.path.isfile(self.db_path):
            with open(self.db_path, 'w', newline='') as f:
                writer = csv.writer(f)
                # Added project_name and project_status
                writer.writerow(['timestamp', 'topic', 'mastery', 'notes', 'full_ai_response', 'project_name'])

    def get_recent_history(self, limit=5):
        if not os.path.isfile(self.db_path):
            return "No prior session history."
        try:
            with open(self.db_path, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if not rows: return "No prior session history."
                
                recent = rows[-limit:]
                summary = "PREVIOUS SESSION HISTORY (Resume from here):\n"
                for row in recent:
                    topic = row.get('topic', 'General')
                    notes = row.get('notes', 'N/A')
                    project = row.get('project_name', 'None')
                    summary += f"- Topic: {topic} | Project: {project} | Notes: {notes}\n"
                return summary
        except Exception as e:
            return f"Error loading history: {e}"

    def log_interaction(self, data, tutor_text, project_name="General"):
        with self.lock:
            # Create backup before writing
            if os.path.exists(self.db_path):
                import shutil
                backup_path = self.db_path.replace('.csv', '_backup.csv')
                shutil.copy2(self.db_path, backup_path)

            with open(self.db_path, 'a', newline='') as f:
                fieldnames = ['timestamp', 'topic', 'mastery', 'notes', 'full_ai_response', 'project_name']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                entry = {
                    'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'topic': data.get('topic', 'Unknown'),
                    'mastery': data.get('mastery', 0),
                    'notes': data.get('notes', ''),
                    'full_ai_response': tutor_text,
                    'project_name': project_name
                }
                writer.writerow(entry)

class TutorSession:
    def __init__(self, api_key, model_name="gemini-2.0-flash", debug=False):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.chat = None
        self.project_name = "General"
        self.tracker = ProgressTracker()
        self.debug = debug

    def start_session(self, project_name="General"):
        self.project_name = project_name
        history_context = self.tracker.get_recent_history()
        
        system_instruction = f"""
        You are an expert AI Tutor specialized in Statistics, Machine Learning, and AI.
        
        CURRENT PROJECT: {self.project_name}
        
        PEDAGOGICAL APPROACH (SOCRATIC METHOD):
        1. Do NOT just give the answer. Guide the student with questions.
        2. Check for understanding. Ask the student to explain concepts back to you.
        3. Use analogies relevant to the student's project.
        4. If the student is stuck, provide a hint, then a stronger hint, then the solution.
        
        GOAL:
        Deep comprehension and problem-solving skills.
        
        CONTEXT:
        {history_context}
        """
        
        self.chat = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=types.Content(parts=[types.Part(text=system_instruction)])
            )
        )
        return f"Session started for project: {self.project_name}"

    def send_message(self, user_input):
        if not self.chat:
            raise ValueError("Session not started.")
        
        response = self.chat.send_message(user_input)
        return response.text

    def generate_report_card(self):
        if not self.chat:
            return "No session to report on."
            
        history = self.chat.history
        if not history:
            return "No interaction history."

        report_model = "gemini-2.0-flash"
        prompt = f"""
        Generate a Session Report Card for the student.
        Project: {self.project_name}
        
        Review the conversation history and provide:
        1. Topics Covered
        2. Mastery Assessment (1-10)
        3. Key Takeaways
        4. Recommended Homework/Next Steps
        
        Format as Markdown.
        """
        
        try:
            # Send the history as context (simplified for this implementation)
            # In a real scenario, we might send the actual history object or a summary
            response = self.client.models.generate_content(
                model=report_model,
                contents=[
                    types.Content(parts=[types.Part(text=prompt)]),
                    # We rely on the model to have context if we were continuing the chat, 
                    # but here we are using a fresh call. 
                    # Ideally we should pass the chat history.
                    # For simplicity, we'll ask the *current* chat to generate it.
                ]
            )
            # Better approach: Ask the existing chat session to generate the report
            response = self.chat.send_message(prompt)
            report_content = response.text
            
            # Save to file
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/Report_{self.project_name}_{timestamp}.md"
            os.makedirs("reports", exist_ok=True)
            
            with open(filename, "w") as f:
                f.write(report_content)
                
            return f"Report Card generated: {filename}\n\n{report_content}"
            
        except Exception as e:
            return f"Failed to generate report: {e}"

    def log_async(self, user_input, tutor_response):
        """Logs the interaction in the background."""
        thread = threading.Thread(
            target=self._analyze_and_log,
            args=(user_input, tutor_response)
        )
        thread.daemon = True
        thread.start()

    def _analyze_and_log(self, user_input, tutor_response):
        grader_model = "gemini-2.0-flash"
        prompt = f"""
        Analyze interaction. Return JSON.
        Student: "{user_input}"
        Tutor: "{tutor_response}"
        Schema: {{ "topic": str, "mastery": int, "notes": str }}
        """
        try:
            response = self.client.models.generate_content(
                model=grader_model,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            data = json.loads(response.text)
            self.tracker.log_interaction(data, tutor_response, self.project_name)
            
            if self.debug:
                print(f"\n   [System: Progress Saved for '{self.project_name}' ✓]")
        except Exception as e:
            if self.debug:
                print(f"\n   [Log Error: {e}]")
