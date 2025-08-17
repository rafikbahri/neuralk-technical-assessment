from client import Client
import pytest

@pytest.fixture(scope="session")
def client():
    """Create a client instance for the test class."""
    return Client()