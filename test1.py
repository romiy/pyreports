import pyodbc 
conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=PC-TP3-02;'
                      'Database=BR_RK7_MAIN;'
                      'Trusted_Connection=yes;')

print("Connected")

cursor = conn.cursor()
cursor.execute("select cast(cast(sqlquery as varbinary(max)) as nvarchar(max)) as sqlquery from PLG_IR_DATASETS where code = 126")

for row in cursor:
    ts = row[0]
    s = str(ts)
    s = s.replace(":USE_ALT_LANG","/*:USE_ALT_LANG*/0")
    
    tmpc = conn.cursor()
    tmpc.execute("select guidstring from restaurants where code = 26")
    for tr in tmpc:
        s = s.replace(":RESTAURANT","'"+str(tr[0])+"'")

    tmpc.execute("select guidstring from classificatorgroups where sifr = 10 and numingroup = 0")
    for tr in tmpc:
        s = s.replace(":CLASS","'"+str(tr[0]+"'"))

    tmpc.close

    s = s.replace(":date1","'2001-01-01'")
    s = s.replace(":date2","'2020-01-01'")

print(s)

cursor.execute(s)
for row in cursor:
    print(row)
    
cursor.close
conn.close
