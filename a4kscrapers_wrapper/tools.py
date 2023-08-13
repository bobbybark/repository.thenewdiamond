import unicodedata
import hashlib, json

import copy
import importlib
import json
import random
import re
import sys
import time
#from collections import OrderedDict, Counter

import inspect
import requests
import string
import os

from inspect import currentframe, getframeinfo

BROWSER_AGENTS = [
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537."
	"36 Edge/12.246",
	"Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) "
	"Version/9.0.2 Safari/601.3.9"
	"Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
	"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
]

try:
	unicode = unicode  # noqa # pylint: disable=undefined-variable
except NameError:
	unicode = str

from inspect import currentframe, getframeinfo
folder = getframeinfo(currentframe()).filename
folder = folder.replace(getframeinfo(currentframe()).filename.split('/')[-1],'')

#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

#ADDON_USERDATA_PATH = './user_data'
ADDON_USERDATA_PATH = os.path.join(folder, 'user_data')
ADDON_NAME = 'plugin.video.a4kWrapper'
A4KPROVIDERS_PATH = os.path.join(ADDON_USERDATA_PATH, 'providers')
SETTING_XML = os.path.join(ADDON_USERDATA_PATH, 'settings.xml')
PROVIDERS_JSON = os.path.join(ADDON_USERDATA_PATH, 'provider.json')
OPENSUB_USERNAME = 'username'
OPENSUB_PASSWORD = 'password'
PID_FILE = os.path.join(ADDON_USERDATA_PATH, 'pid')

VIDEO_META = None
SUB_FILE = None

filter_string = 'HI10,DV,HDR,HC,WMV,3D,HEVC,HYBRID,SCR,CAM'


PRE_TERM_BLOCK = False

exclusions = ["soundtrack", "gesproken"]
_APOSTROPHE_SUBS = re.compile(r"\\'s|'s|&#039;s| 039 s")
_SEPARATORS = re.compile(r'[:|/,!?()"[\]\-\\_.{}]|(?<![:|/,!?()"[\]\-\\_.{}\s]dd)\+')
_WHITESPACE = re.compile(r'\s+')
_SINGLE_QUOTE = re.compile(r"['`]")
_AMPERSAND = re.compile(r'&#038;|&amp;|&')
_EPISODE_NUMBERS = re.compile(r'.*((?:s\d+ ?e\d+ )|(?:season ?\d+ ?(?:episode|ep) ?\d+)|(?: \d+ ?x ?\d+ ))')
_ASCII_NON_PRINTABLE = re.compile(r'[^{}]'.format(re.escape(string.printable)))

approved_qualities = ["4K", "1080p", "720p", "SD"]
approved_qualities_set = set(approved_qualities)

INFO_TYPES = {
	"AVC": ["x264", "x 264", "h264", "h 264", "avc"],
	"HEVC": ["x265", "x 265", "h265", "h 265", "hevc"],
	"XVID": ["xvid"],
	"DIVX": ["divx"],
	"MP4": ["mp4"],
	"WMV": ["wmv"],
	"MPEG": ["mpeg"],
	"REMUX": ["remux", "bdremux"],
	"DV": [" dv ", "dovi", "dolby vision", "dolbyvision"],
	"HDR": [
		" hdr ",
		"hdr10",
		"hdr 10",
		"uhd bluray 2160p",
		"uhd blu ray 2160p",
		"2160p uhd bluray",
		"2160p uhd blu ray",
		"2160p bluray hevc truehd",
		"2160p bluray hevc dts",
		"2160p bluray hevc lpcm",
		"2160p us bluray hevc truehd",
		"2160p us bluray hevc dts",
	],
	"SDR": [" sdr"],
	"AAC": ["aac"],
	"DTS-HDMA": ["hd ma", "hdma"],
	"DTS-HDHR": ["hd hr", "hdhr", "dts hr", "dtshr"],
	"DTS-X": ["dtsx", " dts x"],
	"ATMOS": ["atmos"],
	"TRUEHD": ["truehd", "true hd"],
	"DD+": ["ddp", "eac3", " e ac3", " e ac 3", "dd+", "digital plus", "digitalplus"],
	"DD": [" dd ", "dd2", "dd5", "dd7", " ac3", " ac 3", "dolby digital", "dolbydigital", "dolby5"],
	"MP3": ["mp3"],
	"WMA": [" wma"],
	"2.0": ["2 0 ", "2 0ch", "2ch"],
	"5.1": ["5 1 ", "5 1ch", "6ch"],
	"7.1": ["7 1 ", "7 1ch", "8ch"],
	"BLURAY": ["bluray", "blu ray", "bdrip", "bd rip", "brrip", "br rip"],
	"WEB": [" web ", "webrip", "webdl", "web rip", "web dl", "webmux"],
	"HD-RIP": [" hdrip", " hd rip"],
	"DVDRIP": ["dvdrip", "dvd rip"],
	"HDTV": ["hdtv"],
	"PDTV": ["pdtv"],
	"CAM": [
		" cam ", "camrip", "cam rip",
		"hdcam", "hd cam",
		" ts ", " ts1", " ts7",
		"hd ts", "hdts",
		"telesync",
		" tc ", " tc1", " tc7",
		"hd tc", "hdtc",
		"telecine",
		"xbet",
		"hcts", "hc ts",
		"hctc", "hc tc",
		"hqcam", "hq cam",
	],
	"SCR": ["scr ", "screener"],
	"HC": [
		"korsub", " kor ",
		" hc ", "hcsub", "hcts", "hctc", "hchdrip",
		"hardsub", "hard sub",
		"sub hard",
		"hardcode", "hard code",
		"vostfr", "vo stfr",
	],
	"3D": [" 3d"],
}


