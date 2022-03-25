# library imports
import yagmail

# project imports


class EmailSender:
    """
    Responsible to send emails for the web-application
    """

    def __init__(self,
                 user_name: str,
                 password: str):
        try:
            self._api = yagmail.SMTP(user_name,
                                     password)
        except Exception as error:
            pass

    def send(self,
             to_email: str,
             subject: str,
             content: str,
             attachments: list):
        try:
            self._api.send(to=to_email,
                           subject=subject,
                           contents=content,
                           attachments=attachments)
        except Exception as error:
            pass
