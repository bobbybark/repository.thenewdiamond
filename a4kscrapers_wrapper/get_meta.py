import requests
import os
import json
import hashlib
import time

try:
	from resources.lib.modules.globals import g
except:
	import tools


try:
	unicode = unicode  # noqa # pylint: disable=undefined-variable
except NameError:
	unicode = str

def log(*args, **kwargs):
	for i in args:
		try:
			import xbmc
			xbmc.log(str(i)+'===>A4K_Wrapper', level=xbmc.LOGFATAL)
		except:
			print(i)

def selectFromDict(options, name):
	index = 0
	indexValidList = []
	log('Select a ' + name + ':')
	for optionName in options:
		index = index + 1
		indexValidList.extend([options[optionName]])
		log(str(index) + ') ' + optionName)
	inputValid = False
	while not inputValid:
		inputRaw = input(name + ': ')
		inputNo = int(inputRaw) - 1
		if inputNo > -1 and inputNo < len(indexValidList):
			selected = indexValidList[inputNo]
			for i in options:
				if options[i] == selected:
					selection = i
					break
			log('Selected ' +  name + ': ' + selection)
			inputValid = True
			break
		else:
			log('Please select a valid ' + name + ' number')
	return selected


def get_http(url, headers=False):
	succeed = 0
	if not headers:
		headers = {'User-agent': 'Kodi/21.0 ( phil65@kodi.tv )'}
	while (succeed < 2) :
		try:
			request = requests.get(url, headers=headers)
			return request.text
		except Exception as e:
			log('get_http: could not get data from %s' % url)
			xbmc.sleep(500)
			succeed += 1
	return None

def read_all_text(file_path):
	try:
		f = open(file_path, "r")
		return f.read()
	except IOError:
		return None
	finally:
		try:
			f.close()
		except Exception:
			pass

def write_all_text(file_path, content):
	try:
		f = open(file_path, "w")
		return f.write(content)
	except IOError:
		return None
	finally:
		try:
			f.close()
		except Exception:
			pass


def get_response_cache(url='', cache_days=7.0, folder=False, headers=False):
	now = time.time()
	url = url.encode('utf-8')
	hashed_url = hashlib.md5(url).hexdigest()
	try: cache_path = os.path.join(g.ADDON_USERDATA_PATH, folder)
	except: cache_path = os.path.join(tools.ADDON_USERDATA_PATH, folder)

	if not os.path.exists(cache_path):
		os.mkdir(cache_path)
	cache_seconds = int(cache_days * 86400.0)
	path = os.path.join(cache_path, '%s.txt' % hashed_url)
	if os.path.exists(path) and ((now - os.path.getmtime(path)) < cache_seconds):
		results = read_all_text(path)
		try: results = eval(results)
		except: pass
	else:
		response = get_http(url, headers)
		try:
			results = json.loads(response)
			#save_to_file(results, hashed_url, cache_path)
			#file_path = os.path.join(cache_path, hashed_url)
			write_all_text(path, str(results))
		except:
			log('Exception: Could not get new JSON data from %s. Tryin to fallback to cache' % url)
			log(response)
			results = read_all_text(path) if os.path.exists(path) else []
	if not results:
		return None
	return results

def get_tmdb_from_imdb(imdb, media_type):
	response = get_tmdb_data('find/%s?external_source=%s&language=%s&' % (imdb, 'imdb_id', 'en'), 30)
	if media_type == 'movie':
		tmdb = response['movie_results'][0]['id']
	else:
		tmdb = response['tv_results'][0]['id']
	return tmdb

def get_tmdb_data(url='', cache_days=14, folder='TheMovieDB'):
	try: url = 'https://api.themoviedb.org/3/%sapi_key=%s' % (url, tools.tmdb_API_key)
	except: url = 'https://api.themoviedb.org/3/%sapi_key=%s' % (url, g.get_setting("tmdb.apikey"))
	return get_response_cache(url, cache_days, folder)

def get_tvshow_ids(tvshow_id=None, cache_time=14):
	if not tvshow_id:
		return None
	session_str = ''
	response = get_tmdb_data('tv/%s?append_to_response=external_ids&language=%s&include_image_language=en,null,%s&%s' % (tvshow_id, 'en', 'en', session_str), cache_time)
	if not response:
		return False
	external_ids = response.get('external_ids')
	return external_ids

