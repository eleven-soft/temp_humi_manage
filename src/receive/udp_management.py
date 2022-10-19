# -*- coding: utf-8 -*-

from re import S
import socket
from contextlib import closing
import mariadb
import re
import datetime

print("Connect DB start")

conn = mariadb.connect(
    user="root",
    password="xxxxxx",
    host="localhost",
    database="thermal_management",
    port=13306
    )
cur = conn.cursor()

print("Connect DB end")

UDP_IP="192.168.10.101"
UDP_PORT=8890

sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP_IP,UDP_PORT))

with closing(sock):
    while True:
        data,addr = sock.recvfrom(1024)
        print("Send from ESP:",addr)
        print("data:",data)
        data = str(data)
        ondo, situdo = data.split(',')
        ondo2 = re.sub(r"[^\d.]", "", ondo)
        situdo2 = re.sub(r"[^\d.]", "", situdo)
        print(ondo2)
        print(situdo2)
        dt_now = datetime.datetime.now()

        cur.execute("insert into thermal_management.temp_hum (module_no, reception_time, temperature, humidity) values(?, ?, ?, ?);",['1', dt_now, ondo2, situdo2]) 

        conn.commit() 