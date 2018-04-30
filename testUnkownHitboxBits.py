import json
import os
import sys

import bitstruct

from characters import characters

# CCCCCCII IXXXXXBB BBBBBXXD DDDDDDDD
# C = command, I = id, X = unknown-1 (5), B = bone, X = unknown-2 (2), D = damage
# SSSSSSSS SSSSSSSS ZZZZZZZZ ZZZZZZZZ
# S = size, Z = z offset
# YYYYYYYY YYYYYYYY XXXXXXXX XXXXXXXX
# Y = y offset, x = x offset
# AAAAAAAA AKKKKKKK KKWWWWWW WWWXXXHH
# A = angle, K = kb growth, W = weight dep kb, X = unknown-3 (3), H = hitbox interaction
# BBBBBBBB BEEEEEXS SSSSSSFF FFFFFFGA
# B = base kb, E = element, X = unknown-4 (1), S = shield damage, F = sfx,
#     G = hit grounded, A = hit airborne

# What are these unnknown bits?

def getUnknownHitboxBits(datJson):
    # original:
    fmt = "u3p5u7p2u9 u16s16s16s16 u9u9u9p3u2u9 u5p1u7u8b1b1"
    fmt = fmt.replace("p", "X") # mark the old paddings
    fmt = fmt.replace("u", "p") # make unsigned ints padding
    fmt = fmt.replace("s", "p") # make signed ints padding
    fmt = fmt.replace("b", "p") # make bools padding
    fmt = fmt.replace("X", "u") # turn old padding into uint
    #print(fmt)

    # simplified
    fmt = "p6p3 u1u1u1u1u1 p7 u1u1 p100 u1u1u1 p16 u1 p17"
    #print(fmt)

    fmt = fmt.replace(" ", "")

    ret = []
    for i, subaction in enumerate(datJson["nodes"][0]["data"]["subactions"]):
        hitboxCounter = 1
        hitboxes = []
        for event in subaction["events"]:
            if "name" in event and event["name"] == "hitbox":
                cmd = bytes.fromhex(event["bytes"])
                values = bitstruct.unpack(fmt, cmd)
                hitboxes.append((hitboxCounter, values))
                hitboxCounter += 1
        ret.append((i, subaction["shortName"], hitboxes))

    return ret

def listStrJust(lst, just=4):
    if just == None:
        just = 0
        for e in lst:
            just = max(just, len(str(e)))
    return [str(x).ljust(just) for x in lst]


def printHistograms(unknownBits):
    # hist
    zero = [0]*11
    one = [0]*11
    for char, subactions in unknownBits.items():
        charZero = [0]*11
        charOne = [0]*11
        for subactionId, subactionName, hitboxes in subactions:
            for hitbox, bits in hitboxes:
                for i in range(11):
                    if bits[i] == 0:
                        charZero[i] += 1
                    if bits[i] == 1:
                        charOne[i] += 1
        print()
        print(char.ljust(15))
        print("zero:", listStrJust(charZero))
        print("one: ", listStrJust(charOne))

        for i in range(11):
            zero[i] += charZero[i]
            one[i] += charOne[i]

    print()
    print("Total")
    print("zero:", listStrJust(zero))
    print("one: ", listStrJust(one))

def printWithBits(unknownBits, bit, value):
    print("\n# bit {} == {}".format(bit, value))
    for char, subactions in unknownBits.items():
        for subactionId, subactionName, hitboxes in subactions:
            matchingHitboxes = []
            for hitbox, bits in hitboxes:
                if bits[bit-1] == value:
                    matchingHitboxes.append(str(hitbox))
            if len(matchingHitboxes) > 0:
                print(char.ljust(20), str(subactionId).ljust(6),
                    subactionName.ljust(20), "hitbox", ", ".join(matchingHitboxes))

unknownBits = {}
characterData = {}
for character in characters:
    with open(os.path.join(sys.argv[1], character + ".json")) as f:
        characterData[character] = json.load(f)
        unknownBits[character] = getUnknownHitboxBits(characterData[character])

printHistograms(unknownBits)
# bits 1, 2, 7, 9 are always zero!
# all the other bits are mostly one value and rarely a different value
# here they are:

printWithBits(unknownBits, 3, 1) # unknown-1 (3/5)

printWithBits(unknownBits, 4, 1) # unknown-1 (4/5)
# all characters except Samus: CatchAttack (hb 1, peach: 1, 2, 3)
# Zelda and Mewtwo: CatchWait (hb 1)
# Bowser: SpecialSHit (0x12E and 0x12F) (hb 1), SpecialSEndF (hb 1)
# If I would guess this bit says "don't release from grab"
# --- Tried with CH:
# I tried setting pummel damage to 100 for Samus, but the grab doesn't release
# I tried setting that bit to 0 for Luigi and his pummel damage to 20, but the grab doesn't release either

printWithBits(unknownBits, 5, 1) # unknown-1 (5/5)
# => grabs and zair of tether grab characters!
# But I don't know what the bit does, especially since it's also set for zair.

printWithBits(unknownBits, 6, 1) # unknown-2 (1/2)
# all of these are subaction #263, hitbox 1
# Mewtwo: TMewtwoThrowB
# Mario: TMarioThrowB
# Dr Mario: TDrmarioThrowB
# Game & Watch: TGamewatchThrowB
# Ice Climbers: name missing
# Luigi: TMarioThrowB
# I tried, but I can't even find out when these states are entered.
# I did bthrow on Dr. Mario as Dr. Mario, but that is a different subaction

printWithBits(unknownBits, 8, 0) # unknown-3 (1/3)
# Mario: AttackS4Hi, AttackS4, AttackS4Lw (all hitbox 1)
# Marth: AttackHi4 (hitbox 1, 2)
# Young Link: AirCatch (hitbox 1, 2)
# Samus: AirCatch (hitbox 1, 2)
# Link: AirCatch (hitbox 1, 2)
# Ness: AttackDash (hitbox 1, 2, 4, 5)
# Mewtwo: AttackS4 (hitbox 2), AttackHi4 (hitbox 1, 2, 3, 4, 5, 6, 7, 8), AttackLw4 (hitbox 1, 2)

# this is very long, so it stays commented out
#printWithBits(unknownBits, 10, 1) # unknown-3 (3/3)
# Swing1, Swing3, Swing4, SwingDash for all characters
# Ness: AttackS4
# Mewtwo: SpecialNLoop
# Kirby: EatWalkSlow, EatWalkMiddle, EatWalkFast, SpecialS, SpecialAirS, SpecialHi2, MtSpecialNLoop
# Peach: ItemParasolOpen
# => All of this is item related
# It might actually be the case that these are ALL the attacks which incorporate items
# Maybe this is some flag that makes the item not get thrown?
# --- Tried with CH:
# CH does not show this bit as 1. Maybe CH throws away the unknown bits along the way sometimes?

printWithBits(unknownBits, 11, 1) # unknown-4
# => very probably not part of shield damage
# => The hitboxes listed here for Sheik, Pichu, Pikachu all kill Bowser @ 0% on FD
# maybe this is some instagib flag? This is not the case for falcon.
# => How many other attacks instagib without having this flag?
