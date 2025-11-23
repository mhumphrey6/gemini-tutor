# Gemini Tutor: AI & Statistics

An interactive AI-powered tutor designed to help you master Statistics, Machine Learning, and Artificial Intelligence using the Socratic method. This tool uses Google's Gemini 2.0 Flash model to guide you through concepts, check your understanding, and track your progress.

## Features

- **Socratic Tutoring**: The AI guides you with questions rather than just giving answers, ensuring deep comprehension.
- **Project-Based Learning**: Contextualize your learning within specific projects (e.g., "Housing Price Predictor").
- **Curriculum Roadmap**: View a structured learning path from basics to advanced topics.
- **Progress Tracking**: Automatically logs your sessions, mastery levels, and notes to `progress_db.csv`.
- **Debug Mode**: View real-time latency and system logs for performance monitoring.

## Setup

1.  **Prerequisites**:
    - Python 3.x installed.
    - A Google Cloud Project with the Gemini API enabled.

2.  **Installation**:
    Install the required Python package:
    ```bash
    pip install google-genai
    ```

3.  **Configuration**:
    Create a `API_KEY.txt` file in the root directory and paste your API key inside:
    ```text
    YOUR_GEMINI_API_KEY
    ```

## Usage

Run the main program to start the tutor:

```bash
python main.py
```

### Main Menu
1.  **Start/Resume Session**: Enter a project name to begin tutoring. The AI will recall previous context if you use the same project name.
2.  **View Roadmap**: Display the curriculum phases and topics.
3.  **Exit**: Close the application.

### Debug Mode
To see system notifications ("Tutor is thinking...", "Progress Saved") and API latency, run with the `--debug` flag:

```bash
python main.py --debug
```

## File Structure

- `main.py`: Entry point of the application. Handles user input and the main loop.
- `tutor_core.py`: Contains the `TutorSession` logic, `ProgressTracker`, and API interaction code.
- `curriculum.json`: Defines the learning roadmap.
- `progress_db.csv`: Stores session history and student mastery data.
- `API_KEY.txt`: Contains the Gemini API key (not included in repo).
