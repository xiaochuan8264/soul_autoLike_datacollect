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
    command_dump = 'adb shell uiautomator dump /sdcard/00_Temp/ui.xml'
    os.popen(command_dump)
    time.sleep(0.3)
    # 从手机中将文件导入到电脑
    command_pull = "adb pull /sdcard/00_Temp/ui.xml G:/04_Py_Projects/00_MyProjects/operatePhone/Tempdata"
    os.popen(command_pull)


def verifyStatus(file):
    if os.path.exists(file):
        os.remove(file)
    else:
        pass

def getTapPosition(xlmFile):
    """返回一个点赞位置"""
    with open(xlmFile, 'r', encoding='utf-8') as f:
        contents = f.read()
    soup = bf(contents, 'lxml')
    nodes = soup.find_all('node')
    taps = []
    for each in nodes:
        if each.has_attr('text'):
            if each['text'] == '点赞':
                taps.append(each)
    where_to_tap = []
    def get_position(node_tag):
        pattern = re.compile('\d{1,4}')
        approx_p = pattern.findall(node_tag['bounds'])
        x_positon = int(approx_p[0]) + abs(int(approx_p[0]) - int(approx_p[2]))//2
        y_positon = int(approx_p[1]) + abs(int(approx_p[1]) - int(approx_p[3]))//2
        return (x_positon, y_positon)
    for each in taps:
        p = get_position(each)
        where_to_tap.append(p)
    return where_to_tap

def tapLikes(coordinates):
    for each in coordinates:
        command_tap = 'adb shell input tap %d %d' % (each[0], each[1])
        os.popen(command_tap)
        print('点赞 %d x %d'% (each[0], each[1]))
        time.sleep(1)

if __name__ == "__main__":
    file = 'G:/04_Py_Projects/00_MyProjects/operatePhone/Tempdata/ui.xml'
    verifyStatus(file)
    getButtonPage()
    time.sleep(1)
    tap_position = getTapPosition(file)
    tapLikes(tap_position)
