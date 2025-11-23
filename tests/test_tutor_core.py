import pytest
import os
import csv
from unittest.mock import MagicMock, patch
from tutor_core import ConfigManager, ProgressTracker, TutorSession

# --- ConfigManager Tests ---
def test_config_manager_load_key(tmp_path):
    api_key_file = tmp_path / "API_KEY.txt"
    api_key_file.write_text("test_api_key")
    
    config = ConfigManager(config_path=str(api_key_file))
    assert config.api_key == "test_api_key"

def test_config_manager_missing_file(tmp_path):
    config = ConfigManager(config_path=str(tmp_path / "missing.txt"))
    assert config.api_key is None

# --- ProgressTracker Tests ---
@pytest.fixture
def mock_db_path(tmp_path):
    return str(tmp_path / "test_progress.csv")

def test_progress_tracker_init_creates_db(mock_db_path):
    tracker = ProgressTracker(db_path=mock_db_path)
    assert os.path.exists(mock_db_path)
    with open(mock_db_path, 'r') as f:
        header = f.readline().strip()
        assert "timestamp,topic,mastery" in header

def test_progress_tracker_log_interaction(mock_db_path):
    tracker = ProgressTracker(db_path=mock_db_path)
    data = {'topic': 'Math', 'mastery': 8, 'notes': 'Good'}
    tracker.log_interaction(data, "Tutor response", "Test Project")
    
    with open(mock_db_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]['topic'] == 'Math'
        assert rows[0]['project_name'] == 'Test Project'

def test_progress_tracker_backup(mock_db_path):
    """Test that a backup is created when logging interaction."""
    tracker = ProgressTracker(db_path=mock_db_path)
    # First interaction to create the file
    tracker.log_interaction({'topic': 'A'}, "Resp A", "Proj A")
    
    # Second interaction should trigger backup
    tracker.log_interaction({'topic': 'B'}, "Resp B", "Proj B")
    
    backup_path = mock_db_path.replace('.csv', '_backup.csv')
    assert os.path.exists(backup_path)
    
    # Verify backup content has the first interaction
    with open(backup_path, 'r') as f:
        content = f.read()
        assert "Resp A" in content
        assert "Resp B" not in content

def test_progress_tracker_get_history(mock_db_path):
    tracker = ProgressTracker(db_path=mock_db_path)
    tracker.log_interaction({'topic': 'A', 'mastery': 1}, "Resp A", "Proj A")
    tracker.log_interaction({'topic': 'B', 'mastery': 2}, "Resp B", "Proj B")
    
    history = tracker.get_recent_history(limit=1)
    assert "Topic: B" in history
    assert "Topic: A" not in history # Should only show last 1

# --- TutorSession Tests ---
@patch('tutor_core.genai.Client')
def test_tutor_session_start(mock_client_class):
    # Mock the client and chat
    mock_client = mock_client_class.return_value
    mock_chat = MagicMock()
    mock_client.chats.create.return_value = mock_chat
    
    session = TutorSession(api_key="dummy")
    msg = session.start_session("My Project")
    
    assert "Session started" in msg
    assert session.project_name == "My Project"
    mock_client.chats.create.assert_called_once()

@patch('tutor_core.genai.Client')
def test_tutor_session_send_message(mock_client_class):
    mock_client = mock_client_class.return_value
    mock_chat = MagicMock()
    mock_chat.send_message.return_value.text = "AI Response"
    mock_client.chats.create.return_value = mock_chat
    
    session = TutorSession(api_key="dummy")
    session.start_session("My Project")
    response = session.send_message("Hello")
    
    assert response == "AI Response"
    mock_chat.send_message.assert_called_with("Hello")