def strip_non_ascii_and_unprintable(text):
	"""
	Stirps non ascii and unprintable characters from string
	:param text: text to clean
	:return: cleaned text
	"""
	return _ASCII_NON_PRINTABLE.sub("", text)

def deaccent_string(text):
	"""Deaccent the provided text leaving other unicode characters intact
	Example: Mîxéd ДљфӭЖ Tëst -> Mixed ДљфэЖ Test
	:param: text: Text to deaccent
	:type text: str|unicode
	:return: Deaccented string
	:rtype:str|unicode
	"""
	nfkd_form = unicodedata.normalize('NFKD', text)  # pylint: disable=c-extension-no-member
	deaccented_text = str("").join(
		[c for c in nfkd_form if not unicodedata.combining(c)]  # pylint: disable=c-extension-no-member
	)
	return deaccented_text

def clean_title(title, broken=None):
	"""
	Returns a cleaned version of the provided title
	:param title: title to be cleaned
	:param broken: set to 1 to remove apostophes, 2 to replace with spaces
	:return: cleaned title
	"""
	title = deaccent_string(title)
	title = strip_non_ascii_and_unprintable(title)
	title = title.lower()

	apostrophe_replacement = "s"
	if broken == 1:
		apostrophe_replacement = ""
	elif broken == 2:
		apostrophe_replacement = " s"

	title = _APOSTROPHE_SUBS.sub(apostrophe_replacement, title)

	title = _SINGLE_QUOTE.sub("", title)
	title = _SEPARATORS.sub(" ", title)
	title = _WHITESPACE.sub(" ", title)
	title = _AMPERSAND.sub("and", title)

	return title.strip()

from difflib import SequenceMatcher

def get_accepted_resolution_set():
	"""
	Fetches set of accepted resolutions per settings
	:return: set of resolutions
	:rtype set
	"""
	resolutions = ["4K", "1080p", "720p", "SD"]
	max_res = get_setting("general.maxResolution", 'int')
	min_res = get_setting("general.minResolution", 'int')

	return set(resolutions[max_res:min_res+1])



def full_meta_episode_regex(args):
	"""
	Takes an episode items full meta and returns a regex object to use in title matching
	:param args: Full meta of episode item
	:return: compiled regex object
	"""
	episode_info = args["info"]
	show_title = clean_title(episode_info["tvshowtitle"])
	country = episode_info.get("country", "")
	if isinstance(country, (list, set)):
		country = '|'.join(country)
	country = country.lower()
	year = episode_info.get("year", "")
	episode_title = clean_title(episode_info.get("title", ""))
	season = str(episode_info.get("season", ""))
	episode = str(episode_info.get("episode", ""))

	if episode_title == show_title or len(re.findall(r"^\d+$", episode_title)) > 0:
		episode_title = None

	reg_string = (
		r"(?#SHOW TITLE)(?:{show_title})"
		r"? ?"
		r"(?#COUNTRY)(?:{country})"
		r"? ?"
		r"(?#YEAR)(?:{year})"
		r"? ?"
		r"(?:(?:[s[]?)0?"
		r"(?#SEASON){season}"
		r"[x .e]|(?:season 0?"
		r"(?#SEASON){season} "
		r"(?:episode )|(?: ep ?)))(?:\d?\d?e)?0?"
		r"(?#EPISODE){episode}"
		r"(?:e\d\d)?\]? "
	)

	reg_string = reg_string.format(show_title=show_title, country=country, year=year, season=season, episode=episode)

	if episode_title:
		reg_string += "|{eptitle}".format(eptitle=episode_title)

	reg_string = reg_string.replace("*", ".")

	return re.compile(reg_string)


