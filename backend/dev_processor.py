from __future__ import division
import json
import os,sys
import databaseapi
import readdata
from pathlib import Path
import re
from util import levenshtein_distance, LCS_distance, cal_residual, extract_sequence, label_residual
import util
import networkx as nx
import scipy.cluster.hierarchy as hierarchy
from time import time
from copy import deepcopy
from datasketch import MinHashLSH, MinHash
from collections import Counter
import numpy as np
import math

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

def _split2subSequence(result2, problemid):
    finalSeq = []
    for userdata in result2:
        if len(userdata["_id"].strip()) < 3:
            continue
        lid = re.split(r"[0]{3,}",userdata["_id"])[1]
        tmp = [ ]
        lasttime = float(userdata["data"][0]["time2"])
        lasttype = "mousemove"
        tid = lid+"_"+problemid
        if tid in readdata.recentScore:
            for item in userdata["data"]:
                time2 = float(item["time2"])
                if lasttime - time2 > 2000:
                    # finalSeq.append([ [lid, problemid, readdata.recentScore[tid][3], readdata.recentScore[tid][4] ] ] + tmp)
                    tmp = []
                elif item['time'] <= readdata.recentScore[tid][4] and item['time'] > readdata.recentScore[tid][4]-86400:
                    if item["type"] == "mousemove":
                        if lasttype == "mousedown":
                            tmp.append([ int(item["x"]), int(item["y"]), 0, "mousedrag", time2, item["time"]])
                        else:
                            tmp.append([ int(item["x"]), int(item["y"]), 0, "mousemove", time2, item["time"]])
                    elif item["type"] == "mouseup":
                        tmp.append([ int(item["x"]), int(item["y"]) , 0 , "mouseup", time2, item["time"]])
                        lasttype = "mousemove"
                    else:
                        tmp.append([ int(item["x"]), int(item["y"]) , 0 , "mousedown", time2, item["time"]])
                        lasttype = "mousedown"
                else:
                    break
                lasttime = time2
            finalSeq.append([ [lid, problemid, readdata.recentScore[tid][3], readdata.recentScore[tid][4] ] ] + tmp)
    return finalSeq

def _getUserSequenceByProblem(problemid):
    if not Path("./cache/" + problemid + "/" + "tmp").exists():
        return str({"data":[]})
    with open("./cache/" + problemid + "/" + "tmp", "r") as f:
        result = json.load(f)
    filterscale = result["config"]["cellRadius"]
    baseFilterSet = result["data"]
    result2 = databaseapi.userSequenceByProblem(problemid)
    data = []
    new_result2 = _split2subSequence(result2, problemid)
    for userdata in new_result2:
        states = []
        eventTypes = []
        eventTimes= []
        for ui in range(1, len(userdata)):
            item = userdata[ui]
            x = int((int(item[0])/filterscale))
            y = int((int(item[1])/filterscale))
            index = (str(x)+"_"+str(y))
            if index in baseFilterSet:
                states.append(baseFilterSet[index])
                eventTypes.append(item[3])
                eventTimes.append(item[4])
            elif item[3] != 'mousemove':
                minDistance = 10000
                minState = 0
                for point in baseFilterSet:
                    baseX = int(point.split('_')[0])
                    baseY = int(point.split('_')[1])
                    if (x - baseX)**2 + (y - baseY)**2 < minDistance:
                        minDistance = (x - baseX)**2 + (y - baseY)**2
                        minState = baseFilterSet[point]
                states.append(minState)
                eventTypes.append(item[3])
                eventTimes.append(item[4])
        if len(states) > 10:
            data.append({"timestamp":eventTimes, "states":states,"eventtypes":eventTypes,"userid":userdata[0][0], "score":[userdata[0][2]]})
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


