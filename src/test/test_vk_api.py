from foobnix.regui.service.vk_service import VKService
from foobnix.fc.fc_base import FCBase
FCBase().vk_login, FCBase().vk_password = "ivan.ivanenko@gmail.com",""
vk_service = VKService(True)
#print vk_service.api.get('getServerTime')
#print vk_service.api.get('audio.search',q='madonna')

#uids = vk_service.api.get('friends.get')

#print vk_service.api.my_user_id
#uids = [6851750] + uids
#print uids 
#for user in vk_service.api.get('getProfiles',uids= uids):
#    print  user['first_name'], user['last_name'], user

#k = 0
#for i in vk_service.api.get('audio.get',gid=162):
#    print  i
    
#print getGroups()

