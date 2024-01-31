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
class InterpolationError		(E):pass
class PseudoDecoratorError		(E):pass
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
	wgo_required:int							= 255   		# [0,255]
	hgo_required:int							= 255   		# [0,255]
	hint:list									= []			# Type: list[Hint]
	wish:list									= []			# Type: list[WishGroup]

	offset:int									= 0				# A ms value (>=0)
	bpms:list[Tuple[float,float]]				= []			# (Bartime, BPM)
	scales_layer1:list[Tuple[float,float]]		= [(0,1)]		# (Bartime, Scale)
	scales_layer2:list[Tuple[float,float]]		= [(0,1)]		# Bartime>=0   BPM>0

	current_angle:int							= 90			# Degree [-1800,1800]
	last_hint									= None			# Type: Hint


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

	@NonManual
	def __call__(self) -> dict:
		'''
		A compromise considering both the auto-completing and the exporting.
		'''
		return {
			"nodes" : self.__nodes,
			"childs" : self.__childs,
			"of_layer2" : self.__of_layer2,
			"max_visible_distance" : self.__max_visible_distance,
			"last_child" : self.__last_child,
			"useless" : self.__useless
		}

	def __truediv__(self, func) -> Self:
		'''
		With PseudoDecorator, you may add custom chaining methods for WishGroup instances
		outside the WishGroup class like this:

			def pattern1(param1,param2···):
				def rtn(w):
					# Do some stuff to the WishGroup w
					# Returns of the function "rtn" will be discarded.
				return rtn

		Call your customized methods using "/" instead of "." ,
		For example:

			wgvar / pattern1(param1,param2···) / pattern2(param1,param2···)

		'''
		if type(func) != FunctionType:
			raise PseudoDecoratorError("""The PseudoDecorator must return a function with the method signature "func(w : WishGroup) -> None". """)
		func(self)
		return self


	# Compositional Methods for WishGroup instances
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

	def c(self, bar:float, nmr:int = 0, dnm:int = 1, angle:int = Arf2Prototype.current_angle) -> Self:
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


	# Tool Methods for WishGroup instances
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
		bartime = float(bar) + float(nmr) / float(dnm)
		if bartime < 0:
			raise ValueError("Bartime(bar+nmr/dnm) must be larger than 0.")

		h = Hint(bartime, self)
		Arf2Prototype.hint.append(h)
		Arf2Prototype.last_hint = h
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
		self.__useless = bool(useless)
		return self
	
	def GET(self, bartime:float) -> Union[ None, Tuple[float,float,float,float,PosNode,PosNode] ]:
		'''
		--------
		Not suitable for method chaining
		This method doesn't return the WishGroup instance "Self".
		--------

		Get the interpolation result accoring to the Bartime input.
		Mostly used internally.

		Args:
			bartime (float): the Original Bartime
		
		Returns:
			None  ->  if the interpolation fails
			Tuple ->  (x, y, original_ratio, actual_ratio, current_posnode, next_posnode)
		'''
		pnsize = len(self.__nodes)
		if pnsize < 2:
			raise InterpolationError("At least 2 PosNodes are required to complete an interpolation.")
		
		if bartime < 0:
			raise ValueError("Bartime(bar+nmr/dnm) must be larger than 0.")
		elif bartime < self.__nodes[0].bartime: return
		elif bartime >= self.__nodes[-1].bartime: return

		for i in range(pnsize-1):
			current_posnode = self.__nodes[i]
			next_posnode = self.__nodes[i+1]

			t0 = current_posnode.bartime
			if bartime < t0: continue

			x0 = current_posnode.x
			y0 = current_posnode.y
			dx = next_posnode.x - x0
			dy = next_posnode.y - y0
			dt = next_posnode.bartime - t0
			original_ratio = float(bartime - t0) / float(dt)

			# Evaluating the ease_ratio
			easetype = current_posnode.easetype
			ci = current_posnode.curve_init
			ce = current_posnode.curve_end
			if easetype == 0:
				ease_ratio = 0
			



		return
		


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