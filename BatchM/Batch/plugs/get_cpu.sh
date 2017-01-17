#!/bin/sh
 
#功能：计算CPU的利用率,选取采样点
#计算公式：
#方法1：cpu usage=(idle2-idle1)/(cpu2-cpu1)*100
#方法2: cpu usage=[(user_2 +sys_2+nice_2) - (user_1 + sys_1+nice_1)]/(total_2 - total_1)*100
#方法3:(本脚本采用)
#total_0=USER[0]+NICE[0]+SYSTEM[0]+IDLE[0]+IOWAIT[0]+IRQ[0]+SOFTIRQ[0]
#total_1=USER[1]+NICE[1]+SYSTEM[1]+IDLE[1]+IOWAIT[1]+IRQ[1]+SOFTIRQ[1]
#cpu usage=(IDLE[0]-IDLE[1]) / (total_0-total_1) * 100
 
##echo user nice system idle iowait irq softirq
CPULOG_1=$(awk '/\<cpu\>/{print $2" "$3" "$4" "$5" "$6" "$7" "$8}' /proc/stat)
SYS_IDLE_1=$(echo $CPULOG_1 | awk '{print $4}')
Total_1=$(echo $CPULOG_1 | awk '{print $1+$2+$3+$4+$5+$6+$7}')

sleep 0.5

CPULOG_2=$(awk '/\<cpu\>/{print $2" "$3" "$4" "$5" "$6" "$7" "$8}' /proc/stat)
SYS_IDLE_2=$(echo $CPULOG_2 | awk '{print $4}')
Total_2=$(echo $CPULOG_2 | awk '{print $1+$2+$3+$4+$5+$6+$7}')

SYS_IDLE=`expr $SYS_IDLE_2 - $SYS_IDLE_1`

Total=`expr $Total_2 - $Total_1`

#echo $SYS_IDLE $Total
echo "scale=2; 100-$SYS_IDLE/$Total*100"  |bc
echo `free -m |awk '/\<Mem\>/{print $3/$2*100}'`
#method 1
#SYS_USAGE=`expr $SYS_IDLE/$Total*100 |bc -l`
#SYS_Rate=`expr 100-$SYS_USAGE |bc -l`

#method2
#tmp_rate=`expr 1-$SYS_IDLE/$Total | bc -l`
#SYS_Rate=`expr $tmp_rate*100 | bc -l`

#display
#Disp_SYS_Rate=`expr "scale=3; $SYS_Rate/1" |bc`
#echo $Disp_SYS_Rate%
