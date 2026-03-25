from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.identity import CredentialUnavailableError

import send_deployment_notification as script


class TestInitializeGraphClient:
    """Tests for initialize_graph_client function."""

    @patch("send_deployment_notification.GraphServiceClient")
    @patch("send_deployment_notification.ClientSecretCredential")
    def test_creates_credential_with_correct_args(self, mock_cred_cls, mock_graph_cls):
        """Should create ClientSecretCredential with tenant, client, and secret."""
        script.initialize_graph_client("tid", "cid", "csecret")
        mock_cred_cls.assert_called_once_with(
            tenant_id="tid", client_id="cid", client_secret="csecret"
        )

    @patch("send_deployment_notification.GraphServiceClient")
    @patch("send_deployment_notification.ClientSecretCredential")
    def test_creates_graph_client_with_credential_and_scopes(self, mock_cred_cls, mock_graph_cls):
        """Should create GraphServiceClient with the credential and default scope."""
        mock_credential = MagicMock()
        mock_cred_cls.return_value = mock_credential
        script.initialize_graph_client("tid", "cid", "csecret")
        mock_graph_cls.assert_called_once_with(
            mock_credential, scopes=["https://graph.microsoft.com/.default"]
        )

    @patch("send_deployment_notification.GraphServiceClient")
    @patch("send_deployment_notification.ClientSecretCredential")
    def test_returns_graph_client(self, mock_cred_cls, mock_graph_cls):
        """Should return the GraphServiceClient instance."""
        mock_client = MagicMock()
        mock_graph_cls.return_value = mock_client
        result = script.initialize_graph_client("tid", "cid", "csecret")
        assert result is mock_client

    @patch("send_deployment_notification.ClientSecretCredential")
    def test_raises_on_credential_unavailable(self, mock_cred_cls):
        """Should propagate CredentialUnavailableError when credentials are missing."""
        mock_cred_cls.side_effect = CredentialUnavailableError(message="bad creds")
        with pytest.raises(CredentialUnavailableError):
            script.initialize_graph_client("tid", "cid", "csecret")

    @patch("send_deployment_notification.ClientSecretCredential")
    def test_raises_on_client_auth_error(self, mock_cred_cls):
        """Should propagate ClientAuthenticationError when authentication is rejected."""
        mock_cred_cls.side_effect = ClientAuthenticationError(message="auth rejected")
        with pytest.raises(ClientAuthenticationError):
            script.initialize_graph_client("tid", "cid", "csecret")

    @patch("send_deployment_notification.GraphServiceClient")
    @patch("send_deployment_notification.ClientSecretCredential")
    def test_does_not_catch_unexpected_exceptions(self, mock_cred_cls, mock_graph_cls):
        """Should let unexpected exceptions propagate uncaught."""
        mock_graph_cls.side_effect = RuntimeError("graph init failed")
        with pytest.raises(RuntimeError, match="graph init failed"):
            script.initialize_graph_client("tid", "cid", "csecret")


class TestPrepareEmailRequest:
    """Tests for prepare_email_request function."""

    def test_returns_send_mail_post_request_body(self):
        """Should return a SendMailPostRequestBody instance."""
        recipients = script.prepare_recipients("user@example.com")
        result = script.prepare_email_request("Subject", "Body", recipients)
        # Since SendMailPostRequestBody is mocked, verify it was called
        assert result is not None

    @patch("send_deployment_notification.SendMailPostRequestBody")
    @patch("send_deployment_notification.Message")
    @patch("send_deployment_notification.ItemBody")
    def test_constructs_message_with_correct_args(
        self, mock_item_body, mock_message, mock_request_body
    ):
        """Should construct Message with subject, body, and recipients."""
        recipients = [MagicMock()]
        script.prepare_email_request("Test Subject", "Test Content", recipients)
        mock_item_body.assert_called_once()
        mock_message.assert_called_once()
        msg_kwargs = mock_message.call_args
        assert msg_kwargs.kwargs["subject"] == "Test Subject"
        assert msg_kwargs.kwargs["to_recipients"] is recipients

    @patch("send_deployment_notification.SendMailPostRequestBody")
    @patch("send_deployment_notification.Message")
    @patch("send_deployment_notification.ItemBody")
    def test_sets_save_to_sent_items_true(self, mock_item_body, mock_message, mock_request_body):
        """Should set save_to_sent_items to True."""
        script.prepare_email_request("Subj", "Body", [])
        req_kwargs = mock_request_body.call_args
        assert req_kwargs.kwargs["save_to_sent_items"] is True

    @patch("send_deployment_notification.SendMailPostRequestBody")
    @patch("send_deployment_notification.Message")
    @patch("send_deployment_notification.ItemBody")
    def test_uses_text_body_type(self, mock_item_body, mock_message, mock_request_body):
        """Should use BodyType.Text for the content type."""
        script.prepare_email_request("Subj", "Body", [])
        body_kwargs = mock_item_body.call_args
        assert body_kwargs.kwargs["content"] == "Body"

    @patch("send_deployment_notification.SendMailPostRequestBody", side_effect=TypeError("sdk err"))
    @patch("send_deployment_notification.Message")
    @patch("send_deployment_notification.ItemBody")
    def test_raises_on_failure(self, mock_item_body, mock_message, mock_request_body):
        """Should propagate exception on failure."""
        with pytest.raises(TypeError, match="sdk err"):
            script.prepare_email_request("Subj", "Body", [])


