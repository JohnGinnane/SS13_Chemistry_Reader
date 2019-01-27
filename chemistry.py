import json
import math
import operator
import sys

print("Python version: " + sys.version)
chemicals = []
reactions = []
steps = []

print("Reading data...")
with open("chemicals.json") as f:
    chemicals = json.load(f)
    print("Read " + str(len(chemicals)) + " chemicals")
with open("Reactions.json") as f:
    reactions = json.load(f)
    print("Read " + str(len(reactions)) + " reactions")

def ceil5(number):
    return math.ceil(number / 5) * 5

def getdepth(step):
    return step[1]

def getnextid():
    global steps
    maxid = 0
    for step in steps:
        if step[1] > maxid:
            maxid = step[1]
    return maxid + 1

def findchem(target, printsimilar = False):
    global chemicals
    result = None
    similar = []
    for chem in chemicals:
        if "id" in chem and chem["id"] == target:
            return chem.copy()
        elif "name" in chem and chem["name"] == target:
            return chem.copy()
        if not result:
            if chem["id"].find(target) >= 0 or chem["id"].lower() == target.lower():
                similar.append(chem)

    if printsimilar and not result:
        if len(similar) == 1:
            return similar[0]

        print("Couldn't find anything for '" + str(target) + "'")
        if len(similar) > 1:
            print("Did you mean any of the following?")
            similar_str = ""
            for sim in similar:
                if similar_str != "":
                    similar_str = similar_str + ", "
                similar_str = similar_str + sim["id"]

            print(similar_str)
    return result

def printreactions(target):
    global chemicals
    global reactions
    
    if not target:
        return False
    
    for k in target:
        print(str(k) + ": " + str(target[k]))
    print("------------------------------")
    print("Created by the following reactions:\n")
    for react in reactions:
        if "results" in react:
            for result in react["results"]:
                if target["id"] == result:
                    for k in react:
                        print(str(k) + ": " + str(react[k]))
                    print("")
    print("------------------------------")
    print("Used in the following reactions:\n")
    for react in reactions:
        if "required_reagents" in react:
            for required in react["required_reagents"]:
                if target["id"] == required:
                    for k in react:
                        print(str(k) + ": " + str(react[k]))
                    print("")
                    break

def findrecipe(target, amount, exactly):
    global steps
    amount = ceil5(amount)
    amountmulti = 1
    thisid = getnextid()

    if target["dispensable"]:
        steps.append([len(steps), thisid, {"chem":target, "amount":amount}])
        return

    recipe = None
    global reactions
    for react in reactions:
        # check to make sure it's an acquirable reaction
        if "required_other" in react:
            if react["required_other"]:
                continue
        if "required_container" in react:
            if react["required_container"] != "":
                continue
        # lasy but just use first reaction we can find
        if "results" in react:
            for result in react["results"]:
                requires_self = False
                if target["id"] == result:
                    # check to make sure this ingredient isn't also part of the requirements
                    if "required_reagents" in react:
                        for required in react["required_reagents"]:
                            if target["id"] == required:
                                requires_self = True
                                break
                    if requires_self:
                        continue
                    recipe = react.copy()
                    amountmulti = math.ceil(amount / float(recipe["results"][result]) / 5) * 5
                    break
    if recipe:
        if "required_reagents" in recipe:
            for require in recipe["required_reagents"]:
                chem = findchem(require)
                if chem:
                    findrecipe(chem, ceil5(float(recipe["required_reagents"][require]) * amountmulti), exactly)
        if "required_catalysts" in recipe:
            for require in recipe["required_catalysts"]:
                chem = findchem(require)
                if chem:
                    findrecipe(chem, ceil5(float(recipe["required_catalysts"][require])), exactly)
        if "required_temp" in recipe:
            steps.append([len(steps), thisid, "heat to " + recipe["required_temp"] + "K"])
        if "pressure_required" in recipe:
            steps.append([len(steps), thisid, "pressurize to " + recipe["pressure_required"] + " bars"])
        if "radioactivity_required" in recipe:
            steps.append([len(steps), thisid, "radioactive to " + recipe["radioactivity_required"] + "PBq"])

        # tell us what we should be getting for sanity
        givesus = "RESULT: "
        for result in recipe["results"]:
            if givesus != "RESULT: ":
                givesus = givesus + ", "
            givesus = givesus + result + " " + str(ceil5(float(recipe["results"][result]) * amountmulti)) + "u"
        
        steps.append([len(steps), thisid, givesus])
        # remove excess material
        if exactly:
            for result in recipe["results"]:
                if target["id"] != result:
                    removethis = "REMOVE " + result + " " + str(ceil5(float(recipe["results"][result]) * amountmulti)) + "u"
                    steps.append([len(steps), thisid, removethis])
                else:
                    # check for excess amount
                    excess = ceil5(float(recipe["results"][result]) * amountmulti) - amount
                    if excess > 0:
                       steps.append([len(steps), thisid, "DESTROY " + result + " " + str(excess) + "u"])
    else:
        # couldn't find a recipe, just tell us the chem
        steps.append([len(steps), thisid, {"chem":target, "amount":amount}])

