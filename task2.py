import time
from typing import Dict


class ThrottlingRateLimiter:
    def __init__(self, min_interval: float = 10.0):
        self.min_interval = min_interval
        self.last_message: Dict[str, float] = {}

    def can_send_message(self, user_id: str) -> bool:
        current_time = time.time()
        if user_id not in self.last_message:
            return True

        return (current_time - self.last_message[user_id]) >= self.min_interval

    def record_message(self, user_id: str) -> bool:
        if self.can_send_message(user_id):
            self.last_message[user_id] = time.time()
            return True

        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        current_time = time.time()
        if user_id not in self.last_message:
            return 0.0

        remaining = self.min_interval - (current_time - self.last_message[user_id])

        return max(remaining, 0.0)