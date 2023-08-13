import getSources
#getSources.setup_userdata_folder()
#getSources.setup_providers('https://bit.ly/a4kScrapers')

#getSources.enable_disable_providers()
#getSources.rd_auth()

from getSources import Sources

info = {'info': {'episode': 7, 'season': 1, 'year': '2020', 'imdbnumber': 'tt9170108', 'imdb_id': 'tt9170108', 'tvdb_id': 368643, 'tmdb_id': 85723, 'mediatype': 'episode', 'title': 'Happiness', 'trakt_show_id': 152958, 'tmdb_show_id': 85723, 'tvdb_show_id': 368643, 'tvshowtitle': 'Raised by Wolves', 'tvshow.year': '2020', 'tvshow.imdb_id': 'tt9170108', 'tvshow.trakt_id': 152958, 'tvshow.tvdb_id': 368643, 'tvshow.tmdb_id': 85723}, 'season_count': 2, 'show_episode_count': 18, 'episode_count': 8, 'is_airing': 0, 'absoluteNumber': 7}
uncached, sources_list, item_information= Sources(info).get_sources()


for i in sources_list:
	print(i, '\n')
