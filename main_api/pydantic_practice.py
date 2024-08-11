from pydantic import BaseModel

class Email(BaseModel):
    to: str
    sender: str
    # timestamp: datetime
    subject: str

if __name__ == '__main__':
    email1 = Email(to="test@gmail.com", sender="sender@gmail.com", subject=10)
