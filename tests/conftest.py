# tests/conftest.py
import pytest
from dotenv import load_dotenv

def pytest_configure(config):
    load_dotenv(override=True)