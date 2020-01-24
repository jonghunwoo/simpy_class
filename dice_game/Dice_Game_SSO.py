import simpy
import random

# name 얼마든지 추가해도 됨 / Sink는 마지막 사람의 out을 위해 만들어 놓은 것 -> 없애면 안됨
names = ["Woo", "Nam", "Kong", "Seo", "ZHU", "Jo", "Sink"]

dict = {}  # name을 key값으로 하여 [count, total_score]을 value값으로 갖는 dictionary
match = "i"
for name in names:
    dict[name] = [0, 0]  # [count(넘긴 개수), total_score]

env = simpy.Environment()


class Player(object):
    def __init__(self, name, dict, env):
        self.store = simpy.Store(env)
        self.env = env
        self.name = name
        self.dict = dict
        self.pre = None  # 이전 사람의 그릇에 성냥의 개수를 받기 위함
        self.out = None  # 순서를 위해 다음 공정을 돌려주기 위함

    def run(self, dice_n):
        while True:
            if self.name == "Sink":  # Sink에 해당하면 run을 마쳐줌
                return None
            elif self.name == "Woo":  # 첫번째 사람이면
                for i in range(dice_n):
                    self.store.put(match)
                self.dict["Woo"][0] += dice_n
                self.dict["Woo"][1] += dice_n - 3.5
                print("Woo : dice number = {}, total score = {} / Woo has {} matches".format(
                    dice_n, self.dict["Woo"][1], len(self.store.items)))

            else:  # 첫번째 사람이 아니면
                if len(self.pre.store.items) >= dice_n:  # 내 store에 충분한 양의 성냥이 있을 경우
                    self.dict[self.name][0] += dice_n  # count
                    self.dict[self.name][1] += dice_n - 3.5  # score
                    for i in range(dice_n):
                        msg = (yield self.pre.get())
                        self.store.put(msg)
                    print("{} : dice number = {}, total score = {} / {} has {} matches / {} has {} matches ".format(
                        self.name, dice_n, self.dict[self.name][1], self.name, len(self.store.items), self.pre.name, len(self.pre.store.items)))

                else:  # 내 store에 충분한 양의 성냥이 없는 경우
                    self.dict[self.name][0] += len(self.pre.store.items)  # count
                    self.dict[self.name][1] += len(self.pre.store.items) - 3.5  # score
                    for i in range(len(self.pre.store.items)):
                        msg = (yield self.pre.get())
                        self.store.put(msg)
                    print("{} : dice number = {}, total score = {} / {} has {} matches / {} has {} matches ".format(
                        self.name, dice_n, self.dict[self.name][1], self.name, len(self.store.items), self.pre.name,
                        len(self.pre.store.items)))
            # 다음 공정을 실행해줌
            n = random.randint(1, 6)
            yield self.env.process(self.out.run(n))
            return None

    def get(self):
        return self.store.get()

# name 별로 Player 함수 할당하기 위함
Players = []
for name in names:
    Players.append(Player(name, dict, env))

# 순서 지정해줌 - pre, out 지정
for i in range(1, len(names)):
    Players[i].pre = Players[i-1]
    Players[i-1].out = Players[i]


# 첫번째 사람 실행
def process_1(env, first_player):
    while True:
        for i in range(50):
            print("################## Turn {} ###################".format(i + 1))
            n = random.randint(1, 6)
            yield env.process(first_player.run(n))
            print("#############################################")
        return None


env.process(process_1(env, Players[0]))
env.run()

for i in range(len(names)-1):
    print("{} : total count = {} / total score = {}".format(names[i], dict[names[i]][0], dict[names[i]][1]))