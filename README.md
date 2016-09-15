# zimbra-response-time-checker
Simple Python script to report response time of Zimbra's SMTP server and webmail site to Slack channel.

## Installation
You can install it by typing:
```bash
git clone https://github.com/deanrock/zimbra-response-time-checker/
cd zimbra-response-time-checker/
virtualenv -ppython3 ./venv/
source ./venv/
pip install -r requirements.txt
```

## Usage
The script is configured via the following environmental variables:
* SLACK_TOKEN = token of slack bot user
* SLACK_CHANNEL = channel where it should post notification
* CHECK_INTERVAL = interval in seconds after which is should report current response time (even if it's below treshold
* THRESHOLD = interval in seconds (float) that should trigger instant Slack notification if any check exceeds this theshold
* WEBMAIL = URL to webmail
* USER = email address and username used to connect to SMTP/webmail
* PASSWORD = password of the user to connect to SMTP/webmail
* HOST = Zimbra SMTP host
* PORT = Zimbra SMTP port

You can create script `script.sh` similar to this:
```bash
#!/bin/bash
export SLACK_TOKEN=xoxb-...
export SLACK_CHANNEL=#zimbra
export CHECK_INTERVAL=7200
export THRESHOLD=3
export WEBMAIL=https://mail.example.com/zimbra/
export USER=test.zimbra@example.com
export PASSWORD=somePassword
export HOST=mail.example.com
export PORT=587
python script.py
```
and then you can start the checker via:
```bash
chmod +x ./script.sh
./script.sh
```
