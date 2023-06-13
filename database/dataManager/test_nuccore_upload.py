from requests_toolbelt.multipart.encoder import MultipartEncoder

import json
import time
import unittest

import requests

from database.dataManager.test_pre import test_pre, homepage, headers


class test_nuccore_upload(unittest.TestCase):
    pre = test_pre()
    pre.login()

    # 修改文件标识字段，保证每次上传文件不重复
    def file_rename_acc(self):
        with open('D:/TestCase/database/dataManager/nuccore_backup.gb', 'r', encoding='utf-8') as f_old:
            with open('D:/TestCase/database/dataManager/nuccore_testRW.gb', 'w', encoding='utf-8') as f_new:
                for line in f_old:
                    if "testRW" in line:
                        i = line.index("testRW")
                        line = line.replace(line[i:i+17], "testRW_"
                                            + time.strftime("%m%d%H%M%S", time.localtime()))
                    f_new.write(line)
        f_old.close()
        f_new.close()

    # 调用接口/ardb/upload_data，导入本地文件创建数据，返回accession
    def nuccore_upload(self):
        user_id = self.pre.get_userID()
        file = open('D:/TestCase/database/dataManager/nuccore_testRW.gb', 'rb')
        self.file_rename_acc()

        data = {"token": "BPNF", "user_id": user_id, "database_type_name": "nuccore",
                "source_name": "NCBI.NUCCORE", "create_type": "import",
                'file': ("1.gb", file)}
        form_data = MultipartEncoder(data)

        headers["Content-Type"] = form_data.content_type
        headers["ignoreCancelToke"] = "true"

        resp = requests.post(url=homepage + "/ardb/upload_data",
                             headers=headers, data=form_data).json()
        file.close()

        self.assertEqual(resp["code"], "200", resp)
        acc = resp["result_msg"][0]["id"]

        self.recover_env_header()
        return acc

    # 审核通过，返回新增数据的bioEntryID
    def nuccore_audit(self, acc):
        # 调用/api/nucleicAcid/dataPage，获取新导入数据的bioEntryid
        time_stamp = int(round(1000 * time.time()))
        resp_get_bioId = requests.get(url=homepage + "/api/nucleicAcid/dataPage?", headers=headers,
                                      params={"pageNum": 1, "pageSize": 200, "_t": time_stamp,
                                              "stateList": "1,2,3"}).json()
        self.assertEqual(resp_get_bioId["code"], 200)

        bioId = 0
        for r in resp_get_bioId["data"]["record"]:
            if acc in r["title"]:
                bioId = r["bioentryId"]
                break

        # 调用/api/nucleicAcid/audit，审核通过新导入的数据
        resp_audit = requests.post(url=homepage + "/api/nucleicAcid/audit", headers=headers,
                                   data=json.dumps({"state": 2, "ids": [bioId], "sourceNames": ["nuccore"],
                                                    "sourceDatabase": [18]})).json()
        self.assertEqual(resp_audit["code"], 200, resp_audit)

        return bioId

    # 恢复环境，删除新添加的数据
    def recover_remove(self, bioEntryId):
        print("******************删除{}*****************".format(bioEntryId))
        resp_rmv_id = requests.delete(url=homepage + "/api/nucleicAcid/remove", headers=headers,
                                      data=json.dumps({"ids": [bioEntryId], "sourceIds": [18]})).json()

        self.assertEqual(resp_rmv_id["code"], 200, resp_rmv_id)
        print("******************删除成功*****************")

    # 恢复环境，还原消息头
    def recover_env_header(self):
        headers["Content-Type"] = "application/json;charset=UTF-8"
        del headers["ignoreCancelToke"]

    def test_debug(self):
        acc = self.nuccore_upload()
        bioId = self.nuccore_audit(acc)
        self.recover_remove(bioId)
        pass
