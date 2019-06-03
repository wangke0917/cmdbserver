from repository.models import *


class DiskParse(object):

    def __init__(self, server_obj, hostname):
        self.server_obj = server_obj
        self.hostname = hostname
        self.old_disk_slot = []
        self.old_disk_data = None
        self.new_disk_data = None
        self.new_disk_slot = []

    def parse(self, data):
        if data['disk']['status'] == 100:
            # disk解析
            self.old_disk_data = Disk.objects.filter(server=self.server_obj).all()
            for old_disk in self.old_disk_data:
                self.old_disk_slot.append(old_disk.slot)

            self.new_disk_data = data['disk']['data']
            self.new_disk_slot = list(self.new_disk_data.keys())

            # 增加
            add_slot = set(self.new_disk_slot).difference(set(self.old_disk_slot))
            if add_slot:
                self.__add(add_slot)
            # 删除
            del_slot = set(self.old_disk_slot).difference(set(self.new_disk_slot))
            if del_slot:
                self.__del(del_slot)
            # 修改
            update_solt = set(self.old_disk_slot).intersection(set(self.new_disk_slot))
            if update_solt:
                self.__update(update_solt)
            return True
        else:
            ErrorLog.objects.create(asset=self.server_obj.asset, content=data['disk']['data'])
            return False

    def __add(self, add_slot):

        change_log = []
        for slot in add_slot:
            Disk.objects.create(server=self.server_obj, **self.new_disk_data[slot])
            tmp = "{hostname}主机硬盘,增加了{slot}插槽,型号为{pd_type},容量为{capacity},类型是{model}". \
                format(hostname=self.hostname, **self.new_disk_data[slot])
            change_log.append(tmp)
        content = ';\n'.join(change_log)
        AssetRecord.objects.create(asset=self.server_obj.asset, content=content)

    def __del(self, del_slot):
        change_log = []
        for slot in del_slot:
            Disk.objects.filter(server=self.server_obj, slot=slot).delete()
            tmp = "{hostname}主机硬盘,删除了{slot}插槽". \
                format(hostname=self.hostname, slot=slot)
            change_log.append(tmp)
        content = ';\n'.join(change_log)
        AssetRecord.objects.create(asset=self.server_obj.asset, content=content)

    def __update(self, update_solt):
        change_log = []
        key_code = {
            'slot': '插槽',
            'pd_type': '磁盘型号',
            'capacity': '磁盘容量',
            'model': '磁盘类型'
        }
        for slot in update_solt:
            new_slot_dict = self.new_disk_data[slot]
            old_slot_obj = Disk.objects.filter(server=self.server_obj, slot=slot).first()
            for k, new_attr in new_slot_dict.items():
                old_attr = str(getattr(old_slot_obj, k))
                if str(old_attr) != str(new_attr):
                    setattr(old_slot_obj, k, new_attr)
                    tmp = "%s主机硬盘,%s插槽进行了修改,%s由%s修改为%s" \
                          % (self.hostname, slot, key_code[k], old_attr, new_attr)
                    change_log.append(tmp)
            old_slot_obj.save()
        if change_log:
            content = ';\n'.join(change_log)
            AssetRecord.objects.create(asset=self.server_obj.asset, content=content)
