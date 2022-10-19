# -*- coding: utf-8 -*-

import os
from re import T, X
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
import mariadb 
from datetime import *
from PyQt5 import uic
from time import mktime
import pandas as pd

# 時間軸アイテムクラス
class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super(TimeAxisItem, self).__init__(*args, **kwargs)
        #ラベルにプレフィックス”G"がついてしまうのを回避
        self.autoSIPrefix = False
    def tickStrings(self, values, scale, spacing):
        ret = []
        fmt = '%H:%M'
        for x in values:
            try:
                t = datetime.fromtimestamp(x)
                ret.append(t.strftime(fmt))
            except ValueError:
                ret.append('')

        return ret

# DB接続情報
conn = mariadb.connect(
    user='root',
    password='xxxxxx',
    host='localhost',
    database='thermal_management',
    port=13306
    )
cur = conn.cursor() 

# 当日の温度・湿度取得SQL
select_temp_hum= '''
-- 当日の計測結果
with today_list as (
    -- 受信日の５分ごとの仮想表
    select
        date_format(date_add(concat(date_format(CURDATE(),'%Y/%m/%d') ,' 00:00:00') , interval (generate_series-1) * 5 minute) ,'%Y/%m/%d %H:%i:%S') as reception_time
    ,   generate_series
    from 
    (
        select 0 generate_series from dual where (@num:=1-1) * 0 
        union all
        select @num:=@num+1 from `information_schema`.columns
        limit 288
    ) as temp
)
, survay_list as (
    -- ５分ごとの測定結果集計
    select
          min(no) as no
        , module_no
        , concat(date_format(reception_time, '%Y/%m/%d %H'), ':', lpad(truncate(cast(date_format(reception_time, '%i') as integer) / 5 , 0) * 5, 2, '0'),':00' ) as reception_time
        , truncate(avg(temperature), 1) as temperature 
        , truncate(avg(humidity), 1) as humidity 
    from
        temp_hum 
    where
        date (reception_time) = curdate() 
    group by
        concat(date_format(reception_time, '%Y/%m/%d %H'), ':', lpad(truncate(cast(date_format(reception_time, '%i') as integer) / 5 , 0) * 5, 2, '0'),':00' ) 
    order by
        no asc
)
select
    tl.reception_time
,   sl.no
,   sl.module_no
,   sl.temperature  as temperature
,   sl.humidity  as humidity 
from
    today_list tl
    left outer join survay_list sl
        on tl.reception_time = sl.reception_time
where
    sl.no is not null
order by
    tl.reception_time
'''

# SQL実行
cur.execute(select_temp_hum) 
list_x = []
list_y1 = []
list_y2 = []
for reception_time, no, module_no,  temperature, humidity in cur: 
    print(f"no: {no}, module_no: {module_no}, datetime: {reception_time}, temperature: {temperature}, humidity: {humidity}")

    list_x.append(datetime.strptime(reception_time, '%Y/%m/%d %H:%M:%S'))
    list_y1.append(float(temperature))
    list_y2.append(float(humidity))


conn.close()

# 画面設定
app = pg.mkQApp('温度・湿度管理画面')
win = uic.loadUi(os.path.dirname(__file__) + '/temp_local.ui')
win.setWindowTitle('温度・湿度管理画面' + '(' + datetime.now().strftime('%Y年%m月%d日') + ')')
pg.setConfigOptions(antialias=True)

# 温度グラフ設定
axis = TimeAxisItem(orientation='bottom',units='xxxx')
axis.setTickSpacing(levels=[(3600, 0), (60, 0)])

graph = win.graphicsViewTemperature.addPlot(title="温度計測")
graph.setAxisItems({'bottom':axis})
curve = graph.plot(
    pen='y'
    ,symbol='o'
    ,symbolPen='y'
    ,symbolBrush=0.2
    ,symbolSize=5
    ,x=[x.timestamp() for x in list_x]
    ,y=list_y1
    ,axisItems = {'bottom': axis}
)
graph.setLabel('left', '温度(℃)')
graph.setLabel('bottom', '時間', units='時:分')

# 湿度グラフ設定
axis2 = TimeAxisItem(orientation='bottom')
axis2.setTickSpacing(levels=[(3600, 0), (60, 0)])
graph2 = win.graphicsViewHumidity.addPlot(title='湿度計測')
graph2.setAxisItems({'bottom':axis2})
curve = graph2.plot(
    pen='b'
    ,symbol='o'
    ,symbolPen='b'
    ,symbolBrush=0.2
    ,symbolSize=5
    ,x=[x.timestamp() for x in list_x]
    ,y=list_y2
    ,axisItems = {'bottom': axis2}
)
graph2.setLabel('left', '湿度(％)')
graph2.setLabel('bottom', '時間(時:分)')

# 画面表示
win.show()

# メイン
if __name__ == '__main__':
    pg.exec()   

