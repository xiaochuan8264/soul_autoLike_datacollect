from bs4 import BeautifulSoup as bf
import re
import random
import os
import time

class AutoLike:
    """1st step: self.verifyPc() #to make sure the old file in computer is removed
           if exists:
               remove file in pc
       2nd step: get all the contents of current screen
       3rd step: delete files in phone, should consider async or threading operation
       4th step: get exact tap positions
       5th step: tap likes
       6th step: roll page down"""


    def __init__(self):
        # self._mobile_file = '/sdcard/00_Temp/ui.xml'
        self._pc_file = 'G:/04_Py_Projects/00_MyProjects/operatePhone/Tempdata/ui.xml'
        self.pc = True # default exists
        self.mobile = True # default exists
        self.dump_errors = 0 #count how many times failed to dump
        self.pull_errors = 0 #count how many times failed to pull
        self.coordinates = [] # coordinates to tap
        self.limit = True # limit the tap positon, not to tap certain area
        self.likes = 0
        self.xy_temp = []
        self.wait = False
        self.screen = ''
        self.location = True


    def dump_error(self):
        if self.dump_errors/10 != 0 and isinstance(self.dump_errors/10, int):
            print('dump failed %d times' % self.dump_errors)

    def pull_error(self):
        if self.pull_errors/10 != 0 and isinstance(self.pull_errors/10, int):
            print('pull failed %d times' % self.pull_errors)


    def _verifyPc(self):
        """check if the file already exists"""
        if os.path.exists(self._pc_file):
            # print('exists')
            self.pc = True
        else:
            # print('empty')
            self.pc = False


    def _delPc(self):
        """delete file in pc if it exists"""
        while self.pc:
            os.remove(self._pc_file)
            print(self.pc)
            self._verifyPc()



    def _verifyMobile(self):
        """verify if the file exists"""
        test = os.popen('adb shell ls sdcard/00_Temp/ui.xml').read()
        # print(test)
        if test.find('No') == -1:
            self.mobile = True
        else:
            self.mobile = False


    def _delMobile(self):
        """delete file in mobile if it exists"""
        while self.mobile:
            os.popen('adb shell rm /sdcard/00_Temp/ui.xml')
            self._verifyMobile()
            # verify = 'No such file or directory'
            # if res.find(verify) == -1 :
            #     return
            # else:
            #     return False

    def _limitTap(self, y):
        if y >= 1588:
            self.limit = True
        else:
            self.limit = False

    def getcp(self): # get currentpage of the phone
        command_dump = 'adb shell uiautomator dump /sdcard/00_Temp/ui.xml'
        command_pull = "adb pull /sdcard/00_Temp/ui.xml G:/04_Py_Projects/00_MyProjects/operatePhone/Tempdata"
        while True:
            print('first circle')
            self._verifyMobile()
            if self.mobile:
                self._delMobile()
            os.popen(command_dump)
            time.sleep(1)
            self._verifyMobile()
            time.sleep(1)
            if self.mobile:
                break
            else:
                self.dump_errors += 1
                self.dump_error()
        while True:
            print('second circle')
            self._verifyPc()
            if self.pc:
                self._delPc()
            os.popen(command_pull)
            time.sleep(1)
            self._verifyPc()
            time.sleep(1)
            if self.pc:
                with open(self._pc_file, 'r', encoding='utf-8') as f:
                    self.screen = f.read()
                break
            else:
                self.pull_errors += 1
                self.pull_error()

    def _get_position(self, node_tag):
        pattern = re.compile('\d{1,4}')
        approx_p = pattern.findall(node_tag['bounds'])
        x_positon = (int(approx_p[0]) + int(approx_p[2]))//2
        y_positon = (int(approx_p[1]) + int(approx_p[3]))//2
        return (x_positon, y_positon)

    def getTapPosition(self):
        """返回一个点赞位置"""
        nodes = bf(self.screen, 'lxml').find_all('node')
        taps = []
        for each in nodes:
            if each['resource-id'] == 'cn.soulapp.android:id/ll_double':
                p = self._get_position(each)
                self.coordinates.append(p)

    def tap(self):
        for each in self.coordinates:
            self._limitTap(each[1])
            if self.limit:
                continue
            command_tap = 'adb shell input tap %d %d' % (each[0], each[1])
            for i in range(2):
                os.popen(command_tap)
                time.sleep(0.1)
            print('点赞 %d x %d'% (each[0], each[1]))
            self.likes += 1
            time.sleep(1)
        self.xy_temp = self.coordinates.copy()
        self.coordinates.clear()

    def rollPage(self):
        os.popen('adb shell input swipe 700 1500 700 400 500') # from 700x1500 to 700x400 in 0.5s
        print('rolled down')
        time.sleep(1)

    def wait_or_not(self):
        if re.search(re.compile('text="加载中\.\.\.'), self.screen) != None:
            self.wait = True

    def rebootApp(self):
        os.popen('adb shell am force-stop cn.soulapp.android')
        time.sleep(0.5)
        os.popen('adb shell am start -n cn.soulapp.android/.ui.main.MainActivity')
        time.sleep(5)
        os.popen('adb shell input tap 324 1718')

    def check_location(self):
        try:
            res = re.search(re.compile('cn\.soulapp\.android:id/main_tab_center_img'), self.screen).group()
        except AttributeError:
            self.location = False
        else:
            self.loaction = True

    def go_back(self):
        os.popen('adb shell input keyevent 4')


if __name__ == "__main__":
    soul = AutoLike()
    print('实例化完成')
    count = 0
    while True:
        soul.getcp()
        time.sleep(1)
        soul.check_location()
        time.sleep(1)
        while not soul.location:
            print('go back')
            soul._delPc()
            time.sleep(1)
            soul._delMobile()
            time.sleep(1)
            os.popen('adb shell input keyevent 4')
            soul.getcp()
            time.sleep(3)
            soul.check_location()
            print('*'*30)
            print(soul.location)
            print('*'*30)
        print('获取到页面')
        soul.wait_or_not()
        if soul.wait:
            print('等待加载')
            time.sleep(2)
            soul._delMobile()
            print('删除手机文件')
            count += 1
            if count == 3:
                soul.rebootApp()
            continue
        soul._delMobile()
        print('删除手机文件')
        soul.getTapPosition()
        print('获取点赞位置')
        soul.tap()
        soul.rollPage()
