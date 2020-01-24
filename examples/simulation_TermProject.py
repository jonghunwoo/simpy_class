import pandas as pd
import datetime
import operator

# location code를 key값으로 가지고, 이외의 정보들을 저장한 list를 value값으로 가지는 dictionary
block_name = []

# 데이터 가공 전
block_project = {}
block_project_2 = {}

# activity 종류
activity = []

data1 = pd.read_excel('./data/MCM_ACTIVITY.xls')

# STARTDATE의 자료형을 계산의 편의성을 위해 datetime 형식으로 바꾸어줌
pd.to_datetime(data1['PLANSTARTDATE'], unit='s')

# 처음 시작 날짜 - 보완할 점 : 직접 입력 형식이 아닌 min 찾아주는 것 - 이후에
initial_date_str = '2018-12-10 00:00:00'
initial_date = datetime.datetime.strptime(initial_date_str, '%Y-%m-%d %H:%M:%S')

# 전체 data의 개수
data_num = len(data1)

'''
딕셔너리의 키값 -> '호선번호 블럭번호'를 키값으로 가지는 하나의 딕셔너리로 만들어보기 아직 안함 
'''

# 데이터 받아오기
for i in range(data_num):
    project = data1.loc[i]  # 한 행 읽어주기
    proj_name = project.PROJECTNO  # 호선 번호
    proj_block = project.LOCATIONCODE  # block code
    activity_code = project.ACTIVITYCODE[5:]

    # 2005년도 자료 + ACTIVITYCODE가 '#'으로 시작하는 데이터는 버림
    if (project.PLANSTARTDATE.year >= 2018) and (proj_block != 'OOO'):
        # 호선 이름을 key값으로 갖는 dictionary 만들어주기 -> value는 블럭 이름을 키값으로 갖는 딕셔너리
        if proj_name not in block_name:
            block_name.append(proj_name)
            block_project[proj_name] = {}
            block_project_2[proj_name] = {}
        if proj_block not in block_project[proj_name].keys():
            # 블럭 이름을 키값으로 갖는 dictionary 만들어주기 -> value는 각 activitycode, 시작, 종료 날짜를 기록한 list를 담을 수 있는 list
            # location code : {ACTIVITYCODE : start date, finish date}
            block_project[proj_name][proj_block] = {}
            block_project_2[proj_name][proj_block] = {}

        # 시작 날짜 = 0으로 하여 일 기준으로 시간 차이 계산해 줌
        del_day = project.PLANSTARTDATE - initial_date   # + datetime.timedelta(days=1)

        if activity_code not in activity:
            activity.append(activity_code)

        # [시작 시간 간격, 총 공정 시간]
        block_project[proj_name][proj_block][activity_code] = [del_day.days, project.PLANDURATION]
        block_project_2[proj_name][proj_block][activity_code] = [del_day.days, project.PLANDURATION]


# 날짜 순서대로 정리
for name in block_name:
    for location_code in block_project[name].keys():
        # 시작 날짜 기준으로 정렬해 줌
        process_sorted = sorted(block_project[name][location_code].items(), key=lambda x: x[1][0])
        process_sorted_2 = sorted(block_project_2[name][location_code].items(), key=lambda x: x[1][0])
        block_project[name][location_code] = process_sorted
        block_project_2[name][location_code] = process_sorted_2


# 첫 공정 시작 시간 순서로 정렬
for name in block_name:
    block_list = list(block_project[name].items())
    block_sorted = sorted(block_list, key=lambda x: x[1][0][1][0])
    block_project[name] = block_sorted

    block_list_2 = list(block_project_2[name].items())
    block_sorted_2 = sorted(block_list_2, key=lambda x: x[1][0][1][0])
    block_project_2[name] = block_sorted_2


# block간 시작 시간 간격 / 처음 = 0 / i번째 : i - (i-1)
IAT = {}
for name in block_name:
    IAT[name] = []
    for i in range(len(block_project[name])):
        if i == 0:
            IAT[name].append(0)
        else:
            del_AT = block_project[name][i][1][0][1][0] - block_project[name][i-1][1][0][1][0]
            IAT[name].append(del_AT)
    dict_block = dict(block_project_2[name])
    block_project_2[name] = dict_block

