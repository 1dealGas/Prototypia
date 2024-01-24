# Common Imports
from ast import NotIn, Tuple
from typing import Self
import sys
import atexit
import functools
import flatbuffers

# Flatbuffers Related Imports
import Arf2 as FB_Arf2
import Arf2Index as FB_Index
import WishChild as FB_WishChild
import WishGroup as FB_WishGroup


# Error Handling & Tools
E = Exception
class                                		ManualProhibition(E):
	def __str__(self) -> str: return 	''' The "new method is prohibited to call in the __main__ script. '''
class                                		PnOverlapProhibition(E):
	def __str__(self) -> str: return 	''' Adding multiple PosNodes with the same Bartime to a single WishGroup is prohibited. '''

def NonManual(f) -> function:
	def decorated(*args, **kwargs) -> None:
		if __name__ == "__main__": raise ManualProhibition
		return f(*args, **kwargs)
	return decorated

@functools.cmp_to_key
def PosNodeSorter(a,b) -> int:
	if a.bartime > b.bartime: return 1
	elif a.bartime < b.bartime: return -1
	elif id(a)==id(b): return 0
	else: raise PnOverlapProhibition


# Arf2 Data Structure Classes
class Arf2Prototype:
	'''
	A rough Singeleton class of the Prototype Data of an Arf2 chart[fumen].
	'''
	_hint:list									= []	# Type: list[Hint]
	_wish:list									= []	# Type: list[WishGroup]
	_offset:int									= 0		# A ms value (>=0)
	_current_angle:int							= 90	# Degree [-1800,1800]
	_last_hint									= None	# Type: Hint
	_bpms:list[tuple(float,float)]				= []	# (Bartime, BPM)
	_scales_layer1:list[tuple(float,float)]		= []	# (Bartime, Scale)
	_scales_layer2:list[tuple(float,float)]		= []	# Bartime>=0   BPM>0
	
class Hint:
	'''
	Hint represents the Tap Note of Aerials.
	The position(x,y) will be determined in the compiling progress.
	'''
	@NonManual
	def __init__(self, Bartime:float, Ref) -> None:
		'''
		The type of Ref is "WishGroup".
		'''
		self.bartime = Bartime
		self.ref = Ref
		self.is_special = False

		self._ms = 0
		self._x = 0
		self._y = 0

class PosNode:
	'''
	Class of Nodes that a Wish passes by.
	'''
	@NonManual
	def __init__(self, Bartime:float, X:float, Y:float, EaseType:int, CurveInit:float, CurveEnd:float) -> None:
		self.bartime = Bartime
		self.x = X
		self.y = Y
		if EaseType == 4:
			self.easetype = 3
			self.curve_init = CurveEnd
			self.curve_end = CurveInit
		else:
			self.easetype = EaseType
			self.curve_init = CurveInit
			self.curve_end = CurveEnd
		self._ms = 0

class WishChild:
	'''
	WishChild refers a WishGroup's position and the current DTime to determine its position
	in a polar-coordinate-like way.
	'''
	@NonManual
	def __init__(self, Bartime:float) -> None:
		self.bartime = Bartime
		self.is_default_angle:bool = True
		self.anodes = [
			# AngleNode: Tuple(Bartime, Angle, EaseType)
			(0, Arf2Prototype._current_angle, WishChild.STASIS)
		]
		self._dt = 0
		self._final_anodes = []


