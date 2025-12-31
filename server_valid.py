import common


class ServerValid:
	def valid_server(self, server_name):
		req_path = '/vserver/v2/getServerInstanceList?serverName=' + server_name + '&responseFormatType=json'.format('string')
		res = common.send(req_path)

		#리턴 되는 결과값은 like 결과이므로, for 문을 통한 정확한 이름 검색 필요
		for object in res['getServerInstanceListResponse']['serverInstanceList']:
			if server_name == object['serverName']:
				#print("server_name = " + server_name + " is exist.")	
				return object['serverInstanceNo']
		
		print(">>> server_name = " + server_name + " is none exist.")
		return False


	def valid_server_status(self, server_name, status_code, print_yn):
		req_path = '/vserver/v2/getServerInstanceList?serverName=' + server_name + '&responseFormatType=json'.format('string')
		res = common.send(req_path)


		#리턴 되는 결과값은 like 결과이므로, for 문을 통한 정확한 이름 검색 필요
		for object in res['getServerInstanceListResponse']['serverInstanceList']:
			#print("servername = " +  object['serverName'] + ", server no = " + object['serverInstanceNo'])
			#print("servername = " +  object['serverName'] + ", status = " + object['serverInstanceStatus']['code'])
			if server_name == object['serverName']:
				status = object['serverInstanceStatus']['code']
				#print("status  = " + status )	
				if ("RUN" == status_code or "NSTOP" == status_code):
					if status == status_code:
						return object['serverInstanceNo']
				else:
					if status == "RUN" or status == "NSTOP":
						return object['serverInstanceNo']

				if print_yn:
					print(">>> valid_server_status() status not matched. find status_code = " + status_code)
					print(">>> valid_server_status() server_name = " + server_name + ", now_status = " + status)						
					return False

		if print_yn:
			print(">>> valid_server_status() can't find. server_name = " + server_name)

		return False

	
	def get_server_instancelist(self, print_yn):
		req_path = '/vserver/v2/getServerInstanceList?responseFormatType=json'.format('string')
		res = common.send(req_path)

		if print_yn:
			print(">>>>>>>>>>  server infomation  <<<<<<<<<<")
			for object in res['getServerInstanceListResponse']['serverInstanceList']:
				print("server_name = " + object['serverName'] + ",  uptime = " + object['uptime'])
			print(">>>>>>>>>>  ===    END    ===  <<<<<<<<<<")

		return res
 

	# 블록 스토리지 리스트 조회
	def get_blockStorage_list(self, print_yn):
		req_path = '/vserver/v2/getBlockStorageInstanceList?responseFormatType=json'.format('string')
		res = common.send(req_path)

		if print_yn:
			print(">>>>>>>>>>  blockStorage infomation  <<<<<<<<<<")
			for object in res['getBlockStorageInstanceListResponse']['blockStorageInstanceList']:
				print("blockStorageInstanceNo = " + object['blockStorageInstanceNo'] + ",  blockStorageName = " + object['blockStorageName'])
			print(">>>>>>>>>>  ===    END    ===  <<<<<<<<<<")

		return res

	# 블록스토리지 할당 해제
	def detach_blockStorage(self, storageNo, print_yn): 
		req_path = '/vserver/v2/detachBlockStorageInstances?blockStorageInstanceNoList.1=' + storageNo + '&responseFormatType=json'.format('string')
		res = common.send(req_path) 
  
		if print_yn:
			print(">>>>>>>>>>  detach_blockStorage infomation  <<<<<<<<<<")
			print(res)
			print(">>>>>>>>>>  ===    END    ===  <<<<<<<<<<")
   
		if res['detachBlockStorageInstancesResponse']['returnMessage'] == "success":
			return True
		else:
			return False


	# 블록스토리지 반납 보호 해제   
	def set_blockStorage_return_protection(self, server_no, print_yn): 
		req_path = '/vserver/v2/setBlockStorageReturnProtection?blockStorageInstanceNo=' + server_no + '&isReturnProtection=false&responseFormatType=json'.format('string')
		res = common.send(req_path) 
  
		if print_yn:
			print(">>>>>>>>>>  set_blockStorage_return_protection infomation  <<<<<<<<<<")
			print(res)
			print(">>>>>>>>>>  ===    END    ===  <<<<<<<<<<")
   
		if res['setBlockStorageReturnProtectionResponse']['returnMessage'] == "success":
			return True
		else:
			return False

	# 서버 반납 보호 해제   
	def set_protect_server_termination(self, server_no, print_yn): 
		req_path = '/vserver/v2/setProtectServerTermination?serverInstanceNo=' + server_no + '&isProtectServerTermination=false&responseFormatType=json'.format('string')
		res = common.send(req_path) 
  
		if print_yn:
			print(">>>>>>>>>>  set_protect_server_termination infomation  <<<<<<<<<<")
			print(res)
			print(">>>>>>>>>>  ===    END    ===  <<<<<<<<<<")
   
		if res['setProtectServerTerminationResponse']['returnMessage'] == "success":
			return True
		else:
			return False


	# 서버 반납
	def terminate_server(self, server_no, print_yn):
		req_path = '/vserver/v2/terminateServerInstances?serverInstanceNoList.1=' + server_no + '&responseFormatType=json'.format('string')
		res = common.send(req_path)
  
		if print_yn:
			print(">>>>>>>>>>  terminate_server infomation  <<<<<<<<<<")
			print(res)
			print(">>>>>>>>>>  ===    END    ===  <<<<<<<<<<")
   
		if res['terminateServerInstancesResponse']['returnMessage'] == "success":
			return True
		else:
			return False

	# publicIp 조회
	def get_publicIp_list(self, print_yn):
		req_path = '/vserver/v2/getPublicIpInstanceList?responseFormatType=json'.format('string')
		res = common.send(req_path)

		if print_yn:
			print(">>>>>>>>>>  publicIp infomation  <<<<<<<<<<")
			for object in res['getPublicIpInstanceListResponse']['publicIpInstanceList']:
				print("publicIpInstanceNo = " + object['publicIpInstanceNo'] + ",  publicIp = " + object['publicIp'])
			print(">>>>>>>>>>  ===    END    ===  <<<<<<<<<<")

		return res
	
	# publicIp 삭제
	def delete_publicIp(self, server_no, print_yn):
		req_path = '/vserver/v2/deletePublicIpInstances?publicIpInstanceNoList.1=' + server_no + '&responseFormatType=json'.format('string')
		res = common.send(req_path)

		if print_yn:
			print(">>>>>>>>>>  publicIp infomation  <<<<<<<<<<")
			for object in res['getPublicIpInstanceListResponse']['publicIpInstanceList']:
				print("publicIpInstanceNo = " + object['publicIpInstanceNo'] + ",  publicIp = " + object['publicIp'])
			print(">>>>>>>>>>  ===    END    ===  <<<<<<<<<<")

		return res    



