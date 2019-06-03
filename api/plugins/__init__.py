from django.conf import settings
import importlib


class PluginsManager(object):
    def __init__(self):
        self.plugins = settings.PLUGINS_DICT

    def execute_parse(self, server_obj, hostname, data):
        response = {}
        for k, v in self.plugins.items():
            v = v.rsplit('.', 1)
            module = importlib.import_module(v[0])
            cls = getattr(module, v[1])
            res = cls(server_obj, hostname).parse(data)
            response[k] = res
        return response
