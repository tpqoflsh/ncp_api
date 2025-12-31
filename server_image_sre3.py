import common 
import datetime
 

class server_image_sre3:
    global TODAY
    TODAY = datetime.date.today().strftime('%y%m%d')
    
    # 서버 이비지 생성
    def create_server_image(self, server_name):
        
        if not self.valid_server(server_name):
            return
        server_id = self.valid_server(server_name)
        
        ## Server 이미지 생성
        image_name = self._create_server_image(server_id, server_name)
        print(">>> create_server_image() Success. server_name = " + server_name + ", image_name = " + image_name)
        
    
    def _create_server_image(self, server_id, server_name) :
        #checking server image status
        if self._get_server_image_status(server_id, "INIT"):
            print(">>> _create_image() Fail. " + server_name + " server_image is being created.")
            return False		

		# get server image name
        image_name = self._get_server_image_unique_name(server_name)
		# create server image 
        self._req_create_server_image(server_id, server_name, image_name)
        
        slack_msg =  "Successfully create serverImage( " + TODAY + "). server_name : " + server_name + "image_name : " + image_name 
        common.send_slack_message(slack_msg)

        return image_name


    def _get_server_image_status(self, server_name, status):		
        req_path = '/vserver/v2/getMemberServerImageInstanceList?responseFormatType=json'.format('string')
        res = common.send(req_path)
        
        for object in res['getMemberServerImageInstanceListResponse']['memberServerImageInstanceList']:
            if server_name == object['originalServerInstanceNo'] and object['memberServerImageInstanceStatus']['code'] == status:
                return True
        return False


    def _get_server_image_unique_name(self, server_name):		
        if server_name.find("vm-", 0) == 0:
            server_name = server_name[3:30]

        if len(server_name) > 19:
            server_name = server_name[0:19]
        server_name = "img-" + server_name
 
        org_image_name = server_name
        image_name = org_image_name		

        seq_number = 0
        while(True):
            if self._check_server_image_name(image_name):
                seq_number = seq_number + 1
                if seq_number < 10:
                    image_name = org_image_name + '-0' + str(seq_number)
                else:
                    image_name = org_image_name + '-' + str(seq_number)
            else:
                break

        return image_name + '-' + TODAY
    
    
    def _check_server_image_name(self, image_name):
        req_path = '/vserver/v2/getMemberServerImageInstanceList?memberServerImageName=' + image_name \
                + '&responseFormatType=json'.format('string')
        res = common.send(req_path)
        ret_count = res['getMemberServerImageInstanceListResponse']['totalRows']
 
        if int(ret_count) > 0:
            return True
        return False
    
    
    def _req_create_server_image(self, server_ids, server_name, image_name):		
        req_path = '/vserver/v2/createMemberServerImageInstance?serverInstanceNo=' + server_ids \
					+ '&memberServerImageName=' + image_name \
					+ '&memberServerImageDescription=' + server_name + '_Auto_Create_serverImage_by_Cloit_SRE3_cloudFUnction' \
					+ '&responseFormatType=json'.format('string')
        common.send(req_path)


    def valid_server(self, server_name):
        req_path = '/vserver/v2/getServerInstanceList?serverName=' + server_name + '&responseFormatType=json'.format('string')
        res = common.send(req_path)
 
        for object in res['getServerInstanceListResponse']['serverInstanceList']:
            if server_name == object['serverName']:
                return object['serverInstanceNo']
	
        print(">>> server_name = " + server_name + " is none exist.")
        return False