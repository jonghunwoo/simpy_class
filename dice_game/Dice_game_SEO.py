import random
import simpy


RANDOM_SEED = 42


def player1(env, store1,point1):
    point1.put(0)
    i1 = 1
    store1.put(0)
    while True:
        yield env.timeout(1)
        num_dice_1=random.randint(1,6)
        inventory1=yield store1.get() #전 단계에서 남아있던 재공을 뺌
        stock1=num_dice_1+inventory1  #나온 dice number를 더해줌
        yield store1.put(stock1) #다시 player의 store에 넣어줌
        p1=num_dice_1-3.5
        final1 = yield point1.get()
        yield point1.put(final1+p1) #point를 계산해서 넣어줌
        #print("{:6.2f}: 1Number of Dice{}, store left{}".format(env.now,num_dice_1,store1.items))
        #print("Player1 Points :{}".format(point1.items))
        i1 += 1



def player2(env, store1, store2, point2):
    point2.put(0)
    i2 = 1
    store2.put(0)
    while True:
        yield env.timeout(1.0001) #event의 순서를 강제하기 위해 timeout 시간을 맞춰줌
        num_dice_2 = random.randint(1,6)
        stock1 = yield store1.get() #전 player의 재공 확인
        inventory2 = yield store2.get() #전 단계의 본인의 재공 뺌
        if num_dice_2 < stock1: #나온 dice number가 전 player의 재공보다 적으면 그대로 넘겨주어 점수 및 재공 계산
            yield store1.put(stock1-num_dice_2)
            yield store2.put(num_dice_2+inventory2)
            p2 = num_dice_2-3.5
            final2= yield point2.get()
            yield point2.put(p2+final2)
        else: #나온 dice number가 전 player의 재공보다 크면 재공만큼 다 넘겨주어 점수 및 재공 계산
            yield store1.put(0)
            yield store2.put(stock1+inventory2)
            p2 = stock1-3.5
            final2 = yield point2.get()
            yield point2.put(p2+final2)
        #print("{:6.2f}: 2Number of Dice{}, store left{}{}".format(env.now,num_dice_2,store1.items,store2.items))
        #print("Player2 Points :{}".format(point2.items))
        i2 += 1

def player3(env, store1, store2, store3,point3):
    point3.put(0)
    i3 = 1
    store3.put(0)
    while True:
        yield env.timeout(1.0002)
        num_dice_2 = random.randint(1,6)
        stock2 = yield store2.get()
        inventory3=yield store3.get()
        if num_dice_2 < stock2:
            yield store2.put(stock2-num_dice_2)
            yield store3.put(num_dice_2+inventory3)
            p3 = num_dice_2-3.5
            final3 = yield point3.get()
            yield point3.put(p3+final3)
        else:
            yield store2.put(0)
            yield store3.put(stock2+inventory3)
            p3 = stock2-3.5
            final3= yield point3.get()
            yield point3.put(p3+final3)
        #print("{:6.2f}: 3Number of Dice{}, store left{}{}{}".format(env.now,num_dice_2,store1.items,store2.items,store3.items))
        #print("Player3 Points :{}".format(point3.items))
        i3+=1


def player4(env,store1,store2, store3, store4,point4):
    point4.put(0)
    i4 = 1
    store4.put(0)
    while True:
        yield env.timeout(1.0003)
        num_dice_2=random.randint(1,6)
        num_dice_1= yield store3.get()
        inventory4=yield store4.get()
        if num_dice_2<num_dice_1:
            yield store3.put(num_dice_1-num_dice_2)
            yield store4.put(num_dice_2+inventory4)
            p4 = num_dice_2-3.5
            final4= yield point4.get()
            yield point4.put(p4+final4)
        else:
            yield store3.put(0)
            yield store4.put(num_dice_1+inventory4)
            p4 = num_dice_1-3.5
            final4= yield point4.get()
            yield point4.put(p4+final4)
        #print("{:6.2f}: 4Number of Dice{}, store left{}{}{}{}".format(env.now,num_dice_2,store1.items,store2.items,store3.items,store4.items))
        #print("Player4 Points :{}".format(point4.items))
        i4+=1

def player5(env, store1, store2,store3,store4,store5,point1,point2,point3,point4,point5):
    point5.put(0)
    i5 = 1
    store5.put(0)
    while True:
        yield env.timeout(1.0004)
        num_dice_2 = random.randint(1,6)
        num_dice_1 = yield store4.get()
        inventory5 = yield store5.get()
        if num_dice_2<num_dice_1:
            yield store4.put(num_dice_1-num_dice_2)
            yield store5.put(num_dice_2+inventory5)
            p5 = num_dice_2-3.5
            final5=yield point5.get()
            yield point5.put(p5+final5)
        else:
            yield store4.put(0)
            yield store5.put(num_dice_1+inventory5)
            p5 = num_dice_1-3.5
            final5=yield point5.get()
            yield point5.put(p5+final5)
        #print("{:6.2f}: 5Number of Dice{}, store left{}{}{}{}{}".format(env.now,num_dice_2,store1.items,store2.items,store3.items,store4.items,store5.items))
        print("{}Player Points :{}{}{}{}{}".format(i5,point1.items,point2.items,point3.items,point4.items,point5.items))
        i5+=1




#set up and start dice game
print('Dice Game')
random.seed(RANDOM_SEED)
env=simpy.Environment()
#각 player들의 store와 point를 생성
store1=simpy.Store(env,capacity=1)
store2=simpy.Store(env,capacity=1)
store3=simpy.Store(env,capacity=1)
store4=simpy.Store(env,capacity=1)
store5=simpy.Store(env,capacity=1)
point1=simpy.Store(env,capacity=1)
point2=simpy.Store(env,capacity=1)
point3=simpy.Store(env,capacity=1)
point4=simpy.Store(env,capacity=1)
point5=simpy.Store(env,capacity=1)

#Start Process and Run
play1=env.process(player1(env,store1,point1))
play2=env.process(player2(env,store1,store2,point2))
play3=env.process(player3(env,store1,store2,store3,point3))
play4=env.process(player4(env,store1,store2,store3,store4,point4))
play5=env.process(player5(env,store1,store2,store3,store4,store5,point1,point2,point3,point4,point5))


env.run(until=51) #50번의 시행을 실행
