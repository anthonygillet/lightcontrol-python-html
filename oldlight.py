#! /usr/bin/python
import time
import socket
import MySQLdb

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import cgi, cgitb
cgitb.enable()

HOST = "localhost"
PORT = 1234

db_conn = MySQLdb.Connect(host="localhost", user="", passwd="", db="lights")
db_cur = db_conn.cursor()

data = ""
form = cgi.FieldStorage()

error = False
ui = "yes"
if "ui" in form:
    ui = form["ui"].value

print "Content-Type: text/html\n\n"

command = ""
if "cmd" in form:
    command = form["cmd"].value

if (command == "sections"):
    db_cur.execute("""SELECT name FROM sections ORDER BY id""")
    res = db_cur.fetchone()
    while (res is not None):
        print res[0]
        res = db_cur.fetchone()
    db_cur.close()
    db_conn.close()
    exit()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))

if (command == "status"):
    db_cur.execute("""SELECT name, deviceId, section FROM devices WHERE responder=1 AND thermostat=0 ORDER BY section, name""")
    res = db_cur.fetchone()
    while (res is not None):
        s.send("status." + res[1] + "\r\n")
        data = s.recv(1024)
        result = data.strip()
        if (result[:5] == "error"):
            result = "error"
        print res[0] + '|' + res[1] + '|' + str(res[2]) + '|' + result
        res = db_cur.fetchone()
        if (res is not None):
            time.sleep(0.5)
    db_cur.close()
    db_conn.close()
    s.close()
    exit()
elif (command == "temp_status"):
    db_cur.execute("""SELECT name, deviceId FROM devices WHERE responder=1 AND thermostat=1 ORDER BY id""")
    res = db_cur.fetchone()
    while (res is not None):
        # Get ambient
        s.send("temp_get_ambient." + res[1] + "\r\n")
        data = s.recv(1024)
        ambient = data.strip()
        if (ambient[:5] == "error"):
            ambient = "error"
        time.sleep(0.5)
        
        # Get mode
        s.send("temp_get_mode." + res[1] + "\r\n")
        data = s.recv(1024)
        mode = data.strip()
        if (mode[:5] == "error"):
            mode = "error"
        time.sleep(0.5)
        
        # Get setpoint(s), based on mode
        heatSetpoint = -1
        coolSetpoint = -1
        if (mode != "error"):
            s.send("temp_get_setpoint." + res[1] + "." + mode + "\r\n")
            data = s.recv(1024)
            setpoint = data.strip()
            if (setpoint[:5] == "error"):
                heatSetpoint = "error"
                coolSetpoint = "error"
            elif (mode == "heat" or mode == "prog_heat"):
                heatSetpoint = setpoint
                coolSetpoint = -1
            elif (mode == "cool" or mode == "prog_cool"):
                heatSetpoint = -1
                coolSetpoint = setpoint
            elif (mode == "auto" or mode == "prog_auto"):
                setpoints = setpoint.split('.')
                heatSetpoint = setpoints[0]
                coolSetpoint = setpoints[1]

        print res[0] + '|' + res[1] + '|' + str(ambient) + '|' + str(mode) + '|' + str(coolSetpoint) + '|' + str(heatSetpoint)
        res = db_cur.fetchone()
        if (res is not None):
            time.sleep(1)

    db_cur.close()
    db_conn.close()
    s.close()
    exit()
elif ("device" in form):
    if (command == "on" or command == "off"):
        db_cur.execute("""SELECT multi_way FROM devices WHERE deviceId=%s""", form["device"].value)
        res = db_cur.fetchone()
        if (res is not None and res[0] == 1):
            command += "group"
    command += "." + form["device"].value
    if ("level" in form):
        command += "." + form["level"].value
    s.send("" + command + "\r\n")
    data = s.recv(1024)
    result = data.strip()
    if (result[:5] == "error"):
        error = True
    if (ui == "no"):
        print result
        db_cur.close()
        db_conn.close()
        s.close()
        exit()

