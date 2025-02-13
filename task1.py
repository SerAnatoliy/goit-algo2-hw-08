import time
from collections import deque
from typing import Dict


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_history: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        if user_id in self.user_history:
            dq = self.user_history[user_id]
            while dq and dq[0] <= current_time - self.window_size:
                dq.popleft()
            if not dq:
                del self.user_history[user_id]

    def can_send_message(self, user_id: str) -> bool:
        current_time = time.time()
        if user_id not in self.user_history:
            return True

        self._cleanup_window(user_id, current_time)
        if user_id not in self.user_history:
            return True

        dq = self.user_history[user_id]
        return len(dq) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        if self.can_send_message(user_id):
            current_time = time.time()
            if user_id not in self.user_history:
                self.user_history[user_id] = deque()
            self.user_history[user_id].append(current_time)
            return True

        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        current_time = time.time()
        if user_id not in self.user_history:
            return 0.0

        self._cleanup_window(user_id, current_time)
        if user_id not in self.user_history:
            return 0.0

        dq = self.user_history[user_id]
        if len(dq) < self.max_requests:
            return 0.0

        oldest_time = dq[0]
        wait_time = self.window_size - (current_time - oldest_time)

        return max(wait_time, 0.0)