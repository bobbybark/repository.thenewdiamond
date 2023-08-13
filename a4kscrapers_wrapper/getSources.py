# -*- coding: utf-8 -*-

#from __future__ import absolute_import, division, unicode_literals

import copy
import importlib
import os
import random
import re
import sys
import time
from collections import OrderedDict, Counter

#from database.torrentCache import TorrentCache
from thread_pool import ThreadPool
import real_debrid

import tools
tools.get_pid()

import inspect

from inspect import currentframe, getframeinfo
#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

##SUPPRESS MESSAGES
os.environ['A4KSCRAPERS_TEST_TOTAL'] = '1'


"""
Handling of scraping and cache checking for sources
"""
"""
TEST
import getSources
from getSources import Sources
#sources = Sources({'info': {'mediatype': 'episode'}}).get_sources()

info = {'action_args': {'episode': 7, 'season': 1, 'trakt_id': 5947022, 'trakt_show_id': 152958, 'mediatype': 'episode'}, 'trakt_id': 5947022, 'trakt_show_id': 152958, 'trakt_season_id': 281021, 'info': {'episode': 7, 'sortepisode': 7, 'season': 1, 'sortseason': 2, 'year': '2022', 'premiered': '2022-03-17T07:00:00', 'aired': '2022-03-17T07:00:00', 'imdbnumber': 'tt18393962', 'imdb_id': 'tt18393962', 'trakt_id': 5947022, 'tvdb_id': 8973088, 'tmdb_id': 3533321, 'duration': 3000, 'dateadded': '2023-08-09T12:28:00', 'rating': 7.53, 'votes': 1195, 'rating.trakt': {'rating': 7.53, 'votes': 1195}, 'mediatype': 'episode', 'available_translations': ['de', 'en', 'es', 'fr', 'he', 'hu', 'it', 'ko', 'nl', 'pl', 'pt', 'ru', 'zh'], 'title': 'Happiness', 'originaltitle': 'Happiness', 'sorttitle': 'Happiness', 'plot': 'Grandmother reveals her own agenda, Marcus seeks revenge, and Mother sets out to neutralize the serpent – but is leveled by the fallout.', 'plotoutline': 'Grandmother reveals her own agenda, Marcus seeks revenge, and Mother sets out to neutralize the serpent – but is leveled by the fallout.', 'trakt_show_id': 152958, 'tmdb_show_id': 85723, 'tvdb_show_id': 368643, 'trakt_season_id': 281021, 'tvshowtitle': 'Raised by Wolves', 'director': ['Lukas Ettlin'], 'writer': ['Aaron Guzikowski'], 'overview': 'Grandmother reveals her own agenda, Marcus seeks revenge, and Mother sets out to neutralize the serpent – but is leveled by the fallout.', 'rating.tmdb': {'rating': 7.3, 'votes': 6}, 'mpaa': 'TV-MA', 'genre': ['Drama', 'Fantasy', 'Science Fiction'], 'country': 'United States', 'rating.imdb': {'rating': 7.7, 'votes': 1555}, 'tvshow.year': '2020', 'studio': ['Film Afrika Worldwide', 'Lit Entertainment Group', 'Scott Free Productions', 'Shadycat Productions'], 'country_origin': 'US', 'aliases': ['Raised by Wolves 2'], 'tvshow.imdb_id': 'tt9170108', 'tvshow.trakt_id': 152958, 'tvshow.tvdb_id': 368643, 'tvshow.tmdb_id': 85723}, 'cast': [{'name': 'Amanda Collin', 'role': 'Mother / Lamia', 'order': 0, 'thumbnail': 'https://image.tmdb.org/t/p/w500/bFm5zt8vxD09Ez6irsJItmPigjq.jpg'}, {'name': 'Abubakar Salim', 'role': 'Father', 'order': 1, 'thumbnail': 'https://image.tmdb.org/t/p/w500/cUddJiPnCTDDOBuk7jTmLsiODMb.jpg'}, {'name': 'Winta McGrath', 'role': 'Campion', 'order': 2, 'thumbnail': 'https://image.tmdb.org/t/p/w500/1odtDemopNedhQWZ9Zup3UrEaRk.jpg'}, {'name': 'Niamh Algar', 'role': 'Mary / Sue', 'order': 3, 'thumbnail': 'https://image.tmdb.org/t/p/w500/4FscmD9lWqiJVnOvuWTaVc3ynTb.jpg'}, {'name': 'Travis Fimmel', 'role': 'Caleb / Marcus Drusus', 'order': 4, 'thumbnail': 'https://image.tmdb.org/t/p/w500/kuTSw3I2hqb5N1QqYrXPX8zd8EA.jpg'}, {'name': 'Jordan Loughran', 'role': 'Tempest', 'order': 5, 'thumbnail': 'https://image.tmdb.org/t/p/w500/a3UM3gFUjZjaODZI0gUyaUWaeto.jpg'}, {'name': 'Matias Varela', 'role': 'Lucius', 'order': 6, 'thumbnail': 'https://image.tmdb.org/t/p/w500/bUMXVaKxuUNzHh7ZNLXaWI2CP3h.jpg'}, {'name': 'Felix Jamieson', 'role': 'Paul', 'order': 7, 'thumbnail': 'https://image.tmdb.org/t/p/w500/tesBnjps2Qb7pmn3pm5rUzGQVqG.jpg'}, {'name': 'Ethan Hazzard', 'role': 'Hunter', 'order': 8, 'thumbnail': 'https://image.tmdb.org/t/p/w500/5dvmyzOxaxF3McbnVaLlQ00Jw35.jpg'}, {'name': 'Aasiya Shah', 'role': 'Holly', 'order': 9, 'thumbnail': 'https://image.tmdb.org/t/p/w500/qi6fGjxtR0TkvNsysxJP77CJjcl.jpg'}, {'name': 'Ivy Wong', 'role': 'Vita', 'order': 10, 'thumbnail': 'https://image.tmdb.org/t/p/w500/miSVUr4XliqHpz2hLO2fgpNlWCY.jpg'}, {'name': 'Morgan Santo', 'role': 'Vrille', 'order': 11, 'thumbnail': None}, {'name': 'Jennifer Saayeng', 'role': 'Nerva', 'order': 12, 'thumbnail': 'https://image.tmdb.org/t/p/w500/baeInpugQJx1HNMzStDTWb28zFL.jpg'}, {'name': 'Selina Jones', 'role': 'Grandmother', 'order': 13, 'thumbnail': None}, {'name': 'Riaz Solker', 'role': 'Mars', 'order': 14, 'thumbnail': None}, {'name': 'Jagger Cameron', 'role': 'Girl', 'order': 15, 'thumbnail': None}, {'name': 'Jeshua Boshoff', 'role': 'Colonist', 'order': 16, 'thumbnail': None}, {'name': 'Natalie Robbie', 'role': 'Marcella', 'order': 17, 'thumbnail': 'https://image.tmdb.org/t/p/w500/aEB2gv7WXdrpJwj2NB2f9NAvIbv.jpg'}], 'art': {'thumb': 'https://image.tmdb.org/t/p/w500/k7Cx1ha0MgSBp0eX7kRulufBm6b.jpg', 'poster': 'http://assets.fanart.tv/fanart/tv/368643/tvposter/raised-by-wolves-641012d73d393.jpg', 'fanart': 'http://assets.fanart.tv/fanart/tv/368643/showbackground/raised-by-wolves-5f5745ce7c47a.jpg', 'clearlogo': 'http://assets.fanart.tv/fanart/tv/368643/hdtvlogo/raised-by-wolves-5f55053caf9d4.png', 'tvshow.poster': 'http://assets.fanart.tv/fanart/tv/368643/tvposter/raised-by-wolves-641012d73d393.jpg', 'tvshow.fanart': 'http://assets.fanart.tv/fanart/tv/368643/showbackground/raised-by-wolves-5f5745ce7c47a.jpg', 'tvshow.clearlogo': 'http://assets.fanart.tv/fanart/tv/368643/hdtvlogo/raised-by-wolves-5f55053caf9d4.png', 'tvshow.banner': 'http://assets.fanart.tv/fanart/tv/368643/tvbanner/raised-by-wolves-5f511b30dc623.jpg', 'tvshow.landscape': 'http://assets.fanart.tv/fanart/tv/368643/tvthumb/raised-by-wolves-5f54bfe0bcb1c.jpg', 'tvshow.clearart': 'http://assets.fanart.tv/fanart/tv/368643/hdclearart/raised-by-wolves-5f59e150dd13c.png', 'tvshow.thumb': 'http://assets.fanart.tv/fanart/tv/368643/tvposter/raised-by-wolves-641012d73d393.jpg'}, 'args': '%7B%22mediatype%22%3A%20%22episode%22%2C%20%22trakt_id%22%3A%205947022%2C%20%22trakt_season_id%22%3A%20281021%2C%20%22trakt_show_id%22%3A%20152958%7D', 'play_count': 0, 'resume_time': None, 'percent_played': None, 'user_rating': None, 'season_count': 2, 'show_episode_count': 18, 'episode_count': 8, 'is_airing': 0, 'absoluteNumber': 18}
info = {'action_args': {'episode': 7, 'season': 1, 'trakt_id': 5947022, 'trakt_show_id': 152958, 'mediatype': 'episode'}, 'trakt_id': 5947022, 'trakt_show_id': 152958, 'trakt_season_id': 281021, 'info': {'episode': 7, 'sortepisode': 7, 'season': 1, 'sortseason': 2, 'year': '2022', 'premiered': '2022-03-17T07:00:00', 'aired': '2022-03-17T07:00:00', 'imdbnumber': 'tt18393962', 'imdb_id': 'tt18393962', 'trakt_id': 5947022, 'tvdb_id': 8973088, 'tmdb_id': 3533321, 'duration': 3000, 'dateadded': '2023-08-09T12:28:00', 'rating': 7.53, 'votes': 1195, 'rating.trakt': {'rating': 7.53, 'votes': 1195}, 'mediatype': 'episode', 'available_translations': ['de', 'en', 'es', 'fr', 'he', 'hu', 'it', 'ko', 'nl', 'pl', 'pt', 'ru', 'zh'], 'title': 'Happiness', 'originaltitle': 'Happiness', 'sorttitle': 'Happiness',  'trakt_show_id': 152958, 'tmdb_show_id': 85723, 'tvdb_show_id': 368643, 'trakt_season_id': 281021, 'tvshowtitle': 'Raised by Wolves', 'director': ['Lukas Ettlin'], 'writer': ['Aaron Guzikowski'], 'overview': 'Grandmother reveals her own agenda, Marcus seeks revenge, and Mother sets out to neutralize the serpent – but is leveled by the fallout.', 'rating.tmdb': {'rating': 7.3, 'votes': 6}, 'mpaa': 'TV-MA', 'genre': ['Drama', 'Fantasy', 'Science Fiction'], 'country': 'United States', 'rating.imdb': {'rating': 7.7, 'votes': 1555}, 'tvshow.year': '2020', 'studio': ['Film Afrika Worldwide', 'Lit Entertainment Group', 'Scott Free Productions', 'Shadycat Productions'], 'country_origin': 'US', 'aliases': ['Raised by Wolves 2'], 'tvshow.imdb_id': 'tt9170108', 'tvshow.trakt_id': 152958, 'tvshow.tvdb_id': 368643, 'tvshow.tmdb_id': 85723}, 'art': {'thumb': 'https://image.tmdb.org/t/p/w500/k7Cx1ha0MgSBp0eX7kRulufBm6b.jpg', 'poster': 'http://assets.fanart.tv/fanart/tv/368643/tvposter/raised-by-wolves-641012d73d393.jpg', 'fanart': 'http://assets.fanart.tv/fanart/tv/368643/showbackground/raised-by-wolves-5f5745ce7c47a.jpg', 'clearlogo': 'http://assets.fanart.tv/fanart/tv/368643/hdtvlogo/raised-by-wolves-5f55053caf9d4.png', 'tvshow.poster': 'http://assets.fanart.tv/fanart/tv/368643/tvposter/raised-by-wolves-641012d73d393.jpg', 'tvshow.fanart': 'http://assets.fanart.tv/fanart/tv/368643/showbackground/raised-by-wolves-5f5745ce7c47a.jpg', 'tvshow.clearlogo': 'http://assets.fanart.tv/fanart/tv/368643/hdtvlogo/raised-by-wolves-5f55053caf9d4.png', 'tvshow.banner': 'http://assets.fanart.tv/fanart/tv/368643/tvbanner/raised-by-wolves-5f511b30dc623.jpg', 'tvshow.landscape': 'http://assets.fanart.tv/fanart/tv/368643/tvthumb/raised-by-wolves-5f54bfe0bcb1c.jpg', 'tvshow.clearart': 'http://assets.fanart.tv/fanart/tv/368643/hdclearart/raised-by-wolves-5f59e150dd13c.png', 'tvshow.thumb': 'http://assets.fanart.tv/fanart/tv/368643/tvposter/raised-by-wolves-641012d73d393.jpg'}, 'args': '%7B%22mediatype%22%3A%20%22episode%22%2C%20%22trakt_id%22%3A%205947022%2C%20%22trakt_season_id%22%3A%20281021%2C%20%22trakt_show_id%22%3A%20152958%7D', 'play_count': 0, 'resume_time': None, 'percent_played': None, 'user_rating': None, 'season_count': 2, 'show_episode_count': 18, 'episode_count': 8, 'is_airing': 0, 'absoluteNumber': 18}
info = {'action_args': {'episode': 7, 'season': 1, 'trakt_id': 5947022, 'trakt_show_id': 152958, 'mediatype': 'episode'}, 'trakt_id': 5947022, 'trakt_show_id': 152958, 'trakt_season_id': 281021, 'info': {'episode': 7, 'sortepisode': 7, 'season': 1, 'sortseason': 1, 'year': '2022', 'imdbnumber': 'tt18393962', 'imdb_id': 'tt18393962', 'trakt_id': 5947022, 'tvdb_id': 8973088, 'tmdb_id': 3533321, 'mediatype': 'episode', 'title': 'Happiness', 'originaltitle': 'Happiness', 'trakt_show_id': 152958, 'tmdb_show_id': 85723, 'tvdb_show_id': 368643, 'trakt_season_id': 281021, 'tvshowtitle': 'Raised by Wolves', 'tvshow.year': '2020', 'tvshow.imdb_id': 'tt9170108', 'tvshow.trakt_id': 152958, 'tvshow.tvdb_id': 368643, 'tvshow.tmdb_id': 85723}, 'args': '%7B%22mediatype%22%3A%20%22episode%22%2C%20%22trakt_id%22%3A%205947022%2C%20%22trakt_season_id%22%3A%20281021%2C%20%22trakt_show_id%22%3A%20152958%7D', 'season_count': 2, 'show_episode_count': 18, 'episode_count': 8, 'is_airing': 0, 'absoluteNumber': 18}
info = {'action_args': {'episode': 7, 'season': 1, 'mediatype': 'episode'}, 'info': {'episode': 7, 'season': 1, 'year': '2020', 'imdbnumber': 'tt9170108', 'imdb_id': 'tt9170108', 'tvdb_id': 368643, 'tmdb_id': 85723, 'mediatype': 'episode', 'title': 'Happiness', 'trakt_show_id': 152958, 'tmdb_show_id': 85723, 'tvdb_show_id': 368643, 'tvshowtitle': 'Raised by Wolves', 'tvshow.year': '2020', 'tvshow.imdb_id': 'tt9170108', 'tvshow.trakt_id': 152958, 'tvshow.tvdb_id': 368643, 'tvshow.tmdb_id': 85723}, 'season_count': 2, 'show_episode_count': 18, 'episode_count': 8, 'is_airing': 0, 'absoluteNumber': 7}
info = {'info': {'episode': 7, 'season': 1, 'year': '2020', 'imdbnumber': 'tt9170108', 'imdb_id': 'tt9170108', 'tvdb_id': 368643, 'tmdb_id': 85723, 'mediatype': 'episode', 'title': 'Happiness', 'trakt_show_id': 152958, 'tmdb_show_id': 85723, 'tvdb_show_id': 368643, 'tvshowtitle': 'Raised by Wolves', 'tvshow.year': '2020', 'tvshow.imdb_id': 'tt9170108', 'tvshow.trakt_id': 152958, 'tvshow.tvdb_id': 368643, 'tvshow.tmdb_id': 85723}, 'season_count': 2, 'show_episode_count': 18, 'episode_count': 8, 'is_airing': 0, 'absoluteNumber': 7}
#sources = Sources(info).get_sources()
uncached, sources_list, item_information= Sources(info).get_sources()

for i in reversed(sorted(uncached, key=lambda x: x['seeds'])):
	i



import getSources
getSources.setup_userdata_folder()
getSources.setup_providers('https://bit.ly/a4kScrapers')

getSources.enable_disable_providers()
getSources.rd_auth()

from getSources import Sources
info = {'info': {'episode': 7, 'season': 1, 'year': '2020', 'imdbnumber': 'tt9170108', 'imdb_id': 'tt9170108', 'tvdb_id': 368643, 'tmdb_id': 85723, 'mediatype': 'episode', 'title': 'Happiness', 'trakt_show_id': 152958, 'tmdb_show_id': 85723, 'tvdb_show_id': 368643, 'tvshowtitle': 'Raised by Wolves', 'tvshow.year': '2020', 'tvshow.imdb_id': 'tt9170108', 'tvshow.trakt_id': 152958, 'tvshow.tvdb_id': 368643, 'tvshow.tmdb_id': 85723}, 'season_count': 2, 'show_episode_count': 18, 'episode_count': 8, 'is_airing': 0, 'absoluteNumber': 7}
uncached, sources_list, item_information= Sources(info).get_sources()
for i in sources_list:
	print(i, '\n')
	
	



##RELOAD
import importlib
importlib.reload(getSources)
from getSources import Sources
uncached, sources_list, item_information= Sources(info).get_sources()
"""


