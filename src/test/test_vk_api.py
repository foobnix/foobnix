from foobnix.thirdparty import vkontakte

vk = vkontakte.API('2234333', '0kCUFX5mK3McLmkxPHHB')
print vk.get('getServerTime')

print vk.get('audio.search',q='madonna')



