from foobnix.regui.service.vk_service import VKService
from foobnix.fc.fc_base import FCBase
FCBase().vk_login, FCBase().vk_password = "ivan.ivanenko@gmail.com",""
vk_service = VKService(True)
i =0
for line in vk_service.api.get("video.get", uid=6851750):
    i+=1
    if line ==25:
        continue
    print line['title'] 
    print line['image']
    print line['link']
    print line
    print i
    if i==3:
        break
    

