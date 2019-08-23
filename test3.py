import pyodbc
import re

from http.server import ThreadingHTTPServer, CGIHTTPRequestHandler
from urllib.parse import parse_qs

class myHandler(CGIHTTPRequestHandler):
    def do_GET(self):
        # first send http OK message
        self.send_response(200)
        self.send_header("Content-type","text/html")
        self.end_headers()

        # html message header
        self.wfile.write("<html><head><meta charset=""UTF-8""><style>".encode("utf-8"))
        self.wfile.write("* { font-size: 100%; font-family: Verdana;}".encode("utf-8"))
        self.wfile.write("h1 { font-size: 200%;}".encode("utf-8"))
        self.wfile.write("h2 { font-size: 150%;}".encode("utf-8"))
        self.wfile.write("h3 { font-size: 120%;}".encode("utf-8"))
        self.wfile.write("</style></head><body><h1>R_Keeper</h1>".encode("utf-8"))

        # request parameters parsing
        db = parse_qs(self.path)['/?dbname']
        ds = parse_qs(self.path)['dscode']
        r  = parse_qs(self.path)['rcode']
        d1 = parse_qs(self.path)['d1']
        d2 = parse_qs(self.path)['d2']
        c  = parse_qs(self.path)['class']

        # connect to database if it's name specified
        if len(str(db[0])) != 0: conn = pyodbc.connect('Driver={SQL Server};Server=localhost;Database='+str(db[0])+';Trusted_Connection=yes;')
        else: return

        # get query text
        cursor = conn.cursor()
        cursor.execute('select name, cast(cast(sqlquery as varbinary(max)) as nvarchar(max)) as sqlquery from PLG_IR_DATASETS where code = '+str(ds[0]))

        for row in cursor:
            self.wfile.write("<h2>".encode("utf-8"))
            self.wfile.write(bytes(row.name,"utf-8"))
            self.wfile.write("</h2>".encode("utf-8"))
            self.wfile.write("<h3>".encode("utf-8"))
            self.wfile.write(bytes(str(d1[0])+" - "+str(d2[0]),"utf-8"))
            self.wfile.write("</h3>".encode("utf-8"))
            qry = str(row.sqlquery)
            qry = qry.replace('TXTTRANSLATE','/*TXTTRANSLATE*/')
            qry = qry.replace('txttranslate','/*TXTTRANSLATE*/')            
            x = re.findall(":[a-zA-Z0-9_]+",qry)

        # parse query text for parameters
        y = dict.fromkeys(x)

        for a in y:
            if a.upper() == ":USE_ALT_LANG":
                y[a] = "/*:USE_ALT_LANG*/0"
            if a.upper() == ":CLASS":
                if len(str(c[0])) != 0 : y[a] = "/*:CLASS*/select guidstring from classificatorgroups where sifr = "+str(c[0])+" and numingroup = 0"
                else: y[a] = "/*:CLASS*/select guidstring from classificatorgroups where sifr = 10 and numingroup = 0"                
            if a.upper() == ":RESTAURANT":
                y[a] = "/*:RESTAURANT*/select guidstring from restaurants where code = "+str(r[0])
            if a.upper() == ":DATE1":
                if len(str(d1[0])) != 0 : y[a] = "'"+str(d1[0])+"'"
                else: y[a] = "'01.01.2000'"
            if a.upper() == ":DATE2":
                if len(str(d2[0])) != 0 : y[a] = "'"+str(d2[0])+"'"
                else: y[a] = "'01.01.2100'"

        # and replace query parameters with request parameters or defaults
        for a in y:
            qry = qry.replace(str(a),str(y[a]))

        # execute query
        #print(qry)
        cursor.execute(qry)

        # output query results to html message
        self.wfile.write("<table border=""1""><tr>".encode("utf-8"))
        
        for b in cursor.description:
            self.wfile.write(bytes("<td align=""center""><b>"+b[0]+"</b></td>","utf-8"))
        self.wfile.write("</tr>".encode("utf-8"))

        for row in cursor:
            self.wfile.write("<tr>".encode("utf-8"))
            for field in row:
                self.wfile.write(bytes("<td>"+str(field)+"</td>","utf-8"))
            self.wfile.write("</tr>".encode("utf-8"))

        # finishing, closing and going home
        cursor.close
        conn.close
        
        self.wfile.write("</table>".encode("utf-8"))
        self.wfile.write("</body></html>".encode("utf-8"))
        return

handler = myHandler

try:
    httpd = ThreadingHTTPServer(("", 8000), handler)
    print("Server working on 8000")
    httpd.serve_forever()

except KeyboardInterrupt:
    print("^C received, shutting down the web server")
    httpd.shutdown()