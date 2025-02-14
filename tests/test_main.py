"""
Test cases for the main module.
"""
import pytest
from src.main import main

def test_main_runs_without_error():
    """Test that the main function runs without raising any exceptions."""
    try:
        main()
    except Exception as e:
        pytest.fail(f"main() raised {type(e).__name__} unexpectedly!") 