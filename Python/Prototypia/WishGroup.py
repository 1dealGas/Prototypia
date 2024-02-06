# Source: Arf2.fbs
# Please conform to the License of FlatBuffers(Apache 2.0 License).


# automatically generated by the FlatBuffers compiler, do not modify
# namespace:

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class WishGroup(object):
	__slots__ = ['_tab']

	@classmethod
	def GetRootAs(cls, buf, offset=0):
		n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
		x = WishGroup()
		x.Init(buf, n + offset)
		return x

	@classmethod
	def GetRootAsWishGroup(cls, buf, offset=0):
		"""This method is deprecated. Please switch to GetRootAs."""
		return cls.GetRootAs(buf, offset)
	# WishGroup
	def Init(self, buf, pos):
		self._tab = flatbuffers.table.Table(buf, pos)

	# WishGroup
	def Info(self):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
		if o != 0:
			return self._tab.Get(flatbuffers.number_types.Uint32Flags, o + self._tab.Pos)
		return 4294967295

	# WishGroup
	def Nodes(self, j):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
		if o != 0:
			a = self._tab.Vector(o)
			return self._tab.Get(flatbuffers.number_types.Uint64Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 8))
		return 0

	# WishGroup
	def NodesAsNumpy(self):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
		if o != 0:
			return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Uint64Flags, o)
		return 0

	# WishGroup
	def NodesLength(self):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
		if o != 0:
			return self._tab.VectorLen(o)
		return 0

	# WishGroup
	def NodesIsNone(self):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
		return o == 0

	# WishGroup
	def Childs(self, j):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
		if o != 0:
			x = self._tab.Vector(o)
			x += flatbuffers.number_types.UOffsetTFlags.py_type(j) * 4
			x = self._tab.Indirect(x)
			from WishChild import WishChild
			obj = WishChild()
			obj.Init(self._tab.Bytes, x)
			return obj
		return None

	# WishGroup
	def ChildsLength(self):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
		if o != 0:
			return self._tab.VectorLen(o)
		return 0

	# WishGroup
	def ChildsIsNone(self):
		o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
		return o == 0

def WishGroupStart(builder):
	builder.StartObject(3)

def Start(builder):
	WishGroupStart(builder)

def WishGroupAddInfo(builder, info):
	builder.PrependUint32Slot(0, info, 4294967295)

def AddInfo(builder, info):
	WishGroupAddInfo(builder, info)

def WishGroupAddNodes(builder, nodes):
	builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(nodes), 0)

def AddNodes(builder, nodes):
	WishGroupAddNodes(builder, nodes)

def WishGroupStartNodesVector(builder, numElems):
	return builder.StartVector(8, numElems, 8)

def StartNodesVector(builder, numElems: int) -> int:
	return WishGroupStartNodesVector(builder, numElems)

def WishGroupAddChilds(builder, childs):
	builder.PrependUOffsetTRelativeSlot(2, flatbuffers.number_types.UOffsetTFlags.py_type(childs), 0)

def AddChilds(builder, childs):
	WishGroupAddChilds(builder, childs)

def WishGroupStartChildsVector(builder, numElems):
	return builder.StartVector(4, numElems, 4)

def StartChildsVector(builder, numElems: int) -> int:
	return WishGroupStartChildsVector(builder, numElems)

def WishGroupEnd(builder):
	return builder.EndObject()

def End(builder):
	return WishGroupEnd(builder)
