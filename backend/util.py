def levenshtein_distance(first, second):
    """Find the Levenshtein distance between two lists."""
    if len(first) > len(second):
        first, second = second, first
    if len(second) == 0:
        return len(first)
    first_length = len(first) + 1
    second_length = len(second) + 1
    distance_matrix = [[0] * second_length for x in range(first_length)]
    for i in range(first_length):
       distance_matrix[i][0] = i
    for j in range(second_length):
       distance_matrix[0][j]=j
    for i in range(1, first_length):
        for j in range(1, second_length):
            deletion = distance_matrix[i-1][j] + 1
            insertion = distance_matrix[i][j-1] + 1
            substitution = distance_matrix[i-1][j-1]
            if first[i-1] != second[j-1]:
                substitution += 1
            distance_matrix[i][j] = min(insertion, deletion, substitution)
    return distance_matrix[first_length-1][second_length-1]

def LCS_distance(first, second, isSeq = False, isIdxMatch = -1):
    isMatched = False

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

    if isSeq == False and isIdxMatch == -1:
        return len(first) + len(second) - (2 * distance_matrix[first_length - 1][second_length - 1])
    else:
        # trace back
        rs = []
        i = first_length - 1
        j = second_length - 1
        while i > 0 or j > 0:
            if i == 0:
                break
            if j == 0:
                break
            if first[i-1] == second[j-1]:
                if j-1 == isIdxMatch:
                    isMatched = True
                rs.append(first[i-1])
                i -= 1
                j -= 1
            elif distance_matrix[i][j-1] > distance_matrix[i-1][j]:
                j -= 1
            elif distance_matrix[i][j-1] <= distance_matrix[i-1][j]:
                i -= 1
        rs.reverse()

        if isSeq and isIdxMatch == -1:
            return len(first) + len(second) - (2 * distance_matrix[first_length - 1][second_length - 1]), rs
        elif isSeq == False and isIdxMatch != -1:
            return len(first) + len(second) - (2 * distance_matrix[first_length - 1][second_length - 1]), isMatched
        elif isSeq and isIdxMatch != -1:
            return len(first) + len(second) - (2 * distance_matrix[first_length - 1][second_length - 1]), rs, isMatched

def cal_residual(first, second):
    # calculate the residual of first with respect to second
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

    # trace back
    rs = [[] for i in range(second_length)]
    i = first_length - 1
    j = second_length - 1
    while i > 0 or j > 0:
        if i == 0:
            break
        if j == 0:
            for k in range(i):
                rs[0].append(first[k])
            break
        if first[i-1] == second[j-1]:
            i -= 1
            j -= 1
        elif distance_matrix[i][j-1] > distance_matrix[i-1][j]:
            j -= 1
        elif distance_matrix[i][j-1] <= distance_matrix[i-1][j]:
            rs[j].append(first[i-1])
            i -= 1

    return rs

def label_residual(first, second):
    # label the residual positions of first with respect to second
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

    # trace back
    rs = [False for i in range(first_length - 1)]
    i = first_length - 1
    j = second_length - 1
    while i > 0 or j > 0:
        if i == 0:
            break
        if j == 0:
            for k in range(i):
                rs[k] = True
            break
        if first[i-1] == second[j-1]:
            i -= 1
            j -= 1
        elif distance_matrix[i][j-1] > distance_matrix[i-1][j]:
            j -= 1
        elif distance_matrix[i][j-1] <= distance_matrix[i-1][j]:
            rs[i-1] = True
            i -= 1

    return rs

def extract_sequence(events, valid_events = [], timegap = False):
    # seq = filter(lambda e: e['Type'] == 'DTC' and e['Timestamp'] != None, events)
    seq = filter(lambda e: (e['Type'] == 'DTC' or e['Type'] == 'Symptom') and e['Timestamp'] != None, events)
    seq = sorted(seq, key=lambda e: e['Timestamp'])
    seq = map(lambda e: {'type': e['Description']['L1'] + '_' + e['Description']['L2'], 'Timestamp': e['Timestamp']}, seq)
    if len(valid_events) != 0:
        seq = filter(lambda e: e['type'] in valid_events, seq)

    result = list(map(lambda e: e['type'], seq))

    if timegap == True:
        if len(seq) > 1:
            for i in range(len(seq) - 1):
                timegap = seq[i + 1]['Timestamp'] - seq[i]['Timestamp']
                if timegap < 60:
                    result.insert(2 * i + 1, 'gap_min')
                elif timegap >= 60 and timegap < 3600:
                    result.insert(2 * i + 1, 'gap_hour')
                elif timegap >= 3600 and timegap < 3600*24:
                    result.insert(2 * i + 1, 'gap_day')
                elif timegap >= 3600*24 and timegap < 3600*24*7:
                    result.insert(2 * i + 1, 'gap_week')
                else: 
                    result.insert(2 * i + 1, 'gap_weeks')
    
    return result



if __name__ == "__main__":
    print(LCS_distance(['u3000', 'u3000', 'b108e', 'u3000', 'p00c6', 'p1707', 'u0010', 'u0010', 'u0010', 'u0064', 'u0064', 'p065c', 'b12cd', 'u0447', 'u3000', 'u0011', 'u3003'], \
        ['u3000', 'p00c6', 'p1707', 'u0064', 'u0064', 'p065c', 'b12cd', 'u0447', 'u0011'], True))
    print(levenshtein_distance(['u3000', 'u3000', 'b108e', 'u3000', 'p00c6', 'p1707', 'u0010', 'u0010', 'u0010', 'u0064', 'u0064', 'p065c', 'b12cd', 'u0447', 'u3000', 'u0011', 'u3003'], \
        ['u3000', 'p00c6', 'p1707', 'u0064', 'u0064', 'p065c', 'b12cd', 'u0447', 'u0011']))
    