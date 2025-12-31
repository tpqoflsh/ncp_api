import json
import common
import time
import datetime

from server_valid import ServerValid
from server_ctl import ServerControll


class ServerSnapshot:
	global WAIT_TIME
	WAIT_TIME = 600

	##### create server snapshot #####
	def create_server_snapshot(self, server_name, store_type, store_count):

		server_valid = ServerValid()
		server_ctl = ServerControll()

		server_id = server_valid.valid_server_status(server_name, "NORMAL" ,False)
		if not server_id:
			return

		#find server storage list
		storage_list = self._get_server_storage_list(server_name, server_id)
		if len(storage_list) < 1:
			return

		for storage_id in storage_list:
			if server_ctl.wait_server_status(server_name, "NORMAL", WAIT_TIME):
				if self._create_storage_snapshot_id(storage_id, store_type, store_count):
					time.sleep(10)
			else:
				print(">>> wait_for_server_normal_status() is fail. A long time has elapsed.")
				print(">>> server_name = " + server_name + ", storage_id = " + storage_id)				
				return

		print(">>> create_server_snapshot() completed. server_name = " + server_name)



	##### create storage snapshot by storage_name #####
	def create_storage_snapshot_name(self, storage_name, store_type, store_count):
		storage_id = self._get_storage_id(storage_name)
		if not storage_id:
			print(">>> create_storage_snapshot_name(). storage_name = " + storage_name + " can't find it.")
			return

		if self._check_storage_snapshot(storage_name, storage_id):
			self._create_snapshot(storage_name, storage_id, store_type, store_count)


	##### create storage snapshot by storage_id #####
	def _create_storage_snapshot_id(self, storage_id, store_type, store_count):
		storage_name = self._get_storage_name(storage_id)
		if not storage_name:
			print(">>> _create_storage_snapshot_id(). storage_id = " + storage_id + " can't find it.")
			return

		if self._check_storage_snapshot(storage_name, storage_id):
			self._create_snapshot(storage_name, storage_id, store_type, store_count)

	
	def _create_snapshot(self, storage_name, storage_id, store_type, store_count):
		
		self._delete_storage_snapshot(storage_name, storage_id, store_type, store_count)
		org_storage_name = storage_name
		
		#create storage snapshot
		#blockStorageSnapshotName >> Max Length 30 character	
		# snap-storage_name(22) + '-' + seq_number(2)	
		if storage_name.find("stvm-", 0) == 0:
			storage_name = storage_name[5:30]

		if len(storage_name) > 22:
			storage_name = storage_name[0:22]
		
		storage_name = "snap-" + storage_name

		#org_snapshot_name = storage_name + '-' + common.get_today_yymmdd()
		org_snapshot_name = storage_name
		snapshot_name = org_snapshot_name

		seq_number = 0
		while(True):
			if self._get_storage_snapshot_name(snapshot_name):
				seq_number = seq_number + 1
				if seq_number < 10:
					snapshot_name = org_snapshot_name + '-0' + str(seq_number)
				else:
					snapshot_name = org_snapshot_name + '-' + str(seq_number)
			else:
				break

		#print("storage snapshot, storage_id = " + storage_id)
		req_path = '/vserver/v2/createBlockStorageSnapshotInstance?originalBlockStorageInstanceNo=' + storage_id \
					+ '&blockStorageSnapshotName=' + snapshot_name \
					+ '&blockStorageSnapshotDescription=' + storage_name + '_AutoBackup_by_CloudFunction' \
					+ '&responseFormatType=json'.format('string')
		common.send(req_path)

		print(">>> _create_snapshot() completed. storage_name = " + org_storage_name)


	##### Checking snapshot of storage >> not create operation #####
	def _check_storage_snapshot(self, storage_name, storage_id):
		req_path = '/vserver/v2/getBlockStorageSnapshotInstanceList?originalBlockStorageInstanceNoList.1=' + storage_id + '&responseFormatType=json'.format('string')
		res = common.send(req_path)		

		for object in res['getBlockStorageSnapshotInstanceListResponse']['blockStorageSnapshotInstanceList']:
			if "INIT" == object['blockStorageSnapshotInstanceStatus']['code']:
				##print(">>> _check_storage_snapshot() snapshot_status = " + object['blockStorageSnapshotInstanceStatus']['code'])
				print(">>> _check_storage_snapshot() : storage_name = " + storage_name + " is creating.")
				return False

		return True

	
	##### find storage snapshot name #####
	def _get_storage_snapshot_name(self, snapshot_name):
		req_path = '/vserver/v2/getBlockStorageSnapshotInstanceList?blockStorageSnapshotName=' + snapshot_name + '&responseFormatType=json'.format('string')
		res = common.send(req_path)		

		for object in res['getBlockStorageSnapshotInstanceListResponse']['blockStorageSnapshotInstanceList']:
			if object['blockStorageSnapshotName'] == snapshot_name:
				return True
		return False






	##### delete storage snapshot  #####
	def _delete_storage_snapshot(self, storage_name, storage_id, store_type, store_count):	
		req_path = '/vserver/v2/getBlockStorageSnapshotInstanceList?originalBlockStorageInstanceNoList.1=' + storage_id + '&responseFormatType=json'.format('string')
		res = common.send(req_path)		

		orderArr = {}
		sortedArr = []
		for object in res['getBlockStorageSnapshotInstanceListResponse']['blockStorageSnapshotInstanceList']:
			str = object['createDate']
			key = str[0:4] + str[5:7] + str[8:10] + str[11:13] + str[14:16] + str[17:19]
			#print("create time = " + key + ", no = " + object['blockStorageSnapshotInstanceNo'])
			orderArr[key] = (object['blockStorageSnapshotInstanceNo'], object['blockStorageSnapshotName'], str[0:4], str[5:7], str[8:10])

		if len(orderArr) > 0:
			sortedArr = sorted(orderArr.items())
    
		#delete storage snapshot - Type
		if store_type == "count":
			del_count = len(sortedArr) - store_count + 1
			for object in sortedArr:				
				if del_count > 0:
					#print("del snapshot No = " + object[1][0])
					self._req_delete_storage_snapshot(object[1][0])
					del_count = del_count - 1

		elif store_type == "day":
			#counting server image - date
			today = datetime.date.today()
			for object in sortedArr:				
				createDate = datetime.date(int(object[1][2]), int(object[1][3]), int(object[1][4]))
				diff_days = (today-createDate).days
				print(">>> _delete_server_image() : snapshot No = " + object[1][0] + ", diff_days = ", diff_days)
				if diff_days > store_count:
					self._req_delete_storage_snapshot(object[1][0])

		else:
			print(">>> _delete_storage_snapshot() : Invalid store_type = " + store_type)

		return True





	#####  delete storage snapshot #####
	def _req_delete_storage_snapshot(self, snapshot_id):		
		req_path = '/vserver/v2/deleteBlockStorageSnapshotInstances?blockStorageSnapshotInstanceNoList.1=' + snapshot_id + '&responseFormatType=json'.format('string')
		common.send(req_path)




	##### find server storage list #####
	def _get_server_storage_list(self, server_name, sever_id):
		req_path = '/vserver/v2/getBlockStorageInstanceList?serverInstanceNo=' + sever_id + '&responseFormatType=json'.format('string')
		res = common.send(req_path)

		ret = []
		count = res['getBlockStorageInstanceListResponse']['totalRows']
		if count > 1:
			for object in res['getBlockStorageInstanceListResponse']['blockStorageInstanceList']:
				#print("devicename = " + object['deviceName'])
				#print("deviceID   = " + object['blockStorageInstanceNo'])
				device_name = object['deviceName']
				if device_name == '/dev/xvda' or device_name == 'Disk 0':
					continue
				else:
					#print("device_name = " + device_name + ", ID = " + object['blockStorageInstanceNo'])
					ret.append(object['blockStorageInstanceNo'])			
		else:
			print(">>> _get_server_storage_list() : server_name = " + server_name + ", server_id = " + sever_id + ", can't find storage.")

		return ret



	##### find storage name #####
	def _get_storage_name(self, storage_id):
		req_path = '/vserver/v2/getBlockStorageInstanceList?blockStorageInstanceNoList.1=' + storage_id + '&responseFormatType=json'.format('string')
		res = common.send(req_path)

		ret = False
		count = res['getBlockStorageInstanceListResponse']['totalRows']
		if count == 1:
			for object in res['getBlockStorageInstanceListResponse']['blockStorageInstanceList']:
				ret = object['blockStorageName']
				#print("storage_name = " + ret)
		
		return ret


	##### find storage id #####
	def _get_storage_id(self, storage_name):
		req_path = '/vserver/v2/getBlockStorageInstanceList?blockStorageName=' + storage_name + '&responseFormatType=json'.format('string')
		res = common.send(req_path)

		ret = False
		count = res['getBlockStorageInstanceListResponse']['totalRows']
		if count == 1:
			for object in res['getBlockStorageInstanceListResponse']['blockStorageInstanceList']:
				ret = object['blockStorageInstanceNo']
				#print("storage_id = " + ret)
		
		return ret
