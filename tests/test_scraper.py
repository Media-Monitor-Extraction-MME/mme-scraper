'''
Might need to skip this since scrape function is going to be rewritten due to hidden API's
'''

import pytest
import pytest_asyncio
import pytest_playwright
import asyncio
from unittest.mock import AsyncMock, patch

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))