"""
Bank renege example

Covers:

- Resources: Resource
- Condition events

Scenario:
  A counter with a random service time and customers who renege. Based on the
  program bank08.py from TheBank tutorial of SimPy 2. (KGM)

optimization
- counter : 1 ~ 5
- time in bank : 20 ~ 30
- 총 걸리는 시간이 200초에 가장 가까운 counter, time in bank 값 찾기

counter : 5 // time in bank : 20 일 때 122.0276 sec < 200 sec
- 전체 시간이 늘어가는 방향으로 가야
- counter는 적을수록, time in bank는 클수록 전체 시간이 늘어남
"""

import random
import simpy

RANDOM_SEED = 42
NEW_CUSTOMERS = 10  # Total number of customers
INTERVAL_CUSTOMERS = 10.0  # Generate new customers roughly every x seconds
MIN_PATIENCE = 1  # Min. customer patience
MAX_PATIENCE = 3  # Max. customer patience

def source(env, number, interval, counter):
    """Source generates customers randomly"""
    for i in range(number):
        c = customer(env, 'Customer%02d' % i, counter, time_in_bank)
        env.process(c)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)

def customer(env, name, counter, time_in_bank):
    """Customer arrives, is served and leaves."""
    arrive = env.now - reset_time
    print('%7.4f %s: Here I am' % (arrive, name))

    with counter.request() as req:
        patience = random.uniform(MIN_PATIENCE, MAX_PATIENCE)
        # Wait for the counter or abort at the end of our tether
        results = yield req | env.timeout(patience)

        wait = env.now - arrive - reset_time

        if req in results:
            # We got to the counter
            print('%7.4f %s: Waited %6.3f' % (env.now - reset_time, name, wait))

            tib = random.expovariate(1.0 / time_in_bank)
            yield env.timeout(tib)
            print('%7.4f %s: Finished' % (env.now - reset_time, name))

        else:
            # We reneged
            print('%7.4f %s: RENEGED after %6.3f' % (env.now - reset_time, name, wait))


# Setup and start the simulation
print('Bank renege')
random.seed(RANDOM_SEED)
env = simpy.Environment()

time = {}

# Start processes and run
for my_counter in range(1, 6):
    for time_in_bank in range(20, 31):
        print("||||||||||||||||||||||||||||||||||||||||||||||||||||")
        print("창구의 개수는 {}개, 업무시간은 {}초일 때".format(my_counter, time_in_bank))
        counter = simpy.Resource(env, capacity=my_counter)
        reset_time = env.now

        env.process(source(env, NEW_CUSTOMERS, INTERVAL_CUSTOMERS, counter))
        env.run()

        time_delta = abs(200 - env.now + reset_time)  # 총 걸린 시간과 200초 사이의 시간 차
        my_tuple = (my_counter, time_in_bank)
        time.update({my_tuple: [env.now - reset_time, time_delta]})

optituple = min(time.keys(), key=(lambda k: time[k][1]))

print("\n창구의 개수가 {}개, 업무 시간이 {}초일 때 총 소요시간은 {}초입니다.\n200초와의 차이는 {}로 가장 200초에 가깝습니다. ".format(optituple[0], optituple[1],time[optituple][0], time[optituple][1]))

