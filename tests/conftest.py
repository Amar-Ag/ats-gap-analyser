import pytest
import time
from dotenv import load_dotenv

def pytest_configure(config):
    load_dotenv(override=True)

@pytest.fixture(autouse=True)
def wait_between_tests():
    yield
    time.sleep(10)  # wait 10s after each test to avoid TPM limits