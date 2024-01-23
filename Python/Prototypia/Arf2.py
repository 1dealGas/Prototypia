# automatically generated by the FlatBuffers compiler, do not modify

# namespace: 

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class Arf2(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Arf2()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsArf2(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # Arf2
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # Arf2
    def Before(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint32Flags, o + self._tab.Pos)
        return 0

    # Arf2
    def WgoRequired(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint8Flags, o + self._tab.Pos)
        return 0

    # Arf2
    def HgoRequired(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint8Flags, o + self._tab.Pos)
        return 0

    # Arf2
    def Wish(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            x = self._tab.Vector(o)
            x += flatbuffers.number_types.UOffsetTFlags.py_type(j) * 4
            x = self._tab.Indirect(x)
            from WishGroup import WishGroup
            obj = WishGroup()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # Arf2
    def WishLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # Arf2
    def WishIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        return o == 0

    # Arf2
    def Hint(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(flatbuffers.number_types.Uint64Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 8))
        return 0

    # Arf2
    def HintAsNumpy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Uint64Flags, o)
        return 0

    # Arf2
    def HintLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # Arf2
    def HintIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        return o == 0

    # Arf2
    def SpecialHint(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(14))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint16Flags, o + self._tab.Pos)
        return 0

    # Arf2
    def DtsLayer1(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(16))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(flatbuffers.number_types.Uint64Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 8))
        return 0

    # Arf2
    def DtsLayer1AsNumpy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(16))
        if o != 0:
            return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Uint64Flags, o)
        return 0

    # Arf2
    def DtsLayer1Length(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(16))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # Arf2
    def DtsLayer1IsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(16))
        return o == 0

    # Arf2
    def DtsLayer2(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(18))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(flatbuffers.number_types.Uint64Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 8))
        return 0

    # Arf2
    def DtsLayer2AsNumpy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(18))
        if o != 0:
            return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Uint64Flags, o)
        return 0

    # Arf2
    def DtsLayer2Length(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(18))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # Arf2
    def DtsLayer2IsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(18))
        return o == 0

    # Arf2
    def Index(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(20))
        if o != 0:
            x = self._tab.Vector(o)
            x += flatbuffers.number_types.UOffsetTFlags.py_type(j) * 4
            x = self._tab.Indirect(x)
            from Arf2Index import Arf2Index
            obj = Arf2Index()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # Arf2
    def IndexLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(20))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # Arf2
    def IndexIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(20))
        return o == 0

def Arf2Start(builder):
    builder.StartObject(9)

def Start(builder):
    Arf2Start(builder)

def Arf2AddBefore(builder, before):
    builder.PrependUint32Slot(0, before, 0)

def AddBefore(builder, before):
    Arf2AddBefore(builder, before)

def Arf2AddWgoRequired(builder, wgoRequired):
    builder.PrependUint8Slot(1, wgoRequired, 0)

def AddWgoRequired(builder, wgoRequired):
    Arf2AddWgoRequired(builder, wgoRequired)

def Arf2AddHgoRequired(builder, hgoRequired):
    builder.PrependUint8Slot(2, hgoRequired, 0)

def AddHgoRequired(builder, hgoRequired):
    Arf2AddHgoRequired(builder, hgoRequired)

def Arf2AddWish(builder, wish):
    builder.PrependUOffsetTRelativeSlot(3, flatbuffers.number_types.UOffsetTFlags.py_type(wish), 0)

def AddWish(builder, wish):
    Arf2AddWish(builder, wish)

def Arf2StartWishVector(builder, numElems):
    return builder.StartVector(4, numElems, 4)

def StartWishVector(builder, numElems: int) -> int:
    return Arf2StartWishVector(builder, numElems)

def Arf2AddHint(builder, hint):
    builder.PrependUOffsetTRelativeSlot(4, flatbuffers.number_types.UOffsetTFlags.py_type(hint), 0)

def AddHint(builder, hint):
    Arf2AddHint(builder, hint)

def Arf2StartHintVector(builder, numElems):
    return builder.StartVector(8, numElems, 8)

def StartHintVector(builder, numElems: int) -> int:
    return Arf2StartHintVector(builder, numElems)

def Arf2AddSpecialHint(builder, specialHint):
    builder.PrependUint16Slot(5, specialHint, 0)

def AddSpecialHint(builder, specialHint):
    Arf2AddSpecialHint(builder, specialHint)

def Arf2AddDtsLayer1(builder, dtsLayer1):
    builder.PrependUOffsetTRelativeSlot(6, flatbuffers.number_types.UOffsetTFlags.py_type(dtsLayer1), 0)

def AddDtsLayer1(builder, dtsLayer1):
    Arf2AddDtsLayer1(builder, dtsLayer1)

def Arf2StartDtsLayer1Vector(builder, numElems):
    return builder.StartVector(8, numElems, 8)

def StartDtsLayer1Vector(builder, numElems: int) -> int:
    return Arf2StartDtsLayer1Vector(builder, numElems)

def Arf2AddDtsLayer2(builder, dtsLayer2):
    builder.PrependUOffsetTRelativeSlot(7, flatbuffers.number_types.UOffsetTFlags.py_type(dtsLayer2), 0)

def AddDtsLayer2(builder, dtsLayer2):
    Arf2AddDtsLayer2(builder, dtsLayer2)

def Arf2StartDtsLayer2Vector(builder, numElems):
    return builder.StartVector(8, numElems, 8)

def StartDtsLayer2Vector(builder, numElems: int) -> int:
    return Arf2StartDtsLayer2Vector(builder, numElems)

def Arf2AddIndex(builder, index):
    builder.PrependUOffsetTRelativeSlot(8, flatbuffers.number_types.UOffsetTFlags.py_type(index), 0)

def AddIndex(builder, index):
    Arf2AddIndex(builder, index)

def Arf2StartIndexVector(builder, numElems):
    return builder.StartVector(4, numElems, 4)

def StartIndexVector(builder, numElems: int) -> int:
    return Arf2StartIndexVector(builder, numElems)

def Arf2End(builder):
    return builder.EndObject()

def End(builder):
    return Arf2End(builder)
