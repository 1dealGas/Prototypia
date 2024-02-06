# Source: Arf2.fbs
# Please conform to the License of FlatBuffers(Apache 2.0 License).


# automatically generated by the FlatBuffers compiler, do not modify
# namespace:

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class WishChild(object):
	__slots__ = ['_tab']

	@classmethod
	def GetRootAs(cls, buf, offset=0):
		n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
		x = WishChild()
		x.Init(buf, n + offset)
		return x

	@classmethod
	def GetRootAsWishChild(cls, buf, offset=0):
		"""This method is deprecated. Please switch to GetRootAs."""
		return cls.GetRootAs(buf, offset)
	# WishChild
	def Init(self, buf, pos):
		self._tab = flatbuffers.table.Table(buf, pos)

	# WishChild
	def P(self):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
		if o != 0:
			return self._tab.Get(flatbuffers.number_types.Uint8Flags, o + self._tab.Pos)
		return 255

	# WishChild
	def Dt(self):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
		if o != 0:
			return self._tab.Get(flatbuffers.number_types.Uint32Flags, o + self._tab.Pos)
		return 0

	# WishChild
	def Anodes(self, j):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
		if o != 0:
			a = self._tab.Vector(o)
			return self._tab.Get(flatbuffers.number_types.Uint32Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
		return 0

	# WishChild
	def AnodesAsNumpy(self):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
		if o != 0:
			return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Uint32Flags, o)
		return 0

	# WishChild
	def AnodesLength(self):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
		if o != 0:
			return self._tab.VectorLen(o)
		return 0

	# WishChild
	def AnodesIsNone(self):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
		return o == 0

def WishChildStart(builder):
	builder.StartObject(3)

def Start(builder):
	WishChildStart(builder)

def WishChildAddP(builder, p):
	builder.PrependUint8Slot(0, p, 255)

def AddP(builder, p):
	WishChildAddP(builder, p)

def WishChildAddDt(builder, dt):
	builder.PrependUint32Slot(1, dt, 0)

def AddDt(builder, dt):
	WishChildAddDt(builder, dt)

def WishChildAddAnodes(builder, anodes):
	builder.PrependUOffsetTRelativeSlot(2, flatbuffers.number_types.UOffsetTFlags.py_type(anodes), 0)

def AddAnodes(builder, anodes):
	WishChildAddAnodes(builder, anodes)

def WishChildStartAnodesVector(builder, numElems):
	return builder.StartVector(4, numElems, 4)

def StartAnodesVector(builder, numElems: int) -> int:
	return WishChildStartAnodesVector(builder, numElems)

def WishChildEnd(builder):
	return builder.EndObject()

def End(builder):
	return WishChildEnd(builder)
