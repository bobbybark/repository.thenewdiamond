# -*- coding: utf-8 -*-

import importlib
try:
	from a4kSubtitles.lib import utils
	import tools
	prefix = 'a4kSubtitles'
except:
	from a4kscrapers_wrapper.a4kSubtitles.lib import utils
	from a4kscrapers_wrapper import tools
	prefix = 'a4kscrapers_wrapper.a4kSubtitles'

__all = utils.get_all_relative_entries(__file__)
__display_names = {
	'addic7ed': 'Addic7ed',
	'bsplayer': 'BSPlayer',
	'opensubtitles': 'OpenSubtitles',
	'podnadpisi': 'Podnadpisi',
	'subscene': 'Subscene',
}

def __set_fn_if_missing(service, fn_name, fn):
	if not getattr(service, fn_name, None):
		setattr(service, fn_name, fn)

services = {}
#tools.log(__all)
#__all = ['opensubtitles', 'subscene', 'addic7ed', 'podnadpisi', 'bsplayer']
for service_name in __all:
	try:
	#if 1==1:
		service = services[service_name] = importlib.import_module('a4kSubtitles.services.%s' % service_name)

		service.context = utils.DictAsObject({})
		service.display_name = __display_names[service_name]

		__set_fn_if_missing(service, 'build_auth_request', lambda _, __: None)

		assert service.build_search_requests
		assert service.parse_search_response
		assert service.build_download_request
	except:
		tools.log('SUBTITLE_SERVICES_INIT_EXCEPTION!!')
		continue