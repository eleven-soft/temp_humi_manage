-- 温度湿度
create table temp_hum(
    no               int not null auto_increment
,   module_no        int
,   reception_time   datetime
,   temperature      decimal(3,1)
,   humidity         decimal(3,1)
,   primary key (no)
)
;
