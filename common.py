import json
import datetime
import urllib.request

from api_sender import APISender
from base_auth_info import BaseAuthInfo

####################         sender            ####################	
def send(req_path):
    #print("req_path = " + req_path)
    base_auth_info = BaseAuthInfo()
    base_auth_info.set_req_path(req_path)
    sender = APISender(base_auth_info)
		
    response = sender.request()
    res_list = response.read()		
    return json.loads(res_list.decode('utf-8'))		


####################         billing sender            ####################	
def send_billing(req_path):
     
    base_auth_info = BaseAuthInfo()
    base_auth_info.set_req_path(req_path)
    sender = APISender(base_auth_info)
		
    response = sender.req_billing_send()
    res_list = response.read()		
    return json.loads(res_list.decode('utf-8'))		

####################         email sender            ####################	
def send_email(req_path, mail_info):
     
    base_auth_info = BaseAuthInfo()
    base_auth_info.set_req_path(req_path)
    sender = APISender(base_auth_info)
		
    response = sender.req_email_send(mail_info)
    res_list = response.read()		
    return json.loads(res_list.decode('utf-8'))		

####################         send Slack Message           ####################	
def send_slack_message(message) :
    
    req_path = ""    
    message = {"text" : message}
    
    req = urllib.request.urlopen(req_path,json.dumps(message).encode('utf-8'))
    
    return True

####################         get today            ####################	
def get_today():
    create_time = datetime.datetime.now()
    create_fmt = create_time.strftime('%Y%m%d')
    #print(">>> get_today = " + create_fmt)
    return create_fmt

def get_today_yymmdd():
    create_time = datetime.datetime.now()
    create_fmt = create_time.strftime('%Y%m%d')
    create_fmt = create_fmt[2:8]
    #print(">>> get_today = " + create_fmt)
    return create_fmt