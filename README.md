# SSL Alert

Read domains from file and generate alert if SSL certificate expires within specified number of days (-d/--days)

Usage:
```
./check_ssl.py -d 30
```
Send an email alert:
```
./check_ssl.py -d 30 -e
```
