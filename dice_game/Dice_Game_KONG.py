import random
import simpy

dict = {}
random.seed(42)

def roll_the_dice():
    yield store.put(random.randrange(1,7))

def player(name, env, store):
    dice_number = random.randrange(1,7)

    if(name == 0):

        yield store.put(dice_number)
        dict[name][0] = 0  # 첫째는 재고가 없으므로
        dict[name][1] += dice_number - 3.5  # 이번 턴에서 딴 점수
        # print(store.items)
        # print(name)

    else:

        push = yield store.get()  # 이번 턴에 얘에게 넘어온 성냥개비의 수
        dict[name][0] += push

        if(dict[name][0] >= dice_number):
            store.put(dice_number)# 다음으로 넘어가는 성냥개비 개수
            dict[name][0] -= dice_number# 이번 턴에서 얘의 재고
            dict[name][1] += dice_number - 3.5# 이번 턴에서 딴 점수

        else:
            store.put(dict[name][0])# 다음으로 넘어가는 성냥개비 개수
            dict[name][1] += dict[name][0] - 3.5# 이번 턴에서 딴 점수
            dict[name][0] = 0  # 이번 턴에서 얘의 재고
        # print(store.items)
        # print(name)

store_capacity=1
number_of_player=5

for i in range(0, number_of_player):

    dict[i] = [0,0]# {얘의 번호 : [얘의 재고, 점수]}

def players(env, store, n):

    roll_the_dice()

    for i in range(n):

        new_player = player(i, env, store)
        yield env.timeout(1)
        env.process(new_player)

    yield env.timeout(1)
    print(list(dict.values()))

env = simpy.Environment()

for i in range(50):
    print("\n", "-----------------trial", i + 1, "------------------------")
    store = simpy.Store(env, capacity=store_capacity) #다음턴으로 넘어가는 성냥개비의 수를 저장 (ex: 처음에 5->4->1->2->1)
    env.process(players(env, store, number_of_player))
    env.run()
