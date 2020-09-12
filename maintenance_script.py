#!/usr/bin/python

import sys
import subprocess
from threading import Timer
import argparse
import os



#functions for timeout:

from threading import Timer
kill = lambda process: process.kill()
#----------------------------------#

def check_uptime():
    last_boot_time = subprocess.check_output("sysctl kern.boottime | awk '{print $5}' | tr -d ','", shell=True).decode("utf-8")
    current_time = subprocess.check_output("date '+%s'", shell=True).decode("utf-8")
    time_since_last_boot = int(current_time) - int(last_boot_time)
    print 'Seconds since last boot:', time_since_last_boot
    return time_since_last_boot

def check_how_many_users():
    current_cpu_percent_1 = subprocess.check_output("top -l 2 -n 0 -F | egrep -o ' \d*\.\d+% idle' | tail -1 | sed 's/%//'", shell=True).decode("utf-8")
    current_cpu_percent_1=current_cpu_percent_1.replace('idle', '')
    ave_cpu=100-float(current_cpu_percent_1)
    concurrently_logged_users = subprocess.check_output("users | wc -w", shell=True).decode("utf-8")
    concurrently_logged_users=int(concurrently_logged_users)
    if concurrently_logged_users > 8:
        print "Killing Login Window Process:"
        my_timer = Timer(30, kill, [subprocess.Popen(['sudo pkill -9 loginwindow'], shell=True, stdout=subprocess.PIPE)])
        try:
            my_timer.start()
        finally:
            my_timer.cancel()
    if ave_cpu > 90:
        print "The current cpu usage is: ",ave_cpu
        print "Consider rebooting Server..."
        force_reboot()
        sys.exit()
    else:
        print "The current cpu usage is: ", ave_cpu
        print "Check Complete"
        file = open("/Users/check/Desktop/test.txt", "w")
        file.close()
        sys.exit()





def has_server_been_rebooted_within_one_day():
    if check_uptime() > 86400:
        print("False")
        return False
    else:
        print("True")
        return True

def check_reboot_script():
    if has_server_been_rebooted_within_one_day() == True:
        print("Server has been successfully rebooted within the last day: Proceeding with other checks")
        check_how_many_users()
        sys.exit()
    else:
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
    my_timer = Timer(30, kill, [subprocess.Popen(['sudo pkill -9 loginwindow'], shell=True, stdout=subprocess.PIPE)])
    try:
        my_timer.start()
    finally:
        my_timer.cancel()

    print "Restarting NuoRDS Service:"
    my_timer = Timer(30, kill, [
        subprocess.Popen(['sudo nrdservice stop;sudo nrdservice start;'], shell=True, stdout=subprocess.PIPE)])
    try:
        my_timer.start()
    finally:
        my_timer.cancel()

    print "Killing Adobe Creative Cloud Daemon:"
    my_timer = Timer(30, kill, [subprocess.Popen(['sudo pkill -9 AdobeCRDaemon'], shell=True, stdout=subprocess.PIPE)])
    try:
        my_timer.start()
    finally:
        my_timer.cancel()
    print "Attempting Graceful Restart:"
    my_timer = Timer(30, kill, [subprocess.Popen(['sudo reboot'], shell=True, stdout=subprocess.PIPE)])
    try:
        my_timer.start()
    finally:
        my_timer.cancel()

    print "Graceful Restart failed attempting force reboot"
    subprocess.Popen(['sudo shutdown -r NOW'], shell=True, stdout=subprocess.PIPE)



def main():

    if sys.argv[1] == '-c':
        check_reboot_script()
    elif sys.argv[1] == '-r':
        force_reboot()
    else:
        print("The flag you have run is not an available option")
        print("Usage [-c]: Check if server has been rebooted within 24 hours")
        print("Usage [-r]: Force the reboot of the server")
        sys.exit()


if __name__ == "__main__":
    main()
    sys.exit()
