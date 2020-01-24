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
data_temp = data_all[["APS_CAL", "AP_DATEDIF", "OPS_CAL", "OP_DATEDIF", "PPS_CAL", "PP_DATEDIF"]]
data = data_temp.iloc[:]

data["APS_CAL"] = pd.to_datetime(data["APS_CAL"], format='%Y-%m-%d')
data["OPS_CAL"] = pd.to_datetime(data["OPS_CAL"], format='%Y-%m-%d')
data["PPS_CAL"] = pd.to_datetime(data["PPS_CAL"], format='%Y-%m-%d')

AP_DATEDIF_avg = data[data["AP_DATEDIF"] != 0].mean(axis=0)["AP_DATEDIF"]
OP_DATEDIF_avg = data[data["OP_DATEDIF"] != 0].mean(axis=0)["OP_DATEDIF"]
PP_DATEDIF_avg = data[data["PP_DATEDIF"] != 0].mean(axis=0)["PP_DATEDIF"]
data["AP_DATEDIF"] = data["AP_DATEDIF"].apply(lambda x: AP_DATEDIF_avg if x != 0 else x)
data["OP_DATEDIF"] = data["OP_DATEDIF"].apply(lambda x: OP_DATEDIF_avg if x != 0 else x)
data["PP_DATEDIF"] = data["PP_DATEDIF"].apply(lambda x: PP_DATEDIF_avg  if x != 0 else x)

initial_date = data["APS_CAL"].min()

data["APS_CAL"] = (data["APS_CAL"] - initial_date).dt.days
data["OPS_CAL"] = (data["OPS_CAL"] - initial_date).dt.days
data["PPS_CAL"] = (data["PPS_CAL"] - initial_date).dt.days

data.sort_values(by=["APS_CAL"], inplace=True)
data.reset_index(drop=True, inplace=True)

samp_dist = functools.partial(random.expovariate, 1) # need to be checked


def generator(dataframe):
    for i in range(len(dataframe)):
        data = dataframe.iloc[i]
        dict = OrderedDict()
        dict["Assembly"] = [data["APS_CAL"], data["AP_DATEDIF"]]
        dict["Outfitting"] = [data["OPS_CAL"], data["OP_DATEDIF"]]
        dict["Painting"] = [data["PPS_CAL"], data["PP_DATEDIF"]]
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
env.run(4601)

print("time :", time.time() - start)

total_assy = (Assembly.finish_time - Assembly.start_time[0]) * 10000
total_oft = (Outfitting.finish_time - Outfitting.start_time[0]) * 10000
total_pnt = (Painting.finish_time - Painting.start_time[0]) * 10000

print("utilization of Assembly : {}".format(Assembly.working_time/total_assy))
print("utilization of Outfitting : {}".format(Outfitting.working_time/total_oft))
print("utilization of Painting : {}".format(Painting.working_time/total_pnt))

# 각 공정에서 후행공정으로 넘긴 블록의 수
print(Assembly.parts_rec, Outfitting.parts_rec, Painting.parts_rec)

# Source에서 part 보내는 정도
part_list = []
for i in range(len(Source.start_time_list)):
    part_list.append(i)

plt.plot(part_list[:800], Source.start_time_list[:800])
plt.xlabel("part")
plt.ylabel("time")
plt.show()

## M
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


## WIP
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


# TH
plt.plot(Monitor4.TH_time, Monitor4.TH)
plt.xlabel("time")
plt.ylabel("TH")
plt.show()