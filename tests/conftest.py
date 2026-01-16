import os
import sys
from unittest.mock import MagicMock

# Mock msgraph modules before importing the script
# This allows tests to run without the full msgraph-sdk installed
mock_modules = [
    "msgraph",
    "msgraph.generated",
    "msgraph.generated.users",
    "msgraph.generated.users.item",
    "msgraph.generated.users.item.send_mail",
    "msgraph.generated.users.item.send_mail.send_mail_post_request_body",
    "msgraph.generated.models",
    "msgraph.generated.models.message",
    "msgraph.generated.models.item_body",
    "msgraph.generated.models.body_type",
    "msgraph.generated.models.recipient",
    "msgraph.generated.models.email_address",
]

for mod_name in mock_modules:
    sys.modules[mod_name] = MagicMock()


# Create proper mock classes for the models we actually use in tests
class MockEmailAddress:
    def __init__(self, address=None):
        self.address = address


class MockRecipient:
    def __init__(self, email_address=None):
        self.email_address = email_address


# Patch the mocked modules with our test-friendly versions
sys.modules["msgraph.generated.models.email_address"].EmailAddress = MockEmailAddress
sys.modules["msgraph.generated.models.recipient"].Recipient = MockRecipient

import pytest  # noqa: E402

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    env_vars = {
        "GITHUB_REPOSITORY": "owner/test-repo",
        "GITHUB_ACTOR": "testuser",
        "GITHUB_ENVIRONMENT": "production",
        "NOTIFICATION_TO": "user1@example.com, user2@example.com",
        "NOTIFICATION_FROM": "sender@example.com",
        "AZURE_TENANT_ID": "test-tenant-id",
        "AZURE_CLIENT_ID": "test-client-id",
        "AZURE_CLIENT_SECRET": "test-client-secret",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture
def clean_env(monkeypatch):
    """Remove all notification-related environment variables."""
    keys_to_remove = [
        "GITHUB_REPOSITORY",
        "GITHUB_ACTOR",
        "GITHUB_ENVIRONMENT",
        "NOTIFICATION_TO",
        "NOTIFICATION_FROM",
        "AZURE_TENANT_ID",
        "AZURE_CLIENT_ID",
        "AZURE_CLIENT_SECRET",
    ]
    for key in keys_to_remove:
        monkeypatch.delenv(key, raising=False)


@pytest.fixture
def sample_commit_message(tmp_path, monkeypatch):
    """Create a temporary commit_message.txt file."""
    monkeypatch.chdir(tmp_path)
    commit_file = tmp_path / "commit_message.txt"
    commit_file.write_text("abc1234 - Fix bug in login\ndef5678 - Add new feature")
    return str(commit_file)