try:
	from importlib import reload as reload_module  # pylint: disable=no-name-in-module
except ImportError:
	# Invalid version of importlib
	from imp import reload as reload_module

# Monkey patch the common requests calls

#requests.get = tools._monkey_check(requests.get)
#requests.post = tools._monkey_check(requests.post)
#requests.head = tools._monkey_check(requests.head)
#requests.delete = tools._monkey_check(requests.delete)
#requests.put = tools._monkey_check(requests.put)

#requests.Session.get = tools._monkey_check(requests.Session.get)
#requests.Session.post = tools._monkey_check(requests.Session.post)
#requests.Session.head = tools._monkey_check(requests.Session.head)
#requests.Session.delete = tools._monkey_check(requests.Session.delete)
#requests.Session.put = tools._monkey_check(requests.Session.put)


def patch_ak4_requests():
	patch_line_147 = '            response = None'
	patch_update_147 = """            response = response_err ## PATCH
"""

	patch_line_150 = '                response = request(None)'
	patch_update_150 = """                try: response = request(None) ## PATCH
                except requests.exceptions.ConnectionError: return response ## PATCH
"""

	patch_line_154 = '                response_err = response'
	patch_update_154 = """                if response: ## PATCH
                    response_err = response ## PATCH
                    self._verify_response(response) ## PATCH
                else: ## PATCH
                    self._verify_response(response_err) ## PATCH
"""


	file_path = os.path.join(os.path.join(tools.ADDON_USERDATA_PATH, 'providerModules', 'a4kScrapers') , 'request.py')
	file1 = open(file_path, 'r')
	lines = file1.readlines()
	new_file = ''
	update_flag = False
	for idx, line in enumerate(lines):
		if update_flag == 154:
			update_flag = True
			continue
		if '## PATCH' in str(line):
			update_flag = False
			break
		if idx == 147-1 and line == patch_line_147 or patch_line_147 in str(line):
			new_file = new_file + patch_update_147
			update_flag = True
		elif idx == 150-1 and line == patch_line_150 or patch_line_150 in str(line):
			new_file = new_file + patch_update_150
			update_flag = True
		elif idx == 154-1 and line == patch_line_154 or patch_line_154 in str(line):
			new_file = new_file + patch_update_154
			update_flag = 154
		else:
			new_file = new_file + line
	file1.close()
	if update_flag:
		file1 = open(file_path, 'w')
		file1.writelines(new_file)
		file1.close()

