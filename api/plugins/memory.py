from repository.models import *


class MemoryParse(object):

    def __init__(self, server_obj, hostname):
        self.server_obj = server_obj
        self.hostname = hostname
        self.old_memory_slot = []
        self.old_memory_data = None
        self.new_memory_data = None
        self.new_memory_slot = []

    def parse(self, data):
        if data['memory']['status'] == 100:
            # memory解析
            self.old_memory_data = Memory.objects.filter(server=self.server_obj).all()
            for old_memory in self.old_memory_data:
                self.old_memory_slot.append(old_memory.slot)

            self.new_memory_data = data['memory']['data']
            self.new_memory_slot = list(self.new_memory_data.keys())

            # 增加
            add_slot = set(self.new_memory_slot).difference(set(self.old_memory_slot))
            if add_slot:
                self.__add(add_slot)
            # 删除
            del_slot = set(self.old_memory_slot).difference(set(self.new_memory_slot))
            if del_slot:
                self.__del(del_slot)
            # 修改
            update_solt = set(self.old_memory_slot).intersection(set(self.new_memory_slot))
            if update_solt:
                self.__update(update_solt)
            return True
        else:
            ErrorLog.objects.create(asset=self.server_obj.asset, content=data['memory']['data'])
            return False

    def __add(self, add_slot):

        change_log = []
        for slot in add_slot:
            Memory.objects.create(server=self.server_obj, **self.new_memory_data[slot])
            tmp = "{hostname}主机内存,增加了{slot}插槽,型号为{model},容量为{capacity}," \
                  "内存SN号是{sn},速度为{speed},制造商是{manufacturer}". \
                format(hostname=self.hostname, **self.new_memory_data[slot])
            change_log.append(tmp)
        content = ';\n'.join(change_log)
        AssetRecord.objects.create(asset=self.server_obj.asset, content=content)

    def __del(self, del_slot):
        change_log = []
        for slot in del_slot:
            Memory.objects.filter(server=self.server_obj, slot=slot).delete()
            tmp = "{hostname}主机内存,删除了{slot}插槽". \
                format(hostname=self.hostname, slot=slot)
            change_log.append(tmp)
        content = ';\n'.join(change_log)
        AssetRecord.objects.create(asset=self.server_obj.asset, content=content)

    def __update(self, update_solt):
        change_log = []
        key_code = {
            'slot': '插槽',
            'speed': '速度',
            'capacity': '容量',
            'model': '型号',
            'manufacturer': '制造商',
            'sn': 'SN号'
        }
        for slot in update_solt:
            new_slot_dict = self.new_memory_data[slot]
            old_slot_obj = Memory.objects.filter(server=self.server_obj, slot=slot).first()
            for k, new_attr in new_slot_dict.items():
                old_attr = str(getattr(old_slot_obj, k))
                if str(old_attr) != str(new_attr):
                    setattr(old_slot_obj, k, new_attr)
                    tmp = "%s主机内存,%s插槽进行了修改,%s由%s修改为%s" \
                          % (self.hostname, slot, key_code[k], old_attr, new_attr)
                    change_log.append(tmp)
            old_slot_obj.save()
        if change_log:
            content = ';\n'.join(change_log)
            AssetRecord.objects.create(asset=self.server_obj.asset, content=content)
