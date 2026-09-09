import pytest
from backend.app.core.errors import retry_with_backoff, PanelException, LLMProviderError

@pytest.mark.asyncio
async def test_retry_with_backoff_success():
    call_count = 0
    async def flaky_fn():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("Transient error")
        return "success"

    result = await retry_with_backoff(flaky_fn, max_retries=3, initial_delay=0.01)
    assert result == "success"
    assert call_count == 2
