"""Auto-Training Distributed Learning Module"""
import json, os, requests, base64
from datetime import datetime
from gravitational_memory import CompressedMemory

class AutoTrainer:
    def __init__(self, github_token=None, repo_owner=None, repo_name="synthetic-bot"):
        self.github_token, self.repo_owner, self.repo_name = github_token or os.getenv('GITHUB_TOKEN'), repo_owner, repo_name
        self.memory, self.local_changes, self.sync_threshold = CompressedMemory(15), [], 5
    def learn_correction(self, error_type, error_msg, correction, success):
        pattern_key = f"{error_type}:{error_msg[:50]}"
        existing = self.memory.retrieve_pattern(pattern_key) or {'error_type': error_type, 'error_message': error_msg, 'correction': correction, 'count': 0, 'success_count': 0, 'first_seen': datetime.now().isoformat()}
        existing['count'] += 1
        if success: existing['success_count'] = existing.get('success_count', 0) + 1
        existing['last_seen'] = datetime.now().isoformat()
        self.memory.store_pattern(pattern_key, existing)
        self.local_changes.append({'pattern_key': pattern_key, 'data': existing, 'timestamp': datetime.now().isoformat()})
        if len(self.local_changes) >= self.sync_threshold: self.auto_sync_to_github()
    def auto_sync_to_github(self):
        if not self.github_token or not self.repo_owner: return False
        print(f"🔄 Syncing {len(self.local_changes)} patterns...")
        return True  # Simplified for demo
    def get_learning_summary(self): return {'total_patterns': self.memory.get_stats()['total_patterns'], 'pending_sync': len(self.local_changes)}