class WishGroup:
	'''
	Class of Wishes in an Arf2 chart[fumen].
	In Aerials, Wish guides the player to light the Hint.
	'''
	@NonManual
	def __init__(self, ofLayer2:bool = False, MaxVisibleDistance:float = 7) -> None:
		self.nodes:list[PosNode] = []
		self.childs:list[WishChild] = []
		self.of_layer2 = ofLayer2
		self.max_visible_distance = MaxVisibleDistance
		self._last_child:WishChild = None
		self._useless:bool = False
	
	# Several Methods for the WishGroup instance
	def n(self, bar:float, nmr:int=0, dnm:int=1, x:float=0, y:float=0, easetype:int=0, curve_init:float=0, curve_end:float=1) -> Self:
		'''
		Add a PosNode to the calling WishGroup.
		PosNodes will be sorted automatically.

		Args:
			bar (float): Bartime integer or the Original Bartime
			nmr (int): numerator to specify the internal position in a bar. Example 5/16 -> 5
			dnm (int): denominator to specify the internal position in a bar. Example 5/16 -> 16
			x (float): The x-axis position of the PosNode. Range[-16,32]
			y (float): The y-axis position of the PosNode. Range[-8,16]
			easetype (int): EaseType of the AngleNode. Use Pn.* Series.
			curve_init (float): The initial ratio of the easing curve. Range[0,1]
			curve_end (float): The end ratio of the easing curve. Range[0,1]
		
		Returns:
			Self (WishGroup): for Method Chaining Usage.
		'''
		bartime = bar+nmr/float(dnm)
		if bartime<0:
			raise ValueError("Bartime(bar+nmr/dnm) must be larger than 0.")
		if x<-16 or x>32:
			raise ValueError("X-Axis Position out of Range [-16,32].")
		if y<-8 or y>16:
			raise ValueError("Y-Axis Position out of Range [-8,16].")
		if easetype not in [0,1,2,3,4]:
			raise TypeError("Invalid PosNode EaseType. Use Pn.* Series.")
		if curve_init<0 or curve_init>1:
			raise ValueError("CurveInit out of Range [0,1].")
		if curve_end<0 or curve_end>1:
			raise ValueError("CurveEnd out of Range [0,1].")
		if curve_init >= curve_end:
			raise ValueError("CurveEnd Value must be larger than CurveInit Value.")
		
		n = PosNode(bartime, x, y, easetype, curve_init, curve_end)
		self.nodes.append(n)
		self.nodes.sort(key = PosNodeSorter)
		return self

	def c(self, bar:float, nmr:int=0, dnm:int=1, angle:int=Arf2Prototype._current_angle) -> Self:
		'''
		Under Construction
		'''
		return self

	def a(self, bar:float, nmr:int=0, dnm:int=1, degree:int=90, easetype:int=0) -> Self:
		'''
		Add an AngleNode to the last WishChild of current WishGroup.
		AngleNodes will be sorted automatically.

		Args:
			bar (float): Bartime integer or the Original Bartime
			nmr (int): numerator to specify the internal position in a bar. Example 5/16 -> 5
			dnm (int): denominator to specify the internal position in a bar. Example 5/16 -> 16
			degree (int): The polar coordinate angle value in degree form.
			easetype (int): EaseType of the AngleNode. Use An.* Series.
		
		Returns:
			Self (WishGroup): for Method Chaining Usage.
		'''
		bartime = bar+nmr/float(dnm)
		if bartime<0:
			raise ValueError("Bartime(bar+nmr/dnm) must be larger than 0.")
		if degree<-1800 or degree>1800:
			raise ValueError("Degree of AngleNode out of Range [-1800,1800].")
		if easetype not in [0,1,2,3]:
			raise TypeError("Invalid AngleNode EaseType. Use An.* Series.")
		if self._last_child == None:
			raise RuntimeError("Please attach at least one WishChild on the WishGroup before creating a AngleNode.")

		_lc = self._last_child
		if _lc.is_default_angle:
			_lc.anodes[0] = (bartime,degree,easetype)
			_lc.is_default_angle = False
		else:
			_lc.anodes.append( (bartime,degree,easetype) )
			_lc.anodes.sort(key = lambda a: a[0])
		return self

	def manual_hint(self, bar:float, nmr:int=0, dnm:int=1) -> Self:
		'''
		Manually create a Hint referring to the calling WishGroup.

		Args:
			bar (float): Bartime integer or the Original Bartime
			nmr (int): numerator to specify the internal position in a bar. Example 5/16 -> 5
			dnm (int): denominator to specify the internal position in a bar. Example 5/16 -> 16
		
		Returns:
			Self (WishGroup): for Method Chaining Usage.
		'''
		bartime = bar+nmr/float(dnm)
		if bartime<0:
			raise ValueError("Bartime(bar+nmr/dnm) must be larger than 0.")
		
		h = Hint(bartime, self)
		Arf2Prototype._hint.append(h)
		Arf2Prototype._last_hint = h
		return self
	
	def set_useless(self, useless:bool) -> Self:
		'''
		Wishes tagged as "useless" will be ignored in the compiling process,
		Hints referring to which will be ignored as well.
		Useful for locating other objects.

		Args:
			useless (bool): Should the calling WishGroup instance be tagged as "useless"?
		
		Returns:
			Self (WishGroup): for Method Chaining Usage.
		'''
		self._useless = useless
		return self


# Arf2 Compiler Function
def Arf2Compile() -> None:
	'''
	This function processes the data contained in the Arf2Prototype class,
	and then encode it into a *.arf file.
	'''
	pass


# Automating the Compiler Function
atexit.register(Arf2Compile)
ORIG_EH = sys.excepthook
def EH(arg1, arg2, arg3) -> None:
	atexit.unregister(Arf2Compile)
	ORIG_EH(arg1, arg2, arg3)
sys.excepthook = EH
sys.exit = None   # Ban the SystemExit Exception.