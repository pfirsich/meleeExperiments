import bitstruct
import win32clipboard

# Helper Script to parse/modify/write the copy/paste strings for hitboxes from Crazy Hand
# For experimenting with unknown bits
# I have reason to believe that Crazy Hand doesn't properly read the unknown bits into these strings
# So this is pretty much useless..

fmt = "u6 u3 u1u1u1u1u1 u7 u1u1 u9u16s16s16s16u9u9u9 u1u1u1 u2u9u5 u1 u7u8b1b1".replace(" ", "")
fields = ["command", "id", "unk1-1", "unk1-2", "unk1-3", "unk1-4", "unk1-5",
    "bone", "unk2-1", "unk2-2", "damage", "size", "z", "y", "x",
    "angle", "kb growth", "wdkb", "unk3-1", "unk3-2", "unk3-3", "hb interaction",
    "base kb", "element", "unk4", "shield damage", "sfx", "hit G", "hit A"]

def prettyPrint(values):
    assert len(values) == len(fields)
    for i, v in enumerate(values):
        print(str(i).ljust(3), fields[i].ljust(20), v)

def CHtobytes(s):
    b = bytes(int(b, 16) for b in s.split("'")[:-1])
    assert len(b) == 0x14
    return b

def unpack(b):
    values = list(bitstruct.unpack(fmt, b))
    assert len(values) == len(fields)
    return values

def unpackCH(s):
    return unpack(CHtobytes(s))

def bytestoCH(b):
    return "".join(hex(byte)[2:] + "'" for byte in b)

def pack(v):
    return bitstruct.pack(fmt, *v)

def packCH(v):
    return bytestoCH(pack(v))

def get():
    win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    print(data)
    v = unpackCH(data)
    prettyPrint(v)
    return v

def set(v):
    s = packCH(v)
    print(s)
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(s)
    win32clipboard.CloseClipboard()
