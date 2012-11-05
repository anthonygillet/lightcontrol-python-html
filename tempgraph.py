#! /usr/bin/python
import time
import socket
import MySQLdb
from datetime import datetime, timedelta

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import cgi, cgitb
cgitb.enable()

print "Content-Type: text/html"

form = cgi.FieldStorage()

date = datetime.today()
if ("date" in form):
    date = datetime.fromtimestamp(float(form["date"].value))
    
dateIsToday = True
if (date.month != datetime.today().month or
    date.day != datetime.today().day or
    date.year != datetime.today().year):
    dateIsToday = False
    
db_conn = MySQLdb.Connect(host="localhost", user="", passwd="", db="lights")
db_cur = db_conn.cursor()


print """
<html>
  <head>
    <style type="text/css">
        body {
    	    background: #FFFFFF;
    	    font-family: Verdana, Chicago, sans-serif;
    	    font-size: 11px;
    	    font-weight: normal;
    	}
    	
    	h1 {
        	font-size: 30px;
        	font-weight: bold;
        	margin: 0px;
        	margin-left: auto;
        	margin-right: auto;
        	padding: 0px;
        	text-align: center;
        }
    </style>
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
    google.load("visualization", "1", {packages:["corechart"]});
    google.setOnLoadCallback(drawChart);
    function drawChart()
    {
        var tempData = new google.visualization.DataTable();
        tempData.addColumn('string', 'Time');
        tempData.addColumn('number', 'Temperature');
        tempData.addColumn('number', 'Cool Setpoint');
        tempData.addColumn('number', 'Heat Setpoint');
        tempData.addColumn('number', 'A/C status');
        tempData.addColumn('number', 'Heat status');
        
        tempData.addRows([
"""

if ("all" in form):
    db_cur.execute("""SELECT unix_timestamp(timestamp),  
                             temp,
                             heat_setpoint,
                             cool_setpoint,
                             heat_status,
                             cool_status
                      FROM temperature_data
                      ORDER BY id """)
else:
    db_cur.execute("""SELECT unix_timestamp(timestamp),  
                             temp,
                             heat_setpoint,
                             cool_setpoint,
                             heat_status,
                             cool_status
                      FROM temperature_data
                      WHERE month(timestamp) = %s AND
                            day(timestamp) = %s AND
                            year(timestamp) = %s
                      ORDER BY id """,
                      (date.month, date.day, date.year))
res = db_cur.fetchone()

while (res is not None):
    
    timestamp = datetime.fromtimestamp(res[0])
    temp = res[1]
    heat_setpoint = res[2]
    cool_setpoint = res[3]
    heat_status = res[4]
    cool_status = res[5]
    
    if (temp == 0):
        temp = "null"
    if (heat_setpoint == 0):
        heat_setpoint = "null"
    if (cool_setpoint == 0):
        cool_setpoint = "null"
    if (heat_status == 0):
        heat_status = "null"
    if (cool_status == 0):
        cool_status = "null"
    
    print "          [\"%s\", %s, %s, %s, %s, %s]," % (timestamp.strftime("%I:%M %p"), temp, cool_setpoint, heat_setpoint, heat_status, cool_status)
    res = db_cur.fetchone()

print """
        ]);
        
        var tempOptions = {'width':1000,
                           'height':800,
                           chartArea:{left:50,top:0,width:"800",height:"720"},
                           fontName:'Verdana',
                           fontSize:11,
                           'colors':['black', 'blue', 'red', 'blue', 'red'],
                           'curveType':'function',
                           'vAxis':{'title':'Temp (F)', 'format':'#', 'viewWindowMode':'explicit', 'viewWindow':{'max':81, 'min':64}},
                           'hAxis':{'title':'Time'},
                           'areaOpacity':0,
                           'series': {3:{'areaOpacity':0.1, 'lineWidth':0, 'visibleInLegend': false}, 
                                      4:{'areaOpacity':0.1, 'lineWidth':0, 'visibleInLegend': false}},
                           };
        
        var tempChart = new google.visualization.AreaChart(document.getElementById('temp_chart_div'));
        tempChart.draw(tempData, tempOptions);

        /*
        var statusData = new google.visualization.DataTable();
        statusData.addColumn('string', 'Time');
        statusData.addColumn('number', 'Status');
        
        statusData.addRows([
            ["7:00", null],
            ["7:01", 1],
            ["7:02", 1],
            ["7:03", null],
        ]);
        
        var statusOptions = {'title':'Temperature',
                           'width':800,
                           'height':100,
                           'colors':['black', 'blue', 'red'],
                           'curveType':'function',
                           'vAxis':{'title':'Temp (F)', 'format':'#'}
                           };
        
        var statusChart = new google.visualization.LineChart(document.getElementById('status_chart_div'));
        statusChart.draw(statusData, statusOptions);
        */
    }
    </script>
  </head>

  <body>
    <center>
    <br /> <br />
"""
yesterday = date - timedelta(days = 1)
tomorrow = date + timedelta(days = 1)


if ("all" in form):
    print "<h1>All Data</h1>"
    print "<a href=\"?\">back to today</a>"
else:
    print "<h1>"
    print "<a href=\"?date=" + str(int(time.mktime(yesterday.timetuple()))) + "\">&lt;</a>"
    print "      &nbsp;&nbsp;" + date.strftime("%B %d, %Y") + "&nbsp;&nbsp;"
    if (dateIsToday != True):
        print "<a href=\"?date=" + str(int(time.mktime(tomorrow.timetuple()))) + "\">&gt;</a>"
    else:
        print "&gt;"
    print "</h1>"
    print "<a href=\"?all=yes\">show all data</a>"


print """
        <br /><br />
        <div id="temp_chart_div"></div>
    </center>
  </body>
</html>

"""

db_cur.close()
db_conn.close()
exit()
