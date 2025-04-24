import asyncio
import datetime
import os
import logging
import pytz
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import SendMailPostRequestBody
from msgraph.generated.models.message import Message
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.models.email_address import EmailAddress

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
    eastern = pytz.timezone("US/Eastern")
    eastern_time = local_time.astimezone(eastern)
    return eastern_time.strftime("%Y-%m-%d %H:%M:%S")


# Email Preparation Functions
def prepare_email_content(repository, environment, actor):
    """Prepare the email subject and content."""
    formatted_time = get_formatted_time()
    subject = f"Deployment Successful: {repository} to {environment} on {formatted_time}"
# get contents of commit_message.txt file
    commit_message = ""
    try:
        with open("commit_message.txt", "r") as file:
            commit_message = file.read().strip()
    except FileNotFoundError:
        logging.error("commit_message.txt file not found. No commit message will be included.")
        
    content = (
        f"Repository: {repository}\n"
        f"Environment: {environment}\n"
        f"Deployment Time: {formatted_time}\n"
        f"Status: Successful\n"
        f"Started by: {actor}\n"
        f"Repository URL: https://github.com/{repository}\n\n"
        f"Recent Commit Messages: \n {commit_message}\n"
    )
    return subject, content


def prepare_recipients(notification_to):
    """Create a list of Recipient objects."""
    return [
        Recipient(
            email_address=EmailAddress(
                address=email.strip()
            )
        )
        for email in notification_to.split(',')
    ]


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
        scopes = ['https://graph.microsoft.com/.default']
        return GraphServiceClient(credential, scopes=scopes)
    except Exception as e:
        logging.error(f"Failed to initialize Graph client: {e}")
        raise


def prepare_email_request(subject, content, to_recipients):
    """Prepare the email request body."""
    try:
        return SendMailPostRequestBody(
            message=Message(
                subject=subject,
                body=ItemBody(
                    content_type=BodyType.Text,
                    content=content
                ),
                to_recipients=to_recipients,
            ),
            save_to_sent_items=True
        )
    except Exception as e:
        logging.error(f"Failed to prepare email request body: {e}")
        raise


async def send_email(graph_client, sender, request_body):
    """Async function to send the email."""
    try:
        user_request = graph_client.users.by_user_id(sender)
        if not user_request:
            logging.error("Failed to get user request.")
            raise ValueError("User request initialization failed.")
        
        await user_request.send_mail.post(request_body)
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        raise


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
        # commit_message = get_env_variable("COMMIT_MESSAGE")

        # Prepare email details
        subject, content = prepare_email_content(github_repository, github_environment, github_actor)
        to_recipients = prepare_recipients(notification_to)

        # Initialize Graph client
        graph_client = initialize_graph_client(tenant_id, client_id, client_secret)

        # Prepare email request body
        request_body = prepare_email_request(subject, content, to_recipients)

        # Send the email
        asyncio.run(send_email(graph_client, notification_from, request_body))
    except Exception as e:
        logging.error(f"An error occurred while sending the email: {e}")


# Entry Point
if __name__ == "__main__":
    main()