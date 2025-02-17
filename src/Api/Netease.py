#  Copyright (c) 2023. 秋城落叶, Inc. All Rights Reserved
#  @作者         : 秋城落叶(QiuChenly)
#  @邮件         : 1925374620@qq.com
#  @文件         : 项目 [qqmusic] - Netease.py
#  @修改时间    : 2023-03-08 01:58:56
#  @上次修改    : 2023/3/8 上午1:58
import json
import os
import time

from src.Api.BaseApi import BaseApi
from src.Common import Http
from src.Types.Types import Songs


class Netease(BaseApi):
    __baseUrl = 'http://cloud-music.pl-fe.cn'

    def __init__(self):
        self.__httpServer = Http.HttpRequest()

    def http(self, url, method=0, data={}):
        return self.httpwj(self.__baseUrl + url, method, data)

    def httpwj(self, url, method=0, data={}):
        return self.__httpServer.getHttp2Json(url, method, data)

    def httpw(self, url, method=0, data=b'', head={}):
        return self.__httpServer.getHttp(url, method, data, header=head)

    def search(self, searchKey: str) -> list[Songs]:
        pass

    def cookie(self):
        dt = self.__httpServer.getSession().cookies.get_dict()
        return dt

    def set_cookie(self, ck: dict):
        self.__httpServer.setCookie(ck)

    def checkQrState(self, unikey: str):
        u = '/login/qr/check?key=' + unikey + f"&time={time.time_ns()}"
        log = self.http(u).json()
        log['cookie'] = self.cookie()
        print(u, log)
        return log

    def uploadMusic2NetEaseCloud(self, fileLocate: str):
        """
        上传歌曲到网易云云盘，此函数还未经过代码测试
        Args:
            fileLocate:

        Returns:

        """
        # TODO 需要测试此处代码
        u = '/cloud'
        name = os.path.basename(fileLocate)
        with open(fileLocate, "rb") as conf:
            upFile = {
                'songFile': (name, conf)
            }
        res = self.__httpServer.getSession().post(u, files=upFile, headers={
            'Content-Type': 'multipart/form-data'
        })
        res = res.json()
        print(res)

    def getUserDetail(self):
        u = '/user/account'
        return self.http(u).json()

    def getUserDetail(self):
        u = '/user/account'
        return self.http(u).json()

    def getUserLikeList(self, uid: str):
        """
        传入用户 id, 可获取已喜欢音乐 id 列表(id 数组) 不是必须
        Args:
            uid:

        Returns:

        """
        u = f'/likelist?uid={uid}' + f"&time={time.time_ns()}"
        res = self.http(u).json()
        return res['ids']

    userPlaylist = []

    def getUserPlaylist(self, uid: str):
        """
        获取用户的收藏或创建的歌单
        Args:
            uid:

        Returns:

        """
        u = f'/user/playlist?uid={uid}' + f"&time={time.time_ns()}"
        res = self.http(u).json()
        userPlaylist = [
            {
                'userId': l['userId'],
                'trackCount': l['trackCount'],
                'name': l['name'],
                'id': l['id'],
                'coverImgUrl': l['coverImgUrl']
            } for l in res['playlist']
        ]
        # print("用户所有歌单")
        return userPlaylist

    def getPlayListAllMusic(self, playId, size=1000, offset=0):
        """
        获取歌单里所有音乐
        Args:
            playId:
            size:
            offset:

        Returns:

        """
        u = f'/playlist/track/all?id={playId}&limit={size}&offset={offset}' + f"&time={time.time_ns()}"
        res = self.http(u)
        if res.status_code != 200:
            return []
        if res.text.find(":400}") != -1:
            return []
        js = res.json()
        if js['code'] == 20001:
            return -1
        return [
            {
                "title": li['name'],
                "mid": li['id'],
                'author_simple': li['ar'][0]['name'],  # li['ar'][0]['name'] if len(li['ar']) == 1 else
                "author": li['ar'],  # 数组[{'id': 472822, 'name': 'JJD', 'tns': [], 'alias': []}]
                'publishTime': li['publishTime'],
                'album': li['al']['name']
            } for li in js['songs']
        ]

    def anonimousLogin(self):
        u = "/register/anonimous" + f"?time={time.time_ns()}"
        res = self.http(u)
        res = res.json()
        return res

    def getUserLevel(self):
        u = "/user/level" + f"?time={time.time_ns()}"
        res = self.http(u)
        res = res.json()
        return res

    def qrLogin(self):
        u = '/login/qr/key?' + f"time={time.time_ns()}"
        res = self.http(u)
        uniKey = res.json()['data']['unikey']
        print("uniKey", uniKey)

        u = '/login/qr/create?key=' + uniKey + "&qrimg=1"
        res = self.http(u).json()['data']
        b64 = res['qrimg']
        url = res['qrurl']
        return {
            'url': url,
            'b64': b64,
            'uniKey': uniKey
        }
        # img = base64.b64decode(b64.split(",")[1])
        # with open("./login.png", "wb+") as p:
        #     p.write(img)
        #     p.flush()
        #
        # img = cv2.imread("./login.png")
        # cv2.imshow("", img)
        # cv2.waitKey(0)
        #
        # res = self.checkQrState(unikey)
        # res = res.json()['code']
        # if res == 803:
        #     # Login Success
        #     return True
        # print("登录失败。")
        # return False

    def save_local(self, reinit=False):
        """
        保存cookie到本地 避免重复登录造成账户异常
        Args:
            reinit: True则清空本地cookie重置。

        Returns:

        """
        with open("./NetEase.cfg", 'wb+') as p:
            p.write(json.dumps({
                'cookie': '' if reinit else self.cookie()
                # 'likes': mySubCount
            }).encode())
            p.flush()

    def read_local(self):
        """
        登录成功返回True 否则返回False
        Returns:

        """
        if os.path.exists("./NetEase.cfg"):
            with open("./NetEase.cfg", 'r') as p:
                s = p.read()
                dt = json.loads(s)
                if dt['cookie'] == '':
                    return False
                self.set_cookie(dt['cookie'])
                isLogin = self.getUserDetail()['code'] == 200
                return isLogin
        return False

    def getMusicUrl(self, id=''):
        u = 'http://music.fy6b.com/index/mp3orflac'
        d = f'type=netease&id={id}&option=flac'
        # {
        # 	"url": "http:\/\/m704.music.126.net\/20230305234939\/ccfe8832df4e3431dbe25dfea1118f1e\/jdymusic\/obj\/wo3DlMOGwrbDjj7DisKw\/22975550396\/2dbf\/d87f\/e6f2\/11dac549d861ba74f1d599d2f4f45cea.flac?authSecret=00000186b25ff97815c80aaba23719fb",
        # 	"size": 3278433,
        # 	"br": 512.575
        # }
        r = self.httpw(u, 1, d.encode('utf-8'), {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 8.1.0; MI 5s Build/OPM1.171019.018)"
        })
        r = r.json()
        return r

    def searchMusicByTrd(self, searchKey="周杰伦", pageNum=1, pageSize=100):
        """
        第三方接口搜索网易云歌曲
        Args:
            searchKey:
            pageNum:
            pageSize:

        Returns:

        """
        u = 'http://music.fy6b.com/'
        d = f'type=netease&keyword={searchKey}&page={pageNum}&limit={pageSize}'
        r = self.httpw(u, 1, d.encode('utf-8'), {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; MI 5s Build/TQ1A.230105.002.A1)"
        })
        r = r.json()
        lst = []
        for li in r:
            it = {
                'prefix': "",
                'extra': "flac",
                'notice': "暂无",
                'mid': li['id'],
                'musicid': li['id'],
                'songmid': li['id'],
                'size': "无",
                'title': li['name'],
                'singer': li['singer'],
                'album': "无专辑",
                'time_publish': "无",
                # 'hasLossless': li['hasLossless'],
                'readableText': f"{li['singer']} - {li['name']}"
            }
            lst.append(it)
        return {
            'data': lst,
            'page': {
                'size': 10000,  # 这个接口不反悔这个字段 所以只能固定一万了
                'next': pageNum + 1,
                'cur': pageNum,
                'searchKey': searchKey
            }
        }

    def searchMusic(self, searchKey="周杰伦", pageNum=1, pageSize=100):
        """
        官方接口搜索网易云歌曲
        Args:
            searchKey:
            pageNum:
            pageSize:

        Returns:

        """
        u = f'/cloudsearch?keywords={searchKey}&offset={pageNum}&limit={pageSize}' + f"&time={time.time_ns()}"
        res = self.http(u)
        res = res.json()

        result = res['result']
        lst = []
        for li in result['songs']:
            au_l = li['l']
            au_m = li['m']
            au_h = li['h']
            au_sq = li['sq']
            au_hr = li['hr']

            if au_hr is not None:
                size = au_hr['size']
                extra = 'flac'
                bitrate = round(int(au_hr['br']) / 1000)
            elif au_sq is not None:
                size = au_sq['size']
                extra = 'flac'
                bitrate = round(int(au_sq['br']) / 1000)
            elif au_h is not None:
                size = au_h['size']
                extra = 'mp3'
                bitrate = round(int(au_h['br']) / 1000)
            elif au_m is not None:
                size = au_m['size']
                extra = 'mp3'
                bitrate = round(int(au_m['br']) / 1000)
            else:
                size = au_l['size']
                extra = 'aac'
                bitrate = round(int(au_l['br']) / 1000)

            it = {
                'prefix': "",
                'extra': extra,
                'notice': "FLAC 无损音质" if extra == 'flac' else f'{extra.upper()} {bitrate}Kbps',
                'mid': li['id'],
                'musicid': li['id'],
                'songmid': li['id'],
                'size': "%.2fMB" % (int(size) / 1024 / 1024),
                'title': li['name'],
                'singer': "/".join([
                    it['name'] for it in li['ar']
                ]),
                'author_simple': li['ar'][0]['name'],
                'album': li['al']['name'],
                'time_publish': li['publishTime'],
                # 'hasLossless': li['hasLossless'],
                # 'readableText': f"{li['singer']} - {li['name']}"
            }
            lst.append(it)
        return {
            'data': lst,
            'page': {
                'size': result['songCount'],  # 这个接口不反悔这个字段 所以只能固定一万了
                'next': pageNum + 1,
                'cur': pageNum,
                'searchKey': searchKey
            }
        }
