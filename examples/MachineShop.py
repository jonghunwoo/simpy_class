"""
Machine shop example

Covers:

- Interrupts
- Resources: PreemptiveResource

Scenario:
  A workshop has *n* identical machines. A stream of jobs (enough to
  keep the machines busy) arrives. Each machine breaks down
  periodically. Repairs are carried out by one repairman. The repairman
  has other, less important tasks to perform, too. Broken machines
  preempt theses tasks. The repairman continues them when he is done
  with the machine repair. The workshop works continuously.

"""
import random
import simpy

from datetime import datetime as d############################################################################env.now()는 minute를 가리키고
from datetime import timedelta as t###########################################################################이를 오늘 날짜 00:00:00시부터
today  = d(d.now().year, d.now().month, d.now().day, hour=0, minute=0, second=0)##############################더해주어서 시간을 정렬시켜준다

RANDOM_SEED = 42
PT_MEAN = 10.0  # Avg. processing time in minutes
PT_SIGMA = 2.0  # Sigma of processing time
MTTF = 300.0  # Mean time to failure in minutes
BREAK_MEAN = 1 / MTTF  # Param. for expovariate distribution
REPAIR_TIME = 30.0  # Time it takes to repair a machine in minutes
JOB_DURATION = 30.0  # Duration of other jobs in minutes
NUM_MACHINES = 10  # Number of machines in the machine shop
WEEKS = 4  # Simulation time in weeks
SIM_TIME = WEEKS * 7 * 24 * 60  # Simulation time in minutes


def time_per_part():
    """Return actual processing time for a concrete part."""
    return random.normalvariate(PT_MEAN, PT_SIGMA)


def time_to_failure():
    """Return time until next failure for a machine."""
    return random.expovariate(BREAK_MEAN)


class Machine(object):
    """A machine produces parts and my get broken every now and then.

    If it breaks, it requests a *repairman* and continues the production
    after the it is repaired.

    A machine has a *name* and a numberof *parts_made* thus far.

    """

    def __init__(self, env, name, repairman, num):#######이곳에서 기계를 구별하는 번호 생성
        self.env = env
        self.name = name
        self.parts_made = 0
        self.broken = False
        self.num = num###################################

        # Start "working" and "break_machine" processes for this machine.
        self.process = env.process(self.working(repairman))
        env.process(self.break_machine())

    def working(self, repairman):
        """Produce parts as long as the simulation runs.

        While making a part, the machine may break multiple times.
        Request a repairman when this happens.

        """
        while True:
            # Start making a new part
            done_in = time_per_part()
            while done_in:
                try:
                    # Working on the part
                    start = self.env.now

                    machine_time[self.num].append('part_making_start')########################################################부품만들기 시간 기록 시작
                    machine_time[self.num].append((today + t(minutes=env.now)).strftime("%Y-%m-%d %H:%M:%S"))#################

                    yield self.env.timeout(done_in)
                    done_in = 0  # Set to 0 to exit while loop.

                    machine_time[self.num].append('part_making_end')  ########################################################
                    machine_time[self.num].append((today + t(minutes=env.now)).strftime("%Y-%m-%d %H:%M:%S"))#################

                except simpy.Interrupt:
                    self.broken = True
                    done_in -= self.env.now - start  # How much time left?

                    machine_time[self.num].append('part_making_end')  #########################################################
                    machine_time[self.num].append((today + t(minutes=env.now)).strftime("%Y-%m-%d %H:%M:%S"))##################

                    # Request a repairman. This will preempt its "other_job".
                    with repairman.request(priority=1) as req:
                        yield req

                        repairman_repair_time.append('repair_start')##############################################################################수리공 수리 시간 기록 시작
                        repairman_repair_time.append((today + t(minutes=env.now)).strftime("%Y-%m-%d %H:%M:%S"))##################################

                        yield self.env.timeout(REPAIR_TIME)

                        repairman_repair_time.append('repair_end')###########수리공 수리
                        repairman_repair_time.append((today + t(minutes=env.now)).strftime("%Y-%m-%d %H:%M:%S"))##################################

                    self.broken = False

            # Part is done.
            self.parts_made += 1

    def break_machine(self):
        """Break the machine every now and then."""
        while True:
            yield self.env.timeout(time_to_failure())
            if not self.broken:
                # Only break the machine if it is currently working.
                self.process.interrupt()


