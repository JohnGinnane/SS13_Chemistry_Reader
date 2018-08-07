from pathlib import Path
import re
import json
import io
import configparser

try:
    to_unicode = unicode
except NameError:
    to_unicode = str

current_type = ""
datum = {"typepath":"UNKNOWN","id":"UNKNOWN"}
key = ""
value = ""

revarassign = r"\s*(var\/(list\/|)|)(?P<key>[a-zA-Z0-9_]+)\s*=\s*(?P<value>.+)"
reassoclist = r"\"(?P<key>[^\"]+)\"\s*=\s*(?P<value>[0-9]+)"
rechemical = "^(\/|)datum\/reagent\/[^\(\)\s]+$"
rereaction = "^(\/|)datum\/chemical_reaction\/[^\(\)\s]+$"
redispenser = "^\/obj\/machinery\/chem_dispenser$"
chemicals = []
reactions = []
dispensables = [] # chems we can dispense

def savedatum():
    global chemicals
    global reactions
    global current_type
    global datum
    global key
    global value

    if len(datum) <= 0:
        return False

    for k in datum:
        if type(datum[k]) != type(""):
            continue
        
        # replace white space with single space
        datum[k] = re.sub(r"(\s+)", " ", datum[k]).strip()
        # if wrapped in quotes then remove them
        if re.search("^\".*\"$", datum[k]):
            datum[k] = datum[k][1:len(datum[k])-1]
        # if list then make it into json format
        if re.search("^list\s*\(.*\)$", datum[k]):
            assocs = re.findall(reassoclist, datum[k])
            if assocs:
                datum[k] = dict(assocs)
            else: # standard list
                simplelist = re.findall(r"\"([^\"]*)\"\s*[,\)]", datum[k])

                if simplelist:
                    datum[k] = simplelist
    if current_type == "chemical":
        chemicals.append(datum)
    elif current_type == "reaction":
        reactions.append(datum)
    elif current_type == "dispenser":
        dispensables.append(datum)

    current_type = ""
    datum = {"typepath":"UNKNOWN","id":"UNKNOWN"}
    key = ""
    value = ""

conf = configparser.ConfigParser()
conf.read("config.ini")
conf_path = conf["Path"]["Path"]

print("Reading files from " + conf_path + "...")

pathlist = Path(conf_path).glob("**/*.dm")

for path in pathlist:
    path_in_str = str(path)
    current_type = ""
    datum = {"typepath":"UNKNOWN","id":"UNKNOWN"}
    key = ""
    value = ""

    with open(path_in_str, encoding="utf8", errors="ignore") as fp:
        line = fp.readline()
        while line:
            line = line.rstrip()
            # Remove comments
            if line.find("//") >= 0:
                line = line[:line.find("//")].rstrip()

            # If line begins with / then we've finished reading an object
            if re.search("^\/[^\/].*$", line):
                savedatum()

            if current_type == "":
                checklist = None
                if re.search(rechemical, line):
                    current_type = "chemical"
                    checklist = chemicals
                elif re.search(rereaction, line):
                    current_type = "reaction"
                    checklist = reactions
                elif re.search(redispenser, line):
                    current_type = "dispenser"
                    checklist = dispensables

                if current_type != "" and checklist != None:
                    # check for previous definition
                    for i in range(len(checklist) - 1, -1, -1):
                        if checklist[i]["typepath"] == line:
                            datum = checklist[i].copy() # copy original to datum
                            del checklist[i] # remove original
                            break
                    datum["typepath"] = line
            else:
                groups = re.search(revarassign, line)

                if groups:
                    key = str(groups.group("key")).lower()
                    value = str(groups.group("value"))

                    if key == "id":
                        datum["id"] = value
                    elif key == "name":
                        datum["name"] = value
                    elif key == "results":
                        datum["results"] = value
                    elif key == "required_reagents":
                        datum["required_reagents"] = value
                    elif key == "required_temp":
                        datum["required_temp"] = value
                    elif key == "required_catalysts":
                        datum["required_catalysts"] = value
                    elif key == "required_container":
                        datum["required_container"] = value
                    elif key == "required_other":
                        datum["required_other"] = value
                    elif key == "is_cold_recipe":
                        datum["is_cold_recipe"] = value
                    elif key == "centrifuge_recipe":
                        datum["centrifuge_recipe"] = value
                    elif key == "pressure_required":
                        datum["pressure_required"] = value
                    elif key == "radioactivity_required":
                        datum["radioactivity_required"] = value
                    elif key == "bluespace_recipe":
                        datum["bluespace_recipe"] = value
                    elif key == "dispensable_reagents":
                        datum["dispensable_reagents"] = value
                else: # no key=value on this line, just add to value
                    if key != "" and key in datum:
                        datum[key] += line

            line = fp.readline()
        savedatum()

print("Chemicals found: " + str(len(chemicals)))
print("Reactions found: " + str(len(reactions)))

# mark chemicals as dispensable
for c in chemicals:
    candispense = False
    # look through all dispensables
    for d in dispensables:
        if "dispensable_reagents" in d:
            # look through all dispensable reagents
            for dr in d["dispensable_reagents"]:
                #print(str(dr))
                if dr == c["id"]:
                    # we can dispense this chem
                    candispense = True
                    break
    c["dispensable"] = candispense

print("Saving data...")

with open("chemicals.json", "w", encoding="utf8") as f:
    str_ = json.dumps(chemicals,
                      indent=4,
                      sort_keys=False,
                      separators=(",", ":"),
                      ensure_ascii=False)
    f.write(to_unicode(str_))

with open("reactions.json", "w", encoding="utf8") as f:
    str_ = json.dumps(reactions,
                      indent=4,
                      sort_keys=False,
                      separators=(",", ":"),
                      ensure_ascii=False)
    f.write(to_unicode(str_))
