import random

from requests_toolbelt.multipart.encoder import MultipartEncoder

import json
import time
import unittest

import requests

from database.dataManager.test_pre import test_pre, homepage, headers


class test_nuccore_docking(unittest.TestCase):
    pre = test_pre()
    pre.login()

    # 调用接口/ardb/upload_id，外部对接导入核酸数据
    def nuccore_docking(self, data_id: list):
        time_stamp = int(round(1000 * time.time()))

        whether_exist = {}

        for d in data_id:
            resp_whether_exist = requests.get(url=homepage + "/api/nucleicAcid/page?", headers=headers,
                                              params={"pageNum": 1, "pageSize": 10, "sort": "Default_order",
                                                      "sourceDatabase": "nuccore", "_t": time_stamp,
                                                      "queryStrList": json.dumps([
                                                          {"field_name": "Accession", "term": "", "value": d}])}).json()
            self.assertEqual(resp_whether_exist["code"], 200)

            if resp_whether_exist["data"]["total"] == 0:
                whether_exist[d] = False
            else:
                whether_exist[d] = True

        data_id_str = ",".join(data_id)
        user_id = self.pre.get_userID()

        data = {"token": "BPNF", "user_id": user_id, "database_type_name": "nuccore",
                "source_name": "NCBI.NUCCORE", "create_type": "docking", "gis": data_id_str}

        form_data = MultipartEncoder(data)

        headers["Content-Type"] = form_data.content_type
        headers["ignoreCancelToke"] = "true"

        try:
            print("******************外部对接导入{}*****************".format(data_id_str))
            resp = requests.post(url=homepage + "/ardb/upload_id",
                                 headers=headers, data=form_data).json()

            self.assertEqual(resp["code"], "200")

            for r in resp["result_msg"]:
                if whether_exist[r["id"]]:
                    self.assertEqual("1", r["code"], )
                    print("******************{}未添加*****************".format(r["id"]))
                else:
                    self.assertEqual("0", r["code"])
                    print("******************{}添加成功*****************".format(r["id"]))
        finally:
            self.recover_env_header()
            self.recover_remove(whether_exist)

    def recover_remove(self, whether_exist: dict):
        print("******************恢复环境*****************")
        time_stamp = int(round(1000 * time.time()))

        for accession in whether_exist:
            if not whether_exist[accession]:
                resp_get_bioId = requests.get(url=homepage + "/api/nucleicAcid/page?", headers=headers,
                                              params={"pageNum": 1, "pageSize": 10, "sort": "Default_order",
                                                      "sourceDatabase": "nuccore", "_t": time_stamp,
                                                      "queryStrList": json.dumps([
                                                          {"field_name": "Accession", "term": "",
                                                           "value": accession}])}).json()
                self.assertEqual(resp_get_bioId["code"], 200)
                rmv_id = resp_get_bioId["data"]["record"][0]["bioentryId"]

                print("******************删除{}*****************".format(accession))
                resp_rmv_id = requests.delete(url=homepage + "/api/nucleicAcid/remove", headers=headers,
                                              data=json.dumps({"ids": [rmv_id], "sourceIds": [18]})).json()

                self.assertEqual(resp_rmv_id["code"], 200)
                print("******************删除{}成功*****************".format(accession))

    def recover_env_header(self):
        headers["Content-Type"] = "application/json;charset=UTF-8"
        del headers["ignoreCancelToke"]

    # 每次随机外部导入1个数据，循环20次
    def test_nuccore_dock1(self):
        i = 0
        while i < 20:
            i += 1
            rand_acc = random.randint(1, 940000)
            acc_dock = ["JS" + str(rand_acc).zfill(6)]

            self.nuccore_docking(acc_dock)

    # 一次性导入max个(10)数据
    def test_nuccore_dock_max(self):
        acc_dock = []

        i = 0
        while i < 10:
            i += 1
            rand_acc = random.randint(1, 940000)
            acc_dock.append("JS" + str(rand_acc).zfill(6))

        self.nuccore_docking(acc_dock)

