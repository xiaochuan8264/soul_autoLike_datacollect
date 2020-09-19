"""
REQUIREMENTS:
            1. pakages:[os, re, time, threading, appium, stopit]
            2. environment: [adb, appium]
                # install adb environment, make sure it works in cmd,
                  test connection by using 'adb devices' in cmd when your phone
                  is connected to your computer
                # Install appium into your computer, then configure
                  the environment correctly, you may refer to the tutorial in
                  'https://www.guru99.com/introduction-to-appium.html'
HOW TO USE:
            1. test your connection between phone and computer by command 'adb devecies'
               proceed if successful.
            2. start appium either from desktop or 'appium' in cmd shell.
            3. start the program
"""
import os, re, time, threading, pymysql, sys
from appium import webdriver
from selenium.common.exceptions import *
from stopit import threading_timeoutable as Timeout
import sortout_database as SD

basepath_phone = "/sdcard/Pictures"
basepath_pc = "G:\\04_Py_Projects\\00_MyProjects\\01_operatePhone\\Tempfiles\\ImageShare"


def initiate(path):
    """get all necessay PARAMS that are necessay for this program
       ref['roll_range'] = the range for swiping on the screen
       ref['square'] = the position of square
       ref['latest'] = the position of latest post of soulers"""
    ref = {}
    # os.popen('adb shell uiautomator dump %s/params.xml'%basepath_phone).read()
    # os.popen('adb pull /sdcard/00_Temp/params.xml %s\\params.xml' % path).read()
    while True:
        try:
            driver.find_element_by_id('cn.soulapp.android:id/iv_like')
            break
        except NoSuchElementException as e:
            try:
                button = driver.find_element_by_id('android:id/button1')
                button.click()
            except NoSuchElementException as e:
                pass
            time.sleep(2)
            pass
    content = driver.page_source
    # with open(basepath_pc +'\\params.xml', 'r', encoding='utf-8') as f:
    #     content = f.read()
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
    pattern4 = re.compile('content-desc="推荐".+?bounds="\[\d{1,4},\d{1,4}\]\[\d{1,4},\d{1,4}\]')
    recommend = re.findall('\d{1,4}', pattern4.search(content).group())
    recommend = [int(n) for n in recommend]
    ref['recommend'] = ((recommend[0] + recommend[2])//2 , (recommend[1] + recommend[3])//2) # tuple
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
    head = driver.find_elements_by_class_name('androidx.appcompat.app.ActionBar$d')
    head[1].click()
    time.sleep(1)
    new = driver.find_element_by_id("cn.soulapp.android:id/tvNews")
    new.click()
    return ref

def verify_page():
    """To verify if page is in the right panel"""
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
            if error == 5:
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
        if error == 6:
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
        if "加载失败" in square.text:
            rebootApp(params)
            error = 0
            return False
        if error == 6:
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
    if elements:
        return elements
    else:
        return []

def like(elements): #Appium
    def click(element):
        element.click()
    threads = []
    threads = [threading.Thread(target=click, args=(n,)) for n in elements]
    [_.start() for _ in threads]
    [_.join(1) for _ in threads]
    return len(elements)

def like2(elements): #Appium
    @Timeout()
    def click(element):
        element.click()
    for element in elements:
        click(element, timeout=1)
    return len(elements)

def like_adb(elements):
    def click(x, y):
        os.popen('adb shell input tap %d %d'% (x, y))
        time.sleep(0.1)
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
    # print('分析用时%f秒'%(time.time()-start))
    [click(_[0],_[1]) for _ in coordinates]
    return len(coordinates)

def rebootApp(params):
    os.popen('adb shell am force-stop cn.soulapp.android')
    time.sleep(0.5)
    # os.popen('adb shell am start -n cn.soulapp.android/.ui.main.MainActivity')
    os.popen('adb shell am start -n cn.soulapp.android/.ui.splash.SplashActivity')
    time.sleep(2)
    temp = 0
    while True:
        try:
            square = driver.find_element_by_id('cn.soulapp.android:id/lotSquare')
            break
        except NoSuchElementException as e:
            try:
                button = driver.find_element_by_id('android:id/button1')
                button.click()
            except NoSuchElementException as e:
                pass
            time.sleep(1.5)
            temp += 1
            if temp == 5:
                rebootApp(params)
    os.popen('adb shell input tap %d %d'% params['square'])
    time.sleep(0.1)
    os.popen('adb shell input tap %d %d'% params['square'])
    time.sleep(0.5)
    # head = driver.find_elements_by_class_name('androidx.appcompat.app.ActionBar$d')
    temp = 0
    while True:
        head = driver.find_elements_by_class_name('androidx.appcompat.app.ActionBar$d')
        if len(head) == 3:
            break
        else:
            time.sleep(1.5)
            temp += 1
            if temp == 5:
                rebootApp(params)
    head[1].click()
    time.sleep(1)
    new = driver.find_element_by_id("cn.soulapp.android:id/tvNews")
    new.click()
    # os.popen('adb shell input tap %d %d'% params['recommend'])
    with open('rebootRecords.txt','a', encoding='utf-8') as f:
        f.write('于 %s 重启Soul\n' % time.ctime())
    time.sleep(2)

def roll_adb(swipe,stop):
    os.popen(swipe)
    time.sleep(0.28)
    os.popen(stop)
    time.sleep(0.5)

def roll_appium():
    up = params['roll_range'][2]
    axis = params['axis']
    down = params['roll_range'][1]
    driver.swipe(axis, down, axis, up)
class soulDatabase():
    def __init__(self):
        self.db = pymysql.connect("localhost", "root", "tyc1234","soul_info")
        self.cur = self.db.cursor()

    def write(self, data):
        sql = """insert into souldata(planet, time, content, location) values ("%s", "%s", "%s", "%s");""" % data
        try:
            self.cur.execute(sql)
            self.cur.connection.commit()
            print("%s——[%s]"%(data[3],data[0]))
        except (pymysql.InternalError, pymysql.ProgrammingError) as e:
            try:
                sql = """insert into souldata(planet, time, content, location) values ("%s", "%s", "%s", "%s");""" % (data[0], data[1], '',data[3])
                self.cur.execute(sql)
                self.cur.connection.commit()
                print("%s——[%s]"%(data[3],data[0]))
            except (pymysql.InternalError, pymysql.ProgrammingError) as e:
                print("格式出错：" + str(e))

def filter_content_n_save(driver):
    posts = driver.find_elements_by_id("cn.soulapp.android:id/item_post_all")
    @Timeout()
    def get_post_details(post):
        def updatestatus(status):
            def verifytimeformat(timedata):
                if timedata[5] < 0:
                    timedata[5] += 60
                    timedata[4] -= 1
                if timedata[4] < 0:
                    timedata[4] += 60
                    timedata[3] -= 1
                if timedata[3] < 0:
                    timedata[3] += 24
                    timedata[2] -= 1
                if timedata[2] < 0:
                    timedata[2] = 0
                return tuple(timedata)

            c = list(time.localtime())
            if "秒" in status:
                s = int(re.search('\d{1,2}',status).group())
                c[5] = c[5] - s
                c = verifytimeformat(c)
                finaltime = time.strftime("%Y-%m-%d %H:%M:%S", c)
                return finaltime
            elif "分" in status:
                s = int(re.search('\d{1,2}',status).group())
                c[5] = c[5] - s
                c = verifytimeformat(c)
                finaltime = time.strftime("%Y-%m-%d %H:%M:%S", c)
                return finaltime
            else:
                finaltime = time.strftime("%Y-%m-%d %H:%M:%S", tuple(c))
                return finaltime
        try:
            position = post.find_element_by_id("cn.soulapp.android:id/square_item_location").text
        except (NoSuchElementException, StaleElementReferenceException) as e:
            return None
        try:
            planet = post.find_element_by_id("cn.soulapp.android:id/tv_title").text.replace('来自','')
        except (NoSuchElementException, StaleElementReferenceException) as e:
            return None
        try:
            status = post.find_element_by_id("cn.soulapp.android:id/post_status").text
            postime = updatestatus(status)
        except (NoSuchElementException, StaleElementReferenceException) as e:
            return None
        try:
            status = post.find_element_by_id("cn.soulapp.android:id/post_status").text
        except (NoSuchElementException, StaleElementReferenceException) as e:
            return None
        try:
            content = post.find_element_by_id("cn.soulapp.android:id/square_item_text").text
        except (NoSuchElementException, StaleElementReferenceException) as e:
            return ''
        postinfo = (planet, postime, content, position)
        return postinfo

    for post in posts:
        postinfo = get_post_details(post)
        if postinfo:
            dup_or_not = SD.verify_if_duplicate(soulDB.cur, postinfo)
            if not dup_or_not:
                soulDB.write(postinfo)
            else:
                print('已存在重复数据，跳过——%s——[%s]'%(postinfo[3], postinfo[0]))

# def restart_script():
#     python = sys.executable
#     pass

if __name__ == "__main__":
    while True:
        try:
            # os.popen('adb shell am force-stop cn.soulapp.android')
            soulDB = soulDatabase()
            basepath = basepath_pc
            DesiredCapabilities = {
                                   "platformName": "Android",
                                   "deviceName": "VOG-AL10",
                                   "appPackage": "cn.soulapp.android",
                                   "appActivity": "cn.soulapp.android.ui.splash.SplashActivity",
                                   "noReset": "true",
                                   "fullReset": "false",
                                   "newCommandTimeout": "3600",
                                   # "systemPort": "8210",
                                   }
            # "appActivity": "cn.soulapp.android.splash.SplashActivity"
            # "appActivity": "cn.soulapp.android.ui.splash.SplashActivity",
            print('初始化...')
            driver = webdriver.Remote('http://localhost:4723/wd/hub', DesiredCapabilities)
            # driver = webdriver.Remote('http://localhost:62001/wd/hub', DesiredCapabilities)
            print('等待加载页面')
            time.sleep(10)
            params = initiate(basepath)
            error = 0
            count = 0
            c = time.time()
            swipe = 'adb shell input swipe %d %d %d %d 100'% params['roll_range']
            stop = 'adb shell input tap %d %d'% params['loading']
            blank_page = []
            # try:
            while True:
                try:
                    # if count % 10 == 0:
                    #     print('已点< %d >赞 [累计耗时：%f ]' % (count, (time.time() - c)))
                    try:
                        # start = time.time()
                        elements = tap_position()
                        # verify = verify_page()
                        # print('获取点赞耗时：%f' % (time.time() - start))
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
                    # count += like_adb(elements)
                    try:
                        if elements:
                            # SD.verify_if_duplicate
                            filter_content_n_save(driver)
                    except WebDriverException as e:
                        e = str(e)
                        with open('logs.txt','a', encoding='utf-8') as f:
                            f.write('%s 连接断开，详情：%s\n' % (time.ctime(), e))
                        driver = webdriver.Remote('http://localhost:4723/wd/hub', DesiredCapabilities)
                        time.sleep(10)
                        params = initiate(basepath)
                        continue
                    # count += like2(elements)
                    # if count >= goals:
                    #     break
                    roll_adb(swipe,stop)
                    # roll_appium()
                except KeyboardInterrupt as e:
                    print("*"*60+"\n\n\n")
                    print('Holding Program, press "enter" to continue, input"quit" to end program')
                    print("\n\n\n"+ "*"*60)
                    choice = input('------------------------quit or continue >>>')
                    if choice == 'quit':
                        raise KeyboardInterrupt
                    else:
                        error = 0
                        roll_adb(swipe,stop)
                        continue
                # finally:
                #     cc = time.time()
                #     used_time = round(cc - c, 2)
                #     print('点赞 %d 次, 用时 %f 秒' % (count, used_time))
                #     with open('点赞次数.txt','w') as f:
                #         text = '点赞 %d 次，用时 %f 秒, 平均每分钟 %d 赞' % (count, used_time, round(60/(used_time/count), 2))
                #         f.write(text)
        except KeyboardInterrupt:
            break
        except:
            time.sleep(1)
            # soulDB.db.close()
            with open('代码重启记录.txt','a',encoding='utf-8') as f:
                restart_info = "代码于 %s 重启一次\n"%time.ctime()
                f.write(restart_info)
