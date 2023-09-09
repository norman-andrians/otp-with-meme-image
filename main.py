import os
import random
import ssl
import smtplib

from flask import Flask, jsonify, request
from PIL import Image, ImageDraw, ImageFont

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

app = Flask(__name__)

def add_textimg(text, code):
    path = f"images/output/pos-{str(code)}.jpg"

    try:
        img = Image.open("images/main/shannon.jpg")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("fonts/impact.ttf", 24)

        text_pos1_center = (img.width - draw.textlength(text, font)) // 2
        text_pos2_center = (img.width - draw.textlength(code, font)) // 2

        text_pos_bottom = img.height

        pos1 = (text_pos1_center, text_pos_bottom - 90)
        pos2 = (text_pos2_center, text_pos_bottom - 60)
        text_color = (255, 255, 255)

        draw.text(pos1, text, fill=text_color, font=font)
        draw.text(pos2, code, fill=text_color, font=font)

        if not os.path.exists("images/output"):
            os.mkdir("images/output")
        
        img.save(path)
        img.close()
    except Exception as e:
        print("Failed to add image")
        print(str(e))

@app.route('/hello', methods=['GET'])
def hello():
    return "Hello"

@app.route('/test/otp', methods=['POST'])
def generate_otp():
    try:
        randis = random.randint(1000, 9999)
        add_textimg(f"Your verification code is", str(randis))

        return jsonify({"status": "ok"})
    except Exception as e:
        print("Something went wrong")
        print(str(e))

        return jsonify({"error": str(e)})

@app.route('/send-otp', methods=['POST'])
def send_email():
    # Create an .env file at the root of this project
    # There are two values required here, EMAIL_SENDER and EMAIL_PASSWORD
    # Or you can change the value here and in .env file
    mail_sender = os.environ.get("EMAIL_SENDER")
    mail_password = os.environ.get("EMAIL_PASSWORD")
    mail_receiver = request.args.get('email')

    # Everyone has a different email host service
    # By default we use gmail to test our emails
    mail_host = os.environ.get("HOST") if os.environ.get("HOST") is not None else "smtp.gmail.com"
    mail_port = 465

    if mail_sender is None and mail_password is None:
        return jsonify({
            "status": 400,
            "error": "Bro did you forget to add the sender email and email password variables in the .env file?"
        }), 400

    if mail_receiver is None:
        return jsonify({
            "status": 400,
            "error": "You must include an email address param query to send to email"
        }), 400

    try:
        randis = random.randint(1000, 9999)

        # message variable
        subject = "confirm your account"
        msg = "Here's your email confirmation"

        zmail = MIMEMultipart()
        zmail['From'] = mail_sender
        zmail['To'] = mail_receiver
        zmail['Subject'] = subject

        # attach text
        zmail.attach(MIMEText(msg, 'plain'))

        # attach picure
        add_textimg("Your verification code is", str(randis))
        pict = open(f"images/output/pos-{str(randis)}.jpg", "rb").read()
        zmail.attach(MIMEImage(pict, name="black-man-wearing-suit.jpg"))

        # creating context
        context = ssl.create_default_context()

        # if SSL is a different version, maybe try not using SSL
        # with smtplib.SMTP(mail_host, mail_port) as smtp:
        with smtplib.SMTP_SSL(mail_host, mail_port, context=context) as smtp:
            smtp.login(mail_sender, mail_password)
            smtp.sendmail(mail_sender, mail_receiver, zmail.as_string())

        return jsonify({
            "status": 200,
            "message": "Success sending email",
            "email": {
                "sender": mail_sender,
                "receiver": mail_receiver,
                "subject": subject,
                "body": msg
            }
        })
    except Exception as e:
        print("Failed to send a email")
        print(str(e))

        return jsonify({
            "error": str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True)