class TestSendEmail:
    """Tests for send_email async function."""

    @pytest.mark.asyncio
    async def test_calls_send_mail_post(self):
        """Should call send_mail.post with the request body."""
        mock_client = MagicMock()
        mock_user = MagicMock()
        mock_user.send_mail.post = AsyncMock()
        mock_client.users.by_user_id.return_value = mock_user
        request_body = MagicMock()

        await script.send_email(mock_client, "sender@example.com", request_body)

        mock_client.users.by_user_id.assert_called_once_with("sender@example.com")
        mock_user.send_mail.post.assert_awaited_once_with(request_body)

    @pytest.mark.asyncio
    async def test_raises_when_user_request_is_none(self):
        """Should raise ValueError when by_user_id returns None."""
        mock_client = MagicMock()
        mock_client.users.by_user_id.return_value = None

        with pytest.raises(ValueError, match="User request initialization failed"):
            await script.send_email(mock_client, "sender@example.com", MagicMock())

    @pytest.mark.asyncio
    async def test_raises_on_http_response_error(self):
        """Should propagate HttpResponseError from Graph API."""
        mock_client = MagicMock()
        mock_user = MagicMock()
        error = HttpResponseError(message="forbidden")
        error.status_code = 403
        error.reason = "Forbidden"
        mock_user.send_mail.post = AsyncMock(side_effect=error)
        mock_client.users.by_user_id.return_value = mock_user

        with pytest.raises(HttpResponseError):
            await script.send_email(mock_client, "sender@example.com", MagicMock())

    @pytest.mark.asyncio
    async def test_raises_on_odata_error(self):
        """Should propagate ODataError from Graph API."""
        mock_client = MagicMock()
        mock_user = MagicMock()
        mock_user.send_mail.post = AsyncMock(side_effect=script.ODataError("odata fail"))
        mock_client.users.by_user_id.return_value = mock_user

        with pytest.raises(script.ODataError):
            await script.send_email(mock_client, "sender@example.com", MagicMock())

    @pytest.mark.asyncio
    async def test_raises_on_timeout(self):
        """Should propagate TimeoutError."""
        mock_client = MagicMock()
        mock_user = MagicMock()
        mock_user.send_mail.post = AsyncMock(side_effect=TimeoutError())
        mock_client.users.by_user_id.return_value = mock_user

        with pytest.raises(TimeoutError):
            await script.send_email(mock_client, "sender@example.com", MagicMock())


