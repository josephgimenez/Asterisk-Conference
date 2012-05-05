from django.shortcuts import render_to_response
from django.http import HttpResponse
from datetime import datetime
import re
import shutil
import commands

def kickUser(user_num, line):
	kick_str = ("/usr/sbin/asterisk -r -x 'meetme kick %s %s'" % (line, user_num))
	commands.getoutput(kick_str)

def setLock(lockit, line):
    if (lockit):
        commands.getoutput("/usr/sbin/asterisk -r -x 'meetme lock %s'" % (line))
    else:
        commands.getoutput("/usr/sbin/asterisk -r -x 'meetme unlock %s'" % (line))

def home(request):
    return render_to_response('index.html')


def conference(request):
    conf_count = 0
    locked = False

    conference_info = []

    if 'kick' in request.GET:
		user_num = request.GET['kick']
		confline = request.GET['line']
		kickUser(user_num, confline)

    if 'line' in request.GET:
        confline = request.GET['line']

    if 'addlock' in request.GET:
        locked = True
        setLock(True, confline)

    if 'remlock' in request.GET:
        locked = False
        setLock(False, confline)



    conf = commands.getoutput("/usr/sbin/asterisk -r -x 'meetme'").split('\n')

    for conference in conf[1:]:
    	conference_line = []
    	caller_line = []
    	caller_info = []

        if "Total" not in conference:
            confline = re.search("^\d+", conference)
            #conference_data["line"] = confline.group(0)
            duration = re.search(r"(\d+):(\d+):(\d+)", conference)
            locked = re.search(r"(\w+)\s+$", conference)

            if ('No' in locked.group(0)):
            	locked = None
            else:
                locked  = locked.group(0)

            conference_line = [confline.group(0), duration.group(1), duration.group(2), duration.group(3), locked]

            stat = commands.getoutput("/usr/sbin/asterisk -r -x 'meetme list %s'" % (confline.group(0)))

            conf_count += 1

            for extension in stat.split('\n'):
                if "Channel" in extension:
                    usernum = re.search(r"User #: (\d+)", extension)
                    extuser = re.search(r"\s\s(.+) Channel", extension)
                    duration = re.search(r"(\d+):(\d+):(\d+)", extension)
                    caller_line = [usernum.group(1), extuser.group(1), confline.group(0), duration.group(1), duration.group(2), duration.group(3)]
                    caller_info.append(caller_line)
                else:
                    break

            conference_line.append(caller_info)
            conference_info.append(conference_line)

            del caller_line
            del conference_line
            del caller_info


    return render_to_response('conference/index.html', \
			{'conference_info' : conference_info, 'conf_count' : conf_count})

