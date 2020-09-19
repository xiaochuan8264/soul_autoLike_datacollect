import pymysql

def delete_duplicates(cur):
    def deletequery(duplicates):
        query = """delete from souldata where"""
        left = len(duplicates)
        for duplicate in duplicates:
            temp = " no='%s'"%duplicate[0]
            left -= 1
            if left == 0:
                query = query + temp + ";"
                break
            else:
                query = query + temp + " or"
        return query

    # db = pymysql.connect('localhost', 'root', 'tyc1234', 'soul_info')
    # cur = db.cursor()
    sql = "select planet, content, location from souldata;"
    cur.execute(sql)
    alldata = cur.fetchall()
    unique = set(alldata)
    count = [alldata.count(_) for _ in unique]
    res = list(zip(count, unique))
    final = [_ for _ in res if _[0] != 1]
    for each_duplicate in final:
        query = """select * from souldata
                   where
                   planet="%s" and content="%s" and location="%s";
                   """%each_duplicate[1]
        cur.execute(query)
        duplicates = cur.fetchall()
        duplicates = duplicates[1:]
        del_query = deletequery(duplicates)
        cur.execute(del_query)
        cur.connection.commit()
        print("删除%d条重复数据.."%len(duplicates))

def verify_if_duplicate(cur, single_data):
    planet = single_data[0]
    content = single_data[2]
    location = single_data[3]
    sql = """select planet, content, location from souldata where planet="%s" and content="%s" and location="%s";"""%(planet, content, location)
    try:
        t = cur.execute(sql)
        if t == 0 or t == 1:
            return False
        else:
            return True
    except (pymysql.InternalError, pymysql.ProgrammingError, pymysql.OperationalError) as e:
        return False

if __name__ == "__main__":
    db = pymysql.connect('localhost', 'root', 'tyc1234', 'soul_info')
    cur = db.cursor()
