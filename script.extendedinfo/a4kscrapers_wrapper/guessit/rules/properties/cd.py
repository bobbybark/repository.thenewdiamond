#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cd and cd_count properties
"""
try: from rebulk import Rebulk  #PATCH
except: from a4kscrapers_wrapper.rebulk import Rebulk  #PATCH

try: from rebulk.remodule import re  #PATCH
except: from a4kscrapers_wrapper.rebulk.remodule import re  #PATCH


from ..common import dash
from ..common.pattern import is_disabled
from ...config import load_config_patterns


def cd(config):  # pylint:disable=unused-argument,invalid-name
    """
    Builder for rebulk object.

    :param config: rule configuration
    :type config: dict
    :return: Created Rebulk object
    :rtype: Rebulk
    """
    rebulk = Rebulk(disabled=lambda context: is_disabled(context, 'cd'))
    rebulk = rebulk.regex_defaults(flags=re.IGNORECASE, abbreviations=[dash])

    load_config_patterns(rebulk, config)

    return rebulk

