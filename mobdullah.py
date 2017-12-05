# combat system with easygui

import easygui
import random



def battleround(attacker, defender):
    # can attacker hit the target ?
    d1 = random.random()
    text = ""
    attack = random.choice(attacker.attacks)
    if d1 > attacker.base_attack:
        text += "{} fails to attack with {}\n".format(attacker.form, attack) 
        text += "how embarassing....\n"
        return text 
    text += "{} attacks with {}\n".format(attacker.form, attack)
    d2 = random.random()
    if d2 < defender.base_defense:
        text += "{} dodges the attack! \n".format(defender.form)
        return text
    # hit! 
    slots = {}
    limit = 0
    for name, p in defender.slots.items():
        limit += p
        slots[name] = limit
    #print(slots)
    d3 = random.random()
    for n in slots:
        if d3 <= slots[n]:
            zone = n
            break
    text+= "hit in {}\n".format(zone)
    damage = attacker.base_damage - defender.base_armour[zone]
    text +="{} suffers {:.2f} damage and has {:.2f} hp left\n".format(
           defender.form, damage, defender.hp - damage )
    defender.hp -= damage
    if defender.hp <= 0:
        text += "Victory for {}\n".format(attacker.form)
        Game.log += "{} # {} kills {} #{}\n".format(
                     attacker.form, attacker.number,
                     defender.form, defender.number)
    return text
                
            
    



