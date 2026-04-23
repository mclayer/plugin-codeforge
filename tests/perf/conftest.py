import pytest


@pytest.fixture(autouse=True)
def _mark_benchmark(request: pytest.FixtureRequest) -> None:
    """Auto-apply the `benchmark` marker to every test under tests/perf/**."""
    request.node.add_marker(pytest.mark.benchmark)