def get_best_episode_match(dict_key, dictionary_list, item_information):
	"""
	Attempts to identify the best matching file/s for a given item and list of source files
	:param dict_key: internal key of dictionary in dictionary list to run checks against
	:param dictionary_list: list of dictionaries containing source title
	:param item_information: full meta of episode object
	:return: dictionaries that best matched requested episode
	"""
	regex = full_meta_episode_regex(item_information)
	files = []

	for i in dictionary_list:
		i.update(
			{
				"regex_matches": regex.findall(
					clean_title(i[dict_key].split("/")[-1].replace("&", " ").lower())
				)
			}
		)
		files.append(i)
	files = [i for i in files if len(i["regex_matches"]) > 0]

	if len(files) == 0:
		return None

	files = sorted(files, key=lambda x: len(" ".join(x["regex_matches"])), reverse=True)

	return files[0]


def copy2clip(txt):
	"""
	Takes a text string and attempts to copy it to the clipboard of the device
	:param txt: Text to send to clipboard
	:type txt: str
	:return: None
	:rtype: None
	"""
	import subprocess

	platform = sys.platform
	if platform == "win32":
		try:
			cmd = "echo " + txt.strip() + "|clip"
			return subprocess.check_call(cmd, shell=True)
		except Exception as e:
			log("Failure to copy to clipboard, \n{}".format(e), "error")
	elif platform.startswith("linux") or platform == "darwin":
		try:
			from subprocess import Popen, PIPE

			cmd = "pbcopy" if platform == "darwin" else ["xsel", "-pi"]
			kwargs = {"stdin": PIPE, "text": True} if PYTHON3 else {"stdin": PIPE}
			p = Popen(cmd, **kwargs)
			p.communicate(input=str(txt))
		except Exception as e:
			print("Failure to copy to clipboard, \n{}".format(e), "error")

def download_file(url, save_as):
	from urllib.request import urlopen
	# Download from URL
	with urlopen(url) as file:
		content = file.read()
	# Save to file
	with open(save_as, 'wb') as download:
		download.write(content)

def extract_zip(zip_file, dest_dir):
	import zipfile
	import shutil
	archive = zipfile.ZipFile(zip_file)
	archive_folder = None
	for file in archive.namelist():
		if file[-1] == '/':
			if archive_folder == None:
				archive_folder = file
		archive.extract(file, dest_dir)
	source = os.path.join(dest_dir, archive_folder)
	destination = dest_dir
	files = os.listdir(source)
	for file in files:
		file_name = os.path.join(source, file)
		shutil.move(file_name, destination)
	delete_file(source)

def delete_file(source):
	try: os.rmdir(source)
	except NotADirectoryError: os.remove(source)

def setup_userdata():
	import shutil
	if not os.path.exists(ADDON_USERDATA_PATH):
		os.mkdir(ADDON_USERDATA_PATH)
	if not os.path.exists(SETTING_XML):
		shutil.copy('blank_settings_xml', SETTING_XML)

class PreemptiveCancellation(Exception):
	pass

def _monkey_check(method):

	def do_method(*args, **kwargs):
		"""
		Wrapper method
		:param args: args
		:param kwargs: kwargs
		:return: func results
		"""
		if (any([True for i in inspect.stack() if "providerModules" in i[1]]) or
			any([True for i in inspect.stack() if "providers" in i[1]])) and PRE_TERM_BLOCK:
			raise PreemptiveCancellation('Pre-emptive termination has stopped this request')

		try:
			#print(*args)
			return method(*args, **kwargs)
		except Exception as exc:
			if 'ConnectionResetError' in str(exc):
				if os.getenv('A4KSCRAPERS_TEST_TOTAL') != '1':
					print(args[1], exc)
				#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				raise PreemptiveCancellation('Pre-emptive termination has stopped this request')
			else:
				print(exc)

	return do_method

# Monkey patch the common requests calls

requests.get = _monkey_check(requests.get)
requests.post = _monkey_check(requests.post)
requests.head = _monkey_check(requests.head)
requests.delete = _monkey_check(requests.delete)
requests.put = _monkey_check(requests.put)