def find_shortest_path(graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if not start in graph:
            return None
        shortest = None
        for node in graph[start]:
            if node not in path:
                newpath = find_shortest_path(graph, node, end, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath
        return shortest

def find_all_paths(graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return [path]
        if not start in graph:
            return []
        paths = []
        for node in graph[start]:
            if node not in path:
                newpaths = find_all_paths(graph, node, end, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths



class Game():
    monsters = {}
    boxes = {}
    items = {}
    log = ""
    rooms = {"Startkerker": ["Stadttor", "Wald"],
             "Wald": ["Stadttor", "Startkerker", "Henkerhaus"],
             "Stadttor": ["Startkerker","Wald","Henkerhaus","Dorf", "Museum"],
             "Henkerhaus": ["Marktplatz", "Stadttor", "Dorf"],
             "Museum" : ["Stadttor"],
             "Marktplatz": ["Henkerhaus"],
             "Dorf": ["Stadttor", "Henkerhaus", "Bach"],
             "Bach": ["Dorf", "Fluss"],
             "Fluss": ["Wasserfall"],
             "Wasserfall": ["See"],
             "See": ["Dorf", "Burg"],
             "Burg": ["See"]
             }
    
    
    
    def __init__(self):
        self.room = "Startkerker"
        self.explored = []
        # create player
        self.player = Monster("Startkerker")
        self.player.form = "human"
        self.player.hp = 200
        self.player.max_hp = 200
        self.player.name = easygui.enterbox("What's your name, hero?")
        self.player.points = 0
        # ---- drinks ---
        Potion(carrier=self.player.number, size="small")
        Potion(carrier=self.player.number, size="medium")
        Potion(carrier=self.player.number, size="large")
        
        
       
        
        # create monsters
        for r in Game.rooms:
            # ------ monster ------
            if random.random() < 0.8 :
                Spider(r)
            if random.random() < 0.7 :
                Spider(r)
            if random.random() < 0.5 :
                Tiger(r)
            if random.random() < 0.25:
                Tiger(r)
            # ------ boxes ------
            if random.random() < 0.6:
                Box(r)
            if random.random() < 0.3:
                Box(r)
            # ------ zufallsitems -----
            if random.random() < 0.4:
                Item(r)
            if random.random() < 0.2:
                Item(r)
            if random.random() < 0.05:
                Item(r)
        
        self.run()
    
    def show_monsters(self):
        results = ""
        r = [m for m in Game.monsters.values() if m.number > 1 and m.room == self.room and m.hp > 0]
        for x in r:
            results += "{} nr {} with {} hp\n".format(x.form, x.number, x.hp)
        return results
        
    def show_boxes(self):
        results = ""
        r = [b for b in Game.boxes.values() if b.room == self.room]
        for x in r:
            results += "riddle box # {}\n".format(x.number)  
        return results

    def show_items(self):
        """show items on the ground in this room"""
        text = "----- Items on the ground ---------\n"
        items = [i for i in Game.items.values() if i.room == self.room and i.carrier is None]
        for i in items:
            text += i.__repr__() + "\n"
        return text
    
    
    def riddle(self):
        r = [b for b in Game.boxes.values() if b.room == self.room]
        for x in r:
            self.player.points += x.guess()
        r = [b for b in Game.boxes if Game.boxes[b].room == self.room]
        for x in r:
            del Game.boxes[x]
    
    
    def inventory(self):
        items = [i for i in Game.items.values() if i.carrier == 1]
        #return easygui.choicebox("select item to use", choices=i)
        text = "------ Items in backpack of player ------\n"
        mass = 0
        for i in items:
            text += i.__repr__() +"\n"
            mass += i.mass
        text += "====total mass of backpack: {} kg ====\n".format(mass)
        #text += "----- Items on the ground ---------\n"
        #items = [i for i in Game.items.values() if i.room == self.room and i.carrier is None]
        #for i in items:
        #    text += i.__repr__() + "\n"
        text+=self.show_items()
        number = easygui.integerbox("please enter number of item to use or pick up\n"+
                                    "enter negative number to drop item\n"+
                                  text, lowerbound=-9999, upperbound=9999)
        if number is None:
            return None
        keys = [k for k, v in Game.items.items() if v.carrier==1 or v.room==self.room]
        if number in keys:
            return number
        if number < 0:
            if number * -1 in keys:
                return number # negative number, to drop item!
        return None
    
    def fight(self):
        sounds = ["Zack", "Bumm!", "Krach", "Autsch!", "Aua", "Bammm!"]
  
        
        enemies = [m for m in Game.monsters.values() if m.number > 1 and m.room == self.room and m.hp > 0]
        text = ""
        turn = 0
        while len(enemies) > 0 and turn < 100 and self.player.hp > 0:
            turn += 1
            #print(enemies)
            text += "\n-----====== battle turn {} ======-----\n".format(turn)
            for e in enemies:
                if e.hp >0:
                    text += "\n======player {:.2f} hp  vs. {} # {} with {:2f} hp======\n".format(
                         self.player.hp, e.form, e.number, e.hp)
                    text += battleround(self.player, e)
                if e.hp > 0:
                    text+= "\n----counterblow!------\n"
                    text+= battleround(e, self.player)
                if self.player.hp <= 0:
                    break
            enemies = [m for m in Game.monsters.values() if m.number > 1 and m.room == self.room and m.hp > 0]
        easygui.textbox("combat", text=text)
        
        
        
        
        
        
        #easygui.msgbox("Zack! Bumm! Krach! Aua!")
        
    
    def navi(self):
        target = easygui.choicebox("Where do you want to travel to?\n",
                                   choices=list(Game.rooms))
        paths = find_all_paths(Game.rooms, self.room, target)
        results = []
        for p in paths:
            u = [o for o in p if o not in self.explored]
            results.append( [len(p), p, "not explored:", len(u)] )
            
        easygui.choicebox("Those are the paths:", choices=results)
    
    def run(self):
        while self.player.hp >0:
            text = "you are in {}.\n".format(self.room)
            monsterstext = self.show_monsters()
            if monsterstext != "":
                text += "Here are these monsters:\n{}\n".format(monsterstext)
            boxestext = self.show_boxes()
            if boxestext != "":
                text += "\n---------\nhere are those boxes:\n"
                text += boxestext
            text +=self.show_items() 
            text += "\n\nWhere do you want to go?"
            rooms = Game.rooms[self.room]
            if monsterstext != "":
                rooms.append("Fight")
            if boxestext != "":
                rooms.append("open box")
            #rooms.append("Navi")
            rooms.extend(("Navi","Inventory"))
            status = "hp: {} xp: {}".format(self.player.hp, self.player.points)
           
            potions = [p for p in Game.items.values() if p.carrier == 1]
            status += " potions: {}".format(len(potions))
           
           
            command = easygui.buttonbox(text, title=status, choices=rooms)
            rooms.remove("Navi")
            rooms.remove("Inventory")
            if monsterstext != "":
                rooms.remove("Fight")
            if boxestext != "":
                rooms.remove("open box")
            if command == "Navi":
                self.navi()
                continue
            if command == "Fight":
                self.fight()
                continue
            if command == "open box":
                self.riddle()
                continue
            if command == "Inventory":
                x = self.inventory()
                if x is None:
                    continue
                if x in Game.items:
                    if (Game.items[x].carrier is None and 
                        Game.items[x].room == self.room):
                        # pick up item
                        Game.items[x].room = None
                        Game.items[x].carrier = self.player.number
                        easygui.msgbox("you picked up an item. It is now in your inventory")
                    elif Game.items[x].carrier == self.player.number:
                        Game.items[x].use()
                        easygui.msgbox("you used an item")
                        for k in list(Game.items.keys()):
                            if Game.items[k].destroyed:
                                del Game.items[k]
                if x is not None and -x in Game.items:
                    #print("found", -x)
                    Game.items[-x].carrier = None
                    Game.items[-x].room = self.room
                    easygui.msgbox("you dropped an item. It is now on the floor")
                        
                continue
            if self.room not in self.explored:
                self.explored.append(self.room)
            self.room = command
        easygui.textbox("Game over", text=Game.log)    


class Item():
    
    number = 0
    
    def __init__(self, room="Wald", carrier=None):
        self.room = room
        self.carrier= carrier
        if self.carrier is not None:
            self.room = None
        Item.number += 1
        self.number = Item.number
        Game.items[self.number] = self
        self.destroyed = False
        self.equipped = False
        self.mass = round(random.random(),1) 
        # TODO: Zufallsitem
        self.text= random.choice(("apiece of dirt",
                                  "an old apple",
                                  "a half eaten skull",
                                  "a nice round pebble",
                                  "a little smelly bone"))
                                  
                                  
                                  
    def __repr__(self):
        text = "Item #{}: {} ({} kg) ".format(self.number,self.text,self.mass)
        return text
        
class Weapon(Item):
    
    def __init__(self, room ="Wald", carrier="None",weapontype="Sword"):
        Item.__init__(self,room,carrier)
        self.weapontype = weapontype
        self.quality = random.choice(("good","superior","average","bad"))
        self.magicdamage = random.choice((None,None,None,None,
                                            "Fire","Cold","Electricity"))
        if weapontype == "Sword":
            self.name = "Longsword"
            self.mass = round(random.gauss(1.3,0.2),1)
            self.length = round(random.gauss(1.02,0.12),1)
            self.parry =round(random.gauss(0.4,0.05),3)
            self.damagetype =["pierce","slash"]

        elif weapontype == "Axe":
            self.name = "Axe"
            self.mass = round(random.gauss(
            self.length =round(random.gauss
            self.quality =random.choice((
            self.magicdamage =random.choice((None,None,None,None,"Fire","Cold","Electricity"))
            self.parry =
            
            #TODO spear
            #TODO warhammer
        
        
            
                                  
class Potion(Item):
    
    def __init__(self, room="Wald", carrier=None, effect="Health", size="medium"):
        Item.__init__(self, room, carrier)
        self.effect = effect
        self.size = size
        self.text = "healing potion"
        if self.size =="small":
            self.mass= 0.25
        elif self.size =="medium":
            self.mass=0.5
        elif self.size =="large":
            self.mass=1
            
    def __repr__(self):
        text = "Item #{}: ".format(self.number)
        text += "{} potion of {} ({} kg)".format(self.size, self.effect,self.mass)
        return text
        
    def use(self, drinker=1):
        if self.effect == "Health":
            easygui.msgbox("glup - glup - glup ......Ahhhhhhhhh!")
            if self.size == "small":
                bonus= int(random.gauss(20, 2))
            elif self.size == "medium":
                bonus= int(random.gauss(45, 3))
            elif self.size == "large":
                bonus= int(random.gauss(80, 10))
            Game.monsters[drinker].hp += bonus
            if Game.monsters[drinker].hp > Game.monsters[drinker].max_hp:
                Game.monsters[drinker].hp = Game.monsters[drinker].max_hp+0
            easygui.msgbox("The {} potion gives {} hp".format(
                           self.size, bonus))    
            self.destroyed = True
        

class Box():
    
    number = 0
    
    def __init__(self, room="Wald", difficulty = 1):
        self.room = room
        self.difficulty = difficulty
        Box.number += 1
        self.number = Box.number
        Game.boxes[self.number] = self
        self.n1 = random.randint(2,20)
        self.n2 = random.randint(2,20)
        hard = {2:1,
                3:3,
                4:2,
                5:1,
                6:4,
                7:6,
                8:4,
                9:5,
                10:1,
                11:2,
                12:4,
                13:5,
                14:4,
                15:3,
                16:4,
                17:6,
                18:5,
                19:6,
                20:1}
        self.points = hard[self.n2]    
        

        
    def guess(self):
        while True:
            answer = easygui.integerbox("What is {} divided by {}?\nThis question gives you {} points".format(
                     self.n1*self.n2, self.n2, self.points))
            if answer == self.n1:
                break
        return self.points
                     

class Monster():
    
    number = 0
    
    def __init__(self, room="Wald"):
        Monster.number += 1
        self.number = Monster.number
        Game.monsters[self.number] = self
        self.hp = random.randint(10,30)
        self.max_hp = self.hp + 0
        self.dex = random.randint(5,15)
        self.st = random.randint(5,15)
        self.room = room 
        self.e  = random.randint(10,20)
        self.form = random.choice(("human", "tiger", "spider"))
        # percentage of slot ... 60% body, 10% head etc
        # slot: [ percentage, armour, bonus_attack, bonus_defense, critical]
        self.slots = {"body":0.6, 
                      "legs":0.15,
                      "arms":0.15,
                      "head":0.1}
        self.base_armour = {"body":1,
                            "legs":1,
                            "arms":1,
                            "head":2}
        self.attack_malus = {"legs": 0.2,
                             "arms": 0.5, }
        self.defense_malus = {"legs": 0.1,
                              "arms": 0.4 }
        self.critical = {"head": 0.02}
        self.base_attack = 0.7
        self.base_defense = 0.4
        self.base_damage = 5
        self.attacks = ["punch", "kick", "bite"]
        
        
        
    def __repr__(self):
        return "Monster # {} form: {}\n strenght : {}\n dexterity: {}\n hitpoints: {}\n energy   : {}\n".format(self.number, self.form, self.st*"P", self.dex*"D", self.hp*"H", self.e*"e")
        

class Tiger(Monster):
    
    def __init__(self, room="Wald"):
        Monster.__init__(self, room)
        self.form = "tiger"
        self.hp = random.randint(20,30)
        self.dex = random.randint(10,15)
        self.st = random.randint(9,20)
        self.e  = random.randint(5,10)
        self.attacks = ["slash", "bite", "jump attack"]
        self.slots = {"body":0.6, 
                      "legs":0.3,
                      "head":0.1}
        self.base_armour = {"body":2,
                            "legs":2,
                            "head":2}
        self.attack_malus = {"legs": 0.3,
                             "head": 0.1
                              }
        self.defense_malus = {"legs": 0.2,
                              }
        self.critical = {"head": 0.02}
        self.base_attack = 0.9
        self.base_defense = 0.6
        self.base_damage = 15

class Spider(Monster):
    
    def __init__(self, room="Wald"):
        Monster.__init__(self, room)
        self.form = "spider"
        self.hp = random.randint(1,5)
        self.dex = random.randint(20,30)
        self.st = 1
        self.e  = random.randint(10,15)
        self.attacks = ["bite", "poison bite"]
        self.slots = {"body":0.4, 
                      "legs":0.5,
                      "arms":0.05,
                      "head":0.05}
        self.base_armour = {"body":0,
                            "legs":0,
                            "arms":0,
                            "head":0}
        self.attack_malus = {"legs": 0.05,
                             "arms": 0.0,
                             "head": 0.5 }
        self.defense_malus = {"legs": 0.05,
                              "arms": 0.0 }
        self.critical = {"head": 0.02}
        self.base_attack = 0.5
        self.base_defense = 0.2
        self.base_damage = 1



def gametest():
    #for x in range(5):
    #    Monster()
    
    #for m in Game.monsters:
    #    print(Game.monsters[m])
    
    #print(find_shortest_path(Game.rooms, "Startkerker", "Marktplatz"))
    
    Game()
        
if __name__ == "__main__":
    gametest()
    

        
    
