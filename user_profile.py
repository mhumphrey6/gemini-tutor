import json
import os

class UserProfile:
    def __init__(self, profile_path='user_profile.json'):
        self.profile_path = profile_path
        self.data = self._load_profile()

    def _load_profile(self):
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_profile(self):
        with open(self.profile_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    @property
    def name(self):
        return self.data.get('name')

    @name.setter
    def name(self, value):
        self.data['name'] = value
        self.save_profile()

    @property
    def last_project(self):
        return self.data.get('last_project')

    @last_project.setter
    def last_project(self, value):
        self.data['last_project'] = value
        self.save_profile()
