from foobnix.model.entity import CommonBean, PlaylistBean
bean = PlaylistBean(name="asd", path="", type=CommonBean.TYPE_MUSIC_URL)
print bean.type
