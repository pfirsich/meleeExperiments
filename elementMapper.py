import json
import os
import sys

from stateAnnotations import stateAnnotations
from characters import characters

# Idea:
# In Magus post about the Hitbox command the element with Id 0x08 is annotated with
# "grounded" (just like element 0x09). The "Crazy Hand" tool just lists 0x08 as "unknown".
# What is it?

elementMap = {
    0x00: "normal",
    0x01: "fire",
    0x02: "electric",
    0x03: "slash",
    0x04: "coin",
    0x05: "ice",
    0x06: "sleep_103_frames",
    0x07: "sleep_412_frames",
    0x08: "unknown",
    0x09: "grounded_97_frames",
    0x0A: "grab",
    0x0B: "empty", # gray hitbox that doesn't hit
    0x0C: "disabled",
    0x0D: "darkness",
    0x0E: "screw_attack",
    0x0F: "poison/flower",
    0x10: "nothing", # no graphic on hit
}

for character in characters:
    print(">>", character)
    with open(os.path.join(sys.argv[1], character + ".json")) as f:
        data = json.load(f)

    # element is a 5 bit unsigned integer
    for elementId in range(32):
        element = elementMap.get(elementId, elementId)
        elementNamePrinted = False
        for i, subaction in enumerate(data["nodes"][0]["data"]["subactions"]):
            for event in subaction["events"]:
                if event.get("name") == "hitbox" or event.get("name") == "throw":
                    if event["fields"]["element"] == element and (element == "grab" or elementId > 0x10):
                        if not elementNamePrinted:
                            print("Element: {} {}".format(hex(elementId),
                                " - " + element if isinstance(element, str) else ""))
                            elementNamePrinted = True

                        shortName = subaction["shortName"]
                        if shortName in stateAnnotations:
                            annot = " - " + stateAnnotations[shortName]
                        else:
                            annot = ""
                        print("{:<5} {} {} ({} event)".format(
                            i, subaction["shortName"], annot, event["name"]))
                        break
        if elementNamePrinted:
            print()

# => Results
# For all characters:
# Catch (grab), CatchDash (dashgrab)
# Bowser: SpecialSStart
# Cpt Falcon/Ganondorf: SpecialHi, SpecialAirHi
# Kirby: SpecialN, SpecialNLoop, YsSpecialN1, MtSpecialAirNStart/Loop/Cancel/End
# Mewtwo: SpecialAirNStart/Loop/Cancel/End, SpecialS
# Yoshi: SpecialN1
# => I am very sure this is some sort of grab property, though it seems
#    (limited experimentation with Crazy Hand) that you can not give this property
#    to any attack.
# => This script also verifies that all elements above 0x10 are unused.
