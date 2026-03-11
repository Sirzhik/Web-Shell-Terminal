import os
import sys


# Ensure 'src' directory is on sys.path so tests can import packages there.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest_asyncio
from test_db import db_operator  # or import from your module

@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_db():
    # create tables once for this module
    await db_operator.init_db(create_if_not_exists=True)
    yield
    # optional teardown: drop tables or dispose engine
