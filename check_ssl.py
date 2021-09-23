#!/usr/bin/env python3

import socket
import ssl
import datetime
import smtplib
from email.mime.text import MIMEText
import argparse


sites_to_check = 'sites.conf'
smtp_server = 'smtp.smtp.com'
alert_sender = 'SSL Expiry Alert <you@email.com>'
alert_recipients_list = ['jane@gmail.com', 'bill@email.com']


parser = argparse.ArgumentParser(
    description='Check SSL certificate expiration.')

parser.add_argument('-d', '--days', dest='num_of_days', help='Number of days',
                    required=True, type=int, choices=range(1, 301))
parser.add_argument('-e', '--send_email',
                    action='store_true', help='Send email alert')

args = parser.parse_args()

days_to_expire = args.num_of_days


def ssl_expiry_datetime(hostname):
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'

    try:
        context = ssl.create_default_context()
        conn = context.wrap_socket(socket.socket(
            socket.AF_INET), server_hostname=hostname,)
    except socket.error as e:
        print ('An error occurred connecting to ', hostname, ': ', e)
        pass

    try:
        conn.connect((hostname, 443))
        ssl_info = conn.getpeercert()
        return datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)
    except Exception as e:
        pass


def ssl_valid_time_remaining(hostname):
    expires = ssl_expiry_datetime(hostname)
    return expires - datetime.datetime.utcnow()


def ssl_expires_in(hostname, buffer_days=days_to_expire):

    try:
        remaining = ssl_valid_time_remaining(hostname)
        if remaining < datetime.timedelta(days=0):
            raise AlreadyExpired("Cert expired %s days ago" % remaining.days)
        elif remaining < datetime.timedelta(days=buffer_days):
            return True
        else:
            return False
    except Exception as e:
        print ('An error occurred connecting to ', hostname, ': ', e)
        pass


def send_an_email(message):

    alert_recipients = ", ".join(alert_recipients_list)

    msg = MIMEText(message)

    msg['Subject'] = message
    msg['From'] = alert_sender
    msg['To'] = alert_recipients

    s = smtplib.SMTP(smtp_server)
    s.sendmail(alert_sender, alert_recipients_list, msg.as_string())
    s.quit()


def send_an_email_debugging_server(message):

    # to start local email debugging server
    # python3 -m smtpd -c DebuggingServer -n localhost:1025

    alert_recipients = ", ".join(alert_recipients_list)

    port = 1025
    msg = MIMEText(message)

    msg['Subject'] = message
    msg['From'] = alert_sender
    msg['To'] = alert_recipients

    with smtplib.SMTP('localhost', port) as server:
        server.sendmail(alert_sender, alert_recipients_list, msg.as_string())


def main():

    sites = open(sites_to_check).read().splitlines()

    for s in sites:

        is_expiring = ssl_expires_in(s)
        if is_expiring is True:
            time_remaining = ssl_valid_time_remaining(s)
            days_only = str(time_remaining).split(',')

            alert = 'SSL certificate ' + s + \
                ' expires in ' + days_only[0] + '!'

            print(alert)

            if args.send_email:
                send_an_email_debugging_server(alert)
                # send_an_email(alert)

        else:
            pass


if __name__ == "__main__":
    main()
