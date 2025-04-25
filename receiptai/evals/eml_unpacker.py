import datetime
import email
from pathlib import Path
from typing import List
from receiptai.email import EmailInterface, Email, Attachment

class EmlUnpacker(EmailInterface):
    def search_emails(self, query: str) -> List[Email]:
        emails = []
        emails_dir = Path(__file__).parent / "emails"
        
        for eml_file in emails_dir.glob("*.eml"):
            with open(eml_file, "rb") as f:
                msg = email.message_from_binary_file(f)
                
                # Extract email fields
                subject = msg.get("subject", "")
                from_email = msg.get("from", "")
                to_email = msg.get("to", "")
                date_str = msg.get("date", "")
                
                # Parse date
                try:
                    date = email.utils.parsedate_to_datetime(date_str)
                except (TypeError, ValueError):
                    date = datetime.datetime.now()
                
                # Get email body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()
                
                emails.append(Email(
                    id=str(eml_file),
                    subject=subject,
                    body=body,
                    from_email=from_email,
                    to_email=to_email,
                    date=date
                ))
        
        return emails
    
    def get_attachments(self, email_id: str) -> List[Attachment]:
        attachments = []
        emails_dir = Path(__file__).parent / "emails"
        eml_file = emails_dir / email_id
        
        if not eml_file.exists():
            raise FileNotFoundError(f"Email file not found: {eml_file}")
        
        with open(eml_file, "rb") as f:
            msg = email.message_from_binary_file(f)
            
            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                
                filename = part.get_content_disposition().split("filename=")[1]
                content_type = part.get_content_type()
                content = part.get_payload(decode=True)
                
                attachments.append(Attachment(
                    filename=filename,
                    content_type=content_type,
                    content=content
                ))
        
        return attachments
