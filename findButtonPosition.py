from bs4 import BeautifulSoup as bf
import re
import random
import os
import time

def numGenerator():
    """本意是想为每次截图控件设置不同名字以免冲突
        但是发现是可以直接覆盖的，那就算了吧"""
    count = 1
    while count:
        yield count
        count += 1

def getButtonPage():
    # 获取当前屏幕的所有控件并将文件保存到手机
    def verify():
        test = os.popen('adb shell ls sdcard/00_Temp/ui.xml').read()
        if test.find('No such file or directory') == -1:
            print('xml file stored in phone')
            return True
        else:
            return False
    command_dump = 'adb shell uiautomator dump /sdcard/00_Temp/ui.xml'
    while True:
        os.popen(command_dump)
        time.sleep(1)
        if verify():
            break
    # 从手机中将文件导入到电脑
    command_pull = "adb pull /sdcard/00_Temp/ui.xml G:/04_Py_Projects/00_MyProjects/operatePhone/Tempdata"
    count = 1
    while True:
        os.popen(command_pull)
        time.sleep(0.5)
        if os.path.exists('G:/04_Py_Projects/00_MyProjects/operatePhone/Tempdata/ui.xml'):
            print('succefully extract file from phone')
            count = 1
            break
        else:
            print('pulling file failed, try again. >> %d times tried' % count)
            os.popen(command_dump)
            count += 1
            time.sleep(3)



def verifyStatus(file):
    if os.path.exists(file):
        os.remove(file)
        print('delete the old file')
    else:
        print('now the folder is clean')

def deleteFile_phone():
    res = os.popen('adb shell rm /sdcard/00_Temp/ui.xml').read()
    verify = 'No such file or directory'
    if res.find(verify) == -1 :
        print('removed temp file "ui.xml" from phone')
        return True
    else:
        return False

# def getTapPosition(xlmFile):
#     """返回一个点赞位置"""
#     with open(xlmFile, 'r', encoding='utf-8') as f:
#         contents = f.read()
#     soup = bf(contents, 'lxml')
#     nodes = soup.find_all('node')
#     taps = []
#     for each in nodes:
#         if each.has_attr('text'):
#             if each['text'] == '点赞':
#                 taps.append(each)
#     where_to_tap = []
#     def get_position(node_tag):
#         pattern = re.compile('\d{1,4}')
#         approx_p = pattern.findall(node_tag['bounds'])
#         x_positon = int(approx_p[0]) + abs(int(approx_p[0]) - int(approx_p[2]))//2
#         y_positon = int(approx_p[1]) + abs(int(approx_p[1]) - int(approx_p[3]))//2
#         return (x_positon, y_positon)
#     for each in taps:
#         p = get_position(each)
#         where_to_tap.append(p)
#     print('this page has <%d> likes to tap'% len(where_to_tap))
#     return where_to_tap

def getTapPosition(xlmFile):
    """返回一个点赞位置"""
    with open(xlmFile, 'r', encoding='utf-8') as f:
        contents = f.read()
    soup = bf(contents, 'lxml')
    nodes = soup.find_all('node')
    taps = []
    for each in nodes:
        if each['resource-id'] == 'cn.soulapp.android:id/ll_double':
            taps.append(each)
    where_to_tap = []
    def get_position(node_tag):
        pattern = re.compile('\d{1,4}')
        approx_p = pattern.findall(node_tag['bounds'])
        x_positon = (int(approx_p[0]) + int(approx_p[2]))//2
        y_positon = (int(approx_p[1]) + int(approx_p[3]))//2
        return (x_positon, y_positon)
    for each in taps:
        p = get_position(each)
        where_to_tap.append(p)
    # print('this page has <%d> times to tap'% len(where_to_tap))
    return where_to_tap

def ifWrong(y):
    """超出这个界限会误触到发布瞬间，尽量不误触"""
    if y >= 1588:
        return True
    else:
        return False

def tapLikes(coordinates):
    for each in coordinates:
        if ifWrong(each[1]):
            continue
        command_tap = 'adb shell input tap %d %d' % (each[0], each[1])
        for i in range(2):
            os.popen(command_tap)
            time.sleep(0.1)
        print('点赞 %d x %d'% (each[0], each[1]))
        time.sleep(1)

def rollDownPage():
    os.popen('adb shell input swipe 700 1500 700 400 500') # from 700x1500 to 700x400 in 0.5s
    print('rolled down')
    time.sleep(1)

if __name__ == "__main__":
    file = 'G:/04_Py_Projects/00_MyProjects/operatePhone/Tempdata/ui.xml'
    while True:
        verifyStatus(file)
        time.sleep(0.5)
        getButtonPage()
        delete = deleteFile_phone()
        time.sleep(1)
        tap = getTapPosition(file)
        tapLikes(tap)
        rollDownPage()
