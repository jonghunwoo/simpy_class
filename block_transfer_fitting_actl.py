import simpy
import random
import functools
import scipy.stats as st
import numpy as np
import pandas as pd
import time
from SimComponents_for_simulation_fitting import Sink, Process, Monitor, Source
from collections import OrderedDict
import matplotlib.pyplot as plt

start = time.time()
env = simpy.Environment()
RUN_TIME = 10000

#samp_dist = functools.partial(random.expovariate, 1)
samp_dist = 1

def generator():
    while True:
        dict = OrderedDict()
        temp_iat = st.chi2.rvs(df=1.53, loc=-0, scale=0.22, )
        IAT_assy = np.floor(temp_iat)
        proc_assy = 0
        while proc_assy <= 0:
            proc_assy = np.round(st.exponnorm.rvs(K=7.71, loc=2.40, scale=1.70))

        proc_oft = np.round(st.chi2.rvs(df=1.63, loc=1.00, scale=7.43))
        IAT_oft = 0
        while IAT_oft <= 0:
            IAT_oft = st.expon.rvs(loc=-3.00, scale=9.25)

        IAT_pnt = 0
        while IAT_pnt <= 0:
            IAT_pnt = st.exponnorm.rvs(K=5.33, loc=0.73, scale=2.3)
        proc_pnt = 0
        while proc_pnt <= 0:
            proc_pnt = np.round(st.exponnorm.rvs(K=1.75, loc=8.53, scale=2.63))

        dict["Assembly"] = [IAT_assy, proc_assy]
        #dict["Outfitting"] = [IAT_oft, proc_oft]
        dict["Outfitting"] = [0, proc_oft]
        #dict["Painting"] = [IAT_pnt, proc_pnt]
        dict["Painting"] = [0, proc_pnt]

        yield dict


data_gen = generator()

m_assy = 295
m_oft = 282
m_pnt = 232

Source = Source(env, "Source", data_gen, initial_delay=0)
Sink = Sink(env, "Sink", debug=False, rec_arrivals=True)
Assembly = Process(env, "Assembly", m_assy, qlimit=10000)  # 조립 공정 작업장 수 = 200
Outfitting = Process(env, "Outfitting", m_oft, qlimit=10000)  # 의장 공정 작업장 수 = 185
Painting = Process(env, "Painting", m_pnt, qlimit=10000)  # 도장 공정 작업장 수 = 155

Monitor1 = Monitor(env, Assembly, samp_dist)
Monitor2 = Monitor(env, Outfitting, samp_dist)
Monitor3 = Monitor(env, Painting, samp_dist)
Monitor4 = Monitor(env, Sink, samp_dist)

# Connection
Source.out = Assembly
Assembly.out = Outfitting
Outfitting.out = Painting
Painting.out = Sink

# Run it
env.run(until=RUN_TIME)


print('#'*80)
print("Results of simulation")
print('#'*80)

# 코드 실행 시간
print("time :", time.time() - start)

# 총 리드타임 - 마지막 part가 Sink에 도달하는 시간
print("Total Lead Time : ", Sink.last_arrival)

total_assy = (Assembly.finish_time - Assembly.start_time[0]) * m_assy
total_oft = (Outfitting.finish_time - Outfitting.start_time[0]) * m_oft
total_pnt = (Painting.finish_time - Painting.start_time[0]) * m_pnt

print("utilization of Assembly : {}".format(Assembly.working_time/total_assy))
print("utilization of Outfitting : {}".format(Outfitting.working_time/total_oft))
print("utilization of Painting : {}".format(Painting.working_time/total_pnt))

# 각 공정에서 후행공정으로 넘긴 블록의 수
print(Assembly.parts_rec, Outfitting.parts_rec, Painting.parts_rec)

# M
'''plt.plot(Monitor1.time[:200], Monitor1.M[:200])
plt.xlabel("time")
plt.ylabel("m")
plt.title("Assembly")
plt.show()

plt.plot(Monitor2.time[:200], Monitor2.M[:200])
plt.xlabel("time")
plt.ylabel("m")
plt.title("Outfitting")
plt.show()

plt.plot(Monitor3.time[:200], Monitor3.M[:200])
plt.xlabel("time")
plt.ylabel("m")
plt.title("Painting")
plt.show()'''

# WIP
'''plt.plot(Monitor1.time[:200], Monitor1.WIP[:200])
plt.xlabel("time")
plt.ylabel("WIP")
plt.title("Assembly")
plt.show()

plt.plot(Monitor2.time[:200], Monitor2.WIP[:200])
plt.xlabel("time")
plt.ylabel("WIP")
plt.title("Outfitting")
plt.show()

plt.plot(Monitor3.time[:200], Monitor3.WIP[:200])
plt.xlabel("time")
plt.ylabel("WIP")
plt.title("Painting")
plt.show()'''


# TH
plt.plot(Monitor4.TH_time, Monitor4.TH)
plt.xlabel("time")
plt.ylabel("TH")
plt.show()

# Source에서 part 보내는 정도
part_list = []
for i in range(len(Source.start_time_list)):
    part_list.append(i)

plt.plot(Source.start_time_list, part_list)
plt.xlabel("time")
plt.ylabel("part")
plt.show()

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
ax2.set_ylabel('WIP')
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

######### 추가한 코드
writer = pd.ExcelWriter('./data/block_transfer_result.xlsx', engine='xlsxwriter')
# IAT, 각 공정의 process time 저장 후 excel로 출력
part_dict = {}
name_list = ["Assembly", "Outfitting", "Painting"]
for name in name_list:
    part_dict[name] = []
for i in range(len(Sink.proc_list)):
    for name in name_list:
        part_dict[name].append(Sink.proc_list[i][name + " proc time"])

df_part = pd.DataFrame()
df_part["IAT"] = Sink.IAT_list
for name in name_list:
    df_part[name] = part_dict[name]

df_part.to_excel(writer, sheet_name='process time')

# Monitor 결과를 excel로 출력
df_monitor = pd.DataFrame()
df_monitor["WIP_q_assy"] = Monitor1.WIP
df_monitor["m_assy"] = Monitor1.M
df_monitor["WIP_q_oft"] = Monitor2.WIP
df_monitor["m_oft"] = Monitor2.M
df_monitor["WIP_q_pnt"] = Monitor3.WIP
df_monitor["m_pnt"] = Monitor3.M

df_monitor.to_excel(writer, sheet_name='Monitor 결과')

# TH를 excel로 출력
df_TH = pd.DataFrame()
df_TH["time"] = Monitor4.TH_time
df_TH["TH"] = Monitor4.TH

df_TH.to_excel(writer, sheet_name='TH')

writer.close()

# 공정 별  {t 시점까지의 (total input - total output) = t 시점의 작업중인 작업장 수 + WIP_q} 확인
temp_list = []
for i in range(len(Monitor1.time)):
    temp = (Monitor2.input_list[i] - Monitor2.output_list[i]) - (Monitor2.M[i] + Monitor2.WIP[i])
    temp_list.append(temp)

print(temp_list)