# 잘라주기
for name in block_name:
    for location_code in block_project_2[name].keys():
        for i in range(0, len(block_project_2[name][location_code])-1):
            # 선행 공정의 끝나는 시간
            date1 = block_project_2[name][location_code][i][1][0] + block_project_2[name][location_code][i][1][1] - 1
            # 후행 공정의 시작 시간
            date2 = block_project_2[name][location_code][i+1][1][0]
            # 후행 공정의 끝나는 시간
            date3 = block_project_2[name][location_code][i+1][1][0] + block_project_2[name][location_code][i+1][1][1] - 1

            if date1 > date2:  # 선행공정이 후행공정보다 늦게 끝날 때
                if date1 < date3:  # 선행 공정이랑 후행 공정이랑 겹칠 때
                    block_project_2[name][location_code][i+1][1][0] = date1
                else:  # 포함될 때
                    block_project_2[name][location_code][i+1][1][0] = date1
                    block_project_2[name][location_code][i+1][1][1] = 1
                    block_project_2[name][location_code][i+1][1].append("##")

for name in block_name:
    for location_code in block_project_2[name].keys():
        sso_1 = []
        for i in range(0, len(block_project_2[name][location_code])):
            if len(block_project_2[name][location_code][i][1]) < 3:
                sso_1.append(block_project_2[name][location_code][i])
        block_project_2[name][location_code] = dict(sso_1)

# print(block_project)
# print(IAT)
# print(activity)
########################################################################################################################
import simpy
import random
from collections import OrderedDict
from SimComponents_TermProject import DataframeSource, Sink, Process
import matplotlib.pyplot as plt


# IAT data와 block data를 하나씩 차례대로 생성하는 generator 객체 생성
def gen_schedule(inter_arrival):
    project = list(inter_arrival.keys())[0]
    for i in range(len(inter_arrival[project])):
        yield inter_arrival[project][i]


def gen_block_data(block_data):
    project = list(block_data.keys())[0]
    idx = list(block_data[project].keys())
    for i in range(len(idx)):
        location_code = idx[i]
        activity = OrderedDict(block_data[project][location_code])
        '''
        for j in range(len(block_data[project][location_code])):
            activity[block_data[project][location_code][j][0]] = block_data[project][location_code][j][1]
        '''
        yield [project, location_code, activity]


a = gen_schedule(IAT)
b = gen_block_data(block_project_2)


#시뮬레이션 시작
random.seed(42)

RUN_TIME = 45000

env = simpy.Environment()

process_dict = {}
Source = DataframeSource(env, "Source", a, b, process_dict)
Sink = Sink(env, 'Sink', debug=False, rec_arrivals=True)

process = []
for i in range(len(activity)):
    process.append(Process(env, activity[i], 10, process_dict, 10))

for i in range(len(activity)):
    process_dict[activity[i]] = process[i]

process_dict['Sink'] = Sink

env.run(until=RUN_TIME)

print('#'*80)
print("Results of simulation")
print('#'*80)

print(len(block_project_2['U611']))
print(len(Sink.waits))
#계획 데이터 예시
print(block_project_2['U611']['A11C'])
#시뮬레이션 결과 생성된 데이터 예시
print(Sink.block_project_sim['U611']['A11C'])



#### WIP 계산

process_time = Sink.last_arrival
WIP = [0 for i in range(process_time)]

# for name in block_name:
for location_code in Sink.block_project_sim['U611'].keys():
    p = dict(Sink.block_project_sim['U611'][location_code])
    q = list(p.items())
    Sink.block_project_sim['U611'][location_code] = q
    for i in range(0, len(Sink.block_project_sim['U611'][location_code])-1):
        ###선행공정 끝나는 시간
        date1 = Sink.block_project_sim['U611'][location_code][i][1][0] + Sink.block_project_sim['U611'][location_code][i][1][1] -1
        ###후행공정 시작하는 시간
        date2 = Sink.block_project_sim['U611'][location_code][i+1][1][0]
        lag = date2-date1
        if lag > 3:
            for j in range(date1, date2):
                WIP[j] += 1

plt.plot(WIP)
plt.xlabel('time')
plt.ylabel('WIP')
plt.title('WIP')
plt.show()

fig, axis = plt.subplots()
axis.hist(Sink.waits, bins=100, density=True)
axis.set_title("Histogram for waiting times")
axis.set_xlabel("time")
axis.set_ylabel("normalized frequency of occurrence")
plt.show()

fig, axis = plt.subplots()
axis.hist(Sink.arrivals, bins=100, density=True)
axis.set_title("Histogram for Sink Interarrival times")
axis.set_xlabel("time")
axis.set_ylabel("normalized frequency of occurrence")
plt.show()