def rd_auth():
	'''
import getSources
getSources.rd_auth()
	'''
	rd_api = real_debrid.RealDebrid()
	rd_api.auth()
	print('AUTH_DONE')
	return
	
def get_providers_dict():
	"""
import getSources
getSources.get_providers_dict()
"""

	providers_dict = {}
	providers_dict['hosters'] = []
	providers_dict['torrent'] = []
	providers_dict['adaptive'] = []

	providers_dict_original = {'hosters': [], 
	'torrent': [
	('providers.a4kScrapers.en.torrent', 'bitlord', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'bitsearch', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'btdig', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'cached', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'glo', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'kickass', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'lime', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'magnetdl', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'piratebay', 'a4kScrapers'), 
	#('providers.a4kScrapers.en.torrent', 'rutor', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'showrss', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'torrentdownload', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'torrentio', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'torrentz2', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'yts', 'a4kScrapers')
	], 
	'adaptive': []}

	for root, dirs, files in os.walk(tools.A4KPROVIDERS_PATH, topdown=False):
		for name in files:
			#print(os.path.join(root, name))
			if '.py' == name[-3:] and '__init__.py' != name:
				file = str(os.path.join(root, name).split('providers')[1])
				if '/' in str(file):
					splits = str(file).split('/')
				else:
					splits = str(file).split('\\')
				providers_dict[splits[3]].append(tuple([str('providers.%s.%s.%s') % (splits[1],splits[2],splits[3]), splits[4].replace('.py',''), splits[1], True]))
	#print(providers_dict)
	return providers_dict

