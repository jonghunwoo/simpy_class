import simpy
import random
import functools
import scipy.stats as st
import numpy as np
import time
from SimComponents_for_simulation_fitting import Sink, Process, Monitor, Source
from collections import OrderedDict
import matplotlib.pyplot as plt

start = time.time()

env = simpy.Environment()
RUN_TIME = 3000

samp_dist = functools.partial(random.expovariate, 1)

def generator():
    while True:
        dict = OrderedDict()

        IAT_assy = st.chi2.rvs(df=1.53, loc=-0, scale=0.23)
        IAT_assy = np.floor(IAT_assy)
        proc_assy = 0
        while proc_assy <= 0:
            proc_assy = st.lognorm.rvs(s=0.54, loc=1.46, scale=31.96, size=1)

        IAT_oft = st.pareto.rvs(b=4.75, loc=-4.48, scale=4.48)
        proc_oft = 0
        while proc_oft <= 0:
            proc_oft = st.exponnorm.rvs(K=5.71, loc=5.11, scale=2.78, size=1)

        IAT_pnt = st.exponnorm.rvs(K=3619.86, loc=-0.00, scale=0.00)
        proc_pnt = 0
        while proc_pnt <= 0:
            proc_pnt = st.exponnorm.rvs(K=2.31, loc=8.56, scale=1.74, size=1)

        dict["Assembly"] = [IAT_assy, proc_assy]
        dict["Outfitting"] = [IAT_oft, proc_oft]
        dict["Painting"] = [IAT_pnt, proc_pnt]

        yield dict

###########

data_gen = generator()

Source = Source(env, "Source", data_gen, initial_delay=0)
Sink = Sink(env, "Sink", debug=False, rec_arrivals=True)
Assembly = Process(env, "Assembly", 800, qlimit=10000)  # 조립 공정 작업장 수 = 200
Outfitting = Process(env, "Outfitting", 275, qlimit=10000)  # 의장 공정 작업장 수 = 185
Painting = Process(env, "Painting", 160, qlimit=10000)  # 도장 공정 작업장 수 = 155

# Connection
Source.out = Assembly
Assembly.out = Outfitting
Outfitting.out = Painting
Painting.out = Sink

# Monitor
Monitor1 = Monitor(env, Assembly, samp_dist)
Monitor2 = Monitor(env, Outfitting, samp_dist)
Monitor3 = Monitor(env, Painting, samp_dist)
Monitor4 = Monitor(env, Sink, samp_dist)

# Run it
env.run(until=RUN_TIME)


print('#'*80)
print("Results of simulation")
print('#'*80)

print("time :", time.time() - start)

# 총 리드타임 - 마지막 part가 Sink에 도달하는 시간
print("Total Lead Time : ", Sink.last_arrival)

total_assy = (Assembly.finish_time - Assembly.start_time[0]) * 800
total_oft = (Outfitting.finish_time - Outfitting.start_time[0]) * 275
total_pnt = (Painting.finish_time - Painting.start_time[0]) * 160

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