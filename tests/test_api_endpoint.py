from datetime import datetime, timedelta
import pytest
from openai_load_balancer.api_endpoint import ApiEndpoint


@pytest.fixture
def api_endpoint():
    return ApiEndpoint(api_type="open_ai", base_url="https://api.openai.com/v1", api_key_env="OPENAI_API_KEY")


def test_api_endpoint_initial_state(api_endpoint):
    assert api_endpoint.failure_count == 0
    assert api_endpoint.last_failed_time is None


def test_api_endpoint_is_active(api_endpoint):
    assert api_endpoint.is_active(
        failure_threshold=5, cooldown_period=timedelta(minutes=10))


def test_api_endpoint_mark_failed(api_endpoint):
    api_endpoint.mark_failed()
    assert api_endpoint.failure_count == 1
    assert api_endpoint.last_failed_time is not None


def test_api_endpoint_reset(api_endpoint):
    api_endpoint.mark_failed()
    api_endpoint.reset()
    assert api_endpoint.failure_count == 0
    assert api_endpoint.last_failed_time is None


def test_api_endpoint_reactivate_after_cooldown(api_endpoint):
    api_endpoint.mark_failed()
    api_endpoint.last_failed_time = datetime.now() - timedelta(minutes=11)
    assert api_endpoint.is_active(
        failure_threshold=5, cooldown_period=timedelta(minutes=10))


def test_api_endpoint_active_until_failure_threshold(api_endpoint):
    for _ in range(4):
        api_endpoint.mark_failed()
    assert api_endpoint.is_active(
        failure_threshold=5, cooldown_period=timedelta(minutes=10))


def test_api_endpoint_inactive_after_failure_threshold(api_endpoint):
    for _ in range(5):
        api_endpoint.mark_failed()
    assert not api_endpoint.is_active(
        failure_threshold=5, cooldown_period=timedelta(minutes=10))


def test_api_endpoint_inactive_before_cooldown(api_endpoint):
    # Increment failure_count to reach the threshold
    for _ in range(5):  # Assuming failure_threshold is 5
        api_endpoint.mark_failed()

    # Set last_failed_time to 5 minutes ago (inside the cooldown period)
    api_endpoint.last_failed_time = datetime.now() - timedelta(minutes=5)

    # Test should now correctly expect the endpoint to be inactive
    assert not api_endpoint.is_active(
        failure_threshold=5, cooldown_period=timedelta(minutes=10))


def test_api_endpoint_failure_count_increment(api_endpoint):
    for i in range(1, 4):  # Test multiple failures
        api_endpoint.mark_failed()
        assert api_endpoint.failure_count == i
