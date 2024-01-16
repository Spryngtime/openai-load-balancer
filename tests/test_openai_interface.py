import pytest
from unittest.mock import Mock
from openai_load_balancer.openai_interface import OpenAILoadBalancer


@pytest.fixture
def mock_load_balancer():
    mock = Mock()
    return mock


@pytest.fixture
def openai_load_balancer(mock_load_balancer):
    return OpenAILoadBalancer(mock_load_balancer)


def test_chat_completion_create(openai_load_balancer, mock_load_balancer):
    test_kwargs = {"messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ], "model": "gpt-3.5-turbo"}
    openai_load_balancer.ChatCompletion.create(**test_kwargs)
    mock_load_balancer.try_send_request.assert_called_once_with(
        'chat_completion_create', **test_kwargs)


def test_completion_create(openai_load_balancer, mock_load_balancer):
    test_kwargs = {"prompt": "Hello", "model": "text-davinci-003"}
    openai_load_balancer.Completion.create(**test_kwargs)
    mock_load_balancer.try_send_request.assert_called_once_with(
        'completion_create', **test_kwargs)


def test_embedding_create(openai_load_balancer, mock_load_balancer):
    test_kwargs = {"input": "Hello", "model": "text-embedding-ada-002"}
    openai_load_balancer.Embedding.create(**test_kwargs)
    mock_load_balancer.try_send_request.assert_called_once_with(
        'embedding_create', **test_kwargs)