def get_fanart_data(url='', tmdb_id=None, media_type=None, cache_days=14, folder='FanartTV'):
	try: fanart_api = g.get_setting("fanart.apikey")
	except: fanart_api = tools.fanart_api_key
	if media_type =='tv':
		tvdb_id = get_tvshow_ids(tmdb_id)
		tvdb_id = tvdb_id['tvdb_id']
		url = 'http://webservice.fanart.tv/v3/tv/'+str(tvdb_id)+'?api_key=' + fanart_api
		#response = requests.get(url).json()
	elif media_type =='tv_tvdb':
		url = 'http://webservice.fanart.tv/v3/tv/'+str(tmdb_id)+'?api_key=' + fanart_api
		#response = requests.get(url).json()
	else:
		url = 'http://webservice.fanart.tv/v3/movies/'+str(tmdb_id)+'?api_key=' + fanart_api
		#response = requests.get(url).json()
	return get_response_cache(url, cache_days, folder)


def get_movie_meta(tmdb=None, movie_name=None, year=None, imdb=None):
	if imdb:
		tmdb = get_tmdb_from_imdb(imdb, 'movie')
	if not tmdb:
		if year:
			url = 'search/movie?query=%s&primary_release_year=%s&language=en&page=1&' % (movie_name, year)
			response = get_tmdb_data(url, cache_days=7)
			for i in response['results']:
				if int(year) == int(i['release_date'][:4]):
					tmdb = i['id']
					break
		else:
			url = 'search/movie?query=%s&language=en&page=1&' % (movie_name)
			response = get_tmdb_data(url, cache_days=7)
			options = {}
			if len(response['results']) == 1:
				tmdb = response['results'][0]['id']
			else:
				for i in response['results']:
					list_name = '%s (%s)' % (i['title'], str(i['release_date'][:4]))
					options[list_name] = str(i['id'])
				tmdb = selectFromDict(options, 'Movie')
	log(str(movie_name), 'tmdb=', str(tmdb))
	if tmdb:
		url = 'movie/%s?language=en&append_to_response=external_ids,alternative_titles&' % (tmdb)
		response = get_tmdb_data(url, cache_days=7)
		alternative_titles = []
		for i in response['alternative_titles']['titles']:
			if i['iso_3166_1'] in ('US','UK','GB','AU'):
				alternative_titles.append(i['title'])
		imdb = response['external_ids']['imdb_id']
		movie_name = response['title']
		backdrop_path = 'https://www.themoviedb.org/t/p/original/' + response['backdrop_path']
		imdb = response['imdb_id']
		vote_average = response['vote_average']
		release_date = response['release_date']
		poster_path = 'https://www.themoviedb.org/t/p/original/' + response['poster_path']
		original_title = response['original_title']
		movie_meta = {'download_type': 'movie', 'episode': '', 'imdb_id': imdb, 'is_movie': True, 'is_tvshow': False, 'media_type': 'movie', 'season': '', 'title': movie_name, 'tmdb_id': tmdb, 'tvshow': '', 'tvshow_year': '', 'year': response['release_date'][:4],
		'info': {'mediatype': 'movie', 'episode': '', 'imdb_id': imdb, 'is_movie': True, 'is_tvshow': False, 'media_type': 'movie', 'season': '', 'title': movie_name, 'tmdb_id': tmdb, 'tvshow': '', 'tvshow_year': '', 'year': response['release_date'][:4]}
		}
		return movie_meta

