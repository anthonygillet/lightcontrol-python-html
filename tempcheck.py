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

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))

# Get ambient
s.send("temp_get_ambient.11 BE 1E\r\n")
data = s.recv(1024)
temp = data.strip()
if (temp[:5] == "error"):
    temp = 0
time.sleep(0.5)

# Get mode
s.send("temp_get_mode.11 BE 1E\r\n")
data = s.recv(1024)
mode = data.strip()
if (mode[:5] == "error"):
    mode = "error"
time.sleep(0.5)

# Get setpoint(s), based on mode
heatSetpoint = 0
coolSetpoint = 0
if (mode != "error"):
    s.send("temp_get_setpoint.11 BE 1E." + mode + "\r\n")
    data = s.recv(1024)
    setpoint = data.strip()
    if (setpoint[:5] == "error"):
        heatSetpoint = "error"
        coolSetpoint = "error"
    elif (mode == "heat" or mode == "prog_heat"):
        heatSetpoint = setpoint
        coolSetpoint = 0
    elif (mode == "cool" or mode == "prog_cool"):
        heatSetpoint = 0
        coolSetpoint = setpoint
    elif (mode == "auto" or mode == "prog_auto"):
        setpoints = setpoint.split('.')
        heatSetpoint = setpoints[0]
        coolSetpoint = setpoints[1]
    time.sleep(0.5)

# Get equipment status
heatStatus = 0
coolStatus = 0
# s.send("temp_get_status.11 BE 1E\r\n")
# data = s.recv(1024)
# result = data.strip()
# if (result[:5] == "error"):
#     result = result[:5]
# if (result == "heat"):
#     heatStatus = 1
#     coolStatus = 0
# if (result == "cool"):
#     heatStatus = 0
#     coolStatus = 1    

print "Content-Type: text/html\n"
print "INSERT INTO temperature_data (temp, heat_setpoint, cool_setpoint, heat_status, cool_status) values (%d, %d, %d, %d, %d)" % (int(temp), int(heatSetpoint), int(coolSetpoint), int(heatStatus), int(coolStatus))

db_cur.execute("""INSERT INTO temperature_data (temp, heat_setpoint, cool_setpoint, heat_status, cool_status)
                  values (%s, %s, %s, %s, %s)""", (int(temp), int(heatSetpoint), int(coolSetpoint), int(heatStatus), int(coolStatus)))

db_cur.close()
db_conn.commit()
db_conn.close()
s.close()
exit()

