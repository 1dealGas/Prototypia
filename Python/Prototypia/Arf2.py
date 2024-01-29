# Common Imports
from ast import *
from typing import *

import sys
import atexit
import inspect
import functools
import flatbuffers

# Flatbuffers Related Imports
from . import Arf2Fb
from . import Arf2Index
from . import WishChild as WishChildFb
from . import WishGroup as WishGroupFb


# Error Handling & Tools
E = Exception
class BPMInvalidError			(E):pass
class ScaleInvalidError			(E):pass
class ManualProhibition			(E):pass
class OverlapProhibition		(E):pass

def NonManual(f) -> FunctionType:
	def decorated(*args, **kwargs) -> None:
		if inspect.stack()[1].function == "<module>" : raise ManualProhibition('''This method is prohibited to call manually.''')
		return f(*args, **kwargs)
	return decorated

@functools.cmp_to_key
def PosNodeSorter(a, b) -> int:
	if a.bartime > b.bartime: return 1
	elif a.bartime < b.bartime: return -1
	elif id(a) == id(b): return 0
	else: raise OverlapProhibition('''Adding multiple PosNodes with the same Bartime to a single WishGroup is prohibited.''')


# Arf2 Prototype
class Arf2Prototype:
	'''
	A rough Singeleton class of the Prototype Data of an Arf2 chart[fumen].
	'''
	_wgo_required:int							= 255   		# [0,255]
	_hgo_required:int							= 255   		# [0,255]
	_hint:list									= []			# Type: list[Hint]
	_wish:list									= []			# Type: list[WishGroup]

	_offset:int									= 0				# A ms value (>=0)
	_bpms:list[Tuple[float,float]]				= []			# (Bartime, BPM)
	_scales_layer1:list[Tuple[float,float]]		= [(0,1)]		# (Bartime, Scale)
	_scales_layer2:list[Tuple[float,float]]		= [(0,1)]		# Bartime>=0   BPM>0

	_current_angle:int							= 90			# Degree [-1800,1800]
	_last_hint									= None			# Type: Hint
	_sc1_dflt:bool								= True
	_sc2_dflt:bool								= True


# Arf2 Data Structure Classes
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
		self.bartime:float = Bartime
		self.ref = Ref
		self.is_special:bool = False

		self._ms:int = 0
		self._x:float = 0
		self._y:float = 0

class PosNode:
	'''
	Class of Nodes that a Wish passes by.
	'''
	@NonManual
	def __init__(self, Bartime:float, X:float, Y:float, EaseType:int, CurveInit:float, CurveEnd:float) -> None:
		self.bartime:float = Bartime
		self.x:float = X
		self.y:float = Y
		if EaseType == 4:
			self.easetype:int = 3
			self.curve_init:float = CurveEnd
			self.curve_end:float = CurveInit
		else:
			self.easetype:int = EaseType
			self.curve_init:float = CurveInit
			self.curve_end:float = CurveEnd
		self._ms:int = 0

class WishChild:
	'''
	WishChild refers a WishGroup's position and the current DTime to determine its position
	in a polar-coordinate-like way.
	'''
	@NonManual
	def __init__(self, Bartime:float, DefaultAngle:int) -> None:
		self.bartime = Bartime
		self.is_default_angle:bool = True
		self.anodes:list[Tuple[float,int,int]] = [
			# AngleNode: Tuple(Bartime, Angle, EaseType)
			# An.STASIS == 0
			(0, DefaultAngle, 0)
		]
		self._dt:float = 0
		self._final_anodes:list[Tuple[float,int,int]] = []


