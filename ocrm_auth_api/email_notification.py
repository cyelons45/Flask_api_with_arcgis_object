
import os
import smtplib
from pathlib import Path
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import COMMASPACE, formatdate
from email.mime.base import MIMEBase
from email import encoders

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


  
def send_gmail():
    """
        Send Email Function[accepts multiple attachments]
            subject: Configuration file name
            body: Mail Body
            to_email: recipient email address
            send_from: sender email address
        return: None
    """
    try:
        to_email="" 
        send_from=""
        resetcode="24062"
        username="cyelons45" 

        # Email configuration
        sender_email = send_from
        receiver_email =to_email
        subject = "Password Reset Instructions"
        email_body = email_template()
        email_body=email_body.replace("{{resetcode}}",resetcode)
        email_body=email_body.replace("{{user}}",username)


        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject 
        replyemail="DHEC OCRM Team <DONOTREPLY@dhec.sc.ogov>"
        msg.add_header("Reply-To",replyemail)
        msg.attach(MIMEText(email_body, 'HTML'))

        # Connect to the SMTP server
        smtp_server = ""
        smtp_port = 25  # Or 465 for SSL
        server = smtplib.SMTP(smtp_server, smtp_port)
        # server.starttls()  # Use TLS for security
        # server.login(sender_email, smtp_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()         
    except Exception as e:
        print(str(e))



def email_template():
    try:
        return """<!DOCTYPE html><body>
                <p>Dear {{user}},</p>
                <table>
                    <tbody>
                        <tr>
                            <td>You requested to reset your password. Use the reset code below to reset your password.</td>
                        </tr>
                        <tr>
                            <td style="font-size: 18px; font-weight: bold;color: blue; padding-left: 5rem; letter-spacing:5px">{{resetcode}}</td>
                        </tr>
                    <tr>
                        <td>This reset code will expire in 10 minutes</td>
                    </tr>
                    <tr>
                        <td>Submit this code, together with other requested information on the DHEC webpage to change your password.</td>
                    </tr>
                        <tr>
                            <td>&nbsp;</td>
                        </tr>
                        <tr>
                            <td>If you didn't request to reset your password, please ignore this email. Your password won't change until you submit this reset code.</td>
                        </tr>
                        <tr>
                            <td>&nbsp;</td>
                        </tr>
                    </tbody>
                </table>
                <hr>
                <p>Thank you.</p>
                <p>SCDHEC - OCRM Team</p>
            </body>"""
    except Exception as e:

        print(str(e))

        
    
if __name__=='__main__':
   send_gmail(sys.argv)