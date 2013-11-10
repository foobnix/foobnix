from foobnix.util.id3_util import get_support_music_beans_from_all,\
    udpate_id3_for_beans, add_update_image_paths
from foobnix.playlists.cue_reader import update_id3_for_cue
from foobnix.playlists.m3u_reader import update_id3_for_m3u

def update_id3_wind_filtering(beans):
    beans = update_id3_for_m3u(beans)
    beans = get_support_music_beans_from_all(beans)
    beans = udpate_id3_for_beans(beans)
    beans = update_id3_for_cue(beans)
    beans = add_update_image_paths(beans)
    result = []
    for bean in beans:
        result.append(bean)
    return result