def setup_providers(provider_url):
	"""
import getSources
getSources.setup_providers('https://bit.ly/a4kScrapers')
"""
	provider_url = 'https://bit.ly/a4kScrapers'
	temp_zip = tools.temp_file()
	tools.download_file(provider_url, temp_zip)
	dest_dir = tools.ADDON_USERDATA_PATH
	tools.extract_zip(temp_zip, dest_dir)
	tools.delete_file(temp_zip)
	providers_dict = get_providers_dict()
	tools.write_all_text(tools.PROVIDERS_JSON,str(providers_dict))

def get_providers():
	providers_dict = eval(tools.read_all_text(tools.PROVIDERS_JSON))
	providers_dict_test = providers_dict
	for idx, i in enumerate(providers_dict_test):
		for xdx, x in enumerate(providers_dict_test[i]):
			if x[3] == False or str(x[3]) == 'False':
				providers_dict[i].pop(xdx)
	return providers_dict

def setup_userdata_folder():
	"""
import getSources
getSources.setup_userdata_folder()
"""
	tools.setup_userdata()

def enable_disable_providers():
	"""
import getSources
getSources.enable_disable_providers()
"""
	providers_dict = eval(tools.read_all_text(tools.PROVIDERS_JSON))
	providers_dict_test = providers_dict
	for idx, i in enumerate(providers_dict_test):
		for xdx, x in enumerate(providers_dict_test[i]):
				curr_status = providers_dict[i][xdx][3]
				if curr_status == False or str(curr_status) == 'False':
					toggle = 'ENABLED'
					curr_status = 'DISABLED'
					update_status = True
				else:
					toggle = 'DISABLED'
					curr_status = 'ENABLED'
					update_status = False
				curr_provider = providers_dict_test[i][xdx][1]
				curr_provider_type = i
				curr_provider_source = providers_dict_test[i][xdx][2]
				update = input(str('%s of type %s from %s is %s, toggle %s by any key, ENTER to pass:  ') % (curr_provider.upper(), curr_provider_type, curr_provider_source, curr_status, toggle))
				if update != '':
					providers_dict[i][xdx] = tuple([providers_dict_test[i][xdx][0], providers_dict_test[i][xdx][1], providers_dict_test[i][xdx][2], update_status])
				update = ''
	#print(providers_dict)
	tools.write_all_text(tools.PROVIDERS_JSON,str(providers_dict))
	for idx, i in enumerate(providers_dict_test):
		for xdx, x in enumerate(providers_dict_test[i]):
			print(x)
	return

