# -*- coding: utf-8 -*-
#from __future__ import absolute_import, division, unicode_literals

import time

#from database.cache import use_cache
import tools
from thread_pool import ThreadPool

try:
	from functools import cached_property  # Supported from py3.8
except ImportError:
	from resources.lib.third_party.cached_property import cached_property

from inspect import currentframe, getframeinfo
#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

RD_AUTH_KEY = "rd.auth"
RD_STATUS_KEY = "rd.premiumstatus"
RD_REFRESH_KEY = "rd.refresh"
RD_EXPIRY_KEY = "rd.expiry"
RD_SECRET_KEY = "rd.secret"
RD_CLIENT_ID_KEY = "rd.client_id"
RD_USERNAME_KEY = "rd.username"
RD_AUTH_CLIENT_ID = "X245A4XAIBGVM"


class RealDebrid:

	def __init__(self):
		self.oauth_url = "https://api.real-debrid.com/oauth/v2/"
		self.device_code_url = "device/code?{}"
		self.device_credentials_url = "device/credentials?{}"
		self.token_url = "token"
		self.device_code = ""
		self.oauth_timeout = 0
		self.oauth_time_step = 0
		self.base_url = "https://api.real-debrid.com/rest/1.0/"
		self.cache_check_results = {}
		self._load_settings()
		self.UNRESTRICT_FILE = None

	@cached_property
	def session(self):
		import requests
		from requests.adapters import HTTPAdapter
		from urllib3 import Retry
		session = requests.Session()
		retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
		session.mount("https://", HTTPAdapter(max_retries=retries, pool_maxsize=100))
		return session

	def _auth_loop(self):
		url = "client_id={}&code={}".format(RD_AUTH_CLIENT_ID, self.device_code)
		url = self.oauth_url + self.device_credentials_url.format(url)
		response = self.session.get(url).json()
		if "error" not in response and response.get("client_secret"):
			try:
				tools.set_setting(RD_CLIENT_ID_KEY, response["client_id"])
				tools.set_setting(RD_SECRET_KEY, response["client_secret"])
				self.client_secret = response["client_secret"]
				self.client_id = response["client_id"]
				return True
			except Exception:
				#xbmcgui.Dialog().ok(g.ADDON_NAME, g.get_language_string(30065))
				print("Authentication with Real-Debrid has failed, please try again")
				raise
		return False

	def auth(self):
		self.client_id = tools.get_setting("rd.client_id")
		if self.client_id == '':
			self.client_id = RD_AUTH_CLIENT_ID
		url = "client_id={}&new_credentials=yes".format(self.client_id)
		url = self.oauth_url + self.device_code_url.format(url)
		response = self.session.get(url).json()
		tools.copy2clip(response["user_code"])
		success = False
		
		try:
			line1=str("Open this link in a browser: {}").format(str("https://real-debrid.com/device"))
			line2=str("Enter the code: {}").format(str(response["user_code"]))
			line3=str("This code has been copied to your clipboard")
			print(line1)
			print(line2)
			print(line3)
			print('RD_AUTH_RUNNING_FOR_90s')
			start_time = time.time()
			self.oauth_timeout = int(response["expires_in"])
			token_ttl = int(response["expires_in"])
			self.oauth_time_step = int(response["interval"])
			self.device_code = response["device_code"]
			#while (
			#	not success
			#	and not token_ttl <= 0
			#	and not time.time() > start_time + 90
			#):
			for i in tools.progressbar(range(100), "AUTH: ", 40):
				time.sleep(1) # any code you need
				if token_ttl % self.oauth_time_step == 0:
					success = self._auth_loop()
				progress_percent = int(float((token_ttl * 100) / self.oauth_timeout))
				#progress_dialog.update(progress_percent)
				#print('progress_percent=', progress_percent)
				token_ttl -= 1
				if not success and not token_ttl <= 0 and not time.time() > start_time + 90:
					continue
				else:
					break
			print('success??')
		finally:
			print('finally_success')

		if success:
			self.token_request()

			user_information = self.get_url("user")
			if user_information["type"] != "premium":
				#xbmcgui.Dialog().ok(g.ADDON_NAME, g.get_language_string(30194))
				print("You appear to have authorized a non-premium account and will not be able to play items using this account")
			else:
				print('RD_AUTH_SUCCESS')

	def token_request(self):
		if not self.client_secret:
			return

		url = self.oauth_url + self.token_url
		response = self.session.post(
			url,
			data={
				"client_id": self.client_id,
				"client_secret": self.client_secret,
				"code": self.device_code,
				"grant_type": "http://oauth.net/grant_type/device/1.0",
			},
		).json()
		self._save_settings(response)
		self._save_user_status()
		#xbmcgui.Dialog().ok(g.ADDON_NAME, "Real Debrid " + g.get_language_string(30020))
		print("Authentication is completed")

	def _save_settings(self, response):
		self.token = response["access_token"]
		self.refresh = response["refresh_token"]
		self.expiry = time.time() + int(response["expires_in"])

		print(RD_AUTH_KEY, self.token)
		print(RD_REFRESH_KEY, self.refresh)
		print(RD_EXPIRY_KEY, self.expiry)
		tools.set_setting(RD_AUTH_KEY, self.token)
		tools.set_setting(RD_REFRESH_KEY, self.refresh)
		tools.set_setting(RD_EXPIRY_KEY, self.expiry)

	def _save_user_status(self):
		username = self.get_url("user").get("username")
		status = self.get_account_status().title()
		tools.set_setting(RD_USERNAME_KEY, username)
		tools.set_setting(RD_STATUS_KEY, status)

	def _load_settings(self):
		#self.client_id = g.get_setting("rd.client_id", RD_AUTH_CLIENT_ID)
		self.client_id = tools.get_setting("rd.client_id")
		self.token = tools.get_setting(RD_AUTH_KEY)
		self.refresh = tools.get_setting(RD_REFRESH_KEY)
		try: self.expiry = tools.get_setting(RD_EXPIRY_KEY,'float')
		except: self.expiry = time.time() - 1
		self.client_secret = tools.get_setting(RD_SECRET_KEY)

	@staticmethod
	def _handle_error(response):
		print("Real Debrid API return a {} response".format(response.status_code))
		print(response.text)
		print(response.request.url)

	def _is_response_ok(self, response):
		if 200 <= response.status_code < 400:
			return True
		if response.status_code > 400:
			self._handle_error(response)
			return False

	def try_refresh_token(self, force=False):
		if not self.refresh:
			return
		if not force and self.expiry > float(time.time()):
			return

		try:
			with tools.GlobalLock(self.__class__.__name__, True, self.token):
				url = self.oauth_url + "token"
				response = self.session.post(
					url,
					data={
						"grant_type": "http://oauth.net/grant_type/device/1.0",
						"code": self.refresh,
						"client_secret": self.client_secret,
						"client_id": self.client_id,
					},
				)
				if not self._is_response_ok(response):
					response = response.json()
					print(
						 "Failed to refresh RD token, please manually re-auth"
					)
					print("RD Refresh error: {}".format(response["error"]))
					print(
						"Invalid response from Real Debrid - {}".format(response), "error"
					)
					return False
				response = response.json()
				self._save_settings(response)
				print("Real Debrid Token Refreshed")
				return True
		except tools.RanOnceAlready:
			self._load_settings()
			return

	def _get_headers(self):
		headers = {
			"Content-Type": "application/json",
		}
		if self.token:
			headers["Authorization"] = "Bearer {}".format(self.token)
		return headers

	def post_url(self, url, post_data, fail_check=False):
		original_url = url
		url = self.base_url + url
		if not self.token:
			return None

		response = self.session.post(url, data=post_data, headers=self._get_headers(), timeout=5)
		if not self._is_response_ok(response) and not fail_check:
			self.try_refresh_token(True)
			response = self.post_url(original_url, post_data, fail_check=True)
		try:
			return response.json()
		except (ValueError, AttributeError):
			return response

	def get_url(self, url, fail_check=False):
		original_url = url
		url = self.base_url + url
		if not self.token:
			print("No Real Debrid Token Found")
			return None

		response = self.session.get(url, headers=self._get_headers(), timeout=5)

		if not self._is_response_ok(response) and not fail_check:
			self.try_refresh_token(True)
			response = self.get_url(original_url, fail_check=True)
		try:
			return response.json()
		except (ValueError, AttributeError):
			return response

	def delete_url(self, url, fail_check=False):
		original_url = url
		url = self.base_url + url
		if not self.token:
			print("No Real Debrid Token Found")
			return None

		response = self.session.delete(url, headers=self._get_headers(), timeout=5)

		if not self._is_response_ok(response) and not fail_check:
			self.try_refresh_token(True)
			response = self.delete_url(original_url, fail_check=True)
		try:
			return response.json()
		except (ValueError, AttributeError):
			return response

	def check_hash(self, hash_list):
		if isinstance(hash_list, list):
			hash_list = [hash_list[x : x + 100] for x in range(0, len(hash_list), 100)]
			thread = ThreadPool()
			for section in hash_list:
				thread.put(self._check_hash_thread, sorted(section))
			thread.wait_completion()
			return self.cache_check_results
		else:
			hash_string = "/" + hash_list
			return self.get_url("torrents/instantAvailability" + hash_string)

	def _check_hash_thread(self, hashes):
		hash_string = "/" + "/".join(hashes)
		response = self.get_url("torrents/instantAvailability" + hash_string)
		self.cache_check_results.update(response)

	def add_magnet(self, magnet):
		post_data = {"magnet": magnet}
		url = "torrents/addMagnet"
		response = self.post_url(url, post_data)
		return response

	def list_torrents(self):
		url = "torrents"
		response = self.get_url(url)
		return response

	def torrent_info(self, id):
		url = "torrents/info/{}".format(id)
		return self.get_url(url)

	def torrent_select(self, torrent_id, file_id):
		url = "torrents/selectFiles/{}".format(torrent_id)
		post_data = {"files": file_id}
		return self.post_url(url, post_data)

	def resolve_hoster(self, link):
		url = "unrestrict/link"
		post_data = {"link": link}
		response = self.post_url(url, post_data)
		try:
			self.UNRESTRICT_FILE = response["download"]
			return response["download"]
		except KeyError:
			raise tools.UnexpectedResponse(response)

	def delete_torrent(self, id):
		url = "torrents/delete/{}".format(id)
		self.delete_url(url)

	def common_video_extensions(self):
		getSupportedMedia = '.m4v|.3g2|.3gp|.nsv|.tp|.ts|.ty|.strm|.pls|.rm|.rmvb|.mpd|.m3u|.m3u8|.ifo|.mov|.qt|.divx|.xvid|.bivx|.vob|.nrg|.img|.iso|.udf|.pva|.wmv|.asf|.asx|.ogm|.m2v|.avi|.bin|.dat|.mpg|.mpeg|.mp4|.mkv|.mk3d|.avc|.vp3|.svq3|.nuv|.viv|.dv|.fli|.flv|.001|.wpl|.xspf|.zip|.vdr|.dvr-ms|.xsp|.mts|.m2t|.m2ts|.evo|.ogv|.sdp|.avs|.rec|.url|.pxml|.vc1|.h264|.rcv|.rss|.mpls|.mpl|.webm|.bdmv|.bdm|.wtv|.trp|.f4v|.ssif|.pvr|.disc|'
		return [
			i
			for i in getSupportedMedia.split("|")
			if i not in ["", ".zip", ".rar"]
		]

	def is_file_ext_valid(self, file_name):
		"""
		Checks if the video file type is supported by Kodi
		:param file_name: name/path of file
		:return: True if video file is expected to be supported else False
		"""
		if "." + file_name.split(".")[-1] not in self.common_video_extensions():
			return False
		return True

	def is_streamable_storage_type(self, storage_variant):
		"""
		Confirms that all files within the storage variant are video files
		This ensure the pack from RD is instantly streamable and does not require a download
		:param storage_variant:
		:return: BOOL
		"""
		return (
			False
			if len(
				[
					i
					for i in storage_variant.values()
					if not self.is_file_ext_valid(i["filename"])
				]
			)
			> 0
			else True
		)


	@staticmethod
	def is_service_enabled():
		return (
			tools.get_setting("realdebrid.enabled",'bool')
			and tools.get_setting(RD_AUTH_KEY) is not None
		)

	def get_account_status(self):
		status = None
		status_response = self.get_url("user")
		if isinstance(status_response, dict):
			status = status_response.get("type")
		return status if status else "unknown"
