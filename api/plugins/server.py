from repository.models import *


class ServerParse(object):
    def __init__(self, server_obj, hostname):
        self.server_obj = server_obj
        self.hostname = hostname
        self.new_basic_data = None
        self.old_server_data = None

    def parse(self, data):

        if data['basic']['status'] == 100:

            self.new_basic_data = data['basic']['data']
            new_cpu_data = data['cpu']['data']
            new_board_data = data['board']['data']
            self.new_basic_data.update(new_cpu_data)
            self.new_basic_data.update(new_board_data)

            self.old_server_data = Server.objects.filter(hostname=self.hostname).first()
            # 更新
            self.__update()
            return True

        else:
            ErrorLog.objects.create(asset=self.server_obj.asset, content=data['disk']['data'])
            return False

    def __update(self):
        change_log = []
        key_code = {
            'hostname': '主机名',
            'os_platform': '系统',
            'os_version': '系统版本',
            'cpu_count': 'cpu个数',
            'cpu_model': 'cpu型号',
            'cpu_physical_count': 'cpu物理个数',
            'manufacturer': '制造商',
            'sn': 'SN号',
            'model': '型号'
        }
        for k, new_attr in self.new_basic_data.items():
            old_attr = getattr(self.old_server_data, k)
            if str(old_attr) != str(new_attr):
                setattr(self.old_server_data, k, new_attr)
                tmp = "%s主机, %s由%s修改为%s" % (self.hostname, key_code[k], old_attr, new_attr)
                change_log.append(tmp)
            self.old_server_data.save()
        if change_log:
            content = ';\n'.join(change_log)
            AssetRecord.objects.create(asset=self.server_obj.asset, content=content)
