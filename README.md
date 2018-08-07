# SS13 Chemistry Reader
Uses Python 3 to read .DM files for chemicals and chemical reactions, which are stored as .JSON files. This was designed with [Hippie Station](https://github.com/HippieStation/HippieStation) in mind so should be inherently compatible with [/tg/ station](https://github.com/tgstation/tgstation)

# Configuration
Change the "Path" value in config.ini to to point the root folder of your local repo

# Usage
Run "readdata.py" first, this will go over the path you configured for and try to read all the chemicals and reactions. This data is stored in two files: chemicals.json and reactions.json

Run "chemistry.py" to open the program. This will let you query chemicals and generate a list of steps to create chemicals. 

If you enter the beginning or full id of a chemical it will return the chemicals details and any reactions it is involved in.

If you enter "make <chemical> <amount>" it will return a list of steps used to produce that chemical. 

You can alter this by adding "exactly" to add steps which remove excess chemicals from the container (if you don't have a large container)

You can also add "recipe" to get a "key=value;" recipe which can be used to import into the chem dispenser in the game.

# Requirements
* Python 3

* A local copy of the repo you want to read
