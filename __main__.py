
import sys

from server_image import ServerImage
from server_snapshot import ServerSnapshot
from server_ctl import ServerControll
from server_valid import ServerValid
from server_image_sre3 import server_image_sre3


## parameters valid check ##
def valid_action(data):
	valid_action = ['START_SERVER', 'DELETE_SERVER_INSTANCE', 'STOP_SERVER', 'ALL_STOP_SERVER', 'INFO_SERVER','GET_SERVER_INSTANCELIST',
					'CREATE_SERVER_IMAGE', 'FORCE_CREATE_SERVER_IMAGE', 'CREATE_SERVER_SNAPSHOT', 'CREATE_STORAGE_SNAPSHOT','GET_BLOCKSTORAGE_LIST',
     				'DELETE_PUBLICIP','CHECK_REMAINING_CREDIT',
         			'CREATE_SERVER_IMAGE_SRE3']
					  
	for object in valid_action:
		if object == data:
			return data

	print(">>> valid_action() : Invalid Action = ", data)
	sys.exit()
	return False

def valid_data(data, data_name):
	if not data :
		print(">>> valid_data() : " + data_name + " values is Empty.")
		sys.exit()
	return data

def valid_data_ex(data, data_name): 
	if not data : 
		return "" 
	return data	

def valid_params(data, data_name, params):
	if not data :
		print(">>> valid_data_params() : " + data_name + " values is Empty.")
		sys.exit()

	for param in params:
		if data == param:
			return data
	
	print(">>> valid_data_params() : Invalid " + data_name + " = " + data)
	sys.exit()
	return False

def valid_int(data, data_name):
	if not data :
		print(">>> valid_data_params() : " + data_name + " values is Empty.")
		sys.exit()

	if not (str(type(data)) == "<class 'int'>"):
		print(">>> valid_int() : " + data_name + " is not integer.")
		sys.exit()

	if data < 1:
		print(">>> valid_int() : " + data_name + " is less than '1'.")
		sys.exit()
	return data
	





def main(event):




## 모든 서버 이름 보여주기								
	# event = { "action": "GET_SERVER_INSTANCELIST"	}
  
## 7일 동안 기동하지 않은 서버 삭제
	# event = { "action": "DELETE_SERVER_INSTANCE"	}

## 블록스토리지 조회
	#event = { "action": "GET_BLOCKSTORAGE_LIST"	}
 
## 서버 시작
#	event = { "server_names" : ["yg-ncp3-cftest-01", "yg-ncp3-cftest-02"]	, "action": "START_SERVER"	}	

## 서버 정지
#	event = { "server_names" : ["yg-ncp3-cftest-01", "yg-ncp3-cftest-02"]	, "action": "STOP_SERVER"	}	

# # 제외 대상 서버 외, 모든 서버 정지
	# event = { "except_server_names" : ["nia-ict-sr001"], "action": "ALL_STOP_SERVER" } 
# # 모든 서버 정지
# 	event = { "action": "ALL_STOP_SERVER" } 				

## 정지된 서버인 경우, 서버 이미지 만들기
#	event = { "server_names" : ["vm-cmm-gitlab"]	, "action": "CREATE_SERVER_IMAGE"		, "store_type": "count"	,	"store_value": 3 }
#	event = { "server_names" : ["cf-test-02"]	, "action": "CREATE_SERVER_IMAGE"		, "store_type": "day"	,	"store_value": 10 }

## RUN 상태인 경우 > 서버 STOP > 이미지 만들기 > 서버 RUN
#	event = { "server_names" : ["yg-ncp3-cftest-01"]	, "action": "FORCE_CREATE_SERVER_IMAGE"	, "store_type": "count"	,	"store_value": 3 }
#	event = { "server_names" : ["cf-test-02"]	, "action": "FORCE_CREATE_SERVER_IMAGE"	, "store_type": "day"	,	"store_value": 10 }

## 서버의 OS 영역을 제외한 추가 스토리지 스냅샷 생성
#	event = { "server_names" : ["vm-cmm-gitlab"]	, "action": "CREATE_SERVER_SNAPSHOT"	, "store_type": "count"	,	"store_value": 4 }
#	event = { "server_names" : ["cf-test-01"]	, "action": "CREATE_SERVER_SNAPSHOT"	, "store_type": "day"	,	"store_value": 10 }

