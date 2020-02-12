import random
import pandas as pd
import functools
import simpy
from collections import OrderedDict
from SimComponents_for_simulation_data import DataframeSource, Sink, Process, Monitor
import time
import matplotlib.pyplot as plt

start = time.time()

data_all = pd.read_csv('./data/block_transfer.csv', encoding='euc-kr')
data_temp = data_all[["AAS_CAL", "AA_DATEDIF", "OAS_CAL", "OA_DATEDIF", "PAS_CAL", "PA_DATEDIF"]]
data = data_temp.iloc[:]

data["AAS_CAL"] = pd.to_datetime(data["AAS_CAL"], format='%Y-%m-%d')
data["OAS_CAL"] = pd.to_datetime(data["OAS_CAL"], format='%Y-%m-%d')
data["PAS_CAL"] = pd.to_datetime(data["PAS_CAL"], format='%Y-%m-%d')

data = data[data["AA_DATEDIF"] != 0]
data = data[data["OA_DATEDIF"] != 0]
data = data[data["PA_DATEDIF"] != 0]

data = data[(data["AAS_CAL"].dt.year >= 2015) & (data["AAS_CAL"].dt.year <= 2016)]
#data = data[(data["OAS_CAL"].dt.year >= 2015) & (data["OAS_CAL"].dt.year <= 2016)]
#data = data[(data["PAS_CAL"].dt.year >= 2015) & (data["PAS_CAL"].dt.year <= 2016)]

'''AA_DATEDIF_avg = data[data["AA_DATEDIF"] != 0].mean(axis=0)["AA_DATEDIF"]
OA_DATEDIF_avg = data[data["OA_DATEDIF"] != 0].mean(axis=0)["OA_DATEDIF"]
PA_DATEDIF_avg = data[data["PA_DATEDIF"] != 0].mean(axis=0)["PA_DATEDIF"]
data["AA_DATEDIF"] = data["AA_DATEDIF"].apply(lambda x: AA_DATEDIF_avg if x != 0 else x)
data["OA_DATEDIF"] = data["OA_DATEDIF"].apply(lambda x: OA_DATEDIF_avg if x != 0 else x)
data["PA_DATEDIF"] = data["PA_DATEDIF"].apply(lambda x: PA_DATEDIF_avg  if x != 0 else x)'''

initial_date = data["AAS_CAL"].min()

data["AAS_CAL"] = (data["AAS_CAL"] - initial_date).dt.days
data["OAS_CAL"] = (data["OAS_CAL"] - initial_date).dt.days
data["PAS_CAL"] = (data["PAS_CAL"] - initial_date).dt.days

data.sort_values(by=["AAS_CAL"], inplace=True)
data.reset_index(drop=True, inplace=True)

#samp_dist = functools.partial(random.expovariate, 1) # need to be checked
samp_dist = 1

def generator(dataframe):
    for i in range(len(dataframe)):
        data = dataframe.iloc[i]
        dict = OrderedDict()
        dict["Assembly"] = [data["AAS_CAL"], data["AA_DATEDIF"]]
        dict["Outfitting"] = [data["OAS_CAL"], data["OA_DATEDIF"]]
        dict["Painting"] = [data["PAS_CAL"], data["PA_DATEDIF"]]
        yield dict


data_gen = generator(data)

env = simpy.Environment()

m_assy = 330
m_oft = 300
m_pnt = 250

Source = DataframeSource(env, "Source", data_gen)
Sink = Sink(env, 'Sink', debug=False, rec_arrivals=True)
Assembly = Process(env, "Assembly", m_assy, qlimit=10000)
Outfitting = Process(env, "Outfitting", m_oft, qlimit=10000)
Painting = Process(env, "Painting", m_pnt, qlimit=10000)

Source.out = Assembly
Assembly.out = Outfitting
Outfitting.out = Painting
Painting.out = Sink

Monitor1 = Monitor(env, Assembly, samp_dist)
Monitor2 = Monitor(env, Outfitting, samp_dist)
Monitor3 = Monitor(env, Painting, samp_dist)
Monitor4 = Monitor(env, Sink, samp_dist)

 # 시작 시간 저장

# Run it

env.run(1200)

print("time :", time.time() - start)

total_assy = (Assembly.finish_time - Assembly.start_time[0]) * m_assy
total_oft = (Outfitting.finish_time - Outfitting.start_time[0]) * m_oft
total_pnt = (Painting.finish_time - Painting.start_time[0]) * m_pnt

