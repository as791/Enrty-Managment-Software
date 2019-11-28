from flask import Flask, render_template, flash, redirect, url_for, session, request
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, validators
from passlib.hash import sha256_crypt
import psycopg2
import os
from datetime import datetime
import smtplib,ssl
from twilio.rest import Client
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd

app = Flask(__name__)
#creating database and connecting server of database with flask using sqlalchemy
DB_URI = 'postgresql+psycopg2://postgres:Arya@123@localhost/hotel_register'


app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # silence the deprecation warning

# init SQL
sql = SQLAlchemy(app)
engine = sql.create_engine(DB_URI,{})
connection = engine.raw_connection()

#Creating table first
# cur  = connection.cursor()

# # # Execute query
# cur.execute("CREATE TABLE visitor1(Entry_date VARCHAR(50), Host_name VARCHAR(255), Host_email VARCHAR(255), Host_contact_no VARCHAR(12), Visitor_name VARCHAR(255), Visitor_email VARCHAR(255), Visitor_contact_no VARCHAR(12), check_in_time VARCHAR(50), check_out_time VARCHAR(50))")

# # Commit to DB
# connection.commit()

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

def send_sms(message,phone_no):
    account_sid = 'AC5f5fe8cabdabc0bdf71b6311ea######'  #get your own account id for twilio
    auth_token = '4c887a5cb4c18bfccaa37c934e#####'      #auth token for the password
    client = Client(account_sid, auth_token)
    message = client.messages.create(
                     body=message,
                     from_='+12024105519', #first create your own sending phone number using twilio 
                     to=phone_no
                 );
# Home
@app.route('/')
def home():
    return render_template('home.html')

# About
@app.route('/about')
def about():
    return render_template('about.html')

# User check in
@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    if request.method == 'POST':
        host_name = request.form.get('HostName')
        host_email = request.form.get('HostEmail')
        host_phone_no = request.form.get('HostPhoneNumber')
        visitor_name = request.form.get('VisitorName')
        visitor_email = request.form.get('VisitorEmail')
        visitor_phone_no =request.form.get('VisitorPhoneNumber')

        check_in_time = datetime.now().strftime("%I:%M %p")
        # Create cursor
        cur = connection.cursor()
        entry_date = datetime.now().strftime("%y/%m/%d")
        # Execute query
        cur.execute("INSERT INTO visitor1(entry_date,host_name,host_email,host_contact_no,visitor_name,visitor_email,visitor_contact_no,check_in_time) VALUES(%s,%s, %s, %s, %s, %s, %s, %s);", 
            (entry_date,host_name,host_email,host_phone_no,visitor_name,visitor_email,visitor_phone_no,check_in_time))

        # Commit to DB
        connection.commit()
        # Close connection
        cur.close()

        flash('You have checked in successfully', 'success')

        message = "Hi there " + visitor_name + " is here to visit you.\nContact No: +" + visitor_phone_no + "\nEmail: " + visitor_email + "\nCheck In Time: " + check_in_time
        subject = "You Latest Visitor Details"
        message1 =  '''<html>
                        <head>
                            <meta charset="utf-8">
                                <div class="cover-container d-fle -->x w-100 h-100 p-3 mx-auto flex-column">
                                    <header class="masthead mb-auto">
                                        <div class="text-center">
                                            <h2 class="masthead-brand">Deatils of your visitor</h2>
                                                <body>
                                                    <table border="2">
                                                    <tr>
                                                        <th> Name </th>
                                                        <th> Phone </th>
                                                        <th> Email </th>
                                                        <th> Check In Time </th>
                                                    </tr>
                                                    <tr>
                                                        <th> {} </th>
                                                        <th> +{} </th>
                                                        <th> {} </th>
                                                        <th> {} </th>
                                                    <tr>
                                                </body>
                                             </div>
                                    </header>
                                </div>
                        </head>
                        </html>'''.format(visitor_name,visitor_phone_no,visitor_email,check_in_time)
        print(host_email)
        send_email(host_email,'aryamansinha123@gmail.com','#########',message1,subject)
        send_sms(message,'+'+host_phone_no)  #host_phone_no should be twilio verified !!

        return redirect(url_for('home'))

    return render_template('checkin.html')

# User check out
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        name = request.form.get('VisitorName')
        email = request.form.get('VisitorEmail')
        phone_no = request.form.get('VisitorPhoneNumber')
        
        check_out_time = datetime.now().strftime("%I:%M %p")
        # Create cursor
        cur = connection.cursor()

        check_out_date = datetime.now().strftime("%y/%m/%d")
        cur.execute("SELECT * FROM visitor1 WHERE visitor_name = %s AND entry_date=%s", (name,check_out_date))

        check_cur = cur.fetchone()
        # Get visitor by name 
        if len(check_cur)>0:
        # Get stored hash
            data = cur.fetchone()
            visitor_phone_no = data[6]  #tuple key for the fetched row check accordingly
            visitor_email = data[5]
            check_in_time = data[8]
            # Compare Details
            if visitor_phone_no == phone_no and visitor_email == email:
                # Passed
                session['logged_in'] = True
                session['name'] = name

                cur.execute("UPDATE visitor1 SET check_out_time = %s WHERE  visitor_name = %s" , (check_out_time,name))

                connection.commit()

                flash('You have now checked out successfully', 'success')

                address = "A-578, Queens Consolidated, Starling City"  #Required address of office
                subject = "Your Latest Visit Details"
                message1 = '''
                        <html>
                        <head>
                            <meta charset="utf-8">
                                <div class="cover-container d-fle -->x w-100 h-100 p-3 mx-auto flex-column">
                                    <header class="masthead mb-auto">
                                        <div class="text-center">
                                            <h2 class="masthead-brand">Deatils of your visit</h2>
                                                <body>
                                                    <table border="2">
                                                    <tr>
                                                        <th> Name </th>
                                                        <th> Phone </th>
                                                        <th> Check In Time </th>
                                                        <th> Check Out Time </th>
                                                        <th> Host Name </th>
                                                        <th> Address </th>
                                                    </tr>
                                                    <tr>
                                                        <th> {} </th>
                                                        <th> +{} </th>
                                                        <th> {} </th>
                                                        <th> {} </th>
                                                        <th> {} </th>
                                                        <th> {} </th>
                                                    <tr>
                                                </body>
                                             </div>
                                    </header>
                                </div>
                        </head>
                        </html>'''.format(name,visitor_phone_no,check_in_time,check_out_time,data[1],address)
                
                send_email(visitor_email,'aryamansinha123@gmail.com','#########',message1,subject)

                return redirect(url_for('home'))
            else:
                error = 'Invalid details'
                return render_template('checkout.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Error'
            return render_template('checkout.html', error=error)

    return render_template('checkout.html')


if __name__ == '__main__':
    app.secret_key='secret@123'
    app.run(debug=True)
