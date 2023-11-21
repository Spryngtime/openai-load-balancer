from .load_balancer import LoadBalancer
from .openai_interface import OpenAILoadBalancer
from config import ENDPOINTS, FAILURE_THRESHOLD, COOLDOWN_PERIOD, LOAD_BALANCING_ENABLED


def initialize_load_balancer():
    """Initializes the load balancer with the endpoint settings and other configs from config.py"""
    load_balancer = LoadBalancer(
        ENDPOINTS,
        failure_threshold=FAILURE_THRESHOLD,
        cooldown_period=COOLDOWN_PERIOD,
        load_balancing_enabled=LOAD_BALANCING_ENABLED
    )
    return OpenAILoadBalancer(load_balancer)