print("utilization of Assembly : {}".format(Assembly.working_time/total_assy))
print("utilization of Outfitting : {}".format(Outfitting.working_time/total_oft))
print("utilization of Painting : {}".format(Painting.working_time/total_pnt))

# Source에서 part 보내는 정도
'''part_list = []
for i in range(len(Source.start_time_list)):
    part_list.append(i)

plt.plot(Source.start_time_list, part_list)
plt.xlabel("time")
plt.ylabel("part")
plt.show()'''

## 시간에 따른 작업장 사용률
'''plt.plot(Monitor1.time, Monitor1.M)
plt.xlabel("time")
plt.ylabel("m")
plt.title("Assembly")
plt.show()

plt.plot(Monitor2.time, Monitor2.M)
plt.xlabel("time")
plt.ylabel("m")
plt.title("Outfitting")
plt.show()

plt.plot(Monitor3.time, Monitor3.M)
plt.xlabel("time")
plt.ylabel("m")
plt.title("Painting")
plt.show()'''

## WIP 수준
'''plt.plot(Monitor1.time, Monitor1.WIP)
plt.xlabel("time")
plt.ylabel("WIP")
plt.title("Assembly")
plt.show()

plt.plot(Monitor2.time, Monitor2.WIP)
plt.xlabel("time")
plt.ylabel("WIP")
plt.title("Outfitting")
plt.show()

plt.plot(Monitor3.time, Monitor3.WIP)
plt.xlabel("time")
plt.ylabel("WIP")
plt.title("Painting")
plt.show()'''

'''plt.plot(Monitor4.TH_time, Monitor4.TH)
plt.xlabel("time")
plt.ylabel("TH")
plt.show()'''


## input part 개수 + 가동중인 m의 개수
input_assy = []
input_oft = []
input_pnt = []
for i in range(len(Monitor1.input_list)):
    if i == 0:
        input_assy.append(Monitor1.input_list[0])
        input_oft.append(Monitor2.input_list[0])
        input_pnt.append(Monitor3.input_list[0])
    else:
        input_assy.append(Monitor1.input_list[i] - Monitor1.input_list[i-1])
        input_oft.append(Monitor2.input_list[i] - Monitor2.input_list[i-1])
        input_pnt.append(Monitor3.input_list[i] - Monitor3.input_list[i-1])


fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
data_y11 = ax1.plot(Monitor1.time, Monitor1.M, color='b', linestyle='-.', marker='o', label='M')
data_y12 = ax1.plot(Monitor1.time, input_assy, 'r', label='# of input')
data_y2 = ax2.plot(Monitor1.time, Monitor1.WIP, color='g', linestyle='--', marker='s', label='WIP')
ax1.set_xlabel('time')
ax1.set_ylabel('part')
ax2.set_ylabel('WIP_q')
data_y = data_y11 +data_y2 + data_y12
labels = [l.get_label() for l in data_y]
plt.title('Assembly')
plt.legend(data_y, labels, loc=1)
plt.show()

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
data_y11 = ax1.plot(Monitor2.time, Monitor2.M, color='b', linestyle='-.', marker='o', label='M')
data_y12 = ax1.plot(Monitor2.time, input_oft, 'r', label='# of input')
data_y2 = ax2.plot(Monitor2.time, Monitor2.WIP, color='g', linestyle='--', marker='s', label='WIP')
ax1.set_xlabel('time')
ax1.set_ylabel('part')
ax2.set_ylabel('WIP')
data_y = data_y11 +data_y2 + data_y12
labels = [l.get_label() for l in data_y]
plt.title('Outfitting')
plt.legend(data_y, labels, loc=1)
plt.show()

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
data_y11 = ax1.plot(Monitor3.time, Monitor3.M, color='b', linestyle='-.', marker='o', label='M')
data_y12 = ax1.plot(Monitor3.time, input_pnt, 'r', label='# of input')
data_y2 = ax2.plot(Monitor3.time, Monitor3.WIP, color='g', linestyle='--', marker='s', label='WIP')
ax1.set_xlabel('time')
ax1.set_ylabel('part')
ax2.set_ylabel('WIP')
data_y = data_y11 +data_y2 + data_y12
labels = [l.get_label() for l in data_y]
plt.title('Painting')
plt.legend(data_y, labels, loc=1)
plt.show()

'''temp_list = []
for i in range(len(Monitor1.time)):
    temp = (Monitor1.input_list[i] - Monitor1.output_list[i]) - (Monitor1.M[i] + Monitor1.WIP[i])
    temp_list.append(temp)

print(temp_list)'''