requests.Session.get = _monkey_check(requests.Session.get)
requests.Session.post = _monkey_check(requests.Session.post)
requests.Session.head = _monkey_check(requests.Session.head)
requests.Session.delete = _monkey_check(requests.Session.delete)
requests.Session.put = _monkey_check(requests.Session.put)


def progressbar(it, prefix="", size=60, out=sys.stdout): # Python3.3+
	count = len(it)
	def show(j):
		x = int(size*j/count)
		print("{}[{}{}] {}/{}".format(prefix, "#"*x, "."*(size-x), j, count), 
				end='\r', file=out, flush=True)
	show(0)
	for i, item in enumerate(it):
		yield item
		show(i+1)
	print("\n", flush=True, file=out)


def set_setting(setting_name, setting_value):
	#setting_line = '    <setting id="%s">%s</setting>' % (setting_name, setting_value)
	new_setting_file = ''
	update = False
	with open(SETTING_XML) as f:
		lines = f.readlines()
		for line in lines:
			if setting_name in str(line):
				line_split_1 = line.split('"')[0] + '"'
				line_split_2 = setting_name
				line_split_3 = '"' + line.split('"',2)[2].split('>')[0] + '>'
				line_split_4 = setting_value
				line_split_5 = '<' + line.split('"',2)[2].split('<')[1]
				setting_line = str(line_split_1) + str(line_split_2) + str(line_split_3) + str(line_split_4) + str(line_split_5)
				new_setting_file = new_setting_file + setting_line
				if setting_line != line:
					update = True
			else:
				new_setting_file = new_setting_file + line
	if update == True:
		with open(SETTING_XML, 'w') as file:
			# Write new content to the file
			file.write(new_setting_file)

def get_setting(setting_name, var_type = 'string'):
	return_var = None
	setting_name = setting_name + '"'
	with open(SETTING_XML) as f:
		lines = f.readlines()
		for line in lines:
			if setting_name in str(line):
				return_var = line.split('>')[1].split('</')[0]
	if var_type == 'string':
		return_var = str(return_var)
	elif var_type == 'bool':
		if return_var.lower() == 'true':
			return_var = True
		if return_var.lower() == 'false':
			return_var = False
	elif var_type == 'int':
		return_var = int(return_var)
	elif var_type == 'float':
		return_var = float(return_var)
	return return_var



def get_quality(release_title):
	"""
	Identifies resolution based on release title information
	:param release_title: sources release title
	:return: stringed resolution
	"""
	release_title = release_title.lower()

	if any(q in release_title for q in ["720", "72o"]):
		return "720p"
	if any(q in release_title for q in ["1080", "1o80", "108o", "1o8o"]):
		return "1080p"
	if any(q in release_title for q in ["2160", "216o"]):
		return "4K"
	try:
		if not release_title[release_title.index("4k") + 2].isalnum():
			return "4K"
	except (ValueError, IndexError):
		pass

	return "SD"


def get_info(release_title):
	"""
	Identifies and retrieves a list of information based on release title of source
	:param release_title: Release title of source
	:return: List of info meta
	"""
	title = clean_title(release_title) + " "
	info = {
		info_prop for info_prop, string_list in INFO_TYPES.items()
		if any(i in title for i in string_list)
	}
	if all(i in info for i in ["SDR", "HDR"]):
		info.remove("HDR")
	elif all(i in title for i in ["2160p", "remux"]) and all(i not in info for i in ["HDR", "SDR"]):
		info.add("HDR")
	elif "DV" in info and "hybrid" in title and all(i not in info for i in ["HDR", "SDR"]):
		info.add("HDR")
	if all(i in info for i in ["HDR", "DV"]) and all(i not in title for i in ["hybrid", " hdr"]):
		info.remove("HDR")
	if all(i in info for i in ["HDR", "DV"]):
		info.add("HYBRID")
	if any(i in info for i in ["HDR", "DV"]) and all(i not in info for i in ["HEVC", "AVC"]):
		info.add("HEVC")
	if all(i in info for i in ["DD", "DD+"]):
		info.remove("DD")
	elif any(i in title for i in ["dtshd", "dts hd"]) and all(i not in info for i in ["DTS-HDMA", "DTS-HDHR"]):
		info.add("DTS-HD")
	elif " dts" in title and all(i not in info for i in ["DTS-HDMA", "DTS-HDHR", "DTS-X", "DTS-HD"]):
		info.add("DTS")
	if all(i in title for i in ["sub", "forced"]):
		info.add("HC")
	return info


