import os
import re
import time
import threading
import analyze_planet as ap

def get_params(path):
    """get all necessay PARAMS that are necessay for this program
       ref['roll_range'] = the range for swiping on the screen
       ref['square'] = the position of square
       ref['latest'] = the position of latest post of soulers"""
    print('初始化...')
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
    ref['latest'] = ((latest[0] + latest[2])//2 , (latest[1] + latest[3])//2)
    pattern5 = re.compile('main_tab_center_img.+?bounds="\[\d{1,4},\d{1,4}\]\[\d{1,4},\d{1,4}\]')
    main = re.findall('\d{1,4}', pattern5.search(content).group())
    main = [int(n) for n in main]
    ref['loading'] = ((main[0] + main[2])//2 , main[1] - 40)
    ref['main'] = ((main[0] + main[2])//2 , (main[1] + main[3])//2)
    return ref

def cal_xy(target):
    xy = re.findall(b'\d{1,4}', target)
    x = (int(xy[0]) + int(xy[2]))//2
    y = (int(xy[1]) + int(xy[3]))//2
    return (x, y)

def tap_position(file):
    global error
    # start = time.time()
    f = basepath + '\\' + file
    with open(f, 'rb') as f:
        content = f.read()
    # print('打开文件耗时：%f' %(time.time() - start))
    # while True:
    try:
        page = re.search(b'android:id/main_tab_square', content).group()
    except AttributeError as e:
        error += 1
        if error == 3:
            rebootApp(params)
            error = 0
            return [] #解决后面contents内容分析不匹配问题
        else:
            return []
    try:
        loading = re.search(b'cn\.soulapp\.android:id/footerText', content).group()
        error += 1
        time.sleep(1)
        if error == 3:
            rebootApp(params)
            error = 0
            return [] #解决后面contents内容分析不匹配问题
        else:
            return []
    except AttributeError as e:
        pass
    # strt = time.time()
    pattern = re.compile(b'resource-id="cn\.soulapp\.android:id/iv_like" .+? bounds="\[\d{1,4},\d{1,4}\]\[\d{1,4},\d{1,4}\]')
    # 重大问题：如果重启了APP，这里分析的还是旧的contents，这样子仍会产生坐标，会导致点错目标，解决办法：在前面就return，没出错只是侥幸，出错才是应该
    res = pattern.findall(content)
    # print('正则分析及查找耗时：%f' %(time.time() - start))
    return [cal_xy(n) for n in res]
    # return x_and_y
    # else:
    #     return []

def tap(xy):
    def click(x, y):
        os.popen('adb shell input tap %d %d'% (x, y))
        time.sleep(0.05)
    # count = 0
    # threads = []
    [click(n[0], n[1]) for n in xy]
    # threads = [threading.Thread(target=click, args=(n[0],n[1])) for n in xy]
    # [_.start() for _ in threads]
    # count += 1
        # threads.append(temp)
        # temp.start()
    # [_.join() for _ in threads]
    # time.sleep(0.1)
    return len(xy)

def rebootApp(params):
    os.popen('adb shell am force-stop cn.soulapp.android')
    time.sleep(0.5)
    os.popen('adb shell am start -n cn.soulapp.android/.ui.main.MainActivity')
    time.sleep(1)
    os.popen('adb shell input tap %d %d'% params['square'])
    time.sleep(0.1)
    os.popen('adb shell input tap %d %d'% params['square'])
    time.sleep(0.5)
    os.popen('adb shell input tap %d %d'% params['latest'])
    with open('rebootRecords.txt','a', encoding='utf-8') as f:
        f.write('于 %s 重启Soul\n' % time.ctime())
    time.sleep(2)

def roll(swipe,stop):
    os.popen(swipe)
    time.sleep(0.28)
    os.popen(stop)
    # time.sleep(0.1)
try:
    basepath = os.mkdir(os.getcwd()+'\\Tempfiles')
except FileExistsError as e:
    basepath = os.getcwd()+'\\Tempfiles'
params = get_params(basepath)
error = 0
count = 0
c = time.time()
swipe = 'adb shell input swipe %d %d %d %d 10'% params['roll_range']
stop = 'adb shell input tap %d %d'% params['loading']
i = 0
blank_page = []
goals = int(input('请输入目标点赞数[点赞数到达自动停止]：'))
try:
    while True:
        i += 1
        print('已点< %d >赞 [累计耗时：%f ]' % (count, (time.time() - c)))
        file = 'test_%03d.xml' % i
        dump = 'adb shell uiautomator dump /sdcard/00_Temp/%s' % file
        pull = 'adb pull /sdcard/00_Temp/%s %s\\%s' % (file, basepath, file)
        start = time.time()
        os.popen(dump).read()
        print('生成文件共耗时：%f\n-------------------------' % (time.time() - start))
        # start = time.time()
        os.popen(pull).read()
        # print('拉取文件共耗时：%f' % (time.time() - start))
        try:
            # start = time.time()
            taps = tap_position(file)
            # print('获取点赞耗时：%f' % (time.time() - start))
        except FileNotFoundError as e:
            with open('errorStatistic.txt','a',encoding='utf-8') as f:
                n = '%s 在 %s 拉取失败\n' %(file, time.ctime())
                f.write(n)
            roll(swipe, stop)
            continue
        blank_page.append(taps)
        if len(blank_page) > 10:
            verify = [1 if n else 0 for n in blank_page[-10:]]
            if not sum(verify):
                rebootApp(params)
                blank_page.clear()
                continue
            else:
                blank_page.clear()
        # if not taps:
        #     blank_page.append(taps)
        #     if len(blank_page) == 10:
        # start = time.time()
        count += tap(taps)
        # print('点赞耗时：%f' % (time.time() - start))
        time.sleep(0.2)
        start = time.time()
        if count >= goals:
            break
        #time.sleep(0.5)
        roll(swipe, stop)
        # print('滑动耗时：%f' % (time.time() - start))
        # time.sleep(0.1)

except KeyboardInterrupt as e:
    print('\n中断程序...')
finally:
    cc = time.time()
    used_time = round(cc - c, 2)
    print('点赞 %d 次, 用时 %d 秒' % (count, used_time))
    with open('点赞次数.txt','w') as f:
        text = '点赞 %d 次，用时 %d 秒, 平均每分钟 %d 赞' % (count, used_time, round(60/(used_time/count), 2))
        f.write(text)
    soulers = ap.preserve_data()
    ap.remove_files()
