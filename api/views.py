from django.shortcuts import render, HttpResponse
import json
# Create your views here.
from repository.models import *
from api.plugins import PluginsManager


def asset(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        hostname = data['basic']['data']['hostname']
        server_obj = Server.objects.filter(hostname=hostname).first()
        if not server_obj:
            return HttpResponse('主机不存在')
        else:
            # 数据清洗插件
            response = PluginsManager().execute_parse(server_obj, hostname, data)
            print(response)
            return HttpResponse('ok')
    elif request.method == 'GET':
        # API验证
        client_token = request.META.get('HTTP_TOKEN')
         
        return HttpResponse('ok')