def get_episode_meta(season, episode,tmdb=None, show_name=None, year=None):
	show = {}
	if not tmdb:
		if year:
			url = 'search/tv?query=%s&first_air_date_year=%s&language=en&page=1&' % (show_name, year)
			response = get_tmdb_data(url, cache_days=7)
			for i in response['results']:
				if int(year) == int(i['first_air_date'][:4]):
					tmdb = i['id']
					break
		else:
			url = 'search/tv?query=%s&language=en&page=1&' % (show_name)
			response = get_tmdb_data(url, cache_days=7)
			options = {}
			if len(response['results']) == 1:
				tmdb = response['results'][0]['id']
			for i in response['results']:
				if i['name'] == show_name:
					tmdb = i['id']
			if not tmdb:
				for i in response['results']:
					list_name = '%s (%s)' % (i['name'], str(i['first_air_date'][:4]))
					options[list_name] = str(i['id'])
				tmdb = selectFromDict(options, 'Show')
	log(str(show_name), 'tmdb=', str(tmdb))
	if tmdb:
		url = 'tv/%s?language=en&append_to_response=external_ids,alternative_titles&' % (tmdb)
		response = get_tmdb_data(url, cache_days=7)
		alternative_titles = []
		for i in response['alternative_titles']['results']:
			if i['iso_3166_1'] in ('US','UK','GB','AU'):
				alternative_titles.append(i['title'])

		imdb = response['external_ids']['imdb_id']
		tvdb = response['external_ids']['tvdb_id']
		show_name = response['name']
		status = response['status']
		if status.lower() in ('ended','cancelled'):
			is_airing = 0
		else:
			is_airing = 1
		backdrop_path = 'https://www.themoviedb.org/t/p/original/' + response['backdrop_path']
		episode_run_time = response['episode_run_time']
		first_air_date = response['first_air_date']
		tot_episode_count = 0
		for i in response['seasons']:
			if i['season_number'] == season:
				absolute_tmdb = tot_episode_count + episode
				if episode == 1:
					absolute_tmdb_ep_1 = absolute_tmdb
				else:
					absolute_tmdb_ep_1 = tot_episode_count
			if i['season_number'] > 0:
				tot_episode_count = tot_episode_count + i['episode_count']
			total_seasons = i['season_number']
		url = 'tv/%s/season/%s?language=en&' % (tmdb, season)
		response = get_tmdb_data(url, cache_days=7)

		show_year = '(' + str(first_air_date[:4]) + ')'
		if not show_year in str(show_name) and not str(first_air_date[:4]) in str(show_name):
			alternative_titles.append(show_name + ' ' + show_year)
			alternative_titles.append(show_name + ' - ' + first_air_date[:4])

		season_dict = {}
		season_dict['episodes'] = []
		for i in response['episodes']:
			curr_episode = {'aliases': alternative_titles, 'originaltitle': i['name'],'tvshowtitle': show_name,'tvshow': show_name, 'download_type': 'episode', 'episode': i['episode_number'], 'imdb_id': imdb, 'imdbnumber': imdb,'air_date': i['air_date'],'episode_number': i['episode_number'],'episode_type': i['episode_type'],'name': i['name'],'runtime': i['runtime'],'season_number': i['season_number'],'show_id': i['show_id'],'still_path': 'https://www.themoviedb.org/t/p/original/' +i['still_path'],
			'vote_average': i['vote_average'], 'imdb': imdb, 'tvdb': tvdb, 'tmdb': tmdb, 'season': i['season_number'], 'info': 
			{'aliases': alternative_titles, 'originaltitle': i['name'], 'tvshowtitle': show_name, 'episode': i['episode_number'], 'imdb_id': imdb, 'imdbnumber': imdb, 'mediatype': 'episode', 'season': i['season_number'], 'title': i['name'], 'tmdb_id': tmdb, 'tmdb_show_id': tmdb, 'tvdb_id': tvdb, 'tvdb_show_id': tvdb, 'tvshow': show_name, 'tvshow.imdb_id': imdb, 'tvshow.tmdb_id': tmdb, 'tvshow.tvdb_id': tvdb, 'tvshow.year': str(first_air_date[:4]), 'tvshowtitle': show_name, 'year': str(i['air_date'][:4])}
			, 'is_airing': is_airing, 'is_movie': False, 'is_tvshow': True, 'media_type': 'episode', 'mediatype': 'episode', 'title': i['name'], 'tmdb_id': tmdb, 'tvshow': show_name, 'tvshow_year': first_air_date[:4], 'year': i['air_date'][:4]}
			season_episodes = i['episode_number']
			if i['episode_number'] == episode:
				episode_title = i['name']
				episode_year = i['air_date'][:4]
			if i['episode_number'] == 1:
				curr_episode['absoluteNumber'] = absolute_tmdb_ep_1
			else:
				curr_episode['absoluteNumber'] = absolute_tmdb_ep_1 + i['episode_number'] -1 
			season_dict['episodes'].append(curr_episode)
		for idx, i in enumerate(season_dict['episodes']):
			season_dict['episodes'][idx]['episode_count'] = i['episode_number']
			season_dict['episodes'][idx]['season_count'] = total_seasons
			season_dict['episodes'][idx]['show_episode_count'] = tot_episode_count
		show = {'tmdb': tmdb, 'imdb': imdb, 'tvdb': tvdb, 'name': show_name, 'first_air_date': first_air_date, 'tot_episode_count': tot_episode_count, 'total_seasons': total_seasons, 'backdrop_path': backdrop_path, 'episode_run_time': episode_run_time}
		show['tmdb_seasons'] = season_dict
		show['tmdb_seasons_episode_tot'] = season_episodes
		show['tmdb_absolute_number'] = absolute_tmdb
		show['status'] = status
		show['alternative_titles'] = alternative_titles

		url = 'http://api.tvmaze.com/lookup/shows?thetvdb='+str(tvdb)
		response = get_response_cache(url=url, cache_days=7.0, folder='TVMaze')

		show['tvmaze_runtime'] = response['runtime']
		show['tvmaze_averageRuntime'] = response['averageRuntime']
		show['tvmaze_premiered'] = response['premiered']
		show['tvmaze_show_id'] = response['id']

		url = 'http://api.tvmaze.com/shows/'+str(show['tvmaze_show_id'])+'/episodes'
		response = get_response_cache(url=url, cache_days=7.0, folder='TVMaze')
		season_dict = {}
		season_dict['episodes'] = []
		tot_episode_count = 0
		for i in response: #year
			if i['season'] > 0:
				tot_episode_count = tot_episode_count + 1
			if i['season'] == season:
				curr_episode = {'aliases': alternative_titles,'originaltitle': i['name'], 'tvshowtitle': show_name, 'tvshow': show_name, 'download_type': 'episode', 'episode': i['number'], 'air_date': i['airdate'],'episode_number': i['number'],'episode_type': i['type'],'name': i['name'],'runtime': i['runtime'],'season_number': i['season'],'show_id': show['tvmaze_show_id'],'still_path': i['image']['original'],
				'vote_average': i['rating']['average'], 'tmdb': tmdb, 'imdb': imdb, 'tvdb': tvdb, 'imdb_id': imdb,'imdbnumber': imdb, 'is_airing': is_airing, 'is_movie': False, 'is_tvshow': True, 'media_type': 'episode','mediatype': 'episode', 'season': i['season'], 'title':  i['name'], 'tmdb_id': tmdb, 'tvshow': show_name, 'tvshow_year': first_air_date[:4], 'year': i['airdate'][:4], 
				'info': {'aliases': alternative_titles, 'originaltitle': i['name'], 'tvshowtitle': show_name, 'episode': i['number'],'imdb_id': imdb,'imdbnumber': imdb,'mediatype': 'episode','season': i['season'],'title': i['name'],'tmdb_id': tmdb,'tmdb_show_id': tmdb,'tvdb_id': tvdb,'tvdb_show_id': tvdb,'tvshow': show_name,'tvshow.imdb_id': imdb,'tvshow.tmdb_id': tmdb,'tvshow.tvdb_id': tvdb,'tvshow.year': str(first_air_date[:4]),'tvshowtitle': show_name,'year': str(i['airdate'][:4])},
				}
				season_episodes = i['number']
			if i['season'] == season and i['number'] == episode:
				absolute_tvmaze = tot_episode_count
			if i['season'] == season:
				curr_episode['absoluteNumber'] = tot_episode_count
				season_dict['episodes'].append(curr_episode)
			total_seasons = i['season']
		for idx, i in enumerate(season_dict['episodes']):
			season_dict['episodes'][idx]['season_count'] = total_seasons
			season_dict['episodes'][idx]['show_episode_count'] = tot_episode_count
		show['tvmaze_total_seasons'] = i['season']
		show['tvmaze_seasons'] = season_dict
		show['tvmaze_seasons_episode_tot'] = season_episodes
		show['tvmaze_absolute_number'] = absolute_tvmaze
		show['tvmaze_tot_episode_count'] = tot_episode_count
		show['tvmaze_total_seasons'] = total_seasons

	#import pprint
	#from pprint import pprint
	#pprint(show)
	episode_meta = {'year': episode_year, 'episode': episode,'imdb_id': imdb,'imdbnumber': imdb,'mediatype': 'episode','season': season,'title': episode_title,'tvshow_year': first_air_date[:4], 'tvshow': show_name,'is_movie': False, 'is_tvshow': True, 'tmdb_id': tmdb,'imdb_id': imdb, 'media_type': 'episode', 'download_type': 'episode','absoluteNumber': show['tmdb_absolute_number'],'episode_count': show['tmdb_seasons_episode_tot'],'info': {'tvshow': show_name, 'episode': episode,'imdb_id': imdb,'imdbnumber': imdb,'mediatype': 'episode','season': season,'title': episode_title,'tmdb_id': tmdb,'tmdb_show_id': tmdb,
	'tvdb_id': tvdb,'tvdb_show_id': tvdb,'tvshow.imdb_id': imdb,'tvshow.tmdb_id': tmdb,'tvshow.tvdb_id': tvdb,'tvshow.year': first_air_date[:4],'tvshowtitle': show_name,'year': episode_year},'is_airing': is_airing,'season_count': show['total_seasons'],'show_episode_count': show['tot_episode_count']}
	show['episode_meta'] = episode_meta
	return show
	


