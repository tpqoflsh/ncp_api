import json
import common
import datetime

from server_valid import ServerValid
from server_ctl import ServerControll



class ServerImage:
	global WAIT_TIME
	WAIT_TIME = 600

	## Server NSTOP 상태일때만 서버이미지 생성
	def create_server_image(self, server_name, store_type, store_count):

		server_valid = ServerValid()
		server_id = server_valid.valid_server_status(server_name, "NSTOP", True)
		if not server_id:
			return

		image_name = self._create_server_image(server_id, server_name, store_type, store_count)
		if image_name:
			print(">>> create_server_image() Success. server_name = " + server_name + ", image_name = " + image_name)


	## Server RUN 상태일때, NSTOP 변경 > 서버이미지 생성 > 서버 RUN 재기동
	def force_create_server_image(self, server_name, store_type, store_count):

		server_valid = ServerValid()
		server_ctl = ServerControll()

		if not server_valid.valid_server(server_name):
			return
		
		## Server RUN 상태 체크
		server_id = ""		
		server_status = server_valid.valid_server_status(server_name, "RUN", False)

		## Server RUN >> NSTOP 변경 
		server_id = server_ctl.change_server_status(server_name, "NSTOP", WAIT_TIME)
		if not server_id:
			return
		
		## Server 이미지 생성
		image_name = self._create_server_image(server_id, server_name, store_type, store_count)

		## Server 초기 상태가 RUN 인 경우, 서버 NSTOP >> RUN으로 다시 변경
		if server_status:
			server_ctl.change_server_status(server_name, "RUN", WAIT_TIME)

		print(">>> force_create_server_image() Success. server_name = " + server_name + ", image_name = " + image_name)



	# create server image
	def _create_server_image(self, server_id, server_name, store_type, store_count):
		#checking server image status
		if self._get_server_image_status(server_id, "INIT"):
			print(">>> _create_image() Fail. " + server_name + " server_image is being created.")
			return False		

		self._delete_server_image(server_id, store_type, store_count)		

		#get server image name
		image_name = self._get_server_image_unique_name(server_name)
		#create server image
		self._req_create_server_image(server_id, server_name, image_name)

		return image_name



	##### get server image name #####
	# memberServerImageName >> Max Length 30 character
	# img-server_name(23) + '-' + seq_number(2)

	def _get_server_image_unique_name(self, server_name):
		if server_name.find("vm-", 0) == 0:
			server_name = server_name[3:30]

		if len(server_name) > 23:
			server_name = server_name[0:23]
		
		server_name = "img-" + server_name

		#org_image_name = server_name + '-' + common.get_today_yymmdd()
		org_image_name = server_name
		image_name = org_image_name		

		seq_number = 0
		while(True):
			if self._get_server_image_name(image_name):
				seq_number = seq_number + 1
				if seq_number < 10:
					image_name = org_image_name + '-0' + str(seq_number)
				else:
					image_name = org_image_name + '-' + str(seq_number)
			else:
				break

		return image_name
	

	##### find server image name #####
	def _get_server_image_name(self, image_name):		
		req_path = '/vserver/v2/getMemberServerImageInstanceList?memberServerImageName=' + image_name \
					+ '&responseFormatType=json'.format('string')
		res = common.send(req_path)

		ret_count = res['getMemberServerImageInstanceListResponse']['totalRows']
		#print("ret_count = " + str(ret_count))
		if int(ret_count) > 0:
			return True
		return False


	##### find server image status #####
	def _get_server_image_status(self, server_name, status):		
		req_path = '/vserver/v2/getMemberServerImageInstanceList?responseFormatType=json'.format('string')
		res = common.send(req_path)
		#res = json.dumps(common.send(req_path))
		#print ("res = " + res)

		for object in res['getMemberServerImageInstanceListResponse']['memberServerImageInstanceList']:
			if server_name == object['originalServerInstanceNo'] and object['memberServerImageInstanceStatus']['code'] == status:
					return True
		return False


	
	##### delete server images #####
	def _delete_server_image(self, server_id, store_type, store_count):		
		req_path = '/vserver/v2/getMemberServerImageInstanceList?responseFormatType=json'.format('string')
		res = common.send(req_path)

		orderArr = {}
		sortedArr = []

		for object in res['getMemberServerImageInstanceListResponse']['memberServerImageInstanceList']:
			if server_id == object['originalServerInstanceNo']:
				str = object['createDate']
				key = str[0:4] + str[5:7] + str[8:10] + str[11:13] + str[14:16] + str[17:19]
				#print("server_id = " + server_id + ", create time = " + key)
				orderArr[key] = (object['memberServerImageInstanceNo'], object['memberServerImageName'], str[0:4], str[5:7], str[8:10])

		if len(orderArr) > 0:
			sortedArr = sorted(orderArr.items())

		#delete server image - Type
		if store_type == "count":
			del_count = len(sortedArr) - store_count + 1
			for object in sortedArr:				
				if del_count > 0:
					#print("del image No = " + object[1][0])
					self._req_delete_server_image(object[1][0])
					del_count = del_count - 1

		elif store_type == "day":			
			today = datetime.date.today()
			for object in sortedArr:				
				createDate = datetime.date(int(object[1][2]), int(object[1][3]), int(object[1][4]))
				diff_days = (today-createDate).days
				print(">>> _delete_server_image() : image No = " + object[1][0] + ", diff_days = ", diff_days)
				if diff_days > store_count:
					self._req_delete_server_image(object[1][0])

		else:
			print(">>> _delete_server_image() : Invalid store_type = " + store_type)

		return True


	######  create server image #####
	def _req_create_server_image(self, server_ids, server_name, image_name):		
		req_path = '/vserver/v2/createMemberServerImageInstance?serverInstanceNo=' + server_ids \
					+ '&memberServerImageName=' + image_name \
					+ '&memberServerImageDescription=' + server_name + '_AutoBackup_by_CloudFunction' \
					+ '&responseFormatType=json'.format('string')
		common.send(req_path)


	######  delete server image #####
	def _req_delete_server_image(self, image_id):		
		req_path = '/vserver/v2/deleteMemberServerImageInstances?memberServerImageInstanceNoList.1=' + image_id \
					+ '&responseFormatType=json'.format('string')
		common.send(req_path)


