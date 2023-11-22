# OpenAI Load Balancer

## Description

The OpenAI Load Balancer is a Python library designed to distribute API requests across multiple endpoints (supports both OpenAI and Azure). It implements a round-robin mechanism for load balancing and includes exponential backoff for retrying failed requests.

Supported OpenAI functions: ChatCompletion, Embedding, Completion (will be deprecated soon)

## Features

- **Round Robin Load Balancing**: Distributes requests evenly across a set of API endpoints.
- **Exponential Backoff**: Includes retry logic with exponential backoff for each API call.
- **Failure Detection**: Temporarily removes failed endpoints based on configurable thresholds.
- **Flexible Configuration**: Customizable settings for endpoints, failure thresholds, cooldown periods, and more.
- **Easy Integration**: Designed to be easily integrated into projects that use OpenAI's API.
- **Fallback**: If OpenAI's endpoint goes down, if your Azure endpoint is still up, then your service stays up, and vice versa.

## Installation

To install the OpenAI Load Balancer, run the following command:

```bash
pip install openai-load-balancer
```

PyPi - https://pypi.org/project/openai-load-balancer/

## Usage

First, setup your OpenAI API Endpoints. The API keys and base_url will be read from your env variable.

```python
# Example configuration

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
    }
    # Add more configurations as needed
]
```

If you are using both Azure and OpenAI, specify the mapping of the OpenAI's model name to your Azure's engine name

```python

MODEL_ENGINE_MAPPING = {
    "gpt-4": "gpt4",
    "gpt-3.5-turbo": "gpt-35-turbo",
    "text-embedding-ada-002": "text-embedding-ada-002"
    # Add more mappings as needed
}
```

Import and initialize the load balancer with the endpoints and mapping:

```python
from openai_load_balancer import initialize_load_balancer

openai_load_balancer = initialize_load_balancer(
    endpoints=ENDPOINTS, model_engine_mapping=MODEL_ENGINE_MAPPING)

```

### Making API Calls

Simply replace `openai` with `openai_load_balancer` in your function calls!:

```python
response = openai_load_balancer.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! This is a request."}
    ],
    # Additional parameters...
)
```

### Additional configurations

You can also configure the load balancer with the following variables

```python
# The number of consecutive failures of a request to an endpoint before the endpoint is temporarily marked as inactive
FAILURE_THRESHOLD = 5
# The minimum amount of time an endpoint is marked as inactive before it is reset to active.
COOLDOWN_PERIOD = timedelta(minutes=10)
# Whether or not to enable load balancing. If disabled, the first active endpoint will always be used, and other endpoints will only be used in case the first one fails.
LOAD_BALANCING_ENABLED = True
```

## Contributing

Contributions to the OpenAI Load Balancer are welcome!

## License

This project is licensed under the [MIT License](LICENSE).