def _clusterResultByProblem(problemid):
    if not Path("./cache/" + problemid + "/" + "tmp").exists():
        return str({"data":[]})
    with open("./cache/" + problemid + "/" + "tmp", "r") as f:
        result = json.load(f)
    filterscale = result["config"]["cellRadius"]
    baseFilterSet = result["data"]
    result2 = databaseapi.userSequenceByProblem(problemid)
    data = []
    new_result2 = _split2subSequence(result2, problemid)
    for userdata in new_result2:
        states = []
        eventTypes = []
        eventTimes= []
        for ui in range(1, len(userdata)):
            item = userdata[ui]
            x = int((int(item[0])/filterscale))
            y = int((int(item[1])/filterscale))
            index = (str(x)+"_"+str(y))
            if index in baseFilterSet:
                states.append(baseFilterSet[index])
                eventTypes.append(item[3])
                eventTimes.append(item[4])
            elif item[3] != 'mousemove':
                minDistance = 10000
                minState = 0
                for point in baseFilterSet:
                    baseX = int(point.split('_')[0])
                    baseY = int(point.split('_')[1])
                    if (x - baseX)**2 + (y - baseY)**2 < minDistance:
                        minDistance = (x - baseX)**2 + (y - baseY)**2
                        minState = baseFilterSet[point]
                states.append(minState)
                eventTypes.append(item[3])
                eventTimes.append(item[4])
        if len(states) > 10:
            data.append({"timestamp":eventTimes, "states":states,"eventtypes":eventTypes,"userid":userdata[0][0], "score":[userdata[0][2]]})
    with open("./cache/" + problemid + "/userproblemsequence", "w+") as f:
        f.write(str({"data":data}))

    # Create File Needed by Min =================================
    actResp = []
    for userCount in range(len(data)):
        userAct = []
        if len(data[userCount]['score']) > 0 :
            userScore = int(data[userCount]['score'][-1])
        else: userScore = -50
        for actCount in range(len(data[userCount]['eventtypes'])):
            if data[userCount]['eventtypes'][actCount] != 'mousemove':
                userAct.append(data[userCount]['states'][actCount])
        actResp.append({"userId": data[userCount]['userid'], "score": userScore, "actSeq": userAct})

    seq2Resp_All = []
    scoreResp_All = []
    seq2Resp_fullMark = []
    scoreResp_fullMark = []
    seq2Resp_lessMark = []
    scoreResp_lessMark = []
    idResp_fullMark = []
    idResp_lessMark = []
    idResp_All = []
    seqRatio = 1
    for userCount in range(len(actResp)):
        if len(actResp[userCount]['actSeq']) > 2:
            if actResp[userCount]['score'] == 100:
                seq2Resp_fullMark.append(np.array(actResp[userCount]['actSeq'][0:int(len(actResp[userCount]['actSeq'])/seqRatio)]))
                scoreResp_fullMark.append(actResp[userCount]['score'])
                idResp_fullMark.append(actResp[userCount]['userId'])
            elif actResp[userCount]['score'] >= 0:
                seq2Resp_lessMark.append(np.array(actResp[userCount]['actSeq'][0:int(len(actResp[userCount]['actSeq'])/seqRatio)]))
                scoreResp_lessMark.append(actResp[userCount]['score'])
                idResp_lessMark.append(actResp[userCount]['userId'])

            seq2Resp_All.append(np.array(actResp[userCount]['actSeq'][0:int(len(actResp[userCount]['actSeq'])/seqRatio)]))
            scoreResp_All.append(actResp[userCount]['score'])
            idResp_All.append(actResp[userCount]['userId'])

    for userCount in range(len(seq2Resp_fullMark)):
        repItem = []
        for actCount in range(len(seq2Resp_fullMark[userCount])):
            if actCount == 0:
                lastPoint = seq2Resp_fullMark[userCount][actCount]
            elif seq2Resp_fullMark[userCount][actCount] == seq2Resp_fullMark[userCount][actCount-1]:
                    repItem.append(actCount)
        if len(repItem) != 0:
            seq2Resp_fullMark[userCount] = np.delete(seq2Resp_fullMark[userCount], repItem)

    for userCount in range(len(seq2Resp_All)):
        repItem = []
        for actCount in range(len(seq2Resp_All[userCount])):
            if actCount == 0:
                lastPoint = seq2Resp_All[userCount][actCount]
            elif seq2Resp_All[userCount][actCount] == seq2Resp_All[userCount][actCount-1]:
                    repItem.append(actCount)
        if len(repItem) != 0:
            seq2Resp_All[userCount] = np.delete(seq2Resp_All[userCount], repItem)

    deleteObj = []
    for userCount in range(len(seq2Resp_fullMark)):
        if len(seq2Resp_fullMark[userCount]) < 2:
            deleteObj.append(userCount)
        else:
            seq2Resp_fullMark[userCount][0] = int(seq2Resp_fullMark[userCount][0])
    seq2Resp_fullMark = np.delete(seq2Resp_fullMark, deleteObj).tolist()

    deleteObj_All = []
    for userCount in range(len(seq2Resp_All)):
        if len(seq2Resp_All[userCount]) < 2:
            deleteObj_All.append(userCount)
        else:
            seq2Resp_All[userCount][0] = int(seq2Resp_All[userCount][0])
    seq2Resp_All = np.delete(seq2Resp_All, deleteObj_All).tolist()

    ### Store a file for MDL============================================================
    infoAll_fullMark = {}

    info_fullMark = {}
    eventList = []
    for i in range(len(seq2Resp_fullMark)):
        info_fullMark[idResp_fullMark[i]] = seq2Resp_fullMark[i].tolist()
        for j in range(len(seq2Resp_fullMark[i])):
            if seq2Resp_fullMark[i][j] not in eventList:
                eventList.append(int(seq2Resp_fullMark[i][j]))
    infoAll_fullMark['seqs'] = info_fullMark
    infoAll_fullMark['events'] = eventList
    # with open("./cache/" + problemid + '/fullMark_' + problemid + '.json', 'w') as file:
    #     json.dump(infoAll_fullMark, file)

    infoAll_All = {}

    info_All = {}
    eventList_All = []
    for i in range(len(seq2Resp_All)):
        info_All[idResp_All[i]] = seq2Resp_All[i].tolist()
        for j in range(len(seq2Resp_All[i])):
            if seq2Resp_All[i][j] not in eventList_All:
                eventList_All.append(int(seq2Resp_All[i][j]))
    infoAll_All['seqs'] = info_All
    infoAll_All['events'] = eventList_All
    with open("./cache/" + problemid + '/' + problemid + '.json', 'w') as file:
        json.dump(infoAll_All, file)
    ### Store End ======================================================================

    # define distance function
    def distance(a, b):
        return levenshtein_distance(a, b)/float(max(len(a), len(b), 1))

    def dist_matrix(df, data):
        g = nx.Graph()
        g.add_nodes_from(data.keys())
        for a in g.nodes():
            for b in g.nodes():
                g.add_edge(a, b, weight=df(data[a], data[b]))
        return {'matrix': nx.adjacency_matrix(g, weight="weight").toarray(), 'nodes': g.nodes()}

    def cluster_hierarchy(matrix):
        cls = hierarchy.linkage(matrix, method='single')
        order = hierarchy.leaves_list(cls)
        tree = hierarchy.to_tree(cls, False)
        return order, tree

    def extract_sequence_residual(events, valid_events = [], timegap = False):
        seq = filter(lambda e: e['Type'] == 'DTC' and e['Timestamp'] != None, events)
        seq = sorted(seq, key=lambda e: e['Timestamp'])
        seq = map(lambda e: {'type': e['Description']['L1'] + e['Description']['L2'], 'Timestamp': e['Timestamp']}, seq)
        if len(valid_events) != 0:
            seq = filter(lambda e: e['type'] in valid_events, seq)

        result = list(map(lambda e: e['type'], seq))

        if timegap == True:
            if len(seq) > 1:
                for i in range(len(seq) - 1):
                    timegap = seq[i + 1]['Timestamp'] - seq[i]['Timestamp']
                    result.insert(2 * i + 1, timegap)

        return result

    def extract_sequence_full(events, valid_events = []):
        seq = filter(lambda e: e['Type'] == 'DTC' and e['Timestamp'] != None, events)
        seq = sorted(seq, key=lambda e: e['Timestamp'])
        seq = map(lambda e: {'type': e['Description']['L1'] + e['Description']['L2'], 'Timestamp': e['Timestamp']}, seq)
        if len(valid_events) != 0:
            seq = filter(lambda e: e['type'] in valid_events, seq)

        return seq

    # Calculate every sequence's event consistence of every user
    # UserID, Sequence, Valid Event
    def cal_leaf_feature(id, seq, events):
        rs = {}
        rs['id'] = [id]
        rs['size'] = 1
        rs['count'] = {k: [] for k in events}
        rs['pattern'] = seq
        rs['pattern_count'] = [1 for i in range(len(rs['pattern']))]
        rs['cls'] = []
        rs['residual'] = 0
        rs['cost'] = len(rs['pattern'])
        rs['is_cut'] = False

        # calulate the count table, initialize pos and var table
        for key in events:
            count = seq.count(key)
            while count > len(rs['count'][key]):
                rs['count'][key].append(0)

            rs['count'][key][0:count] = [x + 1 for x in rs['count'][key][0:count]]

        return rs

    def calPattern(rs, l ,r, seq, events):
        th = 1.2

        # recalculate pattern
        patternCur = []
        rsCur = []

        # start search with lcs 
        patternArr, candidateArr, idx_in_pattern_l, idx_in_pattern_r, overlapTag = lcsMerge(l, r)
        rsCur = patternArr
        patternCur = list(map(lambda e: e['event'], patternArr))
        rs['pattern'] = patternCur
        residualCur = 0
        for i in range(len(rs['id'])):
            residualCur += LCS_distance(seq[rs['id'][i]], patternCur)
        rs['cost'] = len(patternCur) + (th * residualCur) 
        rs['residual'] = residualCur

        for e in candidateArr:
            candidateIdx = e['pos']
            currentIdx = candidateIdx
            if e['LorR'] == 'l':
                # find the start index in the pattern
                while(idx_in_pattern_l[currentIdx] == -1):
                    currentIdx -= 1
                    if currentIdx == -1:
                        break
                if currentIdx == -1:
                    startIdx_in_pattern = -1
                else:
                    startIdx_in_pattern = idx_in_pattern_l[currentIdx]
                # find the end index in the pattern
                currentIdx = candidateIdx
                while(idx_in_pattern_l[currentIdx] == -1):
                    currentIdx += 1
                    if currentIdx == len(idx_in_pattern_l):
                        break
                if currentIdx == len(idx_in_pattern_l):
                    endIdx_in_pattern = len(patternArr)
                else:
                    endIdx_in_pattern = idx_in_pattern_l[currentIdx]

                # calcualte cost
                cost_min = 1e7
                index_min = -1
                insertEventCount = 0
                for i in range(startIdx_in_pattern + 1, endIdx_in_pattern + 1):
                    patternCur = deepcopy(patternArr)
                    patternCur.insert(i, {'event': e['event'], 'count': 0})
                    patternCur = list(map(lambda e: e['event'], patternCur))

                    residualCur = 0
                    insertEventCountCur = 0
                    for j in range(len(rs['id'])):
                        residualTemp, isMatched = LCS_distance(seq[rs['id'][j]], patternCur, isIdxMatch = i)
                        residualCur += residualTemp
                        if isMatched:
                            insertEventCountCur += 1
                    costCur = len(patternCur) + (th * residualCur) 

                    if costCur < cost_min:
                        cost_min == costCur
                        index_min == i
                        insertEventCount = insertEventCountCur

                if cost_min < rs['cost']:
                    patternArr.insert(index_min, {'event': e['event'], 'count': insertEventCount})
                    rs['cost'] = cost_min
                    rs['residual'] = residualCur
                    rsCur = patternArr
                    idx_in_pattern_l[candidateIdx] = index_min
                    for i in range(candidateIdx + 1, len(idx_in_pattern_l)):
                        if idx_in_pattern_l[i] != -1:
                            idx_in_pattern_l[i] += 1
                    for i in range(len(idx_in_pattern_r)):
                        if idx_in_pattern_r[i] >= index_min:
                            idx_in_pattern_r[i] += 1
                else:
                    break
            
            else:
                # find the start index in the pattern
                while(idx_in_pattern_r[currentIdx] == -1):
                    currentIdx -= 1
                    if currentIdx == -1:
                        break
                if currentIdx == -1:
                    startIdx_in_pattern = -1
                else:
                    startIdx_in_pattern = idx_in_pattern_r[currentIdx]
                # find the end index in the pattern
                currentIdx = candidateIdx
                while(idx_in_pattern_r[currentIdx] == -1):
                    currentIdx += 1
                    if currentIdx == len(idx_in_pattern_r):
                        break
                if currentIdx == len(idx_in_pattern_r):
                    endIdx_in_pattern = len(patternArr)
                else:
                    endIdx_in_pattern = idx_in_pattern_r[currentIdx]

                # calcualte cost
                cost_min = 1e7
                index_min = -1
                insertEventCount = 0
                for i in range(startIdx_in_pattern + 1, endIdx_in_pattern + 1):
                    patternCur = deepcopy(patternArr)
                    patternCur.insert(i, {'event': e['event'], 'count': 0})
                    patternCur = list(map(lambda e: e['event'], patternCur))

                    residualCur = 0
                    insertEventCountCur = 0
                    for j in range(len(rs['id'])):
                        residualTemp, isMatched = LCS_distance(seq[rs['id'][j]], patternCur, isIdxMatch = i)
                        residualCur += residualTemp
                        if isMatched:
                            insertEventCountCur += 1
                    costCur = len(patternCur) + (th * residualCur) 

                    if costCur < cost_min:
                        cost_min = costCur
                        index_min = i
                        insertEventCount = insertEventCountCur

                if cost_min < rs['cost']:
                    patternArr.insert(index_min, {'event': e['event'], 'count': insertEventCount})
                    rs['cost'] = cost_min
                    rs['residual'] = residualCur
                    rsCur = patternArr
                    idx_in_pattern_r[candidateIdx] = index_min
                    for i in range(candidateIdx + 1, len(idx_in_pattern_r)):
                        if idx_in_pattern_r[i] != -1:
                            idx_in_pattern_r[i] += 1
                    for i in range(len(idx_in_pattern_l)):
                        if idx_in_pattern_l[i] >= index_min:
                            idx_in_pattern_l[i] += 1
                else:
                    break

        rs['pattern'] = list(map(lambda e: e['event'], rsCur))
        rs['pattern_count'] = list(map(lambda e: e['count'], rsCur))
        return rs, overlapTag

    def calbound(l, r, seq_all, events, beta = 1):
        th = 1.2

        distBound, patternBound = LCS_distance(l['pattern'], r['pattern'], True)

        up = l['residual'] + r['residual'] + (l['size'] * abs(len(l['pattern']) - len(patternBound))) + (r['size'] * abs(len(r['pattern']) - len(patternBound)))
        up = up * th + len(patternBound)

        low = 0
        # lower bound, #3 strategy
        #lower bound of cost, assume the common events that appear
        #more than half of time in the sequences are always in the right order 
        counts = merge_count(l['count'], r['count'])
        size = l['size'] + r['size']
        for e in counts:
            for i in range(len(counts[e])):
                low += min(counts[e][i] * th, (size - counts[e][i]) * th + 1)
                # low += counts[e][i] if (counts[e][i] * th) < ((size - counts[e][i]) * th + 1) else size - counts[e][i]

        rs = []
        for i in range(len(patternBound)):
            rs.append({'event': patternBound[i]})
        
        # overlapTag = compareTimeThrough(l, r, rs)
        overlapTag_02 = compareTimeDistribute(l, r, rs)

        return [low-l['cost']-r['cost'] - beta, up-l['cost']-r['cost'] - beta], overlapTag_02

    def lcsMerge(l, r):
        idx_in_pattern_l = [-1 for i in range(len(l['pattern']))]
        idx_in_pattern_r = [-1 for i in range(len(r['pattern']))]
        first = l['pattern']
        second = r['pattern']

        first_length = len(first) + 1
        second_length = len(second) + 1
        distance_matrix = [[0] * second_length for x in range(first_length)]
        for i in range(first_length):
            distance_matrix[i][0] = 0
        for j in range(second_length):
            distance_matrix[0][j] = 0
        for i in range(1, first_length):
            for j in range(1, second_length):
                if first[i-1] == second[j-1]:
                    distance_matrix[i][j] = distance_matrix[i-1][j-1] + 1
                else:
                    distance_matrix[i][j] = max(distance_matrix[i][j-1], distance_matrix[i-1][j])

        rs = []
        candidateArr = []

        i = first_length - 1
        j = second_length - 1
        patternCount = 0
        while i > 0 or j > 0:
            if i == 0:
                for k in range(j):
                    candidateArr.append({'event': second[k], 'count': r['pattern_count'][k], 'pos': k, 'LorR': 'r'})
                break
            if j == 0:
                for k in range(i):
                    candidateArr.append({'event': first[k], 'count': l['pattern_count'][k], 'pos': k, 'LorR': 'l'})
                break
            if first[i-1] == second[j-1]:
                rs.append({'event': first[i-1], 'count': l['pattern_count'][i - 1] + r['pattern_count'][j -1]})
                idx_in_pattern_l[i-1] = patternCount
                idx_in_pattern_r[j-1] = patternCount
                patternCount += 1
                i -= 1
                j -= 1
            elif distance_matrix[i][j-1] > distance_matrix[i-1][j]:
                candidateArr.append({'event': second[j-1], 'count': r['pattern_count'][j-1], 'pos': j-1, 'LorR': 'r'})
                j -= 1
            elif distance_matrix[i][j-1] <= distance_matrix[i-1][j]:
                candidateArr.append({'event': first[i-1], 'count': l['pattern_count'][i-1], 'pos': i-1, 'LorR': 'l'})
                i -= 1
        rs.reverse()
        for i in range(len(idx_in_pattern_l)):
            if idx_in_pattern_l[i] != -1:
                idx_in_pattern_l[i] = len(rs) - 1 - idx_in_pattern_l[i]
        for i in range(len(idx_in_pattern_r)):
            if idx_in_pattern_r[i] != -1:
                idx_in_pattern_r[i] = len(rs) - 1 - idx_in_pattern_r[i]

        candidateArr = sorted(candidateArr, key = lambda e: e['count'], reverse = True)

        # overlapTag = compareTimeThrough(l, r, rs)
        overlapTag_02 = compareTimeDistribute(l, r, rs)

        # rs: store the common pattern
        # candidateArr: store the elements not in pattern
        # idx_in_pattern_l: mark the elements in l corresponding to pattern
        # idx_in_pattern_r: mark the elements in r corresponding to pattern
        return rs, candidateArr, idx_in_pattern_l, idx_in_pattern_r, overlapTag_02

    def compareTimeThrough(l, r, rs) :
        # compare the pattern location in both sequences
        lStart = 0
        lEnd = 1
        rStart = 0
        rEnd = 1
        for i in range(len(l['pattern'])):
            if l['pattern'][i] == rs[0]['event']:
                lStart = i/len(l['pattern'])
                break
        for i in range(len(l['pattern'])):
            if l['pattern'][len(l['pattern']) - 1 - i] == rs[len(rs) - 1]['event']:
                lEnd = (len(l['pattern']) -  i)/len(l['pattern'])
                break
        for i in range(len(r['pattern'])):
            if r['pattern'][i] == rs[0]['event']:
                rStart = i/len(r['pattern'])
                break
        for i in range(len(r['pattern'])):
            if r['pattern'][len(r['pattern']) - 1 - i] == rs[len(rs) - 1]['event']:
                rEnd = (len(r['pattern']) -  i)/len(r['pattern'])
                break

        overlapTag = True
        overlapThershold = 0.3
        if lEnd - lStart >= rEnd - rStart:
            if rEnd < lStart or rStart > lEnd:
                overlapTag = False
            elif rEnd > lStart and rStart < lStart:
                if rEnd - lStart < overlapThershold:
                    overlapTag = False
            elif rStart < lEnd and rEnd > lEnd:
                if lEnd - rStart < overlapThershold:
                    overlapTag = False
            else:
                if rEnd - rStart < overlapThershold:
                    overlapTag = False
        else:
            if lEnd < rStart or lStart > rEnd:
                overlapTag = False
            elif lEnd > rStart and lStart < rStart:
                if lEnd - rStart < overlapThershold:
                    overlapTag = False
            elif lStart < rEnd and lEnd > rEnd:
                if rEnd - lStart < overlapThershold:
                    overlapTag = False
            else:
                if lEnd -lStart < overlapThershold:
                    overlapTag = False
        # ==============================================
        return overlapTag

    def compareTimeDistribute(l, r, rs):
        overlapTag_02 = True
        
        lTimeD = []
        rTimeD = []
        timeRatio = 4

        lIndex = 0
        rIndex = 0
        for i in range(len(rs)):
            for j in range(lIndex, len(l['pattern'])):
                if rs[i]['event'] == l['pattern'][j]:
                    lTimeD.append(j*timeRatio//len(l['pattern']))
                    lIndex = j + 1
                    break
            for k in range(rIndex, len(r['pattern'])):
                if rs[i]['event'] == r['pattern'][k]:
                    rTimeD.append(k*timeRatio//len(r['pattern']))
                    rIndex = k + 1
                    break
        lTimeR = []
        rTimeR = []
        for i in range(timeRatio):
            lCount = 0
            rCount = 0
            for j in range(len(lTimeD)):
                if lTimeD[j] == i:
                    lCount += 1
            for k in range(len(rTimeD)):
                if rTimeD[j] == i:
                    rCount += 1
            lTimeR.append(lCount/len(lTimeD))
            rTimeR.append(rCount/len(rTimeD))

        if sum((x - y)**2 for x, y in zip(lTimeR, rTimeR))**0.5 > 0.6:
            overlapTag_02 = False      

        return overlapTag_02

    def merge(l, r, seq, events, beta = 1):
        rs = {}

        rs['id'] = l['id'] + r['id']
        rs['size'] = l['size'] + r['size']
        rs['residual'] = 0
        rs['count'] = merge_count(l['count'], r['count'])
        rs['pattern'] = []
        rs['cost'] = 1e7
        rs['pattern_count'] = []
        rs['cls'] = l['cls'] + r['cls']

        rs, overlapTag = calPattern(rs, l, r, seq, events)
        return rs, rs['cost']-l['cost']-r['cost'] - beta, overlapTag

    def merge_count(l, r):
        rs = {k: [] for k in l}
        for key in l:
            if len(l[key]) >= len(r[key]):
                for i in range(len(l[key])):
                    rs[key].append(l[key][i])
                for i in range(len(r[key])):
                    rs[key][i] += r[key][i]
            else:
                for i in range(len(r[key])):
                    rs[key].append(r[key][i])
                for i in range(len(l[key])):
                    rs[key][i] += l[key][i]
        return rs

    # calculate the residual sequences for a cluster
    def residual(pattern, ids, seq, events):
        rs = [[{'event': events[j], 'count': 0} for j in range(len(events))] for i in range(len(pattern) + 1)]
        for i in range(len(ids)):
            temp = cal_residual(seq[ids[i]], pattern)
            for j in range(len(pattern) + 1):
                for k in range(len(temp[j])):
                    rs[j][events.index(temp[j][k])]['count'] += 1

        for i in range(len(pattern) + 1):
            rs[i] = filter(lambda e: e['count'] > 0, rs[i])
            rs[i] = sorted(rs[i], key=lambda e: e['count'], reverse = True)

        return rs

    def store_cluster(rs, seq, events):
        return 	{'cost': rs['cost'], 'ids': rs['id'], 'size': rs['size'], 'pattern': [{'seq': rs['pattern'][i], 'count': rs['pattern_count'][i], 'gap': []} for i in range(len(rs['pattern']))], 'residual': residual(rs['pattern'], rs['id'], seq, events)}

    def randomize_lsh_search(arr, seq_all, valid_events, th_lsh, sample_size = 128, beta = 1):

        # initialize lsh 
        # calculate occur time of every event
        vector_all = {}
        for sid in arr:
            vector_all[sid] = arr[sid]['pattern']

        m_all = {}
        for sid in vector_all:
            m_all[sid] = MinHash(num_perm=128)
            for d in vector_all[sid]:
                m_all[sid].update(str(d).encode('utf8'))

        lsh = MinHashLSH(threshold = th_lsh, num_perm = sample_size)
        for sid in m_all:
            # 'sid' for the label to put out, 'm_all' is the sequence data to put in
            lsh.insert(str(sid), m_all[sid]) 

        # main loop
        rs = {}
        count = 0
        # find the longest sequence
        longestSeq = 0
        id_to_merge = ""
        for userkey in arr:
            if len(arr[userkey]['pattern']) > longestSeq:
                longestSeq = len(arr[userkey]['pattern'])
                id_to_merge = userkey
        while(len(arr) > 0):

            # find the candidates ------ similar in minHash
            lsh_candidates = lsh.query(m_all[id_to_merge])
            del lsh_candidates[lsh_candidates.index(id_to_merge)]

            cost_min = 0
            cost_temp = 0
            el = {}
            el_temp = {}
            Tag = {}
            bound = {}

            if len(arr) == 1:
                rs[id_to_merge] = arr[id_to_merge]
                break

            for id_candidates in lsh_candidates:
                if arr[id_to_merge]['size'] == 1 and arr[id_candidates]['size'] == 1:
                    el_temp, cost_temp, Tag[id_candidates] = merge(arr[id_to_merge], arr[id_candidates], seq_all, valid_events, beta = beta)	
                    bound[id_candidates] = [cost_temp, cost_temp]
                else:
                    bound[id_candidates], Tag[id_candidates] = calbound(arr[id_to_merge], arr[id_candidates], seq_all, valid_events, beta = beta)
            if len(bound) > 0:
                minBound = min([bound[key][1] for key in bound])

            # find out which candidate is the best for merging
            for id_candidates in lsh_candidates:
                # take the candidate which minimal LCS distance is less than the element counts difference out of consideration 
                if (bound[id_candidates][0] - minBound) > 0.001 and Tag[id_candidates] == False:
                    continue

                count += 1
                el_temp, cost_temp, overlapTag = merge(arr[id_to_merge], arr[id_candidates], seq_all, valid_events, beta = beta)

                if cost_temp < cost_min:
                    cost_min = cost_temp
                    el = el_temp
                    id_merged = id_candidates

            if cost_min < 0:
                del arr[id_to_merge]
                del arr[id_merged]
                del m_all[id_to_merge]
                del m_all[id_merged]
                lsh.remove(id_to_merge)
                lsh.remove(id_merged)

                arr[el['id'][0]] = el

                vector_temp = el['pattern']
                
                m_all[el['id'][0]] = MinHash(num_perm=128)
                for d in vector_temp:
                    m_all[el['id'][0]].update(str(d).encode('utf8'))
                lsh.insert(el['id'][0], m_all[el['id'][0]]) 

            else:
                rs[id_to_merge] = arr[id_to_merge]
                del arr[id_to_merge]
                del m_all[id_to_merge]
                lsh.remove(id_to_merge)

                # find the longest sequence
                longestSeq = 0
                id_to_merge = ""
                for userkey in arr:
                    if len(arr[userkey]['pattern']) > longestSeq:
                        longestSeq = len(arr[userkey]['pattern'])
                        id_to_merge = userkey

        return rs

    def computeClusterRes(arr, seq_all, valid_events, startT):
        rs = []
        for key in arr:
            rs.append(store_cluster(arr[key], seq_all, valid_events))

        if len(rs) > 2:
            startT = time()
            # sort the clusters by the similarity of their patterns
            patterns = {str(i): [rs[i]['pattern'][j]['seq'] for j in range(len(rs[i]['pattern']))] for i in range(len(rs))}

            # build the hierachy tree
            dist = dist_matrix(distance, patterns)
            order, tree = cluster_hierarchy(dist['matrix'])
            _nodes = [list(dist['nodes'])[order[i]] for i in range(len(list(dist['nodes'])))]
            result = []
            for i in range(len(_nodes)):
                result.append(rs[int(_nodes[i])])
            rs= result

            # append the similarity matrix
            for i in range(len(_nodes)):
                rs[i]['orders'] = []
                for j in range(len(_nodes)):
                    rs[i]['orders'].append(dist['matrix'][list(dist['nodes']).index(_nodes[i])][list(dist['nodes']).index(_nodes[j])])
        
        startT = time()
        # add label residual
        data_cluster = rs
        for i in range(len(data_cluster)):
            cluster = data_cluster[i]
            cluster['seqs'] = {}

            pattern = list(map(lambda e: e['seq'], cluster['pattern']))
            for j in range(len(cluster['ids'])):
                seq = seq_all[cluster['ids'][j]] 
                
                labels = label_residual(seq, pattern)
                cluster['seqs'][cluster['ids'][j]] = []
                for k in range(len(seq)):
                    cluster['seqs'][cluster['ids'][j]].append({'type': seq[k], 'isRes': labels[k]})

                data_cluster[i] = cluster

        return data_cluster
    # extract all the exquences and feature
    seq_all = {}
    for key in infoAll_All['seqs']:
        if len(infoAll_All['seqs'][key]) > 0:
            seq_all[key] = infoAll_All['seqs'][key]
    valid_events = infoAll_All['events']

    arr = {}
    for key in seq_all:
        arr[key] = cal_leaf_feature(key, seq_all[key], valid_events)

    startT = time()
    # main loop
    th_lsh = 0.001
    beta = 1
    arr = randomize_lsh_search(arr, seq_all, valid_events, th_lsh, sample_size = 128, beta = beta)
    data_cluster = computeClusterRes(arr, seq_all, valid_events, startT)


    cluster_Set = []
    for i in range(len(data_cluster)):
        cluster_Pattern = []
        for j in range(len(data_cluster[i]['pattern'])):
            cluster_Pattern.append(data_cluster[i]['pattern'][j]['seq'])
        cluster_Set.append({'userid': data_cluster[i]['ids'], 'pattern': cluster_Pattern})

    clusterRes = [ 0 for i in cluster_Set]
    clusterNumLimit = 6
    similarityLimit = 0.9
    initialClusterNum = 0
    final_Cluster_Set = []
    lowestSim = 0.7
    
    labelType = list(Counter(clusterRes).keys())
    for i in range(len(clusterRes)):
        if clusterRes[i] == -1:
            final_Cluster_Set.append(i)
            initialClusterNum += 1

    for i in range(len(labelType)):
        labelSet = []
        if labelType[i] != -1:
            for j in range(len(clusterRes)):
                if clusterRes[j] == labelType[i]:
                    labelSet.append(j)
            initialClusterNum += 1

            comPattern_Set = []
            for index in range(len(labelSet)):
                comPattern_Set.append([labelSet[index], cluster_Set[labelSet[index]]['pattern']])
            comPattern_Set = sorted(comPattern_Set, key=lambda e: len(e[1]), reverse=True)
            print(comPattern_Set)

            while (final_Cluster_Set == [] or initialClusterNum > clusterNumLimit) and similarityLimit > lowestSim:
                final_Cluster_Set = []
                if len(comPattern_Set) > 1:
                    startSeq = 0
                    exceptIndex = [0]
                    while startSeq < len(comPattern_Set) - 1:
                        # Choose the longest pattern as the baseline
                        newCluster = [comPattern_Set[startSeq][0]]
                        for index in range(startSeq+1 , len(comPattern_Set)):
                            if index not in exceptIndex:
                                countRep = 0
                                lastIndex = len(comPattern_Set[startSeq][1]) - 1
                                for seqIndex in range(len(comPattern_Set[index][1])):
                                    for startSeqIndex in range(len(comPattern_Set[startSeq][1]) - 1 - lastIndex, len(comPattern_Set[startSeq][1])):
                                        if comPattern_Set[startSeq][1][len(comPattern_Set[startSeq][1]) - 1 - startSeqIndex] == comPattern_Set[index][1][len(comPattern_Set[index][1]) - 1 - seqIndex]:
                                            countRep += 1
                                            lastIndex = len(comPattern_Set[startSeq][1]) - 1 - startSeqIndex
                                if countRep/len(comPattern_Set[index][1]) > similarityLimit and len(comPattern_Set[startSeq][1])/ len(comPattern_Set[index][1]) < 3.5:
                                    exceptIndex.append(index)
                                    newCluster.append(comPattern_Set[index][0])
                        for i in range(startSeq+1 , len(comPattern_Set)):
                            if i not in exceptIndex:
                                startSeq = i
                                break
                            elif i == len(comPattern_Set) - 1:
                                startSeq = len(comPattern_Set)

                        if startSeq == len(comPattern_Set) - 1:
                            final_Cluster_Set.append(comPattern_Set[startSeq][0])
                        if len(newCluster) < 2:
                            final_Cluster_Set.append(newCluster[0])
                        else:
                            final_Cluster_Set.append(newCluster)
                else:
                    final_Cluster_Set.append(comPattern_Set[0][0])
                initialClusterNum = 0
                for item in final_Cluster_Set:
                    initialClusterNum += 1
                similarityLimit = similarityLimit - 0.05

    final_Cluster_Data = []
    for clusterIndex in range(len(final_Cluster_Set)):
        if type(final_Cluster_Set[clusterIndex]) is int:
            final_Cluster_Data.append(cluster_Set[final_Cluster_Set[clusterIndex]])
        else:
            userid_Set = []
            for subCluster in final_Cluster_Set[clusterIndex]:
                for userid in cluster_Set[subCluster]['userid']:
                    userid_Set.append(userid)
            pattern_Example = cluster_Set[final_Cluster_Set[clusterIndex][0]]['pattern']

            final_Cluster_Data.append({'userid': userid_Set, 'pattern': pattern_Example})

    with open("./cache/" + problemid + '/' + problemid + '_cluster', 'w') as f:
        # json.dump(final_Cluster_Data, f)
        f.write(str({"data":final_Cluster_Data, "fullSeq": data}))
    return str({"data":final_Cluster_Data, "fullSeq": data})
    ##################