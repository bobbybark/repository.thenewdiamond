import getSources
import tools
file_path = 'https://URL_DOWNLOAD_LINK'
video_meta = {'media_type': 'episode', 'download_type': 'episode', 'tmdb_id': 4224500, 'trakt_episode_id': 7350184, 'trakt_show_id': 162206, 'trakt_season_id': 303222, 'year': '2023', 'season': 2, 'episode': 9, 'tvshow': 'Star Trek: Strange New Worlds', 'tvshow_year': '2022', 'title': 'Subspace Rhapsody', 'filename': 'Star.Trek.Strange.New.Worlds.S02E09.720p.x264-FENiX.mkv', 'filename_without_ext': 'Star.Trek.Strange.New.Worlds.S02E09.720p.x264-FENiX', 'subs_filename': 'Star.Trek.Strange.New.Worlds.S02E09.720p.x264-FENiX.srt', 'imdb_id': 'tt22805762', 'filesize': '', 'filehash': '', 'is_tvshow': True, 'is_movie': False, 'url': '', 'magnet': 'magnet:?xt=urn:btih:0D2D32A8EC858DE6E29BACA66A6CF75EF9C68531&', 'release_title': 'Star.trek.strange.new.worlds.s02e09.720p.x264-fenix', 'CURR_LABEL': 'Star.trek.strange.new.worlds.s02e09.720p.x264-fenix', 'package': 'single', 'file_name': 'Star.Trek.Strange.New.Worlds.S02E09.720p.x264-FENiX.mkv', 'item_information.art': {'thumb': 'https://image.tmdb.org/t/p/w500/a7Cu3KpMBkCh8Tgxgja87WgFE6u.jpg', 'poster': 'http://assets.fanart.tv/fanart/tv/382389/tvposter/star-trek-strange-new-worlds-5ec96da7761d2.jpg', 'fanart': 'http://assets.fanart.tv/fanart/tv/382389/showbackground/star-trek-strange-new-worlds-6266990a6d0f9.jpg', 'clearlogo': 'http://assets.fanart.tv/fanart/tv/382389/hdtvlogo/star-trek-strange-new-worlds-626698d2d926e.png', 'tvshow.poster': 'http://assets.fanart.tv/fanart/tv/382389/tvposter/star-trek-strange-new-worlds-5ec96da7761d2.jpg', 'tvshow.fanart': 'http://assets.fanart.tv/fanart/tv/382389/showbackground/star-trek-strange-new-worlds-6266990a6d0f9.jpg', 'tvshow.clearlogo': 'http://assets.fanart.tv/fanart/tv/382389/hdtvlogo/star-trek-strange-new-worlds-626698d2d926e.png', 'tvshow.banner': 'http://assets.fanart.tv/fanart/tv/382389/tvbanner/star-trek-strange-new-worlds-62741e382c2f4.jpg', 'tvshow.landscape': 'http://assets.fanart.tv/fanart/tv/382389/tvthumb/star-trek-strange-new-worlds-62740b84a557c.jpg', 'tvshow.clearart': 'http://assets.fanart.tv/fanart/tv/382389/hdclearart/star-trek-strange-new-worlds-63fdca1b5adc1.png', 'tvshow.thumb': 'http://assets.fanart.tv/fanart/tv/382389/tvposter/star-trek-strange-new-worlds-5ec96da7761d2.jpg'}, 'episode_meta': None}
#video_meta = tools.set_size_and_hash(video_meta, file_path)
getSources.get_subtitles(video_meta, file_path)
print(tools.SUB_FILE)