def other_jobs(env, repairman):
    """The repairman's other (unimportant) job."""
    while True:
        # Start a new job
        done_in = JOB_DURATION
        while done_in:
            # Retry the job until it is done.
            # It's priority is lower than that of machine repairs.
            with repairman.request(priority=2) as req:
                yield req
                try:
                    start = env.now

                    repairman_otherjob_time.append('other_job_start')#####################################################수리공의 부업 시간 기록 시작
                    repairman_otherjob_time.append((today + t(minutes=env.now)).strftime("%Y-%m-%d %H:%M:%S"))############

                    yield env.timeout(done_in)
                    done_in = 0

                    repairman_otherjob_time.append('other_job_end')################################
                    repairman_otherjob_time.append((today + t(minutes=env.now)).strftime("%Y-%m-%d %H:%M:%S"))#############


                except simpy.Interrupt:

                    repairman_otherjob_time.append('other_job_end')########################################################
                    repairman_otherjob_time.append((today + t(minutes=env.now)).strftime("%Y-%m-%d %H:%M:%S"))#############

                    done_in -= env.now - start


# Setup and start the simulation
print('Machine shop')
random.seed(RANDOM_SEED)  # This helps reproducing the results

# Create an environment and start the setup process
env = simpy.Environment()
repairman = simpy.PreemptiveResource(env, capacity=1)
machines = [Machine(env, 'Machine %d' % i, repairman, i)###################### 클래스에 기계 구별 번호 추가 i
            for i in range(NUM_MACHINES)]

machine_time = []#############################################################시간 저장 리스트 생성
for i in range(NUM_MACHINES):#################################################이때 리스트의 제일 첫번째 값은 리스트의 이름으로 설정
    machine_time.append(['Machine #%d' % i])##################################

repairman_otherjob_time = ['Repairman_otherjob']##############################
repairman_repair_time = ['Repairman_repairing']###############################

env.process(other_jobs(env, repairman))

# Execute!
env.run(until=SIM_TIME)

# Analyis/results
print('Machine shop results after %s weeks' % WEEKS)
for machine in machines:
    print('%s made %d parts.' % (machine.name, machine.parts_made))

import plotly.figure_factory as ff#############################################################간트 차트를 그려주는 부분

df = []##########################################################################################################################df에 있는 값을 토대로 차트를 만들어준다

def make_Dictionary(task_time, type):############################################################################################차트를 만들어주는 형식에 맞게 변환해주는 함수
    for i in range(len(task_time) - 4):##########################################################################################여기서 type은 수리공과 기계의 리스트 모양이 달라서 구별을 해주는 것이다
        if (i % 4 == 0):#########################################################################################################시작시간,분,끝시간,분 으로 리스트에 저장되어 있으므로 4개씩 끊어서 읽어준다
            if(type == 1):#######################################################################################################
                df.append(dict(Task=task_time[0], Start=task_time[i + 2], Finish=task_time[i + 4], Resource=task_time[0]))#######여기서 리소스는 색깔로 묶어주는 것이라 보면된다
            else:################################################################################################################색깔이 10개? 이상 넘어가면 오류가 생기므로 기계끼리의 색은 묶어주었다
                df.append(dict(Task=task_time[0], Start=task_time[i + 2], Finish=task_time[i + 4], Resource='Machine'))##########

make_Dictionary(repairman_repair_time, 1)#############################################dictionary 생성 부분
make_Dictionary(repairman_otherjob_time, 1)###########################################
for i in range(NUM_MACHINES):#########################################################
    make_Dictionary(machine_time[i], 2)###############################################

fig = ff.create_gantt(df, index_col='Resource', group_tasks=True)######## index는 리소스 값에 따라 색을 묶어주는 것, group은 한가지 업무는 한줄에 나타내주는 것(안하면 일반 간트차트처럼 새 업무 시에는 줄바꿈이 일어남)
fig.show()###############################################################