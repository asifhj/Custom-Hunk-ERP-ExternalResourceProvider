import os
import subprocess
import sys

_NEW_PYTHON_PATH = '/usr/bin/python'
_SPLUNK_PYTHON_PATH = os.environ['PYTHONPATH']

os.environ['PYTHONPATH'] = _NEW_PYTHON_PATH 
my_process = os.path.join(os.getcwd(), '/opt/sandbox-splunk-mongod/hunk/etc/apps/custom_erp/bin/mongo_pull.py')

line = sys.stdin.readline()
fo = open("/opt/sandbox-splunk-mongod/hunk/etc/apps/custom_erp/bin/config.json", "wb")
fo.write(line)
fo.close()

p = subprocess.Popen([os.environ['PYTHONPATH'], my_process, _SPLUNK_PYTHON_PATH], 
stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output = p.communicate()[0]
print output
