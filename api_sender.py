import hashlib
import hmac
import base64
import time
import urllib.parse
import urllib.request
import ssl
import json


class APISender:

    def __init__(self, base_auth_info):
        self.access_key = base_auth_info.get_access_key()
        self.access_secret = base_auth_info.get_access_secret()
        self.url = base_auth_info.get_url()
        self.email_url = base_auth_info.get_email_url()
        self.billing_url = base_auth_info.get_billing_url()
        self.req_path = base_auth_info.get_req_path()

    def request(self):
        context = ssl._create_unverified_context()

        full_path = self.url + self.req_path
        req = urllib.request.Request(full_path)

        timestamp = self.get_timestamp()
         
        req.add_header('x-ncp-apigw-timestamp', timestamp)
        req.add_header('x-ncp-iam-access-key', self.access_key)
        req.add_header('x-ncp-apigw-signature-v2', self.make_signature(timestamp))

        print("==> full_path : " + full_path)
        print("==> timestamp : " + timestamp)
        print("==> make_signature : " + str(self.make_signature(timestamp)))
        
        response = urllib.request.urlopen(req, context=context)
        
        return response
    
    def req_billing_send(self):
        context = ssl._create_unverified_context()

        full_path = self.billing_url + self.req_path
        req = urllib.request.Request(full_path)

        timestamp = self.get_timestamp()
         
        req.add_header('x-ncp-apigw-timestamp', timestamp)
        req.add_header('x-ncp-iam-access-key', self.access_key)
        req.add_header('x-ncp-apigw-signature-v2', self.make_signature(timestamp))

        print("==> full_path : " + full_path)
        print("==> timestamp : " + timestamp)
        print("==> make_signature : " + str(self.make_signature(timestamp)))
        
        response = urllib.request.urlopen(req, context=context)

        return response
    
    def req_email_send(self, mail_info):

        context = ssl._create_unverified_context()
    
        full_path = self.email_url + self.req_path
        req = urllib.request.Request(full_path)

        timestamp = self.get_timestamp()

        req.add_header('x-ncp-apigw-timestamp', timestamp)
        req.add_header('x-ncp-iam-access-key', self.access_key)
        req.add_header('x-ncp-apigw-signature-v1', self.make_signature_post(timestamp))
        req.add_header('Content-Type', 'application/json')

        json_data = json.dumps(mail_info)
        json_data_bytes = json_data.encode('utf-8')
        print("==> full_path : " + full_path)
        print("==> timestamp : " + timestamp)
        print("==> make_signature : " + str(self.make_signature_post(timestamp)))

        response = urllib.request.urlopen(req, json_data_bytes, context=context)

        return response

    @staticmethod
    def get_timestamp():
        timestamp = int(time.time() * 1000)
        timestamp = str(timestamp)
        return timestamp

    def make_signature(self, timestamp):
        access_secret_bytes = bytes(self.access_secret, 'UTF-8')

        method = "GET"
        ep_path = self.req_path

        message = method + " " + ep_path + "\n" + timestamp + "\n" + self.access_key
        message = bytes(message, 'UTF-8')
        signing_key = base64.b64encode(hmac.new(access_secret_bytes, message, digestmod=hashlib.sha256).digest())
    
        return signing_key

    def make_signature_post(self, timestamp):
        access_secret_bytes = bytes(self.access_secret, 'UTF-8')

        method = "POST"
        ep_path = self.req_path
        
        message = method + " " + ep_path + "\n" + timestamp + "\n" + self.access_key
        message = bytes(message, 'UTF-8')
        signing_key = base64.b64encode(hmac.new(access_secret_bytes, message, digestmod=hashlib.sha256).digest())
    
        return signing_key
