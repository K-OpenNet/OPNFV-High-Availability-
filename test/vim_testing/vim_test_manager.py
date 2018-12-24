# -*- coding: utf-8 -*-
# vim_test_manager.py

from test.vim_testing.plugins import plugin_rally

import logging

LOG = logging.getLogger(__name__)


def start(tool, requestdict):
    """Starts vim testing tool from plugins.

    Args:
        tool: A string that decides specific tools among testing plugins.
        requestdict: A dictionary that is used to execute the Rally testing.

    Returns:
        None.
    """
    LOG.debug("vim_test_manager.py start()")

    vim_test_result = None

    if str(tool) == 'rally':
        vim_test_result = plugin_rally.start(requestdict)

    return vim_test_result