def get_fanart_results(tvdb_id, media_type=None, show_season = None):
	hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo = '', '', '', '', '', '', '', '', '', '', '', '';
	tv_dict = {'hdclearart': None,'seasonposter': None,'seasonthumb': None,'seasonbanner': None,'tvthumb': None,'tvbanner': None,'showbackground': None,'clearlogo': None,'characterart': None,'tvposter': None,'clearart': None,'hdtvlogo': None}

	if 'tv_tvdb' == media_type:
		try: 
			#response = requests.get('http://webservice.fanart.tv/v3/tv/'+str(tvdb_id)+'?api_key='+str(fanart_api)).json()
			response = get_fanart_data(tmdb_id=tvdb_id,media_type='tv_tvdb')
		except: 
			response = None
	else:
		#response = requests.get('http://webservice.fanart.tv/v3/movies/'+str(tmdb_id)+'?api_key='+str(fanart_api)).json()
		response = get_fanart_data(tmdb_id=tvdb_id,media_type='movie')
	
	if 'tv_tvdb' == media_type:
		for i in response:
			#print_log(i)
			for j in response[i]:
				try:
					lang = j['lang']
					if j['lang'] == 'en' or (i == 'showbackground' and j['lang'] == ''):
						if i in ('seasonposter', 'seasonthumb', 'seasonbanner'):
							for k in response[i]:
								if int(k['season']) == show_season and k['lang'] == 'en':
									tv_dict[i] = k['url']
							break
						if i in ('hdclearart', 'tvthumb', 'tvbanner', 'showbackground', 'clearlogo', 'characterart', 'tvposter', 'clearart', 'hdtvlogo'):
							tv_dict[i] = j['url']
							break
				except:
					pass
		#return hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo
		return tv_dict['hdclearart'], tv_dict['seasonposter'], tv_dict['seasonthumb'], tv_dict['seasonbanner'], tv_dict['tvthumb'], tv_dict['tvbanner'], tv_dict['showbackground'], tv_dict['clearlogo'], tv_dict['characterart'], tv_dict['tvposter'], tv_dict['clearart'], tv_dict['hdtvlogo']
	else:
		movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground = '', '', '', '', '', '', '', '', ''
		movie_dict = {'movielogo': None,'hdmovielogo': None,'movieposter': None,'hdmovieclearart': None,'movieart': None,'moviedisc': None,'moviebanner': None,'moviethumb': None,'moviebackground': None}
		for i in response:
			#print_log(i)
			for j in response[i]:
				try:
					lang = j['lang']
					if j['lang'] == 'en' or (i == 'movielogo' and j['lang'] == '') or (i == 'hdmovielogo' and j['lang'] == ''):
						if i in ('movielogo', 'hdmovielogo'):
							tv_dict[i] = j['url']
							break
						if i in ('movieposter','hdmovieclearart','movieart','moviedisc','moviebanner','moviethumb','moviebackground'):
							for k in response[i]:
								if k['lang'] == 'en':
									tv_dict[i] = k['url']
				except:
					pass

		#return movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground
		return movie_dict['movielogo'], movie_dict['hdmovielogo'], movie_dict['movieposter'], movie_dict['hdmovieclearart'], movie_dict['movieart'], movie_dict['moviedisc'], movie_dict['moviebanner'], movie_dict['moviethumb'], movie_dict['moviebackground']