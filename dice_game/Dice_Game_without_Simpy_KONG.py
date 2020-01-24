import random
random.seed(42)

class Person(object):
    def __init__(self, current_my_stock):
        self.current_my_stock = current_my_stock
        self.move=0.0
        self._score=0.0

    def roll_the_dice(self):

        return random.randrange(1,7)

    def put(self, next_man):
        current_my_dice_number = self.roll_the_dice()
        if(self.current_my_stock >= current_my_dice_number):
            next_man.current_my_stock += current_my_dice_number
            self.move = current_my_dice_number
            self.current_my_stock -= current_my_dice_number
        else:
            next_man.current_my_stock += self.current_my_stock
            self.move = self.current_my_stock
            self.current_my_stock = 0

    def score(self):
        self._score += self.move - 3.5
        print(self._score)


Woo = Person(0)
Kong = Person(0)
Seo = Person(0)
Nam = Person(0)
Ju = Person(0)
Table = Person(0)

for i in range(50):
    Woo.current_my_stock = 7
    Woo.put(Kong)
    Kong.put(Seo)
    Seo.put(Nam)
    Nam.put(Ju)
    Ju.put(Table)

    print("\n","-----------------trial", i + 1, "------------------------")
    Woo.score()
    Kong.score()
    Seo.score()
    Nam.score()
    Ju.score()


