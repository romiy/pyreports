import pyodbc
import re

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=PC-TP3-02;'
                      'Database=BR_RK7_MAIN;'
                      'Trusted_Connection=yes;')

#print('Connected')
#print('Input dataset code:')
dscode = 126

cursor = conn.cursor()
cursor.execute('select cast(cast(sqlquery as varbinary(max)) as nvarchar(max)) as sqlquery from PLG_IR_DATASETS where code = '+str(dscode))
  
for row in cursor:
    qry = str(row[0])
    x = re.findall("\:[a-zA-Z0-9_]+",str(row[0]))

y = dict.fromkeys(x)

for a in y:
    if a.upper() == ":USE_ALT_LANG":
        y[a] = "/*:USE_ALT_LANG*/0"
    if a.upper() == ":CLASS":
        y[a] = "/*:CLASS*/select guidstring from classificatorgroups where sifr = 10 and numingroup = 0"
    if a.upper() == ":RESTAURANT":
        y[a] = "/*:RESTAURANT*/select guidstring from restaurants where code = 26"
    if a.upper() == ":DATE1":
        y[a] = "'01.01.2019'"
    if a.upper() == ":DATE2":
        y[a] = "'01.01.2020'"

for a in y:
    qry = qry.replace(str(a),str(y[a]))

#print(y)    
#print(qry)

cursor.execute(qry)

for b in cursor.description:
    print(b[0])

for row in cursor:
    print(row)

input()
