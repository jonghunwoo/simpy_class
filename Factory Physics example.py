import simpy
import random
import functools
import time
import os
import scipy.stats as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from SimComponents import Sink, Process, Monitor, Source


if __name__ == "__main__":
    #data pre-processing
    columns = pd.MultiIndex.from_product([['Process1', 'Process2'], ['start_time', 'process_time']])
    data = pd.DataFrame([], columns=columns)

    blocks = 1000
    start_time_1, start_time_2 = 0.0, 0.0
    for i in range(blocks):
        if i == 0:
            start_time_1 += 0.0
        else:
            start_time_1 += st.expon.rvs(loc=25, scale=1)

        process_time_1, process_time_2 = 0.0, 0.0
        while process_time_1 <= 0:
            process_time_1 = st.gamma.rvs(a=0.1552, loc=0, scale=142.82)
        while process_time_2 <= 0:
            process_time_2 = st.gamma.rvs(a=1.009, loc=0, scale=23.21)

        data.loc[i] = [start_time_1, process_time_1, start_time_2, process_time_2]

    # modeling
    env = simpy.Environment()

    WIP_graph = True
    Throughput_graph = True
    save_graph = True

    if save_graph:
        save_path = './data/example'
        if not os.path.exists(save_path):
            os.makedirs(save_path)

    # samp_dist = functools.partial(random.expovariate, 1)
    samp_dist = 1

    m_1 = 1
    m_2 = 1

    Source = Source(env, "Source", data)
    Sink = Sink(env, "Sink", rec_lead_time=True, rec_arrivals=True)
    Process1 = Process(env, "Process1", m_1, qlimit=10000)  # 조립 공정 작업장 수 = 200
    Process2 = Process(env, "Process2", m_2, qlimit=10000)  # 의장 공정 작업장 수 = 185

    Monitor1 = Monitor(env, Process1, samp_dist)
    Monitor2 = Monitor(env, Process2, samp_dist)

    Source.out = Process1
    Process1.out = Process2
    Process2.out = Sink

    # Run it
    start = time.time()
    env.run()
    finish = time.time()

    print('#' * 80)
    print("Results of simulation")
    print('#' * 80)

    print(np.mean(Monitor2.WIP))

    # 코드 실행 시간
    print("simulation execution time :", finish - start)

    # 총 리드타임 - 마지막 part가 Sink에 도달하는 시간
    print("Total Lead Time :", Sink.last_arrival)

    # 평균 WIP
    print("average WIP of Process1 : {}".format(np.mean(Monitor1.WIP)))
    print("average WIP of Process2 : {}".format(np.mean(Monitor2.WIP)))

    # 가동률
    total_process1 = (Process1.process_finish - Process1.process_start) * m_1
    total_process2 = (Process2.process_finish - Process2.process_start) * m_2

    print("utilization of Assembly : {}".format(Process1.working_time / total_process1))
    print("utilization of Outfitting : {}".format(Process2.working_time / total_process2))

    # throughput and arrival_rate
    if Throughput_graph:
        smoothing = 1000
        throughput_1 = pd.Series(Monitor1.throughput).rolling(window=smoothing, min_periods=1).mean()
        throughput_2 = pd.Series(Monitor2.throughput).rolling(window=smoothing, min_periods=1).mean()
        arrival_rate_1 = pd.Series(Monitor1.arrival_rate).rolling(window=smoothing, min_periods=1).mean()
        arrival_rate_2 = pd.Series(Monitor2.arrival_rate).rolling(window=smoothing, min_periods=1).mean()

        fig, ax = plt.subplots(2, 1, squeeze=False)

        ax[0][0].plot(Monitor1.time, arrival_rate_1, label='arrival_rate')
        ax[0][0].plot(Monitor1.time, throughput_1, label='throughput')
        ax[1][0].plot(Monitor2.time, arrival_rate_2, label='arrival_rate')
        ax[1][0].plot(Monitor2.time, throughput_2, label='throughput')

        ax[0][0].set_xlabel('time')
        ax[0][0].set_ylabel('rate')
        ax[1][0].set_xlabel('time')
        ax[1][0].set_ylabel('rate')

        ax[0][0].set_title("Arrival_rate/Troughput - {0}".format(Monitor1.port.name))
        ax[1][0].set_title("Arrival_rate/Troughput - {0}".format(Monitor2.port.name))

        plt.legend()
        plt.tight_layout()
        plt.show()

        if save_graph:
            fig.savefig(save_path + '/ArrivalRate_Troughput.png')

    # WIP and m
    if WIP_graph:
        fig, ax = plt.subplots(2, 1, squeeze=False)

        ax[0][0].plot(Monitor1.time, Monitor1.WIP, label='WIP')
        ax[0][0].plot(Monitor1.time, Monitor1.M, label='m')
        ax[1][0].plot(Monitor2.time, Monitor2.WIP, label='WIP')
        ax[1][0].plot(Monitor2.time, Monitor2.M, label='m')

        ax[0][0].set_xlabel('time')
        ax[0][0].set_ylabel('num')
        ax[1][0].set_xlabel('time')
        ax[1][0].set_ylabel('num')

        ax[0][0].set_title("WIP/m - {0}".format(Monitor1.port.name))
        ax[1][0].set_title("WIP/m - {0}".format(Monitor2.port.name))

        plt.legend()
        plt.tight_layout()
        plt.show()

        if save_graph:
            fig.savefig(save_path + '/WIP_m.png')