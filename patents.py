
def is_utility_patent(patentNum):
    if patentNum[0:2] =='US':
        patentNum = patentNum[2:] #skip initial 'US'
    print('patentNum=',patentNum)
    if patentNum.startswith('D') or patentNum.startswith('P'):
        return False
    else:
        return True
