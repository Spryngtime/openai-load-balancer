from .load_balancer import LoadBalancer
from .openai_interface import OpenAILoadBalancer
from datetime import timedelta

DEFAULT_MODEL_ENGINE_MAPPING = {
    "gpt-4": "gpt4",
    "gpt-3.5-turbo": "gpt-35-turbo",
    "text-embedding-ada-002": "text-embedding-ada-002"
}


def initialize_load_balancer(endpoints, model_engine_mapping=DEFAULT_MODEL_ENGINE_MAPPING, failure_threshold=5, cooldown_period=timedelta(minutes=10), load_balancing_enabled=True):
    """Initializes the load balancer with the endpoint settings and other configs. 
    @param endpoints: A list of dictionaries containing the OpenAI API endpoint configurations. 
    @param model_engine_mapping: A dictionary mapping the OpenAI model names to the Azure engine names.
    @param failure_threshold: The number of consecutive failures of a request to an endpoint before the endpoint is temporarily marked as inactive
    @param cooldown_period: The minimum amount of time an endpoint is marked as inactive before it is reset to active.
    @param load_balancing_enabled: Whether or not to enable load balancing. If false, the first active endpoint will always be used, and other endpoints will only be used in case the first one fails.
    """
    load_balancer = LoadBalancer(
        endpoints,
        failure_threshold=failure_threshold,
        cooldown_period=cooldown_period,
        load_balancing_enabled=load_balancing_enabled, model_engine_mapping=model_engine_mapping
    )
    return OpenAILoadBalancer(load_balancer)
