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

initial_date = data["AAS_CAL"].min()

data["AAS_CAL"] = (data["AAS_CAL"] - initial_date).dt.days
data["OAS_CAL"] = (data["OAS_CAL"] - initial_date).dt.days
data["PAS_CAL"] = (data["PAS_CAL"] - initial_date).dt.days

data.sort_values(by=["AAS_CAL"], inplace=True)
data.reset_index(drop=True, inplace=True)

samp_dist = functools.partial(random.expovariate, 1) # need to be checked


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

Source = DataframeSource(env, "Source", data_gen)
Sink = Sink(env, 'Sink', debug=False, rec_arrivals=True)
Assembly = Process(env, "Assembly", 10000, qlimit=10000)
Outfitting = Process(env, "Outfitting", 10000, qlimit=10000)
Painting = Process(env, "Painting", 10000, qlimit=10000)

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

env.run(5570)

print("time :", time.time() - start)

total_assy = (Assembly.finish_time - Assembly.start_time[0]) * 10000
total_oft = (Outfitting.finish_time - Outfitting.start_time[0]) * 10000
total_pnt = (Painting.finish_time - Painting.start_time[0]) * 10000

print("utilization of Assembly : {}".format(Assembly.working_time/total_assy))
print("utilization of Outfitting : {}".format(Outfitting.working_time/total_oft))
print("utilization of Painting : {}".format(Painting.working_time/total_pnt))

# Source에서 part 보내는 정도
part_list = []
for i in range(len(Source.start_time_list)):
    part_list.append(i)

plt.plot(part_list[:800], Source.start_time_list[:800])
plt.xlabel("part")
plt.ylabel("time")
plt.show()

## 시간에 따른 작업장 사용률
plt.plot(Monitor1.time, Monitor1.M)
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
plt.show()


## WIP 수준
plt.plot(Monitor1.time, Monitor1.WIP)
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
plt.show()

plt.plot(Monitor4.TH_time, Monitor4.TH)
plt.xlabel("time")
plt.ylabel("TH")
plt.show()
