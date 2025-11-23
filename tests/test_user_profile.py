import pytest
import json
import os
from user_profile import UserProfile

@pytest.fixture
def mock_profile_file(tmp_path):
    """Creates a temporary profile file."""
    file_path = tmp_path / "test_user_profile.json"
    return str(file_path)

def test_user_profile_init_no_file(mock_profile_file):
    """Test initialization when file does not exist."""
    profile = UserProfile(profile_path=mock_profile_file)
    assert profile.data == {}
    assert profile.name is None
    assert profile.last_project is None

def test_user_profile_init_with_file(mock_profile_file):
    """Test initialization with existing file."""
    data = {"name": "Test User", "last_project": "Test Project"}
    with open(mock_profile_file, 'w') as f:
        json.dump(data, f)
    
    profile = UserProfile(profile_path=mock_profile_file)
    assert profile.name == "Test User"
    assert profile.last_project == "Test Project"

def test_user_profile_save_name(mock_profile_file):
    """Test saving name persists to file."""
    profile = UserProfile(profile_path=mock_profile_file)
    profile.name = "New User"
    
    # Verify in memory
    assert profile.name == "New User"
    
    # Verify on disk
    with open(mock_profile_file, 'r') as f:
        data = json.load(f)
    assert data['name'] == "New User"

def test_user_profile_save_last_project(mock_profile_file):
    """Test saving last_project persists to file."""
    profile = UserProfile(profile_path=mock_profile_file)
    profile.last_project = "New Project"
    
    # Verify in memory
    assert profile.last_project == "New Project"
    
    # Verify on disk
    with open(mock_profile_file, 'r') as f:
        data = json.load(f)
    assert data['last_project'] == "New Project"

def test_user_profile_corrupt_file(mock_profile_file):
    """Test handling of corrupt JSON file."""
    with open(mock_profile_file, 'w') as f:
        f.write("{corrupt json")
        
    profile = UserProfile(profile_path=mock_profile_file)
    assert profile.data == {}
