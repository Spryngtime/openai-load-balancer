import os
import dotenv
import openai
from openai_load_balancer.api_endpoint import ApiEndpoint
from tenacity import retry, wait_random_exponential, stop_after_attempt
from config import MODEL_ENGINE_MAPPING, RETRY_WAIT_RANDOM_EXPONENTIAL_MIN, RETRY_WAIT_RANDOM_EXPONENTIAL_MAX, RETRY_STOP_AFTER_ATTEMPT
import threading
dotenv.load_dotenv()


class LoadBalancer:
    def __init__(self, endpoint_configs, failure_threshold, cooldown_period, load_balancing_enabled=True):
        """Initializes the load balancer with the passed in endpoint configurations and other configs"""
        self.api_endpoints = [ApiEndpoint(**config)
                              for config in endpoint_configs]
        self.current_index = 0
        self.failure_threshold = failure_threshold
        self.cooldown_period = cooldown_period
        self.load_balancing_enabled = load_balancing_enabled
        self.lock = threading.Lock()  # Lock for thread safety

    def get_next_active_endpoint(self):
        """Gets the next active endpoint to use. If load balancing is disabled, always returns the first endpoint, unless the first endpoint is in_active, then proceeds to find the next one. If load balancing is enabled, returns the next active endpoint."""
        with self.lock:  # Acquire lock for thread-safe access
            if not self.load_balancing_enabled:
                # If load balancing is disabled, always try the first active endpoint
                if self.api_endpoints[0].is_active(self.failure_threshold, self.cooldown_period):
                    return self.api_endpoints[0]
                else:
                    # If the first endpoint is inactive, proceed to find the next active one
                    self.current_index = 1

            for _ in range(len(self.api_endpoints)):
                # get the current endpoint
                endpoint = self.api_endpoints[self.current_index]

                # Increment the current index (so the next time we call this function, we'll get the next endpoint in the list). If we've reached the end of the list, loop back to the beginning
                self.current_index = (
                    self.current_index + 1) % len(self.api_endpoints)

                if endpoint.is_active(self.failure_threshold, self.cooldown_period):
                    return endpoint

            # If we've tried all endpoints and none are active, raise an exception
            raise Exception("All endpoints are inactive.")

    @retry(wait=wait_random_exponential(min=RETRY_WAIT_RANDOM_EXPONENTIAL_MIN, max=RETRY_WAIT_RANDOM_EXPONENTIAL_MAX), stop=stop_after_attempt(RETRY_STOP_AFTER_ATTEMPT))
    def send_request(self, endpoint, method_name, **kwargs):
        """Calls OpenAI's API with the corresponding method and arguments to the passed in endpoint. If it fails, raises an exception"""
        # openai has a standard base_url, whereas for azure we'll read it from the environment variable
        openai.api_base = str(os.getenv(
            endpoint.base_url)) if endpoint.api_type == "azure" else endpoint.base_url
        openai.api_version = endpoint.version
        openai.api_key = str(os.getenv(endpoint.api_key_env))
        openai.api_type = endpoint.api_type

        # Adjust arguments for Azure
        if endpoint.api_type == "azure":
            # In Azure, instead of using the model keyword, you use the engine keyword. Get the appropriate engine name for the passed in model
            if "model" in kwargs:
                engine_name = MODEL_ENGINE_MAPPING.get(kwargs["model"])
                kwargs["engine"] = engine_name
                del kwargs["model"]
        if endpoint.api_type == "open_ai":
            # Do the same for switching from Azure engine to OpenAI model
            if "engine" in kwargs:
                # since MODEL_ENGINE_MAPPING is a dict going from model -> engine, we need to invert it to get engine -> model
                model_name = {v: k for k, v in MODEL_ENGINE_MAPPING.items()}.get(
                    kwargs["engine"])
                kwargs["model"] = model_name
                del kwargs["engine"]
        # Map method_name to the actual OpenAI function
        if method_name == 'completion_create':
            response = openai.Completion.create(**kwargs)
        elif method_name == 'chat_completion_create':
            response = openai.ChatCompletion.create(**kwargs)
        elif method_name == 'embedding_create':
            response = openai.Embedding.create(**kwargs)

        endpoint.failure_count = 0  # Reset on successful request
        return response

    def try_send_request(self, method_name, **kwargs):
        """Try to send the request to active endpoints. If it fails, mark as failed and try the next active endpoint."""
        # Keep track of attempts. If we've tried all possible endpoints, raise an exception
        attempts = 0
        while attempts < len(self.api_endpoints):
            endpoint = self.get_next_active_endpoint()

            try:
                response = self.send_request(endpoint, method_name, **kwargs)
                # Reset the endpoint on a successful request
                endpoint.reset()
                return response
            except Exception as e:
                # Mark the endpoint as failed
                endpoint.mark_failed()
                attempts += 1

        # If all endpoints have been tried and failed, raise an exception
        raise Exception("All endpoints failed.")