print """
<html>
<head>
<meta name="viewport" content="width=320,user-scalable=false" />
<title>Light Control</title>
</head>
<body>

<a href="/"><h2>Light Control</h2></a>
<br />
"""

if (error):
    print '<font color="red">' + result + '</font><br /><br />' 

db_cur.execute("""SELECT name, deviceId FROM devices WHERE responder=1 AND thermostat=0 ORDER BY section, name""")
res = db_cur.fetchone()

print '<table><tr>'
print '<td><input type="button" value="X10 1-On" name="x10-1-on" onClick="window.location=\'?cmd=x10on&device=1\'" /></td>'
print '<td><input type="button" value="X10 2-On" name="x10-1-on" onClick="window.location=\'?cmd=x10on&device=2\'" /></td>'
print '<td><input type="button" value="X10 3-On" name="x10-1-on" onClick="window.location=\'?cmd=x10on&device=3\'" /></td>'
print '<td><input type="button" value="X10 4-On" name="x10-1-on" onClick="window.location=\'?cmd=x10on&device=4\'" /></td>'
print '<td><input type="button" value="X10 5-On" name="x10-1-on" onClick="window.location=\'?cmd=x10on&device=5\'" /></td>'
print '<td><input type="button" value="X10 6-On" name="x10-1-on" onClick="window.location=\'?cmd=x10on&device=6\'" /></td>'
print '</tr><tr>'
print '<td><input type="button" value="X10 1-Off" name="x10-1-off" onClick="window.location=\'?cmd=x10off&device=1\'" /></td>'
print '<td><input type="button" value="X10 2-Off" name="x10-1-off" onClick="window.location=\'?cmd=x10off&device=2\'" /></td>'
print '<td><input type="button" value="X10 3-Off" name="x10-1-off" onClick="window.location=\'?cmd=x10off&device=3\'" /></td>'
print '<td><input type="button" value="X10 4-Off" name="x10-1-off" onClick="window.location=\'?cmd=x10off&device=4\'" /></td>'
print '<td><input type="button" value="X10 5-Off" name="x10-1-off" onClick="window.location=\'?cmd=x10off&device=5\'" /></td>'
print '<td><input type="button" value="X10 6-Off" name="x10-1-off" onClick="window.location=\'?cmd=x10off&device=6\'" /></td>'
print '</tr></table>'
print '<br />'

while (res is not None):
    
    print '<b>' + res[0] + '</b><br />'
    print '<div>'
    print '<form method="get" name="light">'
    print '<input type="button" value="Turn On" name="on" onClick="window.location=\'?cmd=on&device=%s\'" />' % res[1]
    print '&nbsp; | &nbsp;'
    print '<input type="button" value="Turn Off" name="off" onClick="window.location=\'?cmd=off&device=%s\'" />' % res[1]
    print '&nbsp; | &nbsp;'
    print 'Level&nbsp;'
    
    s.send("status." + res[1] + "\r\n")
    data = s.recv(1024)
    status = data.strip()
    
    if (status[:5] == "error"):
        print '<input type="text" name="level" size="3" value="?"/>'
        print '<font color="red">' + status + '</font>'
    else:
        print '<input type="text" name="level" size="3" value="' + status + '"/>'
    
    print '<br />'
    print '<input type="button" value="Turn On Slowly" name="onslow" onClick="window.location=\'?cmd=slow_on&device=%s\'" />' % res[1]
    print '&nbsp; | &nbsp;'
    print '<input type="button" value="Turn Off Slowly" name="offslow" onClick="window.location=\'?cmd=slow_off&device=%s\'" />' % res[1]
    print '<input type="hidden" name="cmd" value="on"/>'
    print '<input type="hidden" name="device" value="' + res[1] + '"/>'
    print '</form>'
    print '</div>'
    print '<br />'
    
    res = db_cur.fetchone()
    if (res is not None):
        time.sleep(0.7)

print """
</body>
</html>
"""

db_cur.close()
db_conn.close()
s.close()
