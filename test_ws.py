import requests

r = requests.get('https://j3pzzpju7m.us-east-1.awsapprunner.com/healthz')
print(r.status_code)
