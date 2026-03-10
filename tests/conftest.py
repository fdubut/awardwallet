import os

# Set dummy value to prevent RuntimeError during tests
os.environ.setdefault("AWARDWALLET_API_KEY", "dummy-key-for-tests")
