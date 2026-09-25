import json
import os
from datetime import datetime
from typing import Dict, Any, List

DB_FILE = "bot_data.json"

class Database:
    def __init__(self, file_path: str = DB_FILE):
        self.file_path = file_path
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "posted_news": [],
            "posted_education": [],
            "education_progress": {"day": 1, "phase": 1},
            "subscribers": [],
            "stats": {"total_posts": 0, "news_posts": 0, "education_posts": 0},
            "last_calendar_check": None,
            "last_news_post": None
        }

    def _save(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def is_news_posted(self, news_id: str) -> bool:
        return news_id in self.data["posted_news"]

    def mark_news_posted(self, news_id: str):
        if news_id not in self.data["posted_news"]:
            self.data["posted_news"].append(news_id)
            # keep only last 500
            self.data["posted_news"] = self.data["posted_news"][-500:]
            self.data["stats"]["news_posts"] += 1
            self.data["stats"]["total_posts"] += 1
            self._save()

    def is_education_posted(self, edu_id: str) -> bool:
        return edu_id in self.data["posted_education"]

    def mark_education_posted(self, edu_id: str):
        if edu_id not in self.data["posted_education"]:
            self.data["posted_education"].append(edu_id)
            self.data["posted_education"] = self.data["posted_education"][-500:]
            self.data["stats"]["education_posts"] += 1
            self.data["stats"]["total_posts"] += 1
            self._save()

    def get_education_progress(self) -> Dict:
        return self.data["education_progress"]

    def update_education_progress(self, day: int, phase: int = None):
        self.data["education_progress"]["day"] = day
        if phase:
            self.data["education_progress"]["phase"] = phase
        self._save()

    def next_education_day(self):
        current = self.data["education_progress"]["day"]
        next_day = current + 1
        # loop after 30 days
        if next_day > 60:
            next_day = 1
        self.data["education_progress"]["day"] = next_day
        # update phase based on day
        if next_day <= 7:
            self.data["education_progress"]["phase"] = 1
        elif next_day <= 16:
            self.data["education_progress"]["phase"] = 2
        elif next_day <= 22:
            self.data["education_progress"]["phase"] = 3
        else:
            self.data["education_progress"]["phase"] = 4
        self._save()
        return next_day

    def get_stats(self):
        return self.data["stats"]

    def set_last_calendar_check(self):
        self.data["last_calendar_check"] = datetime.now().isoformat()
        self._save()

    def set_last_news_post(self):
        self.data["last_news_post"] = datetime.now().isoformat()
        self._save()

db = Database()