def get_subtitles(VIDEO_META, file_path):
	"""
import getSources
video_meta = {'media_type': 'movie', 'download_type': 'movie', 'tmdb_id': item_information['info']['tmdb_id'], 'year': item_information['info']['year'], 'season': '', 'episode': '', 'tvshow': '', 'tvshow_year': '', 'title': item_information['info']['title'], 'filename': file_name, 'filename_without_ext': filename_without_ext, 'subs_filename': subs_filename,'imdb_id': item_information['info']['imdbnumber'], 'filesize': '', 'filehash': '', 'is_tvshow': False, 'is_movie': True,
'url': stream_link, 'magnet': g.CURR_SOURCE['magnet'], 'release_title': g.CURR_SOURCE['release_title'], 'CURR_LABEL': g.CURR_LABEL, 'package': g.CURR_SOURCE['package'], 'file_name': unquote(stream_link).split('/')[-1], 'item_information.art': item_information['art']}
getSources.get_subtitles(video_meta)

import getSources
file_path = 'https://58.download.real-debrid.com/d/QILWUJI22MD64/Star.Trek.Strange.New.Worlds.S02E09.720p.x264-FENiX.mkv'
video_meta = {'media_type': 'episode', 'download_type': 'episode', 'tmdb_id': 4224500, 'trakt_episode_id': 7350184, 'trakt_show_id': 162206, 'trakt_season_id': 303222, 'year': '2023', 'season': 2, 'episode': 9, 'tvshow': 'Star Trek: Strange New Worlds', 'tvshow_year': '2022', 'title': 'Subspace Rhapsody', 'filename': 'Star.Trek.Strange.New.Worlds.S02E09.720p.x264-FENiX.mkv', 'filename_without_ext': 'Star.Trek.Strange.New.Worlds.S02E09.720p.x264-FENiX', 'subs_filename': 'Star.Trek.Strange.New.Worlds.S02E09.720p.x264-FENiX.srt', 'imdb_id': 'tt22805762', 'filesize': '', 'filehash': '', 'is_tvshow': True, 'is_movie': False, 'url': 'https://58.download.real-debrid.com/d/QILWUJI22MD64/Star.Trek.Strange.New.Worlds.S02E09.720p.x264-FENiX.mkv', 'magnet': 'magnet:?xt=urn:btih:0D2D32A8EC858DE6E29BACA66A6CF75EF9C68531&', 'release_title': 'Star.trek.strange.new.worlds.s02e09.720p.x264-fenix', 'CURR_LABEL': 'Star.trek.strange.new.worlds.s02e09.720p.x264-fenix', 'package': 'single', 'file_name': 'Star.Trek.Strange.New.Worlds.S02E09.720p.x264-FENiX.mkv', 'item_information.art': {'thumb': 'https://image.tmdb.org/t/p/w500/a7Cu3KpMBkCh8Tgxgja87WgFE6u.jpg', 'poster': 'http://assets.fanart.tv/fanart/tv/382389/tvposter/star-trek-strange-new-worlds-5ec96da7761d2.jpg', 'fanart': 'http://assets.fanart.tv/fanart/tv/382389/showbackground/star-trek-strange-new-worlds-6266990a6d0f9.jpg', 'clearlogo': 'http://assets.fanart.tv/fanart/tv/382389/hdtvlogo/star-trek-strange-new-worlds-626698d2d926e.png', 'tvshow.poster': 'http://assets.fanart.tv/fanart/tv/382389/tvposter/star-trek-strange-new-worlds-5ec96da7761d2.jpg', 'tvshow.fanart': 'http://assets.fanart.tv/fanart/tv/382389/showbackground/star-trek-strange-new-worlds-6266990a6d0f9.jpg', 'tvshow.clearlogo': 'http://assets.fanart.tv/fanart/tv/382389/hdtvlogo/star-trek-strange-new-worlds-626698d2d926e.png', 'tvshow.banner': 'http://assets.fanart.tv/fanart/tv/382389/tvbanner/star-trek-strange-new-worlds-62741e382c2f4.jpg', 'tvshow.landscape': 'http://assets.fanart.tv/fanart/tv/382389/tvthumb/star-trek-strange-new-worlds-62740b84a557c.jpg', 'tvshow.clearart': 'http://assets.fanart.tv/fanart/tv/382389/hdclearart/star-trek-strange-new-worlds-63fdca1b5adc1.png', 'tvshow.thumb': 'http://assets.fanart.tv/fanart/tv/382389/tvposter/star-trek-strange-new-worlds-5ec96da7761d2.jpg'}, 'episode_meta': None}
getSources.get_subtitles(video_meta, file_path)
"""
	tools.VIDEO_META = VIDEO_META
	if 'http' in str(file_path):
		tools.VIDEO_META = tools.set_size_and_hash_url(tools.VIDEO_META, file_path)
	else:
		tools.VIDEO_META = tools.set_size_and_hash(tools.VIDEO_META, file_path)
	#os.environ['A4KSUBTITLES_API_MODE'] = str({'kodi': 'false'})
	import subtitles
	subfile = subtitles.SubtitleService().get_subtitle()
	tools.VIDEO_META['SUB_FILE'] = tools.SUB_FILE
	return tools.VIDEO_META


class TorrentCacheCheck:
	def __init__(self, scraper_class):
		self.premiumize_cached = []
		self.realdebrid_cached = []
		self.all_debrid_cached = []
		self.threads = ThreadPool()

		self.episode_strings = None
		self.season_strings = None
		self.scraper_class = scraper_class
		self.rd_api = real_debrid.RealDebrid()

	def store_torrent(self, torrent):
		"""
		Pushes cached torrents back up to the calling class
		:param torrent: Torrent to return
		:type torrent: dict
		:return: None
		:rtype: None
		"""
		try:
			sources_information = self.scraper_class.sources_information
			# Compare and combine source meta
			tor_key = torrent['hash'] + torrent['debrid_provider']
			sources_information['cached_hashes'].add(torrent['hash'])
			if tor_key in sources_information['torrentCacheSources']:
				c_size = sources_information['torrentCacheSources'][tor_key].get('size', 0)
				n_size = torrent.get('size', 0)
				info = torrent.get('info', [])

				if c_size < n_size:
					sources_information['torrentCacheSources'].update({tor_key: torrent})

					sources_information['torrentCacheSources'][tor_key]['info'] \
						.extend([i for i in info if
								 i not in sources_information['torrentCacheSources'][tor_key].get('info', [])])
			else:
				sources_information['torrentCacheSources'].update({tor_key: torrent})
		except AttributeError:
			return

	def torrent_cache_check(self, torrent_list, info):
		"""
		Run cache check threads for given torrents
		:param torrent_list: List of torrents to check
		:type torrent_list: list
		:param info: Metadata on item to check
		:type info: dict
		:return: None
		:rtype: None
		"""
		self.threads.put(self._realdebrid_worker, copy.deepcopy(torrent_list), info)
		self.threads.wait_completion()

	def _realdebrid_worker(self, torrent_list, info):
		#try:
		if 1==1:
			hash_list = [i['hash'] for i in torrent_list]
			api = real_debrid.RealDebrid()
			real_debrid_cache = api.check_hash(hash_list)

			for i in torrent_list:
				try:
					if 'rd' not in real_debrid_cache.get(i['hash'], {}):
						continue
					if len(real_debrid_cache[i['hash']]['rd']) >= 1:
						if self.scraper_class.media_type == 'episode':
							self._handle_episode_rd_worker(i, real_debrid_cache, info)
						else:
							self._handle_movie_rd_worker(i, real_debrid_cache)
				except KeyError:
					pass
		#except Exception:
		#	#g.log_stacktrace()
		#	print(Exception)

	def _handle_movie_rd_worker(self, source, real_debrid_cache):
		for storage_variant in real_debrid_cache[source['hash']]['rd']:
			if not self.rd_api.is_streamable_storage_type(storage_variant):
				continue
			else:
				source['debrid_provider'] = 'real_debrid'
				self.store_torrent(source)

	def _handle_episode_rd_worker(self, source, real_debrid_cache, info):
		for storage_variant in real_debrid_cache[source['hash']]['rd']:

			if not self.rd_api.is_streamable_storage_type(storage_variant):
				continue

			if tools.get_best_episode_match('filename', storage_variant.values(), info):
				source['debrid_provider'] = 'real_debrid'
				self.store_torrent(source)
				break


