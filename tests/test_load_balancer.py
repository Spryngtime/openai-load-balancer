from datetime import timedelta
import pytest
from unittest.mock import patch, create_autospec, Mock
from openai_load_balancer.load_balancer import LoadBalancer
from openai_load_balancer.api_endpoint import ApiEndpoint


@pytest.fixture
def load_balancer():
    endpoint_configs = [
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
    ]
    FAILURE_THRESHOLD = 5
    COOLDOWN_PERIOD = timedelta(minutes=10)

    return LoadBalancer(endpoint_configs, failure_threshold=FAILURE_THRESHOLD, cooldown_period=COOLDOWN_PERIOD)


def test_round_robin(load_balancer):
    first_endpoint = load_balancer.get_next_active_endpoint()
    second_endpoint = load_balancer.get_next_active_endpoint()
    assert first_endpoint != second_endpoint


def test_100_round_robin(load_balancer):
    # create 100 mock endpoints
    mock_endpoints = [create_autospec(
        ApiEndpoint, instance=True) for _ in range(100)]
    # configure all mock endpoints to be active
    for mock_endpoint in mock_endpoints:
        mock_endpoint.is_active.return_value = True
    # replace actual endpoints with mock endpoints
    load_balancer.api_endpoints = mock_endpoints
    # test getting the next active endpoint 100 times, and assert that it's the next endpoint as we expect
    for i in range(100):
        next_endpoint = load_balancer.get_next_active_endpoint()
        assert next_endpoint == mock_endpoints[i]


@patch('openai_load_balancer.load_balancer.LoadBalancer.send_request')
def test_handle_endpoint_failure(mock_send_request, load_balancer):
    # Create separate mock instances for each endpoint
    mock_endpoint1 = create_autospec(ApiEndpoint, instance=True)
    mock_endpoint2 = create_autospec(ApiEndpoint, instance=True)
    mock_endpoint3 = create_autospec(ApiEndpoint, instance=True)

    # Configure the first endpoint to simulate a failure
    mock_endpoint1.is_active.return_value = True
    mock_endpoint1.mark_failed = Mock()

    # Configure the second endpoint to simulate success
    mock_endpoint2.is_active.return_value = True
    mock_endpoint2.mark_failed = Mock()

    # Configure the third endpoint (should not be used in this test)
    mock_endpoint3.is_active.return_value = True
    mock_endpoint3.mark_failed = Mock()

    # Replace actual endpoints with mocks
    load_balancer.api_endpoints = [
        mock_endpoint1, mock_endpoint2, mock_endpoint3]

    # Setup mock for send_request
    mock_send_request.side_effect = [Exception("Failed request"), "Success"]

    # Make a request - it should fail on the first endpoint and succeed on the second
    result = load_balancer.try_send_request('test_method', test_arg='value')

    # Assert that the send_request was called twice (once for each endpoint)
    assert mock_send_request.call_count == 2
    assert result == "Success"
    assert mock_endpoint1.mark_failed.called
    assert not mock_endpoint3.mark_failed.called


@patch('openai_load_balancer.load_balancer.LoadBalancer.send_request')
def test_all_endpoints_failure(mock_send_request, load_balancer):
    # Create a list of mock endpoints
    mock_endpoints = [create_autospec(ApiEndpoint, instance=True) for _ in range(
        len(load_balancer.api_endpoints))]

    # Configure all mock endpoints to simulate failure
    for mock_endpoint in mock_endpoints:
        mock_endpoint.is_active.return_value = True
        mock_endpoint.mark_failed = Mock()

    # Replace actual endpoints with mock endpoints
    load_balancer.api_endpoints = mock_endpoints

    # Setup mock for send_request to always raise an exception
    mock_send_request.side_effect = Exception("Failed request")

    # Attempt to make a request, expecting it to raise an exception
    with pytest.raises(Exception) as excinfo:
        load_balancer.try_send_request('test_method', test_arg='value')

    # Assert that the exception message is as expected
    assert str(excinfo.value) == "All endpoints failed."

    # Assert that mark_failed was called on each endpoint
    for mock_endpoint in mock_endpoints:
        assert mock_endpoint.mark_failed.called