def smart_merge_dictionary(dictionary, merge_dict, keep_original=False, extend_array=True):
	"""Method for merging large multi typed dictionaries, it has support for handling arrays.

	:param dictionary:Original dictionary to merge the second on into.
	:type dictionary:dict
	:param merge_dict:Dictionary that is used to merge into the original one.
	:type merge_dict:dict
	:param keep_original:Boolean that indicates if there are duplicated values to keep the original one.
	:type keep_original:bool
	:param extend_array:Boolean that indicates if we need to extend existing arrays with the enw values..
	:type extend_array:bool
	:return:Merged dictionary
	:rtype:dict
	"""
	if not isinstance(dictionary, dict) or not isinstance(merge_dict, dict):
		return dictionary
	for new_key, new_value in merge_dict.items():
		original_value = copy.deepcopy(dictionary.get(new_key))
		if isinstance(new_value, (dict, Mapping)):
			if original_value is None:
				original_value = {}
			new_value = smart_merge_dictionary(original_value, new_value, keep_original, extend_array)
		else:
			if original_value and keep_original:
				continue
			if extend_array and isinstance(original_value, (list, set)) and isinstance(
					new_value, (list, set)
			):
				if isinstance(original_value, set):
					original_value.update(x for x in new_value if x not in original_value)
					try:
						new_value = set(sorted(original_value))
					except TypeError:  # Sorting of complex array doesn't work.
						new_value = original_value
				else:
					original_value.extend(x for x in new_value if x not in original_value)
					try:
						new_value = sorted(original_value)
					except TypeError:  # Sorting of complex array doesn't work.
						new_value = original_value
		if new_value or new_value == 0 or isinstance(new_value, bool):
			# We want to skip empty lists / dicts / sets
			dictionary[new_key] = new_value
	return dictionary

def _build_simple_show_info(info):
	simple_info = {'show_title': info['info'].get('tvshowtitle', ''),
				   'episode_title': info['info'].get('originaltitle', ''),
				   'year': str(info['info'].get('tvshow.year', info['info'].get('year', ''))),
				   'season_number': str(info['info']['season']),
				   'episode_number': str(info['info']['episode']),
				   'show_aliases': info['info'].get('aliases', []),
				   'country': info['info'].get('country_origin', ''),
				   'no_seasons': str(info.get('season_count', '')),
				   'absolute_number': str(info.get('absoluteNumber', '')),
				   'is_airing': info.get('is_airing', False),
				   'no_episodes': str(info.get('episode_count', '')),
				   'isanime': False}

	if '.' in simple_info['show_title']:
		simple_info['show_aliases'].append(clean_title(simple_info['show_title'].replace('.', '')))
	if any(x in i.lower() for i in info['info'].get('genre', ['']) for x in ['anime', 'animation']):
		simple_info['isanime'] = True

	return simple_info

def _build_simple_movie_info(info):
	simple_info = {
		'title': info['info'].get('title', ''),
		'year': str(info['info'].get('year', '')),
		'aliases': info['info'].get('aliases', []),
		'country': info['info'].get('country_origin', ''),
	}

	if '.' in simple_info['title']:
		simple_info['aliases'].append(
			clean_title(simple_info['title'].replace('.', ''))
		)

	return simple_info


PYTHON3 = True if sys.version_info.major == 3 else False

import struct
__64k = 65536
__longlong_format_char = 'q'
__byte_size = struct.calcsize(__longlong_format_char)

def sum_64k_bytes(file, filehash):
	range_value = __64k / __byte_size
	from a4kSubtitles.lib import utils
	if utils.py3:
		range_value = round(range_value)

	for _ in range(range_value):
		try: chunk = file.readBytes(__byte_size)
		except: chunk = file.read(__byte_size)
		(value,) = struct.unpack(__longlong_format_char, chunk)
		filehash += value
		filehash &= 0xFFFFFFFFFFFFFFFF
		return filehash

def set_size_and_hash(meta, filepath):
	#f = xbmcvfs.File(filepath)
	if 'http' in str(filepath):
		meta = set_size_and_hash_url(meta, filepath)
		return meta
	f = open(filepath, 'rb')
	try:
		#filesize = f.size()
		filesize = os.path.getsize(filepath)
		meta['filesize'] = filesize

		if filesize < __64k * 2:
			return

		# ref: https://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
		# filehash = filesize + 64bit sum of the first and last 64k of the file
		filehash = lambda: None
		filehash = filesize

		filehash = sum_64k_bytes(f, filehash)
		f.seek(filesize - __64k, os.SEEK_SET)
		filehash = sum_64k_bytes(f, filehash)

		meta['filehash'] = "%016x" % filehash
	finally:
		f.close()
	return meta


