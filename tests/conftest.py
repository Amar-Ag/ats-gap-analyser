import pytest
import time
from dotenv import load_dotenv

def pytest_configure(config):
    load_dotenv(override=True)

@pytest.fixture(autouse=True)
def reset_agent_client():
    """Reset agent client to Groq before each test to prevent state pollution"""
    import src.agent.agent as agent_module
    agent_module.client = agent_module.groq_client
    agent_module.ats_tools.client = agent_module.groq_client
    yield
    time.sleep(10)  # wait after each test to avoid TPM limits