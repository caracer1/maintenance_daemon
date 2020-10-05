#!/usr/bin/python

import sys
import subprocess
from threading import Timer
import argparse
import os
import time



#functions for timeout:

from threading import Timer
kill = lambda process: process.kill()
#----------------------------------#
def check_backup_and_storage():
    subprocess.Popen(['date +"%m %d %Y %I:%M %p: Currently checking for Valid Backups within the last 48 Hours" >> /users/check/desktop/maintenance_log.txt'], shell=True, stdout=subprocess.PIPE)
    backup_within_last_two_days = subprocess.check_output("/usr/bin/log show --style syslog --info --last 2d --predicate \'processImagePath contains \"backupd\" and subsystem beginswith \"com.apple.TimeMachine\"\' | sed \'s/..*o]//\' | grep \"Backup completed successfully\" | tail -1", shell=True).decode("utf-8")
    current_storage = subprocess.check_output("df -h /  | awk 'NR==2{print $4}' | sed 's/[^0-9]*//g'", shell=True).decode("utf-8")
    if backup_within_last_two_days:
        subprocess.Popen(['date +"%m %d %Y %I:%M %p: Backup has been completed within 48 hours" >> /users/check/desktop/maintenance_log.txt'], shell=True, stdout=subprocess.PIPE)
    else:
        subprocess.Popen(['date +"%m %d %Y %I:%M %p: No Backup found within 48 hours" >> /users/check/desktop/maintenance_log.txt'], shell=True, stdout=subprocess.PIPE)
    subprocess.Popen(['date +"%m %d %Y %I:%M %p: Checking Free Storage" >> /users/check/desktop/maintenance_log.txt'], shell=True, stdout=subprocess.PIPE)
    if current_storage < 40:
        subprocess.Popen(['date +\"%m %d %Y %I:%M %p: Warning Available Free Space is: \" | perl -pe \'chomp\' >> /users/check/desktop/maintenance_log.txt && df -h / | awk \'NR==2{print $4}\' >> /users/check/desktop/maintenance_log.txt'], shell=True, stdout=subprocess.PIPE)
    else:
        subprocess.Popen(['date +\"%m %d %Y %I:%M %p: Available Free Space is: \" | perl -pe \'chomp\' >> /users/check/desktop/maintenance_log.txt && df -h / | awk \'NR==2{print $4}\' >> /users/check/desktop/maintenance_log.txt'], shell=True, stdout=subprocess.PIPE)




def check_uptime():
    last_boot_time = subprocess.check_output("sysctl kern.boottime | awk '{print $5}' | tr -d ','", shell=True).decode("utf-8")
    current_time = subprocess.check_output("date '+%s'", shell=True).decode("utf-8")
    time_since_last_boot = int(current_time) - int(last_boot_time)
    print 'Seconds since last boot:', time_since_last_boot
    return time_since_last_boot

def check_how_many_users():
    subprocess.Popen(['date +"%m %d %Y %I:%M %p: Checking number of concurrently logged in users" >> /users/check/desktop/maintenance_log.txt'], shell=True, stdout=subprocess.PIPE)
    current_cpu_percent_1 = subprocess.check_output("top -l 2 -n 0 -F | egrep -o ' \d*\.\d+% idle' | tail -1 | sed 's/%//'", shell=True).decode("utf-8")
    current_cpu_percent_1=current_cpu_percent_1.replace('idle', '')
    ave_cpu=100-float(current_cpu_percent_1)
    concurrently_logged_users = subprocess.check_output("users | wc -w", shell=True).decode("utf-8")
    concurrently_logged_users=int(concurrently_logged_users)
    check_backup_and_storage()
    if concurrently_logged_users >= 8:
        print "Killing Login Window Process:"
        subprocess.Popen(['date +"%m %d %Y %I:%M %p: More than 8 users detected - killing loginwindow process" >> /users/check/desktop/maintenance_log.txt'], shell=True, stdout=subprocess.PIPE)
        my_timer = Timer(30, kill, [subprocess.Popen(['sudo pkill -9 loginwindow'], shell=True, stdout=subprocess.PIPE)])
        try:
            my_timer.start()
        finally:
            my_timer.cancel()
    command = ['date +"%m %d %Y %I:%M %p: The current cpu usage is:"', str(ave_cpu) ,'>> /users/check/desktop/maintenance_log.txt']
    subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    #subprocess.Popen(['date +"%m %d %Y %I:%M %p: Maintenance Check Complete - All tests passed - no reboot requested" >> /users/check/desktop/maintenance_log.txt'], shell=True, stdout=subprocess.PIPE)
    print "The current cpu usage is: ", ave_cpu
    print "Check Complete"
    if ave_cpu > 90:
        print "The current cpu usage is: ",ave_cpu
        print "Consider rebooting Server..."
        subprocess.Popen(['date +"%m %d %Y %I:%M %p: Maintenance Check - CPU above 90 percent - attempting reboot " >> /users/check/desktop/maintenance_log.txt'], shell=True, stdout=subprocess.PIPE)
        force_reboot()
        #sys.exit()
    else:
        subprocess.Popen(['date +"%m %d %Y %I:%M %p: Maintenance Check Complete - All tests passed - no reboot requested" >> /users/check/desktop/maintenance_log.txt'], shell=True, stdout=subprocess.PIPE)
        print "The current cpu usage is: ", ave_cpu
        print "Check Complete"
        time.sleep(2)
        #sys.exit()





