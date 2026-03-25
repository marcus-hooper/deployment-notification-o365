import asyncio
import datetime
import logging
import os
import sys
from zoneinfo import ZoneInfo

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.identity import ClientSecretCredential, CredentialUnavailableError
from msgraph import GraphServiceClient
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.message import Message
from msgraph.generated.models.o_data_errors.o_data_error import ODataError
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import (
    SendMailPostRequestBody,
)

# Retry configuration
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1  # seconds
NON_RETRYABLE_STATUS_CODES = {400, 401, 403, 404}

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Utility Functions
def get_env_variable(name, required=True):
    """Fetch and validate environment variables."""
    value = os.getenv(name)
    if required and not value:
        logging.error(f"Missing required environment variable: {name}")
        raise ValueError(f"Environment variable '{name}' is not set.")
    return value


def get_formatted_time():
    """Get the current time formatted in Eastern Time."""
    local_time = datetime.datetime.now()
    eastern_time = local_time.astimezone(ZoneInfo("US/Eastern"))
    return eastern_time.strftime("%Y-%m-%d %H:%M:%S")


# Email Preparation Functions
def prepare_email_content(repository, environment, actor):
    """Prepare the email subject and content."""
    formatted_time = get_formatted_time()
    subject = f"Deployment Successful: {repository} to {environment} on {formatted_time}"

    # Get contents of commit_message.txt file (optional)
    commit_message = ""
    try:
        with open("commit_message.txt") as file:
            commit_message = file.read().strip()
    except FileNotFoundError:
        logging.warning("commit_message.txt not found. No commit message will be included.")

    content = (
        f"Repository: {repository}\n"
        f"Environment: {environment}\n"
        f"Deployment Time: {formatted_time}\n"
        f"Status: Successful\n"
        f"Started by: {actor}\n"
        f"Repository URL: https://github.com/{repository}\n\n"
        f"Recent Commit Messages: \n{commit_message}\n"
    )
    return subject, content


def prepare_recipients(notification_to):
    """Create a list of Recipient objects with email validation."""
    emails = [email.strip() for email in notification_to.split(",")]
    emails = [email for email in emails if email]

    if not emails:
        raise ValueError("No valid email addresses provided in NOTIFICATION_TO")

    invalid = []
    for email in emails:
        if email.count("@") != 1:
            invalid.append(email)
        else:
            local, domain = email.split("@")
            if not local or not domain:
                invalid.append(email)

    if invalid:
        raise ValueError(f"Invalid email address(es): {', '.join(invalid)}")

    return [Recipient(email_address=EmailAddress(address=email)) for email in emails]


# Azure Graph Client Functions
def initialize_graph_client(tenant_id, client_id, client_secret):
    """Initialize the Azure Graph client."""
    try:
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )
        logging.info("Azure credential initialized successfully.")
        scopes = ["https://graph.microsoft.com/.default"]
        return GraphServiceClient(credential, scopes=scopes)
    except CredentialUnavailableError:
        logging.error(
            "Azure credential unavailable: check AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET"
        )
        raise
    except ClientAuthenticationError:
        logging.error("Azure authentication rejected by Azure AD")
        raise


def prepare_email_request(subject, content, to_recipients):
    """Prepare the email request body."""
    try:
        return SendMailPostRequestBody(
            message=Message(
                subject=subject,
                body=ItemBody(content_type=BodyType.Text, content=content),
                to_recipients=to_recipients,
            ),
            save_to_sent_items=True,
        )
    except (TypeError, ValueError) as e:
        logging.error(f"Failed to prepare email request body: {e}")
        raise


def _is_retryable(error):
    """Determine if an error is retryable."""
    if isinstance(error, TimeoutError):
        return True
    if isinstance(error, HttpResponseError):
        return error.status_code not in NON_RETRYABLE_STATUS_CODES
    return False


def _get_retry_delay(error, attempt):
    """Calculate retry delay, respecting Retry-After header for 429 responses."""
    if isinstance(error, HttpResponseError) and error.status_code == 429:
        retry_after = (
            getattr(error, "headers", {}).get("Retry-After") if hasattr(error, "headers") else None
        )
        if retry_after:
            try:
                return int(retry_after)
            except (ValueError, TypeError):
                pass
    return RETRY_BASE_DELAY * (2**attempt)


async def send_email(graph_client, sender, request_body):
    """Async function to send the email with exponential backoff retry."""
    user_request = graph_client.users.by_user_id(sender)
    if not user_request:
        logging.error("Failed to get user request.")
        raise ValueError("User request initialization failed.")

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            await user_request.send_mail.post(request_body)
            logging.info("Email sent successfully.")
            return
        except HttpResponseError as e:
            last_error = e
            logging.error(f"Graph API HTTP error: {e.status_code} {e.reason}")
            if not _is_retryable(e):
                raise
        except ODataError as e:
            logging.error(f"Graph API OData error: {e.error.code if e.error else 'unknown'}")
            raise
        except TimeoutError as e:
            last_error = e
            logging.error("Graph API request timed out")

        if attempt < MAX_RETRIES - 1:
            delay = _get_retry_delay(last_error, attempt)
            logging.info(f"Retrying in {delay}s (attempt {attempt + 2}/{MAX_RETRIES})")
            await asyncio.sleep(delay)

    if last_error is not None:
        raise last_error
    raise RuntimeError("send_email failed: no retries attempted")


# Main Function
def main():
    try:
        # Fetch required environment variables
        github_repository = get_env_variable("GITHUB_REPOSITORY")
        github_actor = get_env_variable("GITHUB_ACTOR")
        github_environment = get_env_variable("GITHUB_ENVIRONMENT")
        notification_to = get_env_variable("NOTIFICATION_TO")
        notification_from = get_env_variable("NOTIFICATION_FROM")
        tenant_id = get_env_variable("AZURE_TENANT_ID")
        client_id = get_env_variable("AZURE_CLIENT_ID")
        client_secret = get_env_variable("AZURE_CLIENT_SECRET")

        # Prepare email details
        subject, content = prepare_email_content(
            github_repository, github_environment, github_actor
        )
        to_recipients = prepare_recipients(notification_to)

        # Initialize Graph client
        graph_client = initialize_graph_client(tenant_id, client_id, client_secret)

        # Prepare email request body
        request_body = prepare_email_request(subject, content, to_recipients)

        # Send the email
        asyncio.run(send_email(graph_client, notification_from, request_body))
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
        sys.exit(1)
    except (CredentialUnavailableError, ClientAuthenticationError) as e:
        logging.error(f"Authentication failed: {type(e).__name__}")
        sys.exit(1)
    except (HttpResponseError, ODataError, TimeoutError) as e:
        logging.error(f"Failed to send email: {type(e).__name__}")
        sys.exit(1)
    except Exception:
        logging.error("An unexpected error occurred while sending the email")
        sys.exit(1)


# Entry Point
if __name__ == "__main__":
    main()
