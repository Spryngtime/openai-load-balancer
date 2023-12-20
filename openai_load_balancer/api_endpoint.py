import threading
from datetime import datetime


class ApiEndpoint:
    def __init__(self, api_type, base_url, api_key_env, deployment, version=None):
        """Inits an API endpoint based on the passed in configuration. You can make adjustments to your configurations in config.py"""
        self.api_type = api_type
        self.base_url = base_url    
        self.api_key_env = api_key_env
        self.deployment = deployment
        self.version = version
        self.failure_count = 0
        self.last_failed_time = None
        self.lock = threading.Lock()  # Adding a lock for thread safety

    def is_active(self, failure_threshold, cooldown_period):
        """Checks if the endpoint is active. If it has failed more than failure_threshold times, it is inactive. If it is currently marked as failed with a last_failed_time within the cooldown_period, it is inactive. If the cooldown_period has passed since the last failure, the endpoint will be reset to active and returns true."""
        with self.lock:  # Ensure thread-safe read
            if self.failure_count < failure_threshold:
                return True
            if self.last_failed_time and datetime.now() - self.last_failed_time > cooldown_period:
                self.reset()
                return True
            return False

    def reset(self):
        """Resets the endpoint to active by setting failure_count to 0 and last_failed_time to None"""
        with self.lock:  # Ensure thread-safe state update
            self.failure_count = 0
            self.last_failed_time = None

    def mark_failed(self):
        """Marks the endpoint as failed by incrementing failure_count and setting last_failed_time to the current time"""
        with self.lock:  # Ensure thread-safe state update
            self.failure_count += 1
            self.last_failed_time = datetime.now()
