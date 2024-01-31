# automatically generated by the FlatBuffers compiler, do not modify

# namespace:

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class Arf2Index(object):
	__slots__ = ['_tab']

	@classmethod
	def GetRootAs(cls, buf, offset=0):
		n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
		x = Arf2Index()
		x.Init(buf, n + offset)
		return x

	@classmethod
	def GetRootAsArf2Index(cls, buf, offset=0):
		"""This method is deprecated. Please switch to GetRootAs."""
		return cls.GetRootAs(buf, offset)
	# Arf2Index
	def Init(self, buf, pos):
		self._tab = flatbuffers.table.Table(buf, pos)

	# Arf2Index
	def Widx(self, j):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
		if o != 0:
			a = self._tab.Vector(o)
			return self._tab.Get(flatbuffers.number_types.Uint16Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 2))
		return 0

	# Arf2Index
	def WidxAsNumpy(self):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
		if o != 0:
			return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Uint16Flags, o)
		return 0

	# Arf2Index
	def WidxLength(self):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
		if o != 0:
			return self._tab.VectorLen(o)
		return 0

	# Arf2Index
	def WidxIsNone(self):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
		return o == 0

	# Arf2Index
	def Hidx(self, j):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
		if o != 0:
			a = self._tab.Vector(o)
			return self._tab.Get(flatbuffers.number_types.Uint16Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 2))
		return 0

	# Arf2Index
	def HidxAsNumpy(self):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
		if o != 0:
			return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Uint16Flags, o)
		return 0

	# Arf2Index
	def HidxLength(self):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
		if o != 0:
			return self._tab.VectorLen(o)
		return 0

	# Arf2Index
	def HidxIsNone(self):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
		return o == 0

def Arf2IndexStart(builder):
	builder.StartObject(2)

def Start(builder):
	Arf2IndexStart(builder)

def Arf2IndexAddWidx(builder, widx):
	builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(widx), 0)

def AddWidx(builder, widx):
	Arf2IndexAddWidx(builder, widx)

def Arf2IndexStartWidxVector(builder, numElems):
	return builder.StartVector(2, numElems, 2)

def StartWidxVector(builder, numElems: int) -> int:
	return Arf2IndexStartWidxVector(builder, numElems)

def Arf2IndexAddHidx(builder, hidx):
	builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(hidx), 0)

def AddHidx(builder, hidx):
	Arf2IndexAddHidx(builder, hidx)

def Arf2IndexStartHidxVector(builder, numElems):
	return builder.StartVector(2, numElems, 2)

def StartHidxVector(builder, numElems: int) -> int:
	return Arf2IndexStartHidxVector(builder, numElems)

def Arf2IndexEnd(builder):
	return builder.EndObject()

def End(builder):
	return Arf2IndexEnd(builder)
