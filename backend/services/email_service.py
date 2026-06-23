import aiosmtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config import settings

async def send_vault_alert_email(
    to_email: str,
    user_name: str,
    vault_name: str,
    current_balance: float,
    allocated_amount: float,
    percentage_left: float
):
    subject = f"Vaults Alert — Your {vault_name} vault is running low"

    html = f"""
    <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto; padding: 24px;">
      <div style="background: #0F0F13; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 24px;">
        <h1 style="color: white; font-size: 24px; margin: 0;">
          <span style="color: #7B6EF6;">V</span>aults
        </h1>
      </div>

      <h2 style="color: #1a1a2e; font-size: 20px;">Hey {user_name},</h2>

      <p style="color: #444; font-size: 16px; line-height: 1.6;">
        Your <strong>{vault_name}</strong> vault is running low.
      </p>

      <div style="background: #f5f5f5; border-radius: 12px; padding: 20px; margin: 20px 0;">
        <p style="margin: 0 0 8px; color: #888; font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em;">
          Current Balance
        </p>
        <p style="margin: 0; font-size: 28px; font-weight: 700; color: #F25C54;">
          ₹{current_balance:,.2f}
        </p>
        <p style="margin: 8px 0 0; color: #888; font-size: 13px;">
          {percentage_left:.0f}% of ₹{allocated_amount:,.2f} allocated
        </p>
        <div style="background: #e0e0e0; border-radius: 100px; height: 6px; margin-top: 12px;">
          <div style="background: #7B6EF6; border-radius: 100px; height: 6px; width: {percentage_left:.0f}%;"></div>
        </div>
      </div>

      <p style="color: #444; font-size: 15px; line-height: 1.6;">
        You set an alert for when this vault drops below a certain threshold.
        Consider allocating more funds or adjusting your spending.
      </p>

      <a href="http://localhost:8000/frontend/dashboard.html"
        style="display: block; background: #7B6EF6; color: white; text-align: center;
          padding: 14px; border-radius: 8px; text-decoration: none; font-weight: 600;
          font-size: 15px; margin-top: 24px;">
        View Dashboard
      </a>

      <p style="color: #aaa; font-size: 12px; text-align: center; margin-top: 24px;">
        You're receiving this because you set up vault alerts on Vaults.
      </p>
    </div>
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"Vaults App <{settings.GMAIL_SENDER}>"
    message["To"] = to_email
    message.attach(MIMEText(html, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=settings.GMAIL_SENDER,
            password=settings.GMAIL_APP_PASSWORD
        )
        print(f"Alert email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_vault_alert_email_sync(
    to_email: str,
    user_name: str,
    vault_name: str,
    current_balance: float,
    allocated_amount: float,
    percentage_left: float
):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            send_vault_alert_email(
                to_email=to_email,
                user_name=user_name,
                vault_name=vault_name,
                current_balance=current_balance,
                allocated_amount=allocated_amount,
                percentage_left=percentage_left
            )
        )
        loop.close()
        return result
    except Exception as e:
        print(f"Email sync error: {e}")
        return False