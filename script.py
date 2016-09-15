import smtplib
import os
import requests
import time
from datetime import datetime
from slackclient import SlackClient


class ZimbraTester:
    def __init__(self):
        self.last_check_time = datetime.strptime(
            '2010-01-01 00:00:00',
            '%Y-%m-%d %H:%M:%S')

        self.sc = None

    def test_smtp(self):
        msg = ("From: %s\r\nTo: %s\r\n\r\n"
               % (self.fromaddr, ", ".join([self.fromaddr])))
        msg += 'Hello!'

        server = smtplib.SMTP(self.host, self.port)
        server.set_debuglevel(1)
        server.login(self.fromaddr, self.password)
        server.sendmail(self.fromaddr, [self.fromaddr], msg)
        server.quit()

        # if we reach this code it means that we successfully forwarded message
        # to SMTP server, otherwise it would already raised an exception
        return True

    def test_webmail(self):
        response = requests.post(self.webmail, {
            'loginOp': 'login',
            'username': self.fromaddr,
            'password': self.password,
            'client': 'preferred'
        })

        if response.status_code == 200:
            return True
        return False

    def check_time_diff_reached(self):
        total = (datetime.now() - self.last_check_time).total_seconds()
        return total > self.check_interval

    def test(self, method):
        start_time = time.time()

        error = None

        try:
            method()
        except Exception as e:
            error = e

        diff = time.time() - start_time

        print(diff)
        print(self.threshold)

        if diff > self.threshold:
            self.notify_slack(name=method.__name__,
                              time_taken=diff, error=error,
                              type='THRESHOLD REACHED')
        elif error:
            self.notify_slack(name=method.__name__,
                              time_taken=diff, error=error,
                              type='ERROR')
        elif self.check_time_diff_reached():
            self.notify_slack(name=method.__name__,
                              time_taken=diff, error=error)

    def notify_slack(self, name, time_taken, error, type=None):
        print('name=%s; time_taken=%s; error: %s'
              % (name, time_taken, error))

        if not self.sc:
            self.sc = SlackClient(self.slack_token)

        message = ''
        if type:
            message = '*%s* ' % type

        self.sc.api_call(
            "chat.postMessage",
            channel=self.slack_channel,
            text="%s*%s* response time: *%ds* (error: %s)"
            % (message, name, int(time_taken), error),
            username='zimbra-checker', icon_emoji=':robot_face:'
        )


if __name__ == '__main__':
    fromaddr = os.environ.get('USER')
    password = os.environ.get('PASSWORD')
    host = os.environ.get('HOST')
    port = os.environ.get('PORT')
    webmail = os.environ.get('WEBMAIL')
    threshold = os.environ.get('THRESHOLD')
    check_interval = os.environ.get('CHECK_INTERVAL')
    slack_token = os.environ.get('SLACK_TOKEN')
    slack_channel = os.environ.get('SLACK_CHANNEL')

    t = ZimbraTester()
    t.fromaddr = fromaddr
    t.password = password
    t.host = host
    t.port = port
    t.webmail = webmail
    t.threshold = float(threshold)
    t.check_interval = float(check_interval)
    t.slack_token = slack_token
    t.slack_channel = slack_channel

    while True:
        reached = t.check_time_diff_reached()

        t.test(t.test_smtp)
        t.test(t.test_webmail)

        if reached:
            t.last_check_time = datetime.now()

        time.sleep(60)