## 지정된 스토리지 이름으로 스냅샷 생성
#	event = { "storage_names"  : ["stvm-cmm-gitlab-01"] , "action": "CREATE_STORAGE_SNAPSHOT", "store_type": "count"	,	"store_value": 5 }
#	event = { "storage_names"  : ["cloud-function-test-02-01"] , "action": "CREATE_STORAGE_SNAPSHOT", "store_type": "day"	,	"store_value": 10 }
  



	valid_data(event, "event")	
	action = valid_data(event.get('action'), "action")	
	action = valid_action(action.upper())

	if action == "GET_SERVER_INSTANCELIST":
		module = ServerValid()		
		module.get_server_instancelist(True)

	elif action == "INFO_SERVER":
		module = ServerValid()
		server_names = valid_data(event.get('server_names'), "server_names")
		for server_name in server_names:
			server_id = module.valid_server(server_name)
			if server_id:
				print (">>> main() : server_name = " + server_name + ", server_id = " + server_id)

	elif action == "START_SERVER":
		module = ServerControll()
		server_names = valid_data(event.get('server_names'), "server_names")
		for server_name in server_names:
			module.start_server(server_name)

	elif action == "STOP_SERVER":
		module = ServerControll()
		server_names = valid_data(event.get('server_names'), "server_names")
		for server_name in server_names:
			module.stop_server(server_name)	

	elif action == "ALL_STOP_SERVER":
		module = ServerControll()
		server_names = valid_data_ex(event.get('except_server_names'), "except_server_names")
		module.all_stop_server(server_names)
   
	elif action == "DELETE_SERVER_INSTANCE":
		module = ServerControll()
		module.delete_server_instance(True)

	elif action == "DELETE_PUBLICIP":
		module = ServerControll()
		module.delete_publicIp(True)
  
	elif action == "GET_BLOCKSTORAGE_LIST":
		module = ServerValid()
		module.get_blockStorage_list(True)
  
	elif action == "CREATE_SERVER_IMAGE":
		module = ServerImage()
		server_names = valid_data(event.get('server_names'), "server_names")
		store_type = valid_params(event.get('store_type')  , "store_type", ["count", "day"])
		store_count = valid_int(event.get('store_value')   , "store_value")

		for server_name in server_names:
			module.create_server_image(server_name, store_type, store_count)

	elif action == "FORCE_CREATE_SERVER_IMAGE":
		module = ServerImage()
		server_names = valid_data(event.get('server_names'), "server_names")
		store_type = valid_params(event.get('store_type')  , "store_type", ["count", "day"])
		store_count = valid_int(event.get('store_value')   , "store_value")
		for server_name in server_names:
			module.force_create_server_image(server_name, store_type, store_count)

	elif action == "CREATE_SERVER_SNAPSHOT":
		module = ServerSnapshot()
		server_names = valid_data(event.get('server_names'), "server_names")
		store_type = valid_params(event.get('store_type')  , "store_type", ["count", "day"])
		store_count = valid_int(event.get('store_value')   , "store_value")
		for server_name in server_names:
			module.create_server_snapshot(server_name, store_type, store_count)

	elif action == "CREATE_STORAGE_SNAPSHOT":
		module = ServerSnapshot()
		storage_names = valid_data(event.get('storage_names'), "storage_names")
		store_type = valid_params(event.get('store_type')  , "store_type", ["count", "day"])
		store_count = valid_int(event.get('store_value')   , "store_value")
		for storage_name in storage_names:
			module.create_storage_snapshot_name(storage_name, store_type, store_count)	
	
	elif action == "CHECK_REMAINING_CREDIT":
		module = ServerControll()
		module.check_remaining_credit(event.get('receiveAddresses'), True)
  
	################  SRE3파트 cloudFunction ################################	
	elif action == "CREATE_SERVER_IMAGE_SRE3":
		module = server_image_sre3()
		server_names = valid_data(event.get('server_names'), "server_names")
		for server_name in server_names:
			module.create_server_image(server_name) 
	else:
		return	

	return {"result": ">>> Cloud Functions Completed. by Cloit"}


if __name__ == '__main__':
    main(None)



