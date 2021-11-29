

import sqlite3


def create_stocks(args):
    

    conn = sqlite3.connect('../stockbase/stocks.db')
    print ("Opened database successfully")
    c = conn.cursor()
    c.execute(r'''CREATE TABLE STOCKS
        (ID INT PRIMARY KEY     NOT NULL,
        NAME           CHAR(50)    NOT NULL,
        NUMBER            INT     NOT NULL,
        DESCRIPTION        CHAR(50),
        PRICE         REAL,
        MARKETVALUE         REAL);''')
    print("Table created successfully")
    conn.commit()
    conn.close()



def import_stock_names():

    shfile = r'C:\new_jyplug\T0002\hq_cache\shm.tnf'
    szfile = r'C:\new_jyplug\T0002\hq_cache\szm.tnf'

    files = [shfile, szfile]

    conn = sqlite3.connect('../stockbase/stocks.db')
    print ("Opened database successfully")

    conn.execute('''delete from stocks''')
    conn.commit()
    

    index = 0;
    for file in files:
        print(file)
 
        fs=open(file,"rb")
        fs.read(50)

        while True:
            data = fs.read(314)
            #print(data)
            if len(data)==0:
                break
            try:
                index = index + 1
                number = int(data[0:6])
                name = str.strip(str(data[23:35], encoding='gb2312'), '\0 ' )

                if number > 600000 and number < 699999 or number < 10000 or number > 300000 and number < 399999:
                    sqlstr = r"INSERT INTO STOCKS (NAME,NUMBER) VALUES('{0}',{1})".format(name, number)
                    conn.execute(sqlstr)
                
            except Exception as ex:
                print(name, number)
                print(ex)
                pass
        fs.close()
        print(index)

    conn.commit()

    conn.close()
    pass


def stock_db_test():
    conn = sqlite3.connect('../stockbase/stocks.db')
    print ("Opened database successfully")

    try:
        
        #sqlstr = r"INSERT INTO STOCKS (NAME,NUMBER) VALUES ('{0}',{1})".format(name, number)
        sqlstr = r"INSERT INTO STOCKS (NAME,NUMBER) VALUES ('上证指数',999999)"
        print(sqlstr)
        conn.execute(sqlstr)
        sqlstr = r"INSERT INTO STOCKS (NAME,NUMBER) VALUES ('创业板指',399006)"
        print(sqlstr)
        conn.execute(sqlstr)
        conn.commit()

        d = conn.execute('select * from stocks')
        print(d.fetchall())
        
    except Exception as ex:
        print(ex)
        pass

if __name__ == "__main__":

    import_stock_names()
    
    stock_db_test()
    pass