def has_server_been_rebooted_within_one_day():
    if check_uptime() > 86400:
        print("False")
        return False
    else:
        print("True")
        return True
def has_server_just_been_rebooted():
    if check_uptime() > 1000:
        print("False")
        return False
    else:
        print("True")
        return True

def check_reboot_script():
    if has_server_been_rebooted_within_one_day() == True:
        subprocess.Popen(['date +"%m %d %Y %I:%M %p: Server has been successfully rebooted within the last day: Proceeding with other checks" >> /users/check/desktop/maintenance_log.txt'], shell=True, stdout=subprocess.PIPE)
        if has_server_just_been_rebooted == True:
            subprocess.Popen(['date +"%m %d %Y %I:%M %p: Maintenance Script called after Startup/Reboot" >> /users/check/desktop/maintenance_log.txt'], shell=True, stdout=subprocess.PIPE)
        print("Server has been successfully rebooted within the last day: Proceeding with other checks")
        check_how_many_users()
        sys.exit()
    else:
        subprocess.Popen(['date +"%m %d %Y %I:%M %p: Server has not been rebooted within the last 24 hours: Executing force reboot attempt" >> /users/check/desktop/maintenance_log.txt'], shell=True, stdout=subprocess.PIPE)
        print("Server needs to be rebooted, executing reboot attempt")
        force_reboot()





def force_reboot():
    print "Rebooting"
    print "Killing Backup process if it is still running: "
    my_timer = Timer(30, kill, [subprocess.Popen(['sudo pkill backupd'], shell=True, stdout=subprocess.PIPE)])
    try:
        my_timer.start()
    finally:
        my_timer.cancel()

    print "Killing Login Window Process:"
    my_timer = Timer(30, kill, [subprocess.Popen(['sudo pkill -9 loginwindow'], shell=True, stdout=subprocess.PIPE).wait()])
    try:
        my_timer.start()
    finally:
        my_timer.cancel()

    print "Restarting NuoRDS Service:"
    my_timer = Timer(30, kill, [
        subprocess.Popen(['sudo nrdservice stop;sudo nrdservice start;'], shell=True, stdout=subprocess.PIPE).wait()])
    try:
        my_timer.start()
    finally:
        my_timer.cancel()

    print "Killing Adobe Creative Cloud Daemon:"
    my_timer = Timer(30, kill, [subprocess.Popen(['sudo pkill -9 AdobeCRDaemon'], shell=True, stdout=subprocess.PIPE).wait()])
    try:
        my_timer.start()
    finally:
        my_timer.cancel()
    print "Attempting Graceful Restart:"
    subprocess.Popen(['date +"%m %d %Y %I:%M %p: Force Reboot Sequence completed - attempting reboot" >> /users/check/desktop/maintenance_log.txt'], shell=True, stdout=subprocess.PIPE)
    my_timer = Timer(30, kill, [subprocess.Popen(['sudo reboot'], shell=True, stdout=subprocess.PIPE).wait()])
    try:
        my_timer.start()
    finally:
        my_timer.cancel()

    print "Graceful Restart failed attempting force reboot"
    subprocess.Popen(['sudo shutdown -r NOW'], shell=True, stdout=subprocess.PIPE)



def main():

    if sys.argv[1] == '-c':
        subprocess.Popen(['date +"%m %d %Y %I:%M %p: Maintenance Check Requested" >> /users/check/desktop/maintenance_log.txt'], shell=True, stdout=subprocess.PIPE)
        check_reboot_script()
    elif sys.argv[1] == '-r':
        subprocess.Popen(['date +"%m %d %Y %I:%M %p: Force Reboot Requested" >> /users/check/desktop/maintenance_log.txt'], shell=True, stdout=subprocess.PIPE)
        force_reboot()
    else:
        print("The flag you have run is not an available option")
        print("Usage [-c]: Check if server has been rebooted within 24 hours")
        print("Usage [-r]: Force the reboot of the server")
        sys.exit()


if __name__ == "__main__":
    main()
    sys.exit()
