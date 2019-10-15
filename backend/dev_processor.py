import json
import os,sys
import databaseapi
import readdata
from pathlib import Path

def _getUserSequenceByUidPid(problemid, userid):
    with open("./cache/" + problemid + "/" + "tmp", "r") as f:
        result = json.load(f)
    filterscale = result["scale"]
    baseFilterSet = result["data"]
    data = []
    states = []
    lastState = -1
    eventTypes = []
    result = databaseapi.userSequenceByUidPid(userid,problemid)
    for item in result:
        x = int((int(item['pageX'])/filterscale))
        y = int((int(item['pageY'])/filterscale))
        index = (str(x)+"_"+str(y))
        if index in baseFilterSet:
            if baseFilterSet[index] != lastState:
                states.append(baseFilterSet[index])
                lastState = baseFilterSet[index]
                eventTypes.append(item['type'])
            elif item['type']=='mousedown' or item['type']=='mouseup':
                eventTypes[len(eventTypes)-1] = item['type']
            data.append({'x': x, 'y':y, "type":item['type']})
    with open("./cache/" + problemid + "/" + userid , "w+") as f:
        f.write(str({"data":data,"states":states,"eventtypes":eventTypes}))
    return str({"data":data,"states":states,"eventtypes":eventTypes})

def _getProblemSequence(problemid):
    if not os.path.isdir("./cache/" + problemid):
        os.mkdir("./cache/"+problemid)
    data = []
    for i in range(0, 960):
        data.append([0] * 600)
    result = databaseapi.problemSequenceById(problemid)
    for obj in result:
        x = int(obj['pageX'])
        y = int(obj['pageY'])
        if x >= 960 or y >= 600:
            continue
        data[x][y] = data[x][y] + 1
    with open("./cache/" + problemid + "/problemsequence", "w+") as f:
        f.write(str({"data":data}))
    return str({"data":data})

def _setImportantArea(problemid, result):
    if not os.path.isdir("./cache/" + problemid):
        os.mkdir("./cache/"+problemid)
    with open("./cache/"+problemid+"/"+"tmp", "w+") as f:
        json.dump(result, f)
    return "true"

def _getUserSequenceByProblem(problemid):
    if not Path("./cache/" + problemid + "/" + "tmp").exists():
        return str({"data":[]})
    with open("./cache/" + problemid + "/" + "tmp", "r") as f:
        result = json.load(f)
    filterscale = result["config"]["cellRadius"]
    baseFilterSet = result["data"]
    result2 = databaseapi.userSequenceByProblem(problemid)
    data = []
    for userdata in result2:
        states = []
        eventTypes = []
        eventTimes= []
        mint = userdata["data"][0]['timestamp']
        maxt = userdata["data"][0]['timestamp']
        for item in userdata["data"]:
            x = int((int(item['pageX'])/filterscale))
            y = int((int(item['pageY'])/filterscale))
            index = (str(x)+"_"+str(y))
            if mint > item['timestamp']:
                mint = item['timestamp']
            if maxt < item['timestamp']:
                maxt = item['timestamp']
            if index in baseFilterSet:
                states.append(baseFilterSet[index])
                eventTypes.append(item['type'])
                eventTimes.append(item['timestamp'])
            # Add by Min ============================
            elif item['type'] != 'mousemove':
                minDistance = 10000
                minState = 0
                for point in baseFilterSet:
                    baseX = int(point.split('_')[0])
                    baseY = int(point.split('_')[1])
                    if (x - baseX)**2 + (y - baseY)**2 < minDistance:
                        minDistance = (x - baseX)**2 + (y - baseY)**2
                        minState = baseFilterSet[point]
                states.append(minState)
                eventTypes.append(item['type'])
                eventTimes.append(item['timestamp'])
            # =======================================
        if len(states) > 10:
            data.append({"timestamp":eventTimes, "states":states,"eventtypes":eventTypes,"userid":userdata["_id"], "score":readdata.getScoreByID(userdata["_id"],problemid),"maxt":maxt, "mint":mint})
    with open("./cache/" + problemid + "/userproblemsequence", "w+") as f:
        f.write(str({"data":data}))
    return str({"data":data})

def _getUserClustersByProblem(problemid):
    return ""

def _getProblemInfomation(problemid, num):
    arr = readdata.readProblemOverNum(num)
    data = []
    for i in arr:
        result = databaseapi.userSequenceByProblem(i[0])
        score = 0
        costtime = 0
        movecount = 0
        clickcount = 0
        usercount = 0
        for userdata in result:
            tmpsc = readdata.getScoreByID(userdata["_id"], i[0])
            if len(tmpsc) == 0:
                continue
            tmpm = 0
            tmpc = 0
            mint = userdata["data"][0]['timestamp']
            maxt = userdata["data"][0]['timestamp']
            for item in userdata["data"]:
                if mint > item['timestamp']:
                    mint = item['timestamp']
                if maxt < item['timestamp']:
                    maxt = item['timestamp']
                if item["type"] == "mousemove":
                    tmpm+=1
                else:
                    tmpc+=1
            if maxt-mint > 3600:
                continue
            score += max([int(x) for x in tmpsc])
            costtime += (maxt-mint)
            usercount += 1
            movecount += tmpm
            clickcount += tmpc
        data.append({"pid":i[0],"movecount":movecount,"clickcount":clickcount, "userid":userdata["_id"], "score":score,"costtime":costtime,"usercount":usercount})
    with open("./cache/" + problemid + "/problemdetails", "w+") as f:
        f.write(str({"data":data}))
    return str({"data":data})