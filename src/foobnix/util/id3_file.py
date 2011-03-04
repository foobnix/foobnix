from foobnix.util.id3_util import get_support_music_beans_from_all,\
    udpate_id3_for_beans, add_upadte_image_paths
from foobnix.cue.cue_reader import update_id3_for_cue

def update_id3_wind_filtering(beans):
    beans = get_support_music_beans_from_all(beans)
    beans = udpate_id3_for_beans(beans)
    beans = update_id3_for_cue(beans)
    beans = add_upadte_image_paths(beans)
    result = []
    for bean in beans:
        result.append(bean)
    return result