class WishGroup:
	'''
	Class of Wishes in an Arf2 chart[fumen].
	In Aerials, Wish guides the player to light the Hint.
	'''
	@NonManual
	def __init__(self, ofLayer2:bool = False, MaxVisibleDistance:float = 7) -> None:
		self.__nodes:list[PosNode] = []
		self.__childs:list[WishChild] = []
		self.__of_layer2 = ofLayer2
		self.__max_visible_distance = MaxVisibleDistance
		self.__last_child:WishChild = None
		self.__useless:bool = False

	# Several Methods for the WishGroup instance
	def n(self, bar:float, nmr:int = 0, dnm:int = 1, x:float = 0, y:float = 0, easetype:int = 0, curve_init:float = 0, curve_end:float = 1) -> Self:
		'''
		Add a PosNode to the calling WishGroup.
		PosNodes will be sorted automatically.

		Args:
			bar (float): Bartime integer or the Original Bartime
			nmr (int): Numerator to specify the internal position in a bar. Example 5/16 -> 5
			dnm (int): Denominator to specify the internal position in a bar. Example 5/16 -> 16
			x (float): The x-axis position of the PosNode. Range[-16,32]
			y (float): The y-axis position of the PosNode. Range[-8,16]
			easetype (int): EaseType of the AngleNode. Use Pn.* Series.
			curve_init (float): The initial ratio of the easing curve. Range[0,1]
			curve_end (float): The end ratio of the easing curve. Range[0,1]

		Returns:
			Self (WishGroup): for Method Chaining Usage.
		'''
		bartime = float(bar) + float(nmr) / float(dnm)
		if bartime < 0:
			raise ValueError("Bartime(bar+nmr/dnm) must be larger than 0.")
		
		x = float(x)
		y = float(y)
		if x < -16  or  x > 32:
			raise ValueError("X-Axis Position out of Range [-16,32].")
		if y < -8  or  y > 16:
			raise ValueError("Y-Axis Position out of Range [-8,16].")
		
		easetype = int(easetype)
		if easetype < 0  or  easetype > 4:
			raise TypeError("Invalid PosNode EaseType. Use Pn.* Series.")
		
		curve_init = float(curve_init)
		curve_end = float(curve_end)
		if curve_init < 0  or  curve_init > 1:
			raise ValueError("CurveInit out of Range [0,1].")
		if curve_end < 0  or  curve_end > 1:
			raise ValueError("CurveEnd out of Range [0,1].")
		if curve_init >= curve_end:
			raise ValueError("CurveEnd Value must be larger than CurveInit Value.")

		n = PosNode(bartime, x, y, easetype, curve_init, curve_end)
		self.__nodes.append(n)
		self.__nodes.sort(key = PosNodeSorter)
		return self

	def c(self, bar:float, nmr:int = 0, dnm:int = 1, angle:int = Arf2Prototype._current_angle) -> Self:
		'''
		Add a WishChild to the calling WishGroup.
		WishChilds will be sorted automatically.

		Args:
			bar (float): Bartime integer or the Original Bartime
			nmr (int): Numerator to specify the internal position in a bar. Example 5/16 -> 5
			dnm (int): Denominator to specify the internal position in a bar. Example 5/16 -> 16
			angle (int): The default angle degree value of the newly-created WishChild. Range [-1800,1800]

		Returns:
			Self (WishGroup): for Method Chaining Usage.
		'''
		bartime = float(bar) + float(nmr) / float(dnm)
		angle = int(angle)
		if bartime < 0:
			raise ValueError("Bartime(bar+nmr/dnm) must be larger than 0.")
		if angle < -1800  or  angle > 1800:
			raise ValueError("Degree of AngleNode out of Range [-1800,1800].")
		
		c = WishChild(bartime, angle)
		self.__last_child = c
		self.__childs.append(c)
		self.__childs.sort( key = lambda wc: wc.bartime )
		return self

	def a(self, bar:float, nmr:int = 0, dnm:int = 1, degree:int = 90, easetype:int = 0) -> Self:
		'''
		Add an AngleNode to the last-created WishChild of calling WishGroup.
		AngleNodes will be sorted automatically.

		Args:
			bar (float): Bartime integer or the Original Bartime
			nmr (int): Numerator to specify the internal position in a bar. Example 5/16 -> 5
			dnm (int): Denominator to specify the internal position in a bar. Example 5/16 -> 16
			degree (int): The polar coordinate angle value in degree form.
			easetype (int): EaseType of the AngleNode. Use An.* Series.

		Returns:
			Self (WishGroup): for Method Chaining Usage.
		'''
		bartime = float(bar) + float(nmr) / float(dnm)
		degree = int(degree)
		if bartime < 0:
			raise ValueError("Bartime(bar+nmr/dnm) must be larger than 0.")
		if degree < -1800  or  degree > 1800:
			raise ValueError("Degree of AngleNode out of Range [-1800,1800].")
		
		easetype = int(easetype)
		if easetype < 0  or  easetype > 3:
			raise TypeError("Invalid AngleNode EaseType. Use An.* Series.")
		
		if self.__last_child == None:
			raise RuntimeError("Please attach at least one WishChild on the WishGroup before creating a AngleNode.")

		_lc = self.__last_child
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
			nmr (int): Numerator to specify the internal position in a bar. Example 5/16 -> 5
			dnm (int): Denominator to specify the internal position in a bar. Example 5/16 -> 16

		Returns:
			Self (WishGroup): for Method Chaining Usage.
		'''
		bartime = bar+nmr/float(dnm)
		if bartime < 0:
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
		self.__useless = useless
		return self
	

	@NonManual
	def _EXPORT_(self) -> dict: return {
		"nodes" : self.__nodes,
		"childs" : self.__childs,
		"of_layer2" : self.__of_layer2,
		"max_visible_distance" : self.__max_visible_distance,
		"last_child" : self.__last_child,
		"useless" : self.__useless
	}


# Arf2 Compiler Function
def Arf2Compile() -> None:
	'''
	This function processes the data contained in the Arf2Prototype class,
	And then encode it into a *.arf file.
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