class Sources(object):
	"""
	Handles fetching and processing of available sources for provided meta data
	"""

	def __init__(self, item_information):
		self.hash_regex = re.compile(r'btih:(.*?)(?:&|$)')
		self.canceled = False
		#self.torrent_cache = TorrentCache()
		self.torrent_threads = ThreadPool()
		#self.hoster_threads = ThreadPool()
		#self.adaptive_threads = ThreadPool()
		self.item_information = item_information
		self.media_type = self.item_information['info']['mediatype']
		self.torrent_providers = []
		#self.hoster_providers = []
		#self.adaptive_providers = []
		#self.cloud_scrapers = []
		self.running_providers = []
		self.language = 'en'
		self.sources_information = {
			"torrentCacheSources": {},
			"cloudFiles": [],
			"allTorrents": {},
			"cached_hashes": set(),
			"statistics": {
				"torrents": {"4K": 0, "1080p": 0, "720p": 0, "SD": 0, "total": 0},
				"torrentsCached": {"4K": 0, "1080p": 0, "720p": 0, "SD": 0, "total": 0},
				"cloudFiles": {"4K": 0, "1080p": 0, "720p": 0, "SD": 0, "total": 0},
				"totals": {"4K": 0, "1080p": 0, "720p": 0, "SD": 0, "total": 0},
				"filtered": {
					"torrents": {"4K": 0, "1080p": 0, "720p": 0, "SD": 0, "total": 0},
					"torrentsCached": {"4K": 0, "1080p": 0, "720p": 0, "SD": 0, "total": 0},
					"cloudFiles": {"4K": 0, "1080p": 0, "720p": 0, "SD": 0, "total": 0},
					"totals": {"4K": 0, "1080p": 0, "720p": 0, "SD": 0, "total": 0},
				},
				"remainingProviders": []
			}
		}

		#self.hoster_domains = {}
		self.progress = 0
		self.timeout_progress = 0
		self.runtime = 0
		#self.host_domains = []
		#self.host_names = []
		self.timeout = 45
		#self.window = SourceWindowAdapter(self.item_information, self)

		#self.silent = g.get_bool_runtime_setting('tempSilent')

		self.source_sorter = tools.SourceSorter(self.item_information)

		self.preem_enabled = False
		self.preem_waitfor_cloudfiles = True
		self.preem_cloudfiles = False
		#self.preem_adaptive_sources = g.get_bool_setting('preem.adaptiveSources')
		#self.preem_type = 0 #g.get_int_setting('preem.type')
		#self.preem_limit = 9 #g.get_int_setting('preem.limit')
		#self.preem_resolutions = tools.approved_qualities[1:self._get_pre_term_min()]
		#tools.PRE_TERM_BLOCK = False
		#self.PRE_TERM_BLOCK = False
		#self._prem_terminate = True
		#os.environ['data_path'] = os.path.join('./user_data/', 'providers')
		os.environ['data_path'] = tools.A4KPROVIDERS_PATH
		patch_ak4_requests()

	def get_sources(self):
		"""
		Main endpoint to initiate scraping process
		:param overwrite_cache:
		:return: Returns (uncached_sources, sorted playable sources, items metadata)
		:rtype: tuple
		"""
		try:
			print('Starting Scraping', 'debug')
			print("Timeout: {}".format(self.timeout), 'debug')
			#print("Pre-term-enabled: {}".format(self.preem_enabled), 'debug')
			#print("Pre-term-limit: {}".format(self.preem_limit), 'debug')
			#print("Pre-term-res: {}".format(self.preem_resolutions), 'debug')
			#print("Pre-term-type: {}".format(self.preem_type), 'debug')
			#print("Pre-term-cloud-files: {}".format(self.preem_cloudfiles), 'debug')
			#print("Pre-term-adaptive-files: {}".format(self.preem_adaptive_sources), 'debug')

			#self._handle_pre_scrape_modifiers()
			self._get_imdb_info()

			#if overwrite_torrent_cache:
			#	self._clear_local_torrent_results()
			#else:
			#	self._check_local_torrent_database()

			self._update_progress()
			if self._prem_terminate():
				print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				return self._finalise_results()

			self._init_providers()

			# Add the users cloud inspection to the threads to be run
			#self.torrent_threads.put(self._user_cloud_inspection)

			# Load threads for all sources
			self._create_torrent_threads()
			#self._create_hoster_threads()
			#self._create_adaptive_threads()

			start_time = time.time()
			while not ( len(self.torrent_providers) ) > 0:
				self.runtime = time.time() - start_time
				if self.runtime > 5:
					print('No providers enabled', 'warning')
					return

			self._update_progress()

			# Keep alive for gui display and threading
			print('Entering Keep Alive', 'info')

			while self.progress < 100:
				self.runtime = time.time() - start_time
				self._update_progress()
				self.timeout_progress = int(100 - float(1 - (self.runtime / float(self.timeout))) * 100)
				self.progress = int(100 - (	len(self.sources_information['statistics']['remainingProviders']) / float(len(self.torrent_providers)) * 100) )

				if self._prem_terminate() is True or (	len(self.sources_information['statistics']['remainingProviders']) == 0 and self.runtime > 5):
					# Give some time for scrapers to initiate
					break
				if self.canceled or self.runtime >= self.timeout:
					tools.PRE_TERM_BLOCK = True
					self.PRE_TERM_BLOCK = True
					break

				time.sleep(0.20)

			print('Exited Keep Alive', 'info')
			return self._finalise_results()

		finally:
			#self.window.close()
			print('EXIT')

	#def _handle_pre_scrape_modifiers(self):
	#	"""
	#	Detects preScrape, disables pre-termination and sets timeout to maximum value
	#	:return:
	#	:rtype:
	#	"""
	#	if g.REQUEST_PARAMS.get('action', '') == "preScrape":
	#		self.silent = True
	#		self.timeout = 180
	#		self._prem_terminate = self._disabled_prem_terminate
	
	#def _disabled_prem_terminate(self):
	#	return False

	def _create_torrent_threads(self):
		random.shuffle(self.torrent_providers)
		for i in self.torrent_providers:
			try: self.torrent_threads.put(self._get_torrent, self.item_information, i)
			except: print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

	def _is_playable_source(self, filtered=False):
		stats = self.sources_information['statistics']
		stats = stats['filtered'] if filtered else stats
		for stype in ["torrentsCached", "cloudFiles"]:
			if stats[stype]["total"] > 0:
				return True
		return False

	def _finalise_results(self):
		#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		self.allow_provider_requests = False
		self._send_provider_stop_event()
		
		print(self.sources_information['allTorrents'].values())
		
		uncached = [i for i in self.sources_information['allTorrents'].values()
					if i['hash'] not in self.sources_information['cached_hashes']]

		# Check to see if we have any playable unfiltered sources, if not do cache assist
		if not self._is_playable_source():
			#if self.silent:
			#	g.notification(g.ADDON_NAME, g.get_language_string(30055))
			return uncached, [], self.item_information

		# Return sources list
		sources_list = (
			list(self.sources_information['torrentCacheSources'].values()) +
			self.sources_information['cloudFiles']
		)
		return uncached, sources_list, self.item_information

	def _get_imdb_info(self):
		if self.media_type == 'movie':
			# Confirm movie year against IMDb's information
			imdb_id = self.item_information['info'].get("imdb_id")
			if imdb_id is None:
				return
			import requests
			try:
				resp = self._imdb_suggestions(imdb_id)
				year = resp.get('y', self.item_information['info']['year'])
				if year is not None and year != self.item_information['info']['year']:
					self.item_information['info']['year'] = str(year)
			except requests.exceptions.ConnectionError as ce:
				print("Unable to obtain IMDB suggestions to confirm movie year", "warning")
				print(ce, "debug")

	@staticmethod
	def _imdb_suggestions(imdb_id):
		try:
			import requests
			from requests.adapters import HTTPAdapter
			from urllib3 import Retry
			session = requests.Session()
			retries = Retry(
				total=5, backoff_factor=0.1, status_forcelist=[429, 500, 502, 503, 504]
			)
			session.mount("https://", HTTPAdapter(max_retries=retries, pool_maxsize=100))

			resp = session.get('https://v2.sg.media-imdb.com/suggestion/t/{}.json'.format(imdb_id))
			resp = json.loads(resp.text)['d'][0]
			return resp
		except (ValueError, KeyError):
			print("Failed to get IMDB suggestion", "warning")
			return {}

	def _send_provider_stop_event(self):
		for provider in self.running_providers:
			if hasattr(provider, 'cancel_operations') and callable(provider.cancel_operations):
				provider.cancel_operations()

	#def _store_torrent_results(self, torrent_list):
	#	if len(torrent_list) == 0:
	#		return
	#	self.torrent_cache.add_torrent(self.item_information, torrent_list)

	def _init_providers(self):
		sys.path.append(tools.ADDON_USERDATA_PATH)
		try:
			if tools.ADDON_USERDATA_PATH not in sys.path:
				sys.path.append(tools.ADDON_USERDATA_PATH)
				providers = importlib.import_module("providers")
			else:
				providers = reload_module(importlib.import_module("providers"))
		except ValueError:
			print('No providers installed', 'warning')
			return

		#providers_dict = {'hosters': [], 
		#'torrent': [('providers.a4kScrapers.en.torrent', 'bitlord', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'bitsearch', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'btdig', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'cached', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'glo', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'kickass', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'lime', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'magnetdl', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'piratebay', 'a4kScrapers'), 
		##('providers.a4kScrapers.en.torrent', 'rutor', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'showrss', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'torrentdownload', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'torrentio', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'torrentz2', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'yts', 'a4kScrapers')], 
		#'adaptive': []}
		#providers_dict = providers.get_relevant(self.language)
		#print(providers_dict)
		
		#providers_dict = get_providers_dict()
		providers_dict = get_providers()
		

		torrent_providers = providers_dict['torrent']
		try:
			self.torrent_providers = torrent_providers
		except:
			print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

	def _exit_thread(self, provider_name):
		if provider_name in self.sources_information['statistics']['remainingProviders']:
			self.sources_information['statistics']['remainingProviders'].remove(provider_name)

	def _process_provider_torrent(self, torrent, provider_name, info):
		torrent['type'] = 'torrent'

		if not torrent.get('info'):
			torrent['info'] = tools.get_info(torrent['release_title'])

		if torrent.get("quality") not in tools.approved_qualities_set:
			torrent['quality'] = tools.get_quality(torrent['release_title'])

		torrent['hash'] = torrent.get('hash', self.hash_regex.findall(torrent['magnet'])[0]).lower()
		torrent['pack_size'], torrent['size'] = self._torrent_filesize(torrent, info)
		torrent['seeds'] = self._torrent_seeds(torrent)

		if 'provider_name_override' in torrent:
			torrent['provider'] = torrent['provider_name_override']
		else:
			torrent['provider'] = provider_name

	def _get_torrent(self, info, provider):
		# Extract provider name from Tuple
		provider_name = provider[1].upper()

		# Begin Scraping Torrent Sources
		try:
			self.sources_information['statistics']['remainingProviders'].append(provider_name)

			provider_module = importlib.import_module("{}.{}".format(provider[0], provider[1]))
			if not hasattr(provider_module, "sources"):
				print("Invalid provider, Source Class missing", "warning")
				return

			provider_source = provider_module.sources()

			if not hasattr(provider_source, self.media_type):
				print("Skipping provider: {} - Does not support {} types".format(provider_name, self.media_type),
					  "warning")
				return

			self.running_providers.append(provider_source)

			if self.media_type == 'episode':
				simple_info = tools._build_simple_show_info(info)

				torrent_results = provider_source.episode(simple_info, info)
			else:
				simple_info = tools._build_simple_movie_info(info)

				try:
					# new `simple_info`-based call
					torrent_results = provider_source.movie(simple_info, info)
				except TypeError:
					# legacy calls
					try:
						torrent_results = provider_source.movie(
							info['info']['title'],
							str(info['info']['year']),
							info['info'].get('imdb_id'),
						)
					except TypeError:
						torrent_results = provider_source.movie(
							info['info']['title'], str(info['info']['year'])
						)

			if torrent_results is None:
				self.sources_information['statistics']['remainingProviders'].remove(provider_name)
				return

			if self.canceled:
				return

			if len(torrent_results) > 0:
				# Begin filling in optional dictionary returns
				for torrent in torrent_results:
					self._process_provider_torrent(torrent, provider_name, info)

				torrent_results = {value['hash']: value for value in torrent_results}.values()
				start_time = time.time()

				# actually stores torrent in the db cache, later it checks RD cache. WRONG_Check Debrid Providers for cached copies
				#self._store_torrent_results(torrent_results)

				if self.canceled:
					return

				[self.sources_information['allTorrents'].update({torrent['hash']: torrent})
				 for torrent in torrent_results]

				# Check Debrid Providers for cached copies
				TorrentCacheCheck(self).torrent_cache_check([i for i in torrent_results], info)

				print("{} cache check took {} seconds".format(provider_name, time.time() - start_time), "debug")

			self.running_providers.remove(provider_source)

			return

		finally:
			self.sources_information['statistics']['remainingProviders'].remove(provider_name)


	def _user_cloud_inspection(self):
		self.sources_information['statistics']['remainingProviders'].append("Cloud Inspection")
		try:
			thread_pool = ThreadPool()
			if self.media_type == 'episode':
				simple_info = tools._build_simple_show_info(self.item_information)
			else:
				simple_info = tools._build_simple_movie_info(self.item_information)

			cloud_scrapers = [
				{"setting": "rd.cloudInspection", "provider": RealDebridCloudScraper,
				 "enabled": g.real_debrid_enabled()},
			]

			self._prem_terminate = False
			for cloud_scraper in cloud_scrapers:
				if cloud_scraper['enabled'] and g.get_bool_setting(cloud_scraper['setting']):
					self.cloud_scrapers.append(cloud_scraper['provider'])
					thread_pool.put(cloud_scraper['provider'](self._prem_terminate).get_sources, self.item_information,
									simple_info)

			sources = thread_pool.wait_completion()
			self.sources_information['cloudFiles'] = sources if sources else []

		finally:
			self.sources_information['statistics']['remainingProviders'].remove("Cloud Inspection")


	def _update_progress(self):

		def _get_quality_count_dict(source_list):
			_4k = 0
			_1080p = 0
			_720p = 0
			_sd = 0

			for source in source_list:
				if source['quality'] == '4K':
					_4k += 1
				elif source['quality'] == '1080p':
					_1080p += 1
				elif source['quality'] == '720p':
					_720p += 1
				elif source['quality'] == 'SD':
					_sd += 1

			return {
				"4K": _4k, "1080p": _1080p, "720p": _720p, "SD": _sd,
				"total": _4k + _1080p + _720p + _sd
			}

		def _get_total_quality_dict(quality_dict_list):
			total_counter = Counter()

			for quality_dict in quality_dict_list:
				total_counter.update(quality_dict)

			return dict(total_counter)

		# Get qualities by source type and store result
		self.sources_information['statistics']['torrents'] = _get_quality_count_dict(
			list(self.sources_information['allTorrents'].values())
		)
		self.sources_information['statistics']['torrentsCached'] = _get_quality_count_dict(
			list(self.sources_information['torrentCacheSources'].values())
		)
		self.sources_information['statistics']['cloudFiles'] = _get_quality_count_dict(
			self.sources_information['cloudFiles']
		)

		self.sources_information['statistics']['totals'] = _get_total_quality_dict(
			[
				self.sources_information['statistics']['torrents'],
				self.sources_information['statistics']['cloudFiles']
			]
		)

		# Get qualities by source type after source filtering and store result
		self.sources_information['statistics']['filtered']['torrents'] = _get_quality_count_dict(
			self.source_sorter.filter_sources(list(self.sources_information['allTorrents'].values()))
		)
		self.sources_information['statistics']['filtered']['torrentsCached'] = _get_quality_count_dict(
			self.source_sorter.filter_sources(list(self.sources_information['torrentCacheSources'].values()))
		)
		self.sources_information['statistics']['filtered']['cloudFiles'] = _get_quality_count_dict(
			self.source_sorter.filter_sources(self.sources_information['cloudFiles'])
		)
		self.sources_information['statistics']['filtered']['totals'] = _get_total_quality_dict(
			[
				self.sources_information['statistics']['filtered']['torrentsCached'],
				self.sources_information['statistics']['filtered']['cloudFiles']
			]
		)

	def _get_pre_term_min(self):
		if self.media_type == 'episode':
			preem_min = tools.get_setting('preem.tvres', 'int') + 1
		else:
			preem_min = tools.get_setting('preem.movieres', 'int') + 1
		return preem_min

	def _get_filtered_count_by_resolutions(self, resolutions, quality_count_dict):
		return sum(quality_count_dict[resolution] for resolution in resolutions)

	
	def _prem_terminate(self):  # pylint: disable=method-hidden
		if self.canceled:
			print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			tools.PRE_TERM_BLOCK = True
			return True

		return False

	"""
		if not self.preem_enabled:
			return False
	

		if (
				self.preem_waitfor_cloudfiles and
				"Cloud Inspection" in self.sources_information['statistics']['remainingProviders']
		):
			return False

		if self.preem_cloudfiles and self.sources_information['statistics']['filtered']['cloudFiles']['total'] > 0:
			self.PRE_TERM_BLOCK = True
			return True
		if self.preem_adaptive_sources and self.sources_information['statistics']['filtered']['adaptive']['total'] > 0:
			self.PRE_TERM_BLOCK = True
			return True

		pre_term_log_string = 'Pre-emptively Terminated'

		try:
			if self.preem_type == 0 and self._get_filtered_count_by_resolutions(
					self.preem_resolutions, self.sources_information['statistics']['filtered']['torrentsCached']
			) >= self.preem_limit:
				print(pre_term_log_string, 'info')
				self.PRE_TERM_BLOCK = True
				return True
			if self.preem_type == 1 and self._get_filtered_count_by_resolutions(
				self.preem_resolutions, self.sources_information['statistics']['filtered']['hosters']
			) >= self.preem_limit:
				print(pre_term_log_string, 'info')
				self.PRE_TERM_BLOCK = True
				return True
			if self.preem_type == 2 and self._get_filtered_count_by_resolutions(
					self.preem_resolutions, self.sources_information['statistics']['filtered']['torrentsCached']
			) + self._get_filtered_count_by_resolutions(
				self.preem_resolutions, self.sources_information['statistics']['filtered']['hosters']
			) >= self.preem_limit:
					print(pre_term_log_string, 'info')
					self.PRE_TERM_BLOCK = True
					return True

		except (ValueError, KeyError, IndexError) as e:
			print("Error getting data for preterm determination: {}".format(repr(e)), "error")
			pass

		return False
	"""

	@staticmethod
	def _torrent_filesize(torrent, info):
		size = torrent.get('size', 0)
		pack_size = size
		try:
			size = float(size)
		except (ValueError, TypeError):
			return 0
		size = int(size)

		if torrent['package'] == 'show':
			size = size / int(info['show_episode_count'])
		elif torrent['package'] == 'season':
			size = size / int(info['episode_count'])
		return pack_size, size

	@staticmethod
	def _torrent_seeds(torrent):
		seeds = torrent.get('seeds')
		if seeds is None or isinstance(seeds, str) and not seeds.isdigit():
			return 0

		return int(torrent['seeds'])

