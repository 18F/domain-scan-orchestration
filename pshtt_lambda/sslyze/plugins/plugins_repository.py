# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from sslyze.plugins.certificate_info_plugin import CertificateInfoPlugin
from sslyze.plugins.compression_plugin import CompressionPlugin
from sslyze.plugins.fallback_scsv_plugin import FallbackScsvPlugin
from sslyze.plugins.heartbleed_plugin import HeartbleedPlugin
from sslyze.plugins.http_headers_plugin import HttpHeadersPlugin
from sslyze.plugins.openssl_ccs_injection_plugin import OpenSslCcsInjectionPlugin
from sslyze.plugins.openssl_cipher_suites_plugin import OpenSslCipherSuitesPlugin
from sslyze.plugins.plugin_base import Plugin
from sslyze.plugins.plugin_base import PluginScanCommand

from sslyze.plugins.session_renegotiation_plugin import SessionRenegotiationPlugin
from sslyze.plugins.session_resumption_plugin import SessionResumptionPlugin
from typing import List
from typing import Optional
from typing import Type


class PluginsRepository(object):
    """An object encapsulating the list of available SSLyze plugins.
    """

    _PLUGIN_CLASSES = [OpenSslCipherSuitesPlugin, CertificateInfoPlugin, CompressionPlugin, FallbackScsvPlugin,
                       HeartbleedPlugin, HttpHeadersPlugin, OpenSslCcsInjectionPlugin, SessionRenegotiationPlugin,
                       SessionResumptionPlugin]

    def __init__(self, plugin_classes=_PLUGIN_CLASSES):
        # type: (Optional[List[Type[Plugin]]]) -> None
        scan_command_classes_to_plugin_classes = {}

        # Create a dict of scan_commands -> plugin_classes
        for plugin_class in plugin_classes:
            for scan_command_class in plugin_class.get_available_commands():

                # Sanity check: no duplicate scan commands
                if scan_command_class in scan_command_classes_to_plugin_classes.keys():
                    raise KeyError('Found duplicate scan command: {}'.format(scan_command_class))

                scan_command_classes_to_plugin_classes[scan_command_class] = plugin_class

        self._scan_command_classes_to_plugin_classes = scan_command_classes_to_plugin_classes

    def get_plugin_class_for_command(self, scan_command):
        # type: (PluginScanCommand) -> Type[Plugin]
        """Get the class of the plugin implementing the supplied scan command.
        """
        return self._scan_command_classes_to_plugin_classes[scan_command.__class__]

    def get_available_commands(self):
        # type: () -> List[Type[PluginScanCommand]]
        """Get the list of all available scan comands across all plugins.
        """
        return self._scan_command_classes_to_plugin_classes.keys()

    def get_available_plugins(self):
        # type: () -> List[Type[Plugin]]
        """Get the list of all available plugin.
        """
        return list(set(self._scan_command_classes_to_plugin_classes.values()))
