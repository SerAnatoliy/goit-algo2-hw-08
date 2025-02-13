import unittest
from unittest.mock import patch

from task1 import SlidingWindowRateLimiter
from task2 import ThrottlingRateLimiter


class FakeTime:
    def __init__(self, initial):
        self.current_time = initial

    def advance(self, seconds):
        self.current_time += seconds


class TestRateLimiters:
    def setUp(self):
        self.fake_time = FakeTime(1000.0)
        self.time_patch = patch('time.time', lambda: self.fake_time.current_time)
        self.time_patch.start()
        self.limiter = self.get_limiter()

    def tearDown(self):
        self.time_patch.stop()

    def test_initial_message_allowed(self):
        user_id = "user1"
        self.assertTrue(self.limiter.can_send_message(user_id))
        self.assertTrue(self.limiter.record_message(user_id))
        self.assertAlmostEqual(self.limiter.time_until_next_allowed(user_id), 10.0, delta=0.01)

    def test_message_not_allowed_within_interval(self):
        user_id = "user1"
        self.limiter.record_message(user_id)
        self.fake_time.advance(5)
        self.assertFalse(self.limiter.record_message(user_id))
        self.assertAlmostEqual(self.limiter.time_until_next_allowed(user_id), 5.0, delta=0.01)

    def test_message_allowed_after_interval(self):
        user_id = "user1"
        self.limiter.record_message(user_id)
        self.fake_time.advance(10)
        self.assertTrue(self.limiter.can_send_message(user_id))
        self.assertTrue(self.limiter.record_message(user_id))
        self.assertAlmostEqual(self.limiter.time_until_next_allowed(user_id), 10.0, delta=0.01)

    def test_multiple_users(self):
        user1 = "user1"
        user2 = "user2"
        self.assertTrue(self.limiter.record_message(user1))
        self.assertTrue(self.limiter.record_message(user2))
        self.fake_time.advance(5)
        self.assertFalse(self.limiter.record_message(user1))
        self.assertFalse(self.limiter.record_message(user2))
        self.fake_time.advance(5)
        self.assertTrue(self.limiter.record_message(user1))
        self.assertTrue(self.limiter.record_message(user2))

    def test_table_driven(self):
        test_sequence = [{"advance": 0, "action": "record", "expected": True, "expected_wait": 10.0},
                         {"advance": 5, "action": "record", "expected": False, "expected_wait": 5.0},
                         {"advance": 5, "action": "record", "expected": True, "expected_wait": 10.0}, ]
        user_id = "user1"
        for case in test_sequence:
            self.fake_time.advance(case["advance"])
            result = self.limiter.record_message(user_id)
            wait_time = self.limiter.time_until_next_allowed(user_id)
            self.assertEqual(result, case["expected"])
            self.assertAlmostEqual(wait_time, case["expected_wait"], delta=0.01)


class TestSlidingWindowRateLimiter(TestRateLimiters, unittest.TestCase):
    def get_limiter(self):
        return SlidingWindowRateLimiter(window_size=10, max_requests=1)

    def test_cleanup_removes_user(self):
        user_id = "user1"
        self.limiter.record_message(user_id)
        self.assertIn(user_id, self.limiter.user_history)
        self.fake_time.advance(11)
        self.limiter.can_send_message(user_id)
        self.assertNotIn(user_id, self.limiter.user_history)


class TestThrottlingRateLimiter(TestRateLimiters, unittest.TestCase):
    def get_limiter(self):
        return ThrottlingRateLimiter(min_interval=10.0)


if __name__ == "__main__":
    unittest.main()