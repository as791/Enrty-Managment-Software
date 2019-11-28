# Enrty Managment Software
This application is built using Python Flask framework to capture the visitor details that we have in the offices. This application saves name, email id, phone number of visitor and host in databases with check in and check out timestamp of the visitor. 
At the back end, once the user enters the information in the form, the backend should store all of the information with time stamp of the entry.This trigger an email and an SMS to the host informing him of the details of the visitor. There is also a provision of the checkout time which is feed to database once the visitor go and checkout manaully using his name, and same email and phone number entered during checking in. This triggers an email to the visitor with the complete form which includes:
- Name     
- Phone
- Check in time
- Check out time
- Host name
- Address visited

## Installation
Before Navigating the application user must install the required libraries using following command
``` bash
pip install -r requirements.txt
```

## Configuration

### Database server setup
First Create a database using postgreSQL which should always be connected with the flask server in the background this is done using sqlalchemy and psycopg2. Then use CREATE TABLE query for creating the proposed table.
```python
app = Flask(__name__)

DB_URI = 'postgresql+psycopg2://username:password@localhost/database'

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # silence the deprecation warning

# init SQL
sql = SQLAlchemy(app)
engine = sql.create_engine(DB_URI,{})
connection = engine.raw_connection()

#Creating table 
cur  = connection.cursor()

#Execute query
cur.execute("CREATE TABLE visitor1(Entry_date VARCHAR(50), Host_name VARCHAR(255), Host_email VARCHAR(255), Host_contact_no VARCHAR(12), Visitor_name VARCHAR(255), Visitor_email VARCHAR(255), Visitor_contact_no VARCHAR(12), check_in_time VARCHAR(50), check_out_time VARCHAR(50))")

# Commit to DB
connection.commit()
```

### Email Function Setup
First enable the less secure apps option by going to google account secuirty settings.
```python
def send_email(reciever_email,sender_email,password,message,subject):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = reciever_email
    html = message
    part1 = MIMEText(html, 'html')
    msg.attach(part1)
    smtp_server = "smtp.gmail.com"
    port = 587
    try:
        server = smtplib.SMTP(smtp_server,port)
        server.starttls() # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email,reciever_email,msg.as_string()) 
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit() 
```

### Message Function Setup
* First register on Twilio.
* Verify the number to get message on.
* Create the sender's number using Twilio service.
* Use authorized account sid, and token to connect to your personlize Twilio server. 
```python
def send_sms(message,phone_no):
    account_sid = 'AC5f5fe8cabdabc0bdf71b6311ea8419e6'
    auth_token = '4c887a5cb4c18bfccaa37c934e4e5bf6'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
                     body=message,
                     from_='+12024105519',
                     to=phone_no
                 );
```
### How to run the application?
* First keep all the files in same directory.
* For windows users create a virtual environment, then run the application OR users can also use sublime text or othe text editor to run the .py file.

### Demonstrated Visuals
- Home Page
![](/Screenshots/home%20page.png)
- About Us Page
![](https://github.com/as791/Enrty-Managment-Software/blob/master/Screenshots/about%20us%20page.png)
- Check-in Page
![](https://github.com/as791/Enrty-Managment-Software/blob/master/Screenshots/checkin%20page.png)
- Check-out Page
![](https://github.com/as791/Enrty-Managment-Software/blob/master/Screenshots/checkout%20page.png)
- Email to Host Preview
![](https://github.com/as791/Enrty-Managment-Software/blob/master/Screenshots/emailtohost.jpeg)
- Email to Visitor Preview
![](https://github.com/as791/Enrty-Managment-Software/blob/master/Screenshots/emailtovisitor.jpeg)
- SMS to Host
![](/Screenshots/smstohost.jpeg)
- Worklow can be viewed using this raw mhtml document :- 
### License
[MIT License](https://choosealicense.com/licenses/mit/)
### Some Key Points To Note
- Name for both Host and Visitor is limited to 50 characters.
- Phone number input is to be given with country code without '+' sign. 
- I have used used zone wise time and visitor has no need to give the check in or check out time, it is handeled automatically using datetime library, as it is more convinient for the visitor.