def temp_file():
	import tempfile
	file = tempfile.NamedTemporaryFile()
	filename = file.name
	return filename

def set_size_and_hash_url(meta, filepath):
	import urllib.request
	url = filepath
	f = urllib.request.urlopen(url)
	filesize = int(f.headers['Content-Length'])
	opener = urllib.request.build_opener()
	opener.addheaders = [('Range', 'bytes=%s-%s' % (0, __64k-1))]
	first_64kb = temp_file()
	last_64kb = temp_file()
	urllib.request.install_opener(opener)
	urllib.request.urlretrieve(url, first_64kb)
	
	opener = urllib.request.build_opener()
	opener.addheaders = [('Range', 'bytes=%s-%s' % (filesize - __64k, 0))]
	urllib.request.install_opener(opener)
	urllib.request.urlretrieve(url, last_64kb)

	#f = xbmcvfs.File(filepath)
	f = open(first_64kb, 'rb')
	try:
		#filesize = f.size()
		meta['filesize'] = filesize

		if filesize < __64k * 2:
			return

		# ref: https://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
		# filehash = filesize + 64bit sum of the first and last 64k of the file
		filehash = lambda: None
		filehash = filesize

		filehash = sum_64k_bytes(f, filehash)
		#f.seek(filesize - __64k, os.SEEK_SET)
		print(first_64kb, 'size='+str(os.path.getsize(first_64kb)),'set_size_and_hash_url')
		f.close()
		f = open(last_64kb, 'rb')
		filehash = sum_64k_bytes(f, filehash)
		print(last_64kb, 'size='+str(os.path.getsize(last_64kb)),'set_size_and_hash_url')
		meta['filehash'] = "%016x" % filehash
	finally:
		f.close()
		delete_file(first_64kb)
		delete_file(last_64kb)
	return meta

def md5_hash(value):
	"""
	Returns MD5 hash of given value
	:param value: object to hash
	:type value: object
	:return: Hexdigest of hash
	:rtype: str
	"""
	if isinstance(value, (tuple, dict, list, set)):
		value = json.dumps(value, sort_keys=True, default=serialize_sets)
	return hashlib.md5(unicode(value).encode("utf-8")).hexdigest()

def serialize_sets(obj):
	if isinstance(obj, set):
		return sorted([unicode(i) for i in obj])
	return obj

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

def get_pid():
	with open(PID_FILE, 'w', encoding='utf-8') as f:
		f.write(str(os.getpid()))


class StackTraceException(Exception):
	def __init__(self, msg):
		print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		tb = traceback.format_exc()
		print("{} \n{}".format(tb, msg) if not tb.startswith("NoneType: None") else msg, "error")

class UnexpectedResponse(StackTraceException):
	def __init__(self, api_response):
		print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		message = "API returned an unexpected response: \n{}".format(api_response)
		super(UnexpectedResponse, self).__init__(message)

class RanOnceAlready(RuntimeError):
	#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
	pass

Running = None
RunOnce = None
CheckSum = None


class GlobalLock(object):
	def __init__(self, lock_name, run_once=False, check_sum=None):
		self._lock_name = lock_name
		self._run_once = run_once
		self._lock_format = "{}.GlobalLock.{}.{}"
		self._check_sum = check_sum or 'global'

	def _create_key(self, value):
		return self._lock_format.format(ADDON_NAME, self._lock_name, value)

	def _run(self):
		while self._running():
			time.sleep(0.1)
		Running = True
		self._check_ran_once_already()

	def _running(self):
		return Running

	def _check_ran_once_already(self):
		if RunOnce and CheckSum == self._check_sum:
			Running = None
			raise RanOnceAlready("Lock name: {}, Checksum: {}".format(self._lock_name, self._check_sum))

	def __enter__(self):
		self._run()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		if self._run_once:
			RunOnce = True
			CheckSum = self._check_sum
		Running = None



class FixedSortPositionObject(object):
	"""
	A class that always returns equality for a comparison with any other object
	"""
	def __lt__(self, other):
		return False

	def __eq__(self, other):
		return True

	def __neg__(self):
		return self


