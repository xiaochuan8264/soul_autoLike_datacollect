import os
import re
import time
import threading
# import analyze_planet as ap
from appium import webdriver
from selenium.common.exceptions import *
from stopit import threading_timeoutable as Timeout

def initiate(path):
    # global driver
    """get all necessay PARAMS that are necessay for this program
       ref['roll_range'] = the range for swiping on the screen
       ref['square'] = the position of square
       ref['latest'] = the position of latest post of soulers"""
    # print('初始化...')
    os.popen('adb shell mkdir /sdcard/00_Temp').read()
    # os.mkdir(path +'\\Tempfiles')
    ref = {}
    os.popen('adb shell uiautomator dump /sdcard/00_Temp/params.xml').read()
    os.popen('adb pull /sdcard/00_Temp/params.xml %s\\params.xml' % path).read()
    with open(path +'\\params.xml', 'r', encoding='utf-8') as f:
        content = f.read()
    pattern1 = re.compile('resource-id="cn\.soulapp\.android:id/tv_tab".+?bounds="\[\d{1,4},\d{1,4}\]\[\d{1,4},\d{1,4}\]')
    up = int(re.findall('\d{1,4}', pattern1.search(content).group())[3]) + 500
    pattern2 = re.compile('resource-id="cn\.soulapp\.android:id/bottomLay".+?bounds="\[\d{1,4},\d{1,4}\]\[\d{1,4},\d{1,4}\]')
    bottom = int(re.findall('\d{1,4}', pattern2.search(content).group())[1]) - 500
    x = int(re.findall('\d{1,4}', os.popen('adb shell wm size').read())[0])
    x = int(x*(1/3))
    ref['roll_range'] = (x, bottom, x, up)
    pattern3 = re.compile('resource-id="cn\.soulapp\.android:id/main_tab_square".+?bounds="\[\d{1,4},\d{1,4}\]\[\d{1,4},\d{1,4}\]')
    square = re.findall('\d{1,4}', pattern3.search(content).group())
    square = [int(n) for n in square]
    ref['square'] = ((square[0] + square[2])//2 , (square[1] + square[3])//2)
    pattern4 = re.compile('content-desc="最新".+?bounds="\[\d{1,4},\d{1,4}\]\[\d{1,4},\d{1,4}\]')
    latest = re.findall('\d{1,4}', pattern4.search(content).group())
    latest = [int(n) for n in latest]
    ref['latest'] = ((latest[0] + latest[2])//2 , (latest[1] + latest[3])//2) # tuple
    pattern5 = re.compile('main_tab_center_img.+?bounds="\[\d{1,4},\d{1,4}\]\[\d{1,4},\d{1,4}\]')
    main = re.findall('\d{1,4}', pattern5.search(content).group())
    main = [int(n) for n in main]
    ref['loading'] = ((main[0] + main[2])//2 , main[1] - 40) # tuple
    ref['main'] = ((main[0] + main[2])//2 , (main[1] + main[3])//2) # tuple

    tv1 = driver.find_element_by_id('cn.soulapp.android:id/tv_tab')
    top_boundary = tv1.location['y']
    main_tab = driver.find_element_by_id('cn.soulapp.android:id/main_tab_center_img')
    bottom_boundary = main_tab.location['y']
    iv_like = driver.find_element_by_id('cn.soulapp.android:id/iv_like')
    axis = iv_like.location['x']
    ref['top'] = top_boundary #single number
    ref['bottom'] = bottom_boundary #single number
    ref['axis'] = axis #single number
    return ref

def verify_page():
    global error

    @Timeout()
    def square():
        square = driver.find_element_by_id('cn.soulapp.android:id/lotSquare')
        return square
    try:
        square_status = square(timeout=3)
        if square_status == None:
            return False
    except NoSuchElementException as e:
        @Timeout()
        def title():
            try:
                title = driver.find_element_by_id('cn.soulapp.android:id/detail_title')
                return True
            except NoSuchElementException as e:
                return False
        @Timeout()
        def image():
            try:
                img = driver.find_element_by_id('cn.soulapp.android:id/index')
                return True
            except NoSuchElementException as e:
                return False
        @Timeout()
        def topic():
            try:
                img = driver.find_element_by_id('cn.soulapp.android:id/topic_title')
                return True
            except NoSuchElementException as e:
                return False
        if title(timeout=2):
            driver.back()
            return False
        elif image(timeout=2):
            driver.back()
            return False
        elif topic(timeout=2):
            driver.back()
            return False
        else:
            e = str(e)
            error += 1
            if error == 3:
                with open('logs.txt','a', encoding='utf-8') as f:
                    f.write('%s 页面错误重启，详情：%s\n' % (time.ctime(), e))
                rebootApp(params)
                error = 0
                return False
            else:
                return False
    except WebDriverException as e:
        e = str(e)
        error += 1
        if error == 3:
            with open('logs.txt','a', encoding='utf-8') as f:
                f.write('%s 页面错误重启，详情：%s\n' % (time.ctime(), e))
            rebootApp(params)
            error = 0
            return False
        else:
            return False
    try:
        square = driver.find_element_by_id('cn.soulapp.android:id/footerText')
        error += 1
        time.sleep(1)
        if error == 3:
            with open('logs.txt','a', encoding='utf-8') as f:
                f.write('%s 页面加载超时重启\n' % (time.ctime()))
            rebootApp(params)
            error = 0
            return False
        else:
            return False
    except NoSuchElementException as e:
        return True

def tap_position():
    if not verify_page():
        return []
    @Timeout()
    def find_like():
        elements = driver.find_elements_by_id('cn.soulapp.android:id/iv_like')
        return elements
    elements = find_like(timeout=3)
    if elements != None:
        return elements
    else:
        return []

def like(elements):
    def click(element):
        element.click()
    threads = []
    threads = [threading.Thread(target=click, args=(n,)) for n in elements]
    [_.start() for _ in threads]
    [_.join(1) for _ in threads]
    return len(elements)

def like2(elements):
    @Timeout()
    def click(element):
        element.click()
    # [element.click() for element in elements]
    for element in elements:
        click(element, timeout=1)
    return len(elements)

def like_adb(elements):
    def click(x, y):
        os.popen('adb shell input tap %d %d'% (x, y))
        time.sleep(0.08)
    coordinates = []
    start = time.time()
    for each in elements:
        try:
            value = list(each.location.values())
            coordinates.append(value)
        except StaleElementReferenceException as e:
            e = str(e)
            with open('logs.txt','a', encoding='utf-8') as f:
                f.write('%s 生成坐标出错，详情：%s\n' % (time.ctime(), e))
    print('分析用时%f秒'%(time.time()-start))
    [click(_[0],_[1]) for _ in coordinates]
    return len(coordinates)

def rebootApp(params):
    os.popen('adb shell am force-stop cn.soulapp.android')
    time.sleep(0.5)
    os.popen('adb shell am start -n cn.soulapp.android/.ui.main.MainActivity')
    time.sleep(2)
    os.popen('adb shell input tap %d %d'% params['square'])
    time.sleep(0.1)
    os.popen('adb shell input tap %d %d'% params['square'])
    time.sleep(0.5)
    os.popen('adb shell input tap %d %d'% params['latest'])
    with open('rebootRecords.txt','a', encoding='utf-8') as f:
        f.write('于 %s 重启Soul\n' % time.ctime())
    time.sleep(2)

def roll_adb(swipe,stop):
    os.popen(swipe)
    time.sleep(0.28)
    os.popen(stop)
    time.sleep(0.1)

# def roll_appium(down):
#     # down = elements[-1].location['y']
#     up = params['top']
#     axis = params['axis']
#
#     driver.swipe(axis, down, axis, up)

def roll_appium():
    stop_x, stop_y = params['loading'][0], params['loading'][1]
    up = params['roll_range'][2]
    axis = params['axis']
    down = params['roll_range'][1]
    driver.swipe(axis, down, axis, up)
    driver.tap([(stop_x, stop_y)])

def test1():
    global count
    try:
        while True:
            print('已点< %d >赞 [累计耗时：%f ]' % (count, (time.time() - c)))
            try:
                start = time.time()
                elements = tap_position()
                print('获取点赞耗时：%f' % (time.time() - start))
            except StaleElementReferenceException as e:
                e = str(e)
                with open('logs.txt','a',encoding='utf-8') as f:
                    n = '%s 出错:%s \n' %(time.ctime(), e)
                    f.write(n)
                roll_adb(swipe, stop)
                continue
            except WebDriverException as e:
                e = str(e)
                with open('logs.txt','a', encoding='utf-8') as f:
                    f.write('%s 页面错误，详情：%s\n' % (time.ctime(), e))
                rebootApp()
                continue
            blank_page.append(elements)
            if len(blank_page) > 10:
                verify = [1 if n else 0 for n in blank_page[-10:]]
                if not sum(verify):
                    rebootApp(params)
                    blank_page.clear()
                    continue
                else:
                    blank_page.clear()
            start = time.time()
            # count += like_adb(elements)
            count += like(elements)
            print('点赞用时：%f 秒'%(time.time()- start))
            start = time.time()
            roll_adb(swipe,stop)
            print('滑动用时：%f 秒'%(time.time()- start))
    except KeyboardInterrupt as e:
        print('\n中断程序...')
    finally:
        cc = time.time()
        used_time = round(cc - c, 2)
        print('点赞 %d 次, 用时 %f 秒' % (count, used_time))
        with open('点赞次数.txt','w') as f:
            text = '点赞 %d 次，用时 %f 秒, 平均每分钟 %d 赞' % (count, used_time, round(60/(used_time/count), 2))
            f.write(text)

if __name__ == "__main__":
    try:
        basepath = os.mkdir(os.getcwd()+'\\Tempfiles')
    except FileExistsError as e:
        basepath = os.getcwd()+'\\Tempfiles'
    DesiredCapabilities = {
                           "platformName": "Android",
                           "deviceName": "LIO-AL00",
                           "appPackage": "cn.soulapp.android",
                           "appActivity": "cn.soulapp.android.ui.splash.SplashActivity",
                           "noReset": "true",
                           "fullReset": "false",
                           "newCommandTimeout": "3600"
                           }
    print('初始化...')
    driver = webdriver.Remote('http://localhost:4723/wd/hub', DesiredCapabilities)
    print('等待加载页面')
    time.sleep(10)
    params = initiate(basepath)

    error = 0
    count = 0
    c = time.time()
    swipe = 'adb shell input swipe %d %d %d %d 10'% params['roll_range']
    stop = 'adb shell input tap %d %d'% params['loading']
    # i = 0
    blank_page = []
    # goals = int(input('请输入目标点赞数[点赞数到达自动停止]：'))
    try:
        while True:
            print('已点< %d >赞 [累计耗时：%f ]' % (count, (time.time() - c)))
            try:
                start = time.time()
                elements = tap_position()
                print('获取点赞耗时：%f' % (time.time() - start))
            except StaleElementReferenceException as e:
                e = str(e)
                with open('logs.txt','a',encoding='utf-8') as f:
                    n = '%s 出错:%s \n' %(time.ctime(), e)
                    f.write(n)
                roll_adb(swipe, stop)
                continue
            except WebDriverException as e:
                e = str(e)
                with open('logs.txt','a', encoding='utf-8') as f:
                    f.write('%s 页面错误，详情：%s\n' % (time.ctime(), e))
                driver = webdriver.Remote('http://localhost:4723/wd/hub', DesiredCapabilities)
                time.sleep(10)
                continue
            blank_page.append(elements)
            if len(blank_page) > 10:
                verify = [1 if n else 0 for n in blank_page[-10:]]
                if not sum(verify):
                    rebootApp(params)
                    blank_page.clear()
                    continue
                else:
                    blank_page.clear()
            start = time.time()
            # count += like_adb(elements)
            count += like(elements)
            # count += like2(elements)
            print('点赞用时：%f 秒'%(time.time()- start))
            # if count >= goals:
            #     break
            start = time.time()
            roll_adb(swipe,stop)
            print('滑动用时：%f 秒'%(time.time()- start))
            # time.sleep(0.05)
    except KeyboardInterrupt as e:
        print('\n中断程序...')
    finally:
        cc = time.time()
        used_time = round(cc - c, 2)
        print('点赞 %d 次, 用时 %f 秒' % (count, used_time))
        with open('点赞次数.txt','w') as f:
            text = '点赞 %d 次，用时 %f 秒, 平均每分钟 %d 赞' % (count, used_time, round(60/(used_time/count), 2))
            f.write(text)
