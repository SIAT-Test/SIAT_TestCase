import requests
import unittest
import time

homepage = "https://ardb-prd.e2yun.com"
headers = {"Accept": "application/json, text/plain, */*",
           "Accept-Encoding": "gzip, deflate, br",
           "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
           "Content-Type": "application/json;charset=UTF-8",
           "Host": "ardb-prd.e2yun.com",
           "Origin": "https://ardb-prd.e2yun.com",
           "Referer": "https://ardb-prd.e2yun.com/",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}
time_stamp = int(round(1000 * time.time()))
default_params = {"pageNum": 1, "pageSize": 10, "sort": "Default_order",
                   "sourceDatabase": "nuccore", "t": time_stamp}


class test_pre(unittest.TestCase):
    def login(self):
        params = {"username": "iCm3LP0wxUFHLNlgRssXzA==", "password": "V2RyXJEG9x5EakpcAwm5eA=="}

        resp = requests.post(url=homepage + "/api/login", params=params).json()

        self.assertEqual(resp["code"], 200)

        token, tokenKey = resp["token"], resp["tokenKey"]
        headers["Authorization"] = token
        headers["Authorization-key"] = tokenKey

    def get_userID(self):
        resp = requests.get(url=homepage + "/api/sys/user/profile?", headers=headers,
                            params={"_t": time_stamp}).json()

        self.assertEqual(resp["code"], 200)

        return resp["data"]["id"]
