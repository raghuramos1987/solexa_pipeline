import config 
import sys


conf_obj = config.Parameters(sys.argv[1], 0)
if int(sys.argv[3]) == 0:
    conf_obj.server.UpdateRunStatusCompressingResults(sys.argv[2])
else:
    conf_obj.server.UpdateRunStatusRsyncQuestResults(sys.argv[2])

