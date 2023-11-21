# This is a Python file containing endpoint configurations
# API keys and base urls are referenced from env variables

from datetime import timedelta

ENDPOINTS = [
    {
        "api_type": "azure",
        "base_url": "AZURE_API_BASE_URL_1",
        "api_key_env": "AZURE_API_KEY_1",
        "version": "2023-05-15"
    },
    {
        "api_type": "open_ai",
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY_1",
        "version": None
    },
    # Add more configurations as needed
]

# Maps the name of OpenAI's model (e.g. gpt-3.5-turbo) to the name of the engine you've deployed in Azure (e.g. gpt-35-turbo)
MODEL_ENGINE_MAPPING = {
    "gpt-4": "gpt4",
    "gpt-3.5-turbo": "gpt-35-turbo",
    "text-embedding-ada-002": "text-embedding-ada-002"
    # Add more mappings as needed
}

# The number of consecutive failures of a request to an endpoint before the endpoint is marked as inactive
FAILURE_THRESHOLD = 5
# The minimum amount of time an endpoint is marked as inactive before it is reset to active.
COOLDOWN_PERIOD = timedelta(minutes=10)
# Whether or not to enable load balancing. If disabled, the first active endpoint will always be used, and other endpoints will only be used in case the first one fails.
LOAD_BALANCING_ENABLED = True

# Retry settings for each api call. See https://tenacity.readthedocs.io/en/latest/api.html#tenacity.retry.retry
RETRY_WAIT_RANDOM_EXPONENTIAL_MIN = 1
RETRY_WAIT_RANDOM_EXPONENTIAL_MAX = 60
RETRY_STOP_AFTER_ATTEMPT = 3
