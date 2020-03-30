"""
Use this module to analyze soulers' infomation that have been
collected in the process of tapping likes.
Then all infomation will saved in database
"""
import os
import re
from datetime import datetime
import json
import pymysql

def filtering(file, pattern):
    """Search in <file> using pre-compiled regex expression <pattern>
       Return True if the pattern is found
       Return False if not found"""
    with open(file,'r',encoding='utf-8') as f:
        content = f.read()
    try:
        res = pattern.search(content).group()
        return True
    except AttributeError as e:
        return False

def update_path():
    """update files that exist in the <base_path>
       return a list containing all absolute path of each file"""
    base_path = os.getcwd() +'\\Tempfiles'
    files = os.listdir(base_path)
    path = [os.path.join(base_path, _) for _ in files]
    return path

def filterDate():
    """Filter files in the <base_path>
       1. The 'loading' page will be filtered out
       2. The 'wrong' page will be filtered out, wrong pages include mistouch when tapping likes
       3. The 'blank' page will be filtered out, blank pages are pages without likes button
       4. Retun an updated file path list unpon finishing the above process
       The path list will contain absolute path of all files in the filtered <base_path>"""
    path = update_path()
    pattern_loading = re.compile('加载中\.\.\.')
    loading = [filtering(_, pattern_loading) for _ in path]
    [os.remove(path[_]) for _ in range(len(loading)) if loading[_]]

    path = update_path()
    pattern_square = re.compile('main_tab_square')
    square = [filtering(_, pattern_square) for _ in path]
    [os.remove(path[_]) for _ in range(len(square)) if not square[_]]

    path = update_path()
    pattern_like = re.compile('android:id/iv_like')
    like = [filtering(_, pattern_like) for _ in path]
    [os.remove(path[_]) for _ in range(len(like)) if not like[_]]

    return update_path()

def planet_info(file):
    def split_c(content):
        """Split <content> into parts according to 'Planet' info """
        index = [] # to store the positions
        temp = (0,0) # use temp to mark position of each key-word
        while True:
            try:
                t = re.search('来自.+?星球', content[temp[1]:]).span()
                index.append(temp[1]+ t[0]) # get the posion of the first 'planet'
                temp = (temp[1] + t[0], temp[1] + t[1]) # update temp to mark the position and use it as a new start
                # temp = re.search('来自.+?星球', content).span()
            except AttributeError as e:
                break #jump out when reachs the end
        parts = [] # slice content into parts
        for i in range(len(index)):
            try:
                c = content[index[i]:index[i+1]]
                parts.append(c)
            except IndexError as e:
                c = content[index[i]:]
                parts.append(c)
        return parts

    def analyze(part):
        # 需要获取的星球内容如下：
        # 1, 来自哪个星球
        # 2, 内容发布时间
        # 3，发布内容-可为无
        # 4, 发布内容标签-可为无
        # 5, 发布地址-可为无
        def gtime(part):
            temp = re.search('text=".+?"', part).span()
            target = part[temp[0]+5:temp[1]].strip('""')
            if '分钟' in target:
                c = int(target.split('分钟')[0])
                d = int(ref_time[14:16]) - c
                final = ref_time.replace(ref_time[14:16],'%02d'%d)
            elif '秒' in target:
                c = int(target.split('秒')[0])
                d = int(ref_time[17:]) - c
                final = ref_time.replace(ref_time[17:],'%02d'%d)
            else:
                final = ref_time
            return final

        def gplanet(part):
            p = part.find('"')
            return part[:p].strip('来自')

        def gcontent(part):
            temp = re.search('container_content".+?text=".+?" resource-id="cn\.soulapp\.android:id/square_item_text"', part)
            try:
                content = temp.group()[re.search('text="', temp.group()).span()[1]:].split('"')[0]
            except AttributeError as e:
                content = ''
            return content

        def gtag(part):
            temp = re.findall('text="#.+?"',part)
            tags = [_.split('"')[1] for _ in temp]
            return tags

        def glocation(part):
            try:
                temp = re.search('resource-id="cn\.soulapp\.android:id/square_item_location', part).span()
                c = part[temp[0] - 20: temp[0]]
                location = c[re.search('text="', c).span()[1]:].split('"')[0]
            except AttributeError as e:
                location = 'NONE'
            return location

        info = {}
        ref_time = filectime
        info['planet'] = gplanet(part)
        info['time'] = gtime(part)
        info['content'] = gcontent(part)
        info['tags'] = gtag(part)
        info['location'] = glocation(part)
        return info
    # 获取文件创建时间
    filectime = datetime.fromtimestamp(os.path.getctime(file)).strftime('%Y-%m-%d %H:%M:%S')
    with open(file,'r',encoding='utf-8') as f:
        content = f.read()
    sliced = split_c(content) # slice content into parts
    info = [analyze(_) for _ in sliced] # analyze each parts and return alist with dict structured infomation
    return info

def extractInfo(info):
    """To format the infomation"""
    temp = [v for k, v in info.items()]
    try:
        re.search('2020-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', temp[1]).group()
    except AttributeError as e:
        temp[1] = "0000-00-00 00:00:00"
    if not temp[2]:
        temp[2] = "NONE"
    if not temp[3]:
        temp[3] = "NONE"
    else:
        temp[3] = ','.join(temp[3])
    return temp

def write_db(soulers):
    # db = pymysql.connect(adress, username, passwaord, database)
    username = input('database username:  ')
    password = input('database password:  ')
    db = pymysql.connect('localhost', username, password)
    cursor = db.cursor()
    create_database = """CREATE DATABASE IF NOT EXISTS soul_info"""
    create_table = """CREATE TABLE IF NOT EXISTS soulers(
                      id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                      planet VARCHAR(100),
                      time DATETIME,
                      content TEXT,
                      tag TEXT,
                      location VARCHAR(100),
                      PRIMARY KEY(id));
                      """
    cursor.execute(create_database)
    cursor.execute("use soul_info")
    cursor.execute(create_table)
    print('写入数据到数据库')
    for i in soulers:
        # print('写入第 %d 条数据到数据库' % (i +1))
        temp = extractInfo(i)
        # temp.insert(0, i+1)
        try:
            sql_1 = '''INSERT INTO soulers(planet, time, content, tag, location) VALUES ("%s", "%s", "%s", "%s", "%s")'''% tuple(temp)
            cursor.execute(sql_1)
        except pymysql.err.InternalError as e:
            print('出错了...', e)
            break
    print('成功写入 %d 条数据到数据库' % len(soulers))
    cursor.connection.commit()
    db.close()

def preserve_data():
    filtered = filterDate()
    soulers = []
    print('共有 %d 个文件\n\n'%len(filtered))
    print('分析文件..')
    for i in filtered:
        # print('分析第 %d 个文件' % i)
        info = planet_info(i)
        soulers.extend(info)
    print('分析完成...')
    with open('soulers.js','w',encoding='utf-8') as f:
        temp = json.dumps(soulers)
        f.write(temp)
    write_db(soulers)
    return soulers

def remove_files():
    paths = update_path()
    remove = [os.remove(_) for _ in paths]

if __name__ == "__main__":
    soulers  = preserve_data()
