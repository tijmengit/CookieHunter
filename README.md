# CookieHunter
## Setup
Clone repo and install requirements
```
git clone https://github.com/tijmengit/CookieHunter.git
cd CookieHunter
pip install -r requirements.txt
```

### Chromedriver
In order to run the Cookie Hunter Hacking Lab tool, you should download the Google Chromedriver from https://chromedriver.chromium.org.  
On Mac, place the chromedriver in:
```
/usr/local/sbin/
```
On Windows:
```
%LOCALAPPDATA%/ChromeDriver/
```
### Database
Create a new Firebase project at https://console.firebase.google.com/.  
Under Project settings -> Service accounts, generate a new private key.  
Move .json to /data/database-cred.json  

### Gmail Credentials
Activate the Gmail API at https://console.cloud.google.com/.  
For the Gmail API, create a OAuth 2.0 Client ID  
Download the .json linked to the new Client ID  
Move .json to /data/credentials.json  

## How to run
The system is created as a command line tool. There are three options on how to use the tool.  
### Option 1, sites.json
By adding websites in the sites.json file, the URL Discovery module will be bypassed.  
Please fill in domains for home page, registration and login as done in the example.  
After editing the json run from the same src directory:  
```
python __main__.py
```
### Option 2, using a domain
By specifying a home URL in the command line, the URL Discovery module will scan this domain for registration and login domains.  
Run from the src directory:  
```
python __main__.py -d example.org
```
### Option 3, using the Alexa list
You can also let the tool run through the Alexa list.   
This can either by done from the start of the list:  
``` 
python __main__.py -a
```
Or from a certain index:  
```
python __main__.py -a -s 1000
```
