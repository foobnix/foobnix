from foobnix.model.entity import EntityBean, PlaylistBean
bean = PlaylistBean(name="asd", path="", type=EntityBean.TYPE_MUSIC_URL)
print bean.type
