from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os


def send_welcome_email(user_email, username):

    message = Mail(
        from_email=os.getenv("FROM_EMAIL"),
        to_emails=user_email,
        subject="Welcome to Hustle Hub 🚀",
        html_content=f"""
        <h2>Welcome to Hustle Hub, {username}!</h2>

        <p>
        Your account was created successfully.
        Start exploring mentors and books today.
        </p>
        """
    )

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))

        sg.send(message)

        print("Welcome email sent!")

    except Exception as e:
        print("SendGrid Error:", e)