def test_load_balancing_disabled(load_balancer):
    """Test that when load balancing is disabled, the LoadBalancer always tries the first endpoint unless it's inactive."""
    load_balancer.load_balancing_enabled = False
    first_endpoint = load_balancer.get_next_active_endpoint()

    # test getting the next active endpoint 10 times
    for _ in range(10):
        next_endpoint = load_balancer.get_next_active_endpoint()
        assert next_endpoint == first_endpoint


def test_load_balancing_disabled_tries_next_endpoint(load_balancer):
    """Test that when load balancing is disabled, the LoadBalancer tries the next endpoint if the first one is inactive."""
    # Create mock endpoints
    mock_endpoint1 = create_autospec(ApiEndpoint, instance=True)
    mock_endpoint2 = create_autospec(ApiEndpoint, instance=True)

    # Configure the first mock endpoint to be inactive
    mock_endpoint1.is_active.return_value = False

    # Configure the second mock endpoint to be active
    mock_endpoint2.is_active.return_value = True

    # Replace actual endpoints with mocks
    load_balancer.api_endpoints = [mock_endpoint1, mock_endpoint2]
    # Disable load balancing
    load_balancer.load_balancing_enabled = False

    # Get the next active endpoint
    next_active_endpoint = load_balancer.get_next_active_endpoint()

    # Assert that the second endpoint is returned, not the first
    assert next_active_endpoint == mock_endpoint2


def test_skipping_inactive_endpoints(load_balancer):
    # Create mock endpoints
    mock_endpoint1 = create_autospec(ApiEndpoint, instance=True)
    mock_endpoint2 = create_autospec(ApiEndpoint, instance=True)
    mock_endpoint1.is_active.return_value = False
    mock_endpoint2.is_active.return_value = True

    load_balancer.api_endpoints = [mock_endpoint1, mock_endpoint2]

    # The load balancer should skip the first inactive endpoint
    assert load_balancer.get_next_active_endpoint() == mock_endpoint2


@patch('openai_load_balancer.load_balancer.LoadBalancer.send_request')
def test_send_request_arguments(mock_send_request, load_balancer):
    """Test that the correct arguments are passed to the send_request method."""
    mock_endpoint = create_autospec(ApiEndpoint, instance=True)
    mock_endpoint.is_active.return_value = True
    load_balancer.api_endpoints = [mock_endpoint]

    test_args = {'arg1': 'value1', 'arg2': 'value2'}
    load_balancer.try_send_request('test_method', **test_args)

    mock_send_request.assert_called_with(
        mock_endpoint, 'test_method', **test_args)


@patch('openai_load_balancer.load_balancer.LoadBalancer.send_request', return_value="Success")
def test_failure_count_reset_on_success(mock_send_request, load_balancer):
    mock_endpoint = create_autospec(ApiEndpoint, instance=True)
    mock_endpoint.is_active.return_value = True
    load_balancer.api_endpoints = [mock_endpoint]

    load_balancer.try_send_request('test_method', test_arg='value')
    mock_endpoint.reset.assert_called()


def test_all_endpoints_inactive(load_balancer):
    mock_endpoints = [create_autospec(ApiEndpoint, instance=True) for _ in range(
        len(load_balancer.api_endpoints))]
    for mock_endpoint in mock_endpoints:
        mock_endpoint.is_active.return_value = False
        mock_endpoint.mark_failed = Mock()
    load_balancer.api_endpoints = mock_endpoints
    with pytest.raises(Exception) as excinfo:
        load_balancer.try_send_request('test_method', test_arg='value')
    assert str(excinfo.value) == "All endpoints are inactive."
