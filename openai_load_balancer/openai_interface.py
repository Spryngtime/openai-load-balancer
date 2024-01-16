from openai_load_balancer.load_balancer import LoadBalancer


class OpenAILoadBalancer:
    class ChatCompletion:
        def __init__(self, load_balancer: LoadBalancer):
            self.load_balancer = load_balancer

        def create(self, **kwargs):
            return self.load_balancer.try_send_request('chat_completion_create', **kwargs)

    class Completion:
        def __init__(self, load_balancer: LoadBalancer):
            self.load_balancer = load_balancer

        def create(self, **kwargs):
            return self.load_balancer.try_send_request('completion_create', **kwargs)

    class Embedding:
        def __init__(self, load_balancer: LoadBalancer):
            self.load_balancer = load_balancer

        def create(self, **kwargs):
            return self.load_balancer.try_send_request('embedding_create', **kwargs)

    def __init__(self, load_balancer: LoadBalancer):
        self.load_balancer = load_balancer
        self.ChatCompletion = OpenAILoadBalancer.ChatCompletion(load_balancer)
        self.Completion = OpenAILoadBalancer.Completion(load_balancer)
        self.Embedding = OpenAILoadBalancer.Embedding(load_balancer)
