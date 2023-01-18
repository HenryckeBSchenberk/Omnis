from dotenv import load_dotenv
import unittest
from os import environ
load_dotenv(f'.env.test', override=True)

if __name__ == "__main__":
    suite = unittest.TestLoader().discover(environ.get("TEST_PATH", "src/"), pattern=environ.get("TEST_PATTERN", "test_*.py"))
    unittest.TextTestRunner(verbosity=2).run(suite)