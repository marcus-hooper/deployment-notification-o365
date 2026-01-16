import send_deployment_notification as script


class TestPrepareEmailContent:
    """Tests for prepare_email_content function."""

    def test_returns_tuple(self):
        """Should return a tuple of (subject, content)."""
        result = script.prepare_email_content("owner/repo", "production", "actor")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_subject_contains_repository(self):
        """Subject should contain the repository name."""
        subject, _ = script.prepare_email_content("owner/test-repo", "staging", "user")
        assert "owner/test-repo" in subject

    def test_subject_contains_environment(self):
        """Subject should contain the environment name."""
        subject, _ = script.prepare_email_content("owner/repo", "production", "user")
        assert "production" in subject

    def test_subject_contains_deployment_successful(self):
        """Subject should indicate successful deployment."""
        subject, _ = script.prepare_email_content("owner/repo", "prod", "user")
        assert "Deployment Successful" in subject

    def test_content_contains_repository(self):
        """Content should contain the repository name."""
        _, content = script.prepare_email_content("owner/test-repo", "staging", "user")
        assert "owner/test-repo" in content

    def test_content_contains_environment(self):
        """Content should contain the environment name."""
        _, content = script.prepare_email_content("owner/repo", "production", "user")
        assert "production" in content

    def test_content_contains_actor(self):
        """Content should contain the actor name."""
        _, content = script.prepare_email_content("owner/repo", "prod", "deploy-user")
        assert "deploy-user" in content

    def test_content_contains_repository_url(self):
        """Content should contain the GitHub repository URL."""
        _, content = script.prepare_email_content("owner/test-repo", "prod", "user")
        assert "https://github.com/owner/test-repo" in content

    def test_content_contains_status(self):
        """Content should contain the deployment status."""
        _, content = script.prepare_email_content("owner/repo", "prod", "user")
        assert "Status: Successful" in content

    def test_content_contains_deployment_time(self):
        """Content should contain a deployment time field."""
        _, content = script.prepare_email_content("owner/repo", "prod", "user")
        assert "Deployment Time:" in content

    def test_handles_special_characters_in_repo(self):
        """Should handle special characters in repository name."""
        subject, content = script.prepare_email_content(
            "org-name/repo_with-special.chars", "prod", "user"
        )
        assert "org-name/repo_with-special.chars" in subject
        assert "org-name/repo_with-special.chars" in content

    def test_includes_commit_message_section(self):
        """Content should have a section for commit messages."""
        _, content = script.prepare_email_content("owner/repo", "prod", "user")
        assert "Recent Commit Messages:" in content

    def test_with_commit_message_file(self, sample_commit_message):
        """Should include commit message content when file exists."""
        _, content = script.prepare_email_content("owner/repo", "prod", "user")
        assert "Fix bug in login" in content
        assert "Add new feature" in content


class TestPrepareRecipients:
    """Tests for prepare_recipients function."""

    def test_returns_list(self):
        """Should return a list."""
        result = script.prepare_recipients("user@example.com")
        assert isinstance(result, list)

    def test_single_recipient(self):
        """Should handle a single recipient."""
        result = script.prepare_recipients("user@example.com")
        assert len(result) == 1

    def test_multiple_recipients_comma_separated(self):
        """Should handle comma-separated recipients."""
        result = script.prepare_recipients("user1@example.com,user2@example.com")
        assert len(result) == 2

    def test_multiple_recipients_with_spaces(self):
        """Should handle comma-separated recipients with spaces."""
        result = script.prepare_recipients("user1@example.com, user2@example.com, user3@example.com")
        assert len(result) == 3

    def test_strips_whitespace(self):
        """Should strip whitespace from email addresses."""
        result = script.prepare_recipients("  user1@example.com  ,  user2@example.com  ")
        assert len(result) == 2
        # Check that addresses are stripped
        addresses = [r.email_address.address for r in result]
        assert "user1@example.com" in addresses
        assert "user2@example.com" in addresses

    def test_recipient_has_email_address_attribute(self):
        """Each recipient should have an email_address attribute."""
        result = script.prepare_recipients("user@example.com")
        assert hasattr(result[0], "email_address")
        assert hasattr(result[0].email_address, "address")

    def test_email_address_value(self):
        """Email address should match the input."""
        result = script.prepare_recipients("test@domain.com")
        assert result[0].email_address.address == "test@domain.com"

    def test_preserves_email_case(self):
        """Should preserve email address case."""
        result = script.prepare_recipients("User@Example.COM")
        assert result[0].email_address.address == "User@Example.COM"

    def test_handles_plus_addressing(self):
        """Should handle plus addressing in emails."""
        result = script.prepare_recipients("user+tag@example.com")
        assert result[0].email_address.address == "user+tag@example.com"