class SourceSorter:
	"""
	Handles sorting of sources according to users preferences
	"""

	FIXED_SORT_POSITION_OBJECT = FixedSortPositionObject()

	def __init__(self, item_information):
		"""
		Handles sorting of sources according to users preference
		"""
		self.item_information = item_information
		self.mediatype = self.item_information['info']['mediatype']

		# Filter settings
		self.resolution_set = get_accepted_resolution_set()
		self.disable_dv = False
		self.disable_hdr = False
		self.filter_set = self._get_filters()

		# Size filter settings
		self.enable_size_limit = True
		setting_mediatype = 'episode' if self.mediatype == 'episode' else 'movie'
		#self.size_limit = g.get_int_setting("general.sizelimit.{}".format(setting_mediatype)) * 1024

		#if setting_mediatype == 'movie':
		#	self.size_limit = 3.59992
		#else:
		#	self.size_limit = 0.9
		#if setting_mediatype == 'movie':
		#	self.size_minimum = 1.1
		#else:
		#	self.size_minimum = 0.1
		self.size_limit = get_setting("general.sizelimit.{}".format(setting_mediatype), 'float') * 1024
		self.size_minimum = get_setting("general.sizeminimum.{}".format(setting_mediatype), 'float') * 1024

		# Sort Settings
		self.quality_priorities = {
			"4K": 3,
			"1080p": 2,
			"720p": 1,
			"SD": 0
		}

		# Sort Methods
		self._get_sort_methods()

	def _get_filters(self):
		filter_string = get_setting('general.filters')
		current_filters = set() if filter_string is None else set(filter_string.split(","))

		# Set HR filters and remove from set before returning due to HYBRID
		self.disable_dv = "DV" in current_filters
		self.disable_hdr = "HDR" in current_filters

		return current_filters.difference({"HDR", "DV"})

	def filter_sources(self, source_list):
		# Iterate sources, yielding only those that are not filtered
		for source in source_list:
			# Quality filter
			if source['quality'] not in self.resolution_set:
				continue
			# Info Filter
			if self.filter_set & source['info']:
				continue
			# DV filter
			if self.disable_dv and "DV" in source['info'] and "HYBRID" not in source['info']:
				continue
			# HDR Filter
			if self.disable_hdr and "HDR" in source['info'] and "HYBRID" not in source['info']:
				continue
			# Hybrid Filter
			if self.disable_dv and self.disable_hdr and "HYBRID" in source['info']:
				continue
			# File size limits filter
			if self.enable_size_limit and not (
					self.size_limit >= float(source.get("size", 0)) >= self.size_minimum
			):
				continue

			# If not filtered, yield source
			yield source

	def sort_sources(self, sources_list):
		"""Takes in a list of sources and filters and sorts them according to Seren's sort settings

		 :param sources_list: list of sources
		 :type sources_list: list
		 :return: sorted list of sources
		 :rtype: list
		 """

		filtered_sources = list(self.filter_sources(sources_list))
		if (len(filtered_sources) == 0 and len(sources_list) > 0):
			#response = None
			#if not g.get_bool_runtime_setting('tempSilent'):
			#	response = xbmcgui.Dialog().yesno("Your filters appear to be too restrictive for this item, would you like to try again without them?")
			#if response or g.get_bool_runtime_setting('tempSilent'):
			#	return self._sort_sources(sources_list)
			#else:
			#	return []
			return self._sort_sources(sources_list)
		return self._sort_sources(filtered_sources)

	def _get_sort_methods(self):
		"""
		Get Seren settings for sort methods
		"""
		sort_methods = []
		sort_method_settings = {
			0: None,
			1: self._get_quality_sort_key,
			2: self._get_type_sort_key,
			3: self._get_debrid_priority_key,
			4: self._get_size_sort_key,
			5: self._get_low_cam_sort_key,
			6: self._get_hevc_sort_key,
			7: self._get_hdr_sort_key,
			8: self._get_audio_channels_sort_key
		}

		#if self.mediatype == 'episode' and g.get_bool_setting("general.lastreleasenamepriority"):
		#	self.last_release_name = g.get_runtime_setting(
		#		"last_resolved_release_title.{}".format(self.item_information['info']['trakt_show_id'])
		#	)
		#	if self.last_release_name:
		#		sort_methods.append((self._get_last_release_name_sort_key, False))

		for i in range(1, 9):
			sm = get_setting("general.sortmethod.{}".format(i),'int')
			reverse = get_setting("general.sortmethod.{}.reverse".format(i),'bool')

			if sort_method_settings[sm] is None:
				break

			if sort_method_settings[sm] == self._get_type_sort_key:
				self._get_type_sort_order()
			if sort_method_settings[sm] == self._get_debrid_priority_key:
				self._get_debrid_sort_order()
			if sort_method_settings[sm] == self._get_hdr_sort_key:
				self._get_hdr_sort_order()

			sort_methods.append((sort_method_settings[sm], reverse))

		self.sort_methods = sort_methods

	def _get_type_sort_order(self):
		"""
		Get seren settings for type sort priority
		"""
		type_priorities = {}
		type_priority_settings = {
			0: None,
			1: "cloud",
			2: "adaptive",
			3: "torrent",
			4: "hoster"
		}

		for i in range(1, 5):
			tp = type_priority_settings.get(
				get_setting("general.sourcetypesort.{}".format(i), 'int')
			)
			if tp is None:
				break
			type_priorities[tp] = -i
		self.type_priorities = type_priorities

	def _get_hdr_sort_order(self):
		"""
		Get seren settings for type sort priority
		"""
		hdr_priorities = {}
		hdr_priority_settings = {
			0: None,
			1: "DV",
			2: "HDR",
		}

		for i in range(1, 3):
			hdrp = hdr_priority_settings.get(get_setting("general.hdrsort.{}".format(i), 'int'))
			if hdrp is None:
				break
			hdr_priorities[hdrp] = -i
		self.hdr_priorities = hdr_priorities

	def _get_debrid_sort_order(self):
		"""
		Get seren settings for debrid sort priority
		"""
		debrid_priorities = {}
		debrid_priority_settings = {
			0: None,
			1: "premiumize",
			2: "real_debrid",
			3: "all_debrid",
		}

		for i in range(1, 4):
			debridp = debrid_priority_settings.get(
				get_setting("general.debridsort.{}".format(i),'int')
			)
			if debridp is None:
				break
			debrid_priorities[debridp] = -i
		self.debrid_priorities = debrid_priorities

	def _sort_sources(self, sources_list):
		"""
		Sort a source list based on sort_methods defined by settings
		All sort method key methods should return key values for *descending* sort.  If a reversed sort is required,
		reverse is specified as a boolean for the second item of each tuple in sort_methods
		:param sources_list: The list of sources to sort
		:return: The list of sorted sources
		:rtype: list
		"""
		sources_list = sorted(sources_list, key=lambda s: s['release_title'])
		return sorted(sources_list, key=self._get_sort_key_tuple, reverse=True)

	def _get_sort_key_tuple(self, source):
		return tuple(
			-sm(source) if reverse else sm(source)
			for (sm, reverse) in self.sort_methods
			if sm
		)

	def _get_type_sort_key(self, source):
		return self.type_priorities.get(source.get("type"), -99)

	def _get_quality_sort_key(self, source):
		return self.quality_priorities.get(source.get("quality"), -99)

	def _get_debrid_priority_key(self, source):
		return self.debrid_priorities.get(source.get("debrid_provider"), self.FIXED_SORT_POSITION_OBJECT)

	def _get_size_sort_key(self, source):
		size = source.get("size", None)
		if size == "Variable":
			return self.FIXED_SORT_POSITION_OBJECT
		if size is None or not isinstance(size, (int, float)) or size < 0:
			size = 0
		return size

	@staticmethod
	def _get_low_cam_sort_key(source):
		return "CAM" not in source.get("info", {})

	@staticmethod
	def _get_hevc_sort_key(source):
		return "HEVC" in source.get("info", {})

	def _get_hdr_sort_key(self, source):
		hdrp = -99
		dvp = -99

		if "HDR" in source.get("info", {}):
			hdrp = self.hdr_priorities.get("HDR", -99)
		if "DV" in source.get("info", {}):
			dvp = self.hdr_priorities.get("DV", -99)

		return max(hdrp, dvp)

	def _get_last_release_name_sort_key(self, source):
		sm = SequenceMatcher(None, self.last_release_name, source['release_title'], autojunk=False)
		if sm.real_quick_ratio() < 1:
			return 0
		ratio = sm.ratio()
		if ratio < 0.85:
			return 0
		return ratio

	@staticmethod
	def _get_audio_channels_sort_key(source):
		audio_channels = None
		info = source['info']
		if info:
			audio_channels = {"2.0", "5.1", "7.1"} & info
		return float(max(audio_channels)) if audio_channels else 0