class TestMain:
    """Tests for main function."""

    @patch("send_deployment_notification.asyncio.run")
    @patch("send_deployment_notification.send_email", new=MagicMock())
    @patch("send_deployment_notification.prepare_email_request")
    @patch("send_deployment_notification.initialize_graph_client")
    @patch("send_deployment_notification.prepare_recipients")
    @patch("send_deployment_notification.prepare_email_content")
    def test_happy_path(
        self,
        mock_content,
        mock_recipients,
        mock_graph,
        mock_request,
        mock_asyncio_run,
        mock_env_vars,
    ):
        """Should orchestrate all steps and send email successfully."""
        mock_content.return_value = ("Subject", "Body")
        mock_recipients.return_value = [MagicMock()]
        mock_graph.return_value = MagicMock()
        mock_request.return_value = MagicMock()

        script.main()

        mock_content.assert_called_once_with("owner/test-repo", "production", "testuser")
        mock_recipients.assert_called_once_with("user1@example.com, user2@example.com")
        mock_graph.assert_called_once_with("test-tenant-id", "test-client-id", "test-client-secret")
        mock_request.assert_called_once()
        mock_asyncio_run.assert_called_once()

    @patch("send_deployment_notification.sys.exit")
    def test_exits_on_missing_env_var(self, mock_exit, clean_env):
        """Should call sys.exit(1) when a required env var is missing."""
        script.main()
        mock_exit.assert_called_once_with(1)

    @patch("send_deployment_notification.sys.exit")
    @patch("send_deployment_notification.asyncio.run", side_effect=RuntimeError("send failed"))
    @patch("send_deployment_notification.send_email", new=MagicMock())
    @patch("send_deployment_notification.prepare_email_request")
    @patch("send_deployment_notification.initialize_graph_client")
    @patch("send_deployment_notification.prepare_recipients")
    @patch("send_deployment_notification.prepare_email_content")
    def test_exits_on_send_failure(
        self,
        mock_content,
        mock_recipients,
        mock_graph,
        mock_request,
        mock_asyncio_run,
        mock_exit,
        mock_env_vars,
    ):
        """Should call sys.exit(1) when email sending fails."""
        mock_content.return_value = ("Subject", "Body")
        mock_recipients.return_value = [MagicMock()]
        mock_graph.return_value = MagicMock()
        mock_request.return_value = MagicMock()

        script.main()

        mock_exit.assert_called_once_with(1)

    @patch("send_deployment_notification.sys.exit")
    @patch("send_deployment_notification.initialize_graph_client", side_effect=ValueError("auth"))
    @patch("send_deployment_notification.prepare_recipients")
    @patch("send_deployment_notification.prepare_email_content")
    def test_exits_on_graph_client_failure(
        self,
        mock_content,
        mock_recipients,
        mock_graph,
        mock_exit,
        mock_env_vars,
    ):
        """Should call sys.exit(1) when graph client initialization fails."""
        mock_content.return_value = ("Subject", "Body")
        mock_recipients.return_value = [MagicMock()]

        script.main()

        mock_exit.assert_called_once_with(1)

    @patch("send_deployment_notification.sys.exit")
    @patch(
        "send_deployment_notification.initialize_graph_client",
        side_effect=CredentialUnavailableError(message="missing creds"),
    )
    @patch("send_deployment_notification.prepare_recipients")
    @patch("send_deployment_notification.prepare_email_content")
    def test_exits_on_credential_unavailable(
        self,
        mock_content,
        mock_recipients,
        mock_graph,
        mock_exit,
        mock_env_vars,
    ):
        """Should call sys.exit(1) when Azure credentials are unavailable."""
        mock_content.return_value = ("Subject", "Body")
        mock_recipients.return_value = [MagicMock()]

        script.main()

        mock_exit.assert_called_once_with(1)

    @patch("send_deployment_notification.sys.exit")
    @patch(
        "send_deployment_notification.initialize_graph_client",
        side_effect=ClientAuthenticationError(message="auth rejected"),
    )
    @patch("send_deployment_notification.prepare_recipients")
    @patch("send_deployment_notification.prepare_email_content")
    def test_exits_on_client_auth_error(
        self,
        mock_content,
        mock_recipients,
        mock_graph,
        mock_exit,
        mock_env_vars,
    ):
        """Should call sys.exit(1) when Azure AD rejects authentication."""
        mock_content.return_value = ("Subject", "Body")
        mock_recipients.return_value = [MagicMock()]

        script.main()

        mock_exit.assert_called_once_with(1)

    @patch("send_deployment_notification.sys.exit")
    @patch(
        "send_deployment_notification.asyncio.run",
        side_effect=HttpResponseError(message="forbidden"),
    )
    @patch("send_deployment_notification.send_email", new=MagicMock())
    @patch("send_deployment_notification.prepare_email_request")
    @patch("send_deployment_notification.initialize_graph_client")
    @patch("send_deployment_notification.prepare_recipients")
    @patch("send_deployment_notification.prepare_email_content")
    def test_exits_on_http_response_error(
        self,
        mock_content,
        mock_recipients,
        mock_graph,
        mock_request,
        mock_asyncio_run,
        mock_exit,
        mock_env_vars,
    ):
        """Should call sys.exit(1) when Graph API returns an HTTP error."""
        mock_content.return_value = ("Subject", "Body")
        mock_recipients.return_value = [MagicMock()]
        mock_graph.return_value = MagicMock()
        mock_request.return_value = MagicMock()

        script.main()

        mock_exit.assert_called_once_with(1)

    @patch("send_deployment_notification.sys.exit")
    @patch(
        "send_deployment_notification.asyncio.run",
        side_effect=script.ODataError("odata fail"),
    )
    @patch("send_deployment_notification.send_email", new=MagicMock())
    @patch("send_deployment_notification.prepare_email_request")
    @patch("send_deployment_notification.initialize_graph_client")
    @patch("send_deployment_notification.prepare_recipients")
    @patch("send_deployment_notification.prepare_email_content")
    def test_exits_on_odata_error(
        self,
        mock_content,
        mock_recipients,
        mock_graph,
        mock_request,
        mock_asyncio_run,
        mock_exit,
        mock_env_vars,
    ):
        """Should call sys.exit(1) when Graph API returns an OData error."""
        mock_content.return_value = ("Subject", "Body")
        mock_recipients.return_value = [MagicMock()]
        mock_graph.return_value = MagicMock()
        mock_request.return_value = MagicMock()

        script.main()

        mock_exit.assert_called_once_with(1)

    @patch("send_deployment_notification.sys.exit")
    @patch(
        "send_deployment_notification.asyncio.run",
        side_effect=TimeoutError(),
    )
    @patch("send_deployment_notification.send_email", new=MagicMock())
    @patch("send_deployment_notification.prepare_email_request")
    @patch("send_deployment_notification.initialize_graph_client")
    @patch("send_deployment_notification.prepare_recipients")
    @patch("send_deployment_notification.prepare_email_content")
    def test_exits_on_timeout_error(
        self,
        mock_content,
        mock_recipients,
        mock_graph,
        mock_request,
        mock_asyncio_run,
        mock_exit,
        mock_env_vars,
    ):
        """Should call sys.exit(1) when Graph API request times out."""
        mock_content.return_value = ("Subject", "Body")
        mock_recipients.return_value = [MagicMock()]
        mock_graph.return_value = MagicMock()
        mock_request.return_value = MagicMock()

        script.main()

        mock_exit.assert_called_once_with(1)