def generatesteps(target, amount, exactly=False):
    global steps
    steps = []
    findrecipe(target, amount, exactly)
    steps = sorted(steps, key = lambda y: (-y[1], y[0]))

def printsteps(target, amount, exactly=False):
    print("Calculating recipe for " + str(target["id"]) + ":")
    generatesteps(target, amount, exactly)
    global steps
    for step in steps:
            message = ""
            if type(step[2]) == type({}):
                chem = step[2]["chem"]
                amount = step[2]["amount"]
                message = "ADD " + str(chem["id"]) + " " + str(amount)
            elif type(step[2]) == type(""):
                message = step[2]
            message = "(" + str(step[0]) + ", " + str(step[1]) + ") " + message
            if message != "":
                print(message)

def printrecipe(target, amount):
    print("Printing recipe for " + str(target["id"]) + ":")
    generatesteps(target, amount)
    global steps
    print("id: " + str(target["id"]))
    recipe = ""
    for step in steps:
        if type(step[2]) == type({}):
            chem = step[2]["chem"]
            amount = step[2]["amount"]
            recipe = recipe + str(chem["id"]) + "=" + str(amount) + ";"
    print("recipe: " + recipe[:-1])

_in = " "
print("Type ? for help")
while _in != "quit":
    _in = input(">> ")
    print(_in)
    if _in.lower() == "quit" or _in.lower() == "exit":
        break
    argv = _in.split(" ")

    if argv[0].strip() == "":
        continue
    if argv[0] == "?":
        print("Enter the name of a chemical you would like to see the reactions for")
        print("Enter 'make', the amount, and the name of a chemical to get a list of steps to make it")
        print("You can add 'exactly' to add steps for removing excess material")
        print("You can add 'recipe' to output the steps into a recipe that can be imported into the chem dispenser")
        print("Enter 'quit' to quit the program")
    elif argv[0] == "create" or argv[0] == "make":
        _amount = 0
        _exactly = False
        _limit = 0 # 0 is unlimited
        _target = ""
        _recipe = False
        tmp = argv.copy()
        for k, v in enumerate(tmp):
            if not v or v == "":
                continue
            if _amount == 0:
                try:
                    _amount = int(v)
                    tmp[k] = ""
                    continue
                except:
                    pass
            if not _exactly and v.lower() == "exactly":
                _exactly = not _exactly
                tmp[k] = ""
                continue
            if not _recipe and v.lower() == "recipe":
                _recipe = not _recipe
                tmp[k] = ""
                continue
            if _limit == 0 and v.lower() == "limit":
                try:
                    _limit = tmp[k+1]
                    tmp[k] = ""
                    tmp[k+1] = "" # set to blank to avoid mixup between amount and limit
                    continue
                except:
                    pass
            _target = v # kinda lazy but we set the target to whatever unresolved string there is

        if _amount == 0:
            print("No amount specified!")
            continue
        if _amount <= 0:
            print("Only positive amounts allowed!")
            continue
        if not _target:
            print("No chemical specified!")
            continue
        
        _target = findchem(_target, printsimilar=True)
        if _target:
            if _recipe:
                printrecipe(_target, _amount)
            else:
                printsteps(_target, _amount, _exactly)
    else:
        chem = findchem(argv[0], printsimilar=True)
        if chem:
            printreactions(chem)