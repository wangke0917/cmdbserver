from repository.models import *


class NicParse(object):

    def __init__(self, server_obj, hostname):
        self.server_obj = server_obj
        self.hostname = hostname
        self.old_nic_name = []
        self.old_nic_data = None
        self.new_nic_data = None
        self.new_nic_name = []

    def parse(self, data):
        if data['nic']['status'] == 100:
            # nic解析
            self.old_nic_data = Nic.objects.filter(server=self.server_obj).all()
            for old_nic in self.old_nic_data:
                self.old_nic_name.append(old_nic.name)

            self.new_nic_data = data['nic']['data']
            self.new_nic_name = list(self.new_nic_data.keys())

            # 增加
            add_name = set(self.new_nic_name).difference(set(self.old_nic_name))
            if add_name:
                self.__add(add_name)
            # 删除
            del_name = set(self.old_nic_name).difference(set(self.new_nic_name))
            if del_name:
                self.__del(del_name)
            # 修改
            update_name = set(self.old_nic_name).intersection(set(self.new_nic_name))
            if update_name:
                self.__update(update_name)
            return True
        else:
            ErrorLog.objects.create(asset=self.server_obj.asset, content=data['nic']['data'])
            return False

    def __add(self, add_name):

        change_log = []
        for name in add_name:
            Nic.objects.create(server=self.server_obj, **self.new_nic_data[name])
            tmp = "{hostname}主机网卡,增加了{name}网卡,mac地址为为{hwaddr},IP地址是{ipaddrs},子网掩码是{netmask}". \
                format(hostname=self.hostname, **self.new_nic_data[name])
            change_log.append(tmp)
        content = ';\n'.join(change_log)
        AssetRecord.objects.create(asset=self.server_obj.asset, content=content)

    def __del(self, del_name):
        change_log = []
        for name in del_name:
            Nic.objects.filter(server=self.server_obj, name=name).delete()
            tmp = "{hostname}主机网卡,删除了{name}网卡". \
                format(hostname=self.hostname, name=name)
            change_log.append(tmp)
        content = ';\n'.join(change_log)
        AssetRecord.objects.create(asset=self.server_obj.asset, content=content)

    def __update(self, update_name):
        change_log = []
        key_code = {
            'name': '网卡名',
            'netmask': '子网掩码',
            'ipaddrs': 'IP地址',
            'hwaddr': 'mac地址',
            'up': '上线状态',
        }
        for name in update_name:
            new_name_dict = self.new_nic_data[name]
            old_name_obj = Nic.objects.filter(server=self.server_obj, name=name).first()
            for k, new_attr in new_name_dict.items():
                old_attr = str(getattr(old_name_obj, k))
                if str(old_attr) != str(new_attr):
                    setattr(old_name_obj, k, new_attr)
                    tmp = "%s主机网卡,%s网卡进行了修改,%s由%s修改为%s" \
                          % (self.hostname, name, key_code[k], old_attr, new_attr)
                    change_log.append(tmp)
            old_name_obj.save()
        if change_log:
            content = ';\n'.join(change_log)
            AssetRecord.objects.create(asset=self.server_obj.asset, content=content)
