import common
import time
import json
import datetime

from api_sender import APISender
from base_auth_info import BaseAuthInfo
from server_valid import ServerValid

class ServerControll:

	def start_server(self, server_name):
		server_valid = ServerValid()
		server_id = server_valid.valid_server_status(server_name, "NSTOP", True)		
		if not (server_id):
			return

		#print("server_id = " + server_id)
		req_path = '/vserver/v2/startServerInstances?serverInstanceNoList.1=' + server_id + '&responseFormatType=json'.format('string')
		res = common.send(req_path)
		#res = json.dumps(common.send(req_path))
		returnMessage = res['startServerInstancesResponse']['returnMessage']

		if returnMessage == "success":
			print(">>> start_server() Success. server_name = " + server_name + ", server_id = " + server_id)		
		else:
			print(">>> start_server() Fail. server_name = " + server_name + ", server_id = " + server_id)		



	def stop_server(self, server_name):
		server_valid = ServerValid()
		server_id = server_valid.valid_server_status(server_name, "RUN", True)
		if not (server_id):
			return
		
		#print("server_id = " + server_id)
		req_path = '/vserver/v2/stopServerInstances?serverInstanceNoList.1=' + server_id + '&responseFormatType=json'.format('string')
		res = common.send(req_path)		
		returnMessage = res['stopServerInstancesResponse']['returnMessage']

		if returnMessage == "success":
			print(">>> stop_server() Success. server_name = " + server_name + ", server_id = " + server_id)		
		else:
			print(">>> stop_server() Fail. server_name = " + server_name + ", server_id = " + server_id)		



	def all_stop_server(self, server_names): 
		server_valid = ServerValid()
		res = server_valid.get_server_instancelist(False)			

		target_server = []
		for object in res['getServerInstanceListResponse']['serverInstanceList']:			
			if object['serverName'] not in server_names and object['serverInstanceStatus']['code'] == "RUN":
				print("target server name = " + object['serverName'])
				target_server.append(object['serverInstanceNo'])
		
		if len(target_server) < 1:
			print(">>> all_stop_server() : Stop target server does not exist.")
			return False

		for server_id in target_server:
			#print("target server_id = " + server_id)
			req_path = '/vserver/v2/stopServerInstances?serverInstanceNoList.1=' + server_id + '&responseFormatType=json'.format('string')
			res = common.send(req_path)	
			returnMessage = res['stopServerInstancesResponse']['returnMessage']
			
			if returnMessage == "success":
				print(">>> all_stop_server() Success. server_id = " + server_id)		
			else:
				print(">>> all_stop_server() Fail. server_id = " + server_id)
			if returnMessage != "success":
				print(">>> all_stop_server() Fail. server_id = " + server_id)
			
		print(">>> all_stop_server() Completed.")
		return True


	def all_stop_server2(self, server_names): 
		print(">>>>>>>>>>>>>> all stop server2 <<<<<<<<<<<<<<<<<<<<<")
		# req_path = '/server/v2/getServerInstanceList?responseFormatType=json'. \
		# 	format(server_names)
		# res = self.sender(req_path)		
		server_valid = ServerValid()
		res = server_valid.get_server_instancelist(False)		
 
		target_server = []
		for object in res['getServerInstanceListResponse']['serverInstanceList']:			
			if object['serverName'] not in server_names and object['serverInstanceStatus']['code'] == "RUN":
				print("target server name = " + object['serverName'])
				target_server.append(object['serverInstanceNo'])
		
		if len(target_server) < 1:
			print("Target server does not exist.")
			return False

		for server_no in target_server:
			print("target server no = " + server_no)
			# req_path = '/server/v2/stopServerInstances?serverInstanceNoList.1=' + server_no + '&responseFormatType=json'. \
			# 	format(server_no)
			# self.sender(req_path)
			print(">>> all_stop_server() completed.")

		return True



	def delete_server_instance(self, print_yn):
		server_valid = ServerValid()
		res_instance_list = server_valid.get_server_instancelist(False)	
		res_blockStorage_list = server_valid.get_blockStorage_list(False)
		today =	datetime.datetime.now().date()
		before7days = today + datetime.timedelta(days=-8)

		target_server = []
		for object in res_instance_list['getServerInstanceListResponse']['serverInstanceList']:
			# 조건 변경 필요! < , STOP
			if datetime.datetime.strptime(object['uptime'][0:10], "%Y-%m-%d").date() < before7days and object['serverInstanceStatus']['code'] == "NSTOP" :				
				if object['isProtectServerTermination'] :
					server_valid.set_protect_server_termination(object['serverInstanceNo'], False) 
				target_server.append(object['serverInstanceNo'])

	
		# 추가 스토리지 할당 해제
		if len(target_server) < 1:
			print(">>> delete_server_instance() : Delete server does not exist.")
			return False
		else:
			for server_id in target_server:		 
				for object in res_blockStorage_list['getBlockStorageInstanceListResponse']['blockStorageInstanceList']: 
					
					if object['serverInstanceNo'] == server_id and object['blockStorageType']['code'] in "SVRBS": 
						if object['isReturnProtection'] :
							server_valid.set_blockStorage_return_protection(server_id, False) 
						res_detach = server_valid.detach_blockStorage(object['blockStorageInstanceNo'], False)
						if res_detach:
							print(">>> detach_blockStorage() Success. blockStorageInstanceNo = " + object['blockStorageInstanceNo'])
						else:
							print(">>> detach_blockStorage() Fail. blockStorageInstanceNo = " + object['blockStorageInstanceNo'])
		
		# 서버 반납
		if len(target_server) < 1:
			print(">>> delete_server_instance() : Delete server does not exist.")
			return False
		else:
			for server_id in target_server:	
				res_terminate = server_valid.terminate_server(server_id, False)	
				if res_terminate:
					print(">>> terminate_server() Success. server_id = " + server_id)
				else:
					print(">>> terminate_server() Fail. server_id = " + server_id)
		
		print(">>> delete_server_instance() Completed.")

		return True
	
 
	def delete_publicIp(self, print_yn) :
    		# publicIP 리스트 조회 getPublicIpInstanceList
		server_valid = ServerValid()  
		res_publicIp_list = server_valid.get_publicIp_list(False)
		

		target_publicIp = []
		for object in res_publicIp_list['getPublicIpInstanceListResponse']['publicIpInstanceList']:
			# 조건 변경 필요! < , STOP
			if object['publicIpInstanceStatusName'] == "created" :
				#print("delete server name = " + object['serverName'])
				target_publicIp.append(object['publicIpInstanceNo'])
		
		# 삭제 진행
		if len(target_publicIp) < 1:
			print(">>> delete_publicIp() : Delete publicIp does not exist.")
			return False
		else:
			for server_id in target_publicIp:	
				res_delete = server_valid.delete_publicIp(server_id, False)	
				if res_delete:
					print(">>> delete_publicIp() Success. server_id = " + server_id )
				else:
					print(">>> delete_publicIp() Fail. server_id = " + server_id)
		
		print(">>> delete_publicIp() Completed." )
  
		return True


	def change_server_status(self, server_name, server_status, wait_time):

		sec = 10
		tot_time = 0
		server_valid = ServerValid()
		ret = False

		while(True):
			if("RUN" == server_status):
				ret = server_valid.valid_server_status(server_name, "RUN", False)
				if ret:
					break
				server_id = server_valid.valid_server_status(server_name, "NSTOP", False)
				if server_id:
					req_path = '/vserver/v2/startServerInstances?serverInstanceNoList.1=' + server_id + '&responseFormatType=json'.format('string')
					res = common.send(req_path)
					#self.start_server(server_name)
				
			elif("NSTOP" == server_status):
				ret = server_valid.valid_server_status(server_name, "NSTOP", False)
				if ret:
					break
				server_id = server_valid.valid_server_status(server_name, "RUN", False)
				if server_id:
					req_path = '/vserver/v2/stopServerInstances?serverInstanceNoList.1=' + server_id + '&responseFormatType=json'.format('string')
					res = common.send(req_path)
					#self.stop_server(server_name)				
			else:
				print (">>> change_server_status(). Unkown server_status = " + server_status)
				return False

			time.sleep(sec)
			tot_time = tot_time + sec
			if(tot_time > wait_time):
				print (">>> change_server_status(). Wait time for server state change has been exceeded. waiting second = ", wait_time)
				return False

		print(">>> change_server_status() completed. server_name = " + server_name)
		return ret


	def wait_server_status(self, server_name, server_status, wait_time):

		sec = 10
		tot_time = 0
		server_valid = ServerValid()

		while(True):
			if("RUN" == server_status):
				if server_valid.valid_server_status(server_name, "RUN", False):
					return True
				
			elif("NSTOP" == server_status):
				if server_valid.valid_server_status(server_name, "NSTOP", False):
					return True

			elif("NORMAL" == server_status):
				if server_valid.valid_server_status(server_name, "NORMAL", False):
					return True

			else:
				print (">>> wait_server_status(). Unkown server_status = " + server_status)
				return False

			time.sleep(sec)
			tot_time = tot_time + sec
			if(tot_time > wait_time):
				print (">>> wait_server_status(). Wait time for server state change has been exceeded. waiting second = ", wait_time)
				return False		
		
		#print(">>> wait_server_status() completed. server_name = " + server_name)
		return True		


	def wait_server_status(self, server_name, server_status, wait_time):

		sec = 10
		tot_time = 0
		server_valid = ServerValid()

		while(True):
			if("RUN" == server_status):
				if server_valid.valid_server_status(server_name, "RUN", False):
					return True
				
			elif("NSTOP" == server_status):
				if server_valid.valid_server_status(server_name, "NSTOP", False):
					return True

			elif("NORMAL" == server_status):
				if server_valid.valid_server_status(server_name, "NORMAL", False):
					return True

			else:
				print (">>> wait_server_status(). Unkown server_status = " + server_status)
				return False

			time.sleep(sec)
			tot_time = tot_time + sec
			if(tot_time > wait_time):
				print (">>> wait_server_status(). Wait time for server state change has been exceeded. waiting second = ", wait_time)
				return False		
		
		#print(">>> wait_server_status() completed. server_name = " + server_name)
		return True		

	def check_remaining_credit(self, senderAddresses, print_yn):
		req_path = "/billing/v1/discount/getCreditHistoryList?responseFormatType=json"
		req_email_path = "/api/v1/mails"
		res = common.send_billing(req_path)
	
		credit_info = ''
		login_info = 'ncpbilling@cloit.com'
		for object in res['getCreditHistoryList']['creditHistoryList']:
			# login_info = object["loginId"]
			credit_info = "RemainingCredit(\) / ReceiveCredit(\) = "+ '{0:,}'.format(object["credit"]["remainingCredit"]) + " / " +  '{0:,}'.format(object["credit"]["receivedCredit"]) 
		if print_yn:
			print(">>>>>>>>>>  credit infomation  <<<<<<<<<<")
			print( credit_info )

      
		recipients = []
		if len(senderAddresses) > 0:
			for senderAddress in senderAddresses:
				recipients.append(
					{
						"address": senderAddress["address"],
						"name": senderAddress["name"],
						"type": "R",
						"parameters": {
							"credit": credit_info,
							"login_info": login_info
						}
					}
    			)
    
			mail_info = {
				"senderAddress": login_info,
				"senderName": "cloudFunction",
				"title": "[확인] NCP 잔여 크레딧 ",
				"body": """안녕하세요. </br>
						클로잇 NCP TEST계정에서 발송한 잔여 크레딧 관리를 위한 자동 메일 발송입니다. </br></br>
		
						NCP ${login_info} 계정의 잔여 크레딧을 확인하시고, 필요하신 경우 요청 하시길 바랍니다. </br>
						POC 크레딧은 매월 23일 이전에 신청해야 해당 월에 충전이 됩니다.  </br></br>
				
						* ${credit} </br></br>
				
						감사합니다.</br>
						""",
				"recipients": [],
				"individual": True,
				"advertising": False
			}	
	
			mail_info["recipients"] = recipients
   
			res_email = common.send_email(req_email_path, mail_info)
			if print_yn:
				print(">>> check_remaining_credit() completed. Successfully send. ")
				print(res_email)
		else:
			print(">>>>>>>>>>  The recipient does not exist.    <<<<<<<<<<")
			
	
		return True