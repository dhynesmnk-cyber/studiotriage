import subprocess
import urllib.parse
import platform
from typing import Optional

from .models import Email, Draft


def open_native_email_draft(
    to: str = "",
    subject: str = "",
    body: str = ""
) -> bool:
    """
    Open the native OS email client with a pre-filled draft.
    CRITICAL: This does NOT send the email. It only opens a draft for user review.
    
    Returns True if successful, False otherwise.
    """
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            return _open_macos_mail(to, subject, body)
        elif system == "Windows":
            return _open_windows_mail(to, subject, body)
        else:
            # Linux or fallback: use mailto URL
            return _open_mailto_url(to, subject, body)
    
    except Exception as e:
        print(f"Error opening native email client: {e}")
        return False


def _open_macos_mail(to: str, subject: str, body: str) -> bool:
    """Open macOS Mail app with a new message draft using AppleScript."""
    
    # Escape quotes in the body for AppleScript
    escaped_body = body.replace('"', '\\"').replace('\n', '\\n')
    escaped_subject = subject.replace('"', '\\"')
    escaped_to = to.replace('"', '\\"')
    
    apple_script = f'''
    tell application "Mail"
        activate
        set newMessage to make new outgoing message
        tell newMessage
            set visible to true
            set subject to "{escaped_subject}"
            set content to "{escaped_body}"
            make new to recipient at end of to recipients with properties {{address:"{escaped_to}"}}
        end tell
    end tell
    '''
    
    result = subprocess.run(
        ['osascript', '-e', apple_script],
        capture_output=True,
        text=True
    )
    
    return result.returncode == 0


def _open_windows_mail(to: str, subject: str, body: str) -> bool:
    """Open Windows default mail client."""
    # On Windows, we use the mailto protocol via start command
    mailto_url = f"mailto:{to}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
    
    result = subprocess.run(
        ['start', mailto_url],
        shell=True,
        capture_output=True
    )
    
    return result.returncode == 0


def _open_mailto_url(to: str, subject: str, body: str) -> bool:
    """Fallback: open mailto URL in default browser/email handler."""
    # Note: mailto URLs have length limitations (~2000 chars for body)
    truncated_body = body[:2000] if len(body) > 2000 else body
    
    mailto_url = f"mailto:{to}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(truncated_body)}"
    
    import webbrowser
    return webbrowser.open(mailto_url)


def create_draft_from_email(email: Email, draft: Draft) -> bool:
    """
    Create a native email draft from a processed email/draft pair.
    Uses the original sender as the recipient and includes the AI-drafted reply.
    """
    return open_native_email_draft(
        to=email.sender,
        subject=f"Re: {email.subject}",
        body=draft.drafted_reply
    )
