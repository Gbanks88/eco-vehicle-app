"""Pytest configuration for recycling tests"""

import pytest
import redis
import os
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
