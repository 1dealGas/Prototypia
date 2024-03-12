# Common Imports
from ast import *
from math import *
from typing import *

import os, sys, atexit, inspect, functools
import time, shutil
import flatbuffers

# Flatbuffers Related Imports
from . import Arf2Fb
from . import Arf2Index
from . import WishChild as WishChildFb
from . import WishGroup as WishGroupFb


# Error Handling & Tools
E = Exception
class MoveError						(E):pass
class BPMInvalidError				(E):pass
class ScaleInvalidError				(E):pass
class AnglenodeInvalidError			(E):pass
class InterpolationError			(E):pass
class PseudoDecoratorError			(E):pass
class ManualProhibition				(E):pass
class OverlapProhibition			(E):pass
class MirrorLRAngleProhibition		(E):pass

def NonManual(f:FunctionType) -> FunctionType:
	def decorated(*args, **kwargs) -> None:
		if inspect.stack()[1].function == "<module>" : raise ManualProhibition('''This method is prohibited to call manually.''')
		return f(*args, **kwargs)
	return decorated

VERSE = []
def NEW_VERSE() -> None:
	'''
	You may use the symbol "VERSE" to operate a series of WishGroup included in,
	this helps you to maneuver things like copy results more easily for a bit.

	The "NEWVERSE" method creates a new "VERSE" list, and discards the former one.
	It's not necessary to explicitly create an initial "VERSE" before writing something.

	Args:
		None

	Returns:
		None
	'''
	global VERSE
	VERSE = []

half_pi = pi / 2
def ESIN(ratio:float) -> float:
	ratio = float(ratio)
	ratio = ratio if ratio>0 else 0
	ratio = ratio if ratio<1 else 1
	return sin(ratio * half_pi)
def ECOS(ratio:float) -> float:
	ratio = float(ratio)
	ratio = ratio if ratio>0 else 0
	ratio = ratio if ratio<1 else 1
	return 1 - cos(ratio * half_pi)
def InQuad(ratio:float) -> float:
	ratio = float(ratio)
	ratio = ratio if ratio>0 else 0
	ratio = ratio if ratio<1 else 1
	return ratio * ratio
def OutQuad(ratio:float) -> float:
	ratio = float(ratio)
	ratio = ratio if ratio>0 else 0
	ratio = ratio if ratio<1 else 1
	ratio = 1 - ratio
	return 1 - ratio * ratio
def get_original(p1:float, p2:float, curve_init:float, curve_end:float, ease_func:FunctionType) -> Tuple[float,float]:
	fci = ease_func(curve_init)
	fce = ease_func(curve_end)
	dnm = fce - fci
	p = (fce*p1 - fci*p2) / dnm
	dp = (p2 - p1) / dnm
	return (p,dp)

@functools.cmp_to_key
def OPSorter(a, b) -> int:
	'''
	To implement the Overlap Prohibition,
	use this sorter instead of "lambda x: x.bartime".
	'''
	if a.bartime > b.bartime: return 1
	elif a.bartime < b.bartime: return -1
	elif id(a) == id(b): return 0
	else: raise OverlapProhibition("Adding multiple PosNodes/WishChilds/Hints with the same Bartime to a single WishGroup is prohibited.")

@functools.cmp_to_key
def OPSorterForAngleNodes(a:Tuple[float,int,int], b:Tuple[float,int,int]) -> int:
	if a[0] > b[0]: return 1
	elif a[0] < b[0]: return -1
	elif id(a) == id(b): return 0
	else: raise OverlapProhibition("Adding multiple AngleNodes with the same Bartime to a single WishChild is prohibited.")

# v0.5: Deprecate the OPSorter for PosNodes.
@functools.cmp_to_key
def TPSorter(a:tuple[Any, int], b:tuple[Any, int]) -> int:
	if a[0].bartime > b[0].bartime: return 1
	elif a[0].bartime < b[0].bartime: return -1
	elif a[1] > b[1]: return 1
	elif a[1] < b[1]: return -1
	else: return 0
def SortPosNodes(l:list) -> None:
	_tl = []
	_idx = 0
	for n in l:
		_tl.append( (n, _idx) )
		_idx += 1
	_tl.sort(key = TPSorter)
	for i in range(len(l)):
		l[i] = _tl[i][0]


# Arf2 Class Defs
class Arf2Prototype:
	'''
	A rough Singeleton class of the Prototype Data of an Arf2 chart[fumen].
	'''
	wgo_required:int							= 255   		# [0,255]
	hgo_required:int							= 255   		# [0,255]
	special_hint:int							= 0				# [0,65535]
	hint:list									= []			# Type: list[Hint]
	wish:list									= []			# Type: list[WishGroup]

	offset:int									= 0				# A ms value (>=0)
	bpms:list[Tuple[float,float]]				= []			# (Bartime, BPM)
	scales_layer1:list[Tuple[float,float]]		= [(0,1)]		# (Bartime, Scale)
	scales_layer2:list[Tuple[float,float]]		= [(0,1)]		# Bartime>=0   BPM>0

	current_angle:int							= 90			# Degree [-1800,1800]
	last_hint									= None			# Type: Hint

class F_VECTOR: '''Refers to a Serialized Flatbuffers Vector.'''
class F_TABLE: '''Refers to a Serialized Flatbuffers Table.'''
class Arf2Serialized:
	before:int = 0
	dts_layer1:F_VECTOR
	dts_layer2:F_VECTOR
	index:Union[list[F_TABLE], F_VECTOR] = []
	wish:Union[list[F_TABLE], F_VECTOR] = []
	wgo_required:int = 0
	hint:F_VECTOR
	hgo_required:int = 0
	special_hint:int = 0
drm_tails:set[int] = {4, 6, 7, 8, 11, 12, 17, 18, 19, 20 ,21, 22, 23, 24}


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

		self._ms:int = None
		self._x:float = None
		self._y:float = None

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
		self._final_anodes:list[Tuple[int,int,int]] = []   # (ms, angle, et)


class WishGroup:
	'''
	Class of Wishes in an Arf2 chart[fumen].
	In Aerials, Wish guides the player to light the Hint.
	'''
	@NonManual
	def __init__(self, ofLayer2:bool = False, MaxVisibleDistance:float = 7) -> None:
		self.__nodes:list[PosNode] = []
		self.__childs:list[WishChild] = []
		self.__mhints:list[Hint] = []
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
			"mhints" : self.__mhints,
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

	def GET(self, bartime:float) -> Union[ None, Tuple[float,float,float,float,PosNode,Union[PosNode,None]] ]:
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

		bartime = float(bartime)
		if bartime < 0:
			raise ValueError("Bartime(bar+nmr/dnm) must be larger than 0.")
		elif bartime < self.__nodes[0].bartime: return
		elif bartime > self.__nodes[-1].bartime: return
		elif bartime == self.__nodes[-1].bartime:
			nd:PosNode = self.__nodes[-1]
			nd_actual = nd.curve_end if nd.curve_end >= nd.curve_init else nd.curve_init
			return(nd.x, nd.y, 1, nd_actual, nd, None)

		for i in range(pnsize-1):
			current_posnode = self.__nodes[i]
			next_posnode = self.__nodes[i+1]

			# bartime [t1,t2)
			t1 = current_posnode.bartime
			t2 = next_posnode.bartime
			if bartime < t1  or  bartime >= t2: continue

			original_ratio = (bartime - t1) / (t2 - t1)
			easetype = current_posnode.easetype
			if easetype:

				x0 = y0 = dx = dy = actual_ratio = 0
				ci = current_posnode.curve_init
				ce = current_posnode.curve_end
				x1 = current_posnode.x
				y1 = current_posnode.y
				x2 = next_posnode.x
				y2 = next_posnode.y

				return_x = return_y = 0
				if (ci == 0  and  ce == 1)  or  (ci == 1  and  ce == 0  and  easetype == 3):
					dx = x2 - x1
					dy = y2 - y1
					actual_ratio = original_ratio

					if easetype == 1:
						return_x = x1 + dx * ESIN(actual_ratio)
						return_y = y1 + dy * ECOS(actual_ratio)
					elif easetype == 2:
						return_x = x1 + dx * ECOS(actual_ratio)
						return_y = y1 + dy * ESIN(actual_ratio)
					elif ci > ce:
						O = OutQuad(actual_ratio)
						return_x = x1 + dx * O
						return_y = y1 + dy * O
					else:
						I = InQuad(actual_ratio)
						return_x = x1 + dx * I
						return_y = y1 + dy * I

				elif easetype == 1:
					x0,dx = get_original(x1, x2, ci, ce, ESIN)
					y0,dy = get_original(y1, y2, ci, ce, ECOS)
					actual_ratio = ci + original_ratio * ( ce - ci )
					return_x = x0 + dx * ESIN(actual_ratio)
					return_y = y0 + dy * ECOS(actual_ratio)
				elif easetype == 2:
					x0,dx = get_original(x1, x2, ci, ce, ECOS)
					y0,dy = get_original(y1, y2, ci, ce, ESIN)
					actual_ratio = ci + original_ratio * ( ce - ci )
					return_x = x0 + dx * ECOS(actual_ratio)
					return_y = y0 + dy * ESIN(actual_ratio)
				elif ci > ce:
					x0,dx = get_original(x1, x2, ce, ci, OutQuad)
					y0,dy = get_original(y1, y2, ce, ci, OutQuad)
					actual_ratio = ce + original_ratio * ( ci - ce )
					O = OutQuad(actual_ratio)
					return_x = x0 + dx * O
					return_y = y0 + dy * O
				else:
					x0,dx = get_original(x1, x2, ci, ce, InQuad)
					y0,dy = get_original(y1, y2, ci, ce, InQuad)
					actual_ratio = ci + original_ratio * ( ce - ci )
					I = InQuad(actual_ratio)
					return_x = x0 + dx * I
					return_y = y0 + dy * I

				return (return_x, return_y, original_ratio, actual_ratio, current_posnode, next_posnode)

			else:
				x0 = current_posnode.x
				y0 = current_posnode.y
				dx = next_posnode.x - x0
				dy = next_posnode.y - y0
				return (x0+dx*original_ratio, y0+dy*original_ratio, original_ratio, original_ratio, current_posnode, next_posnode)

		return


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
		SortPosNodes(self.__nodes)   # self.__nodes.sort(key = OPSorter)
		return self

	def c(self, bar:float, nmr:int = 0, dnm:int = 1, angle:Union[int, None] = None) -> Self:
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
		if angle == None: angle = Arf2Prototype.current_angle
		else: angle = int(angle)

		bartime = float(bar) + float(nmr) / float(dnm)
		if bartime < 0:
			raise ValueError("Bartime(bar+nmr/dnm) must be larger than 0.")
		if angle < -1800  or  angle > 1800:
			raise ValueError("Degree of AngleNode out of Range [-1800,1800].")

		# Hint(s) will be added in the compiling process.
		c = WishChild(bartime, angle)
		self.__last_child = c
		self.__childs.append(c)
		self.__childs.sort( key = OPSorter )
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
			raise RuntimeError("Please attach at least one WishChild on the WishGroup before creating an AngleNode.")

		_lc = self.__last_child
		if _lc.is_default_angle:
			_lc.anodes[0] = (bartime,degree,easetype)
			_lc.is_default_angle = False
		else:
			_lc.anodes.append( (bartime,degree,easetype) )
			_lc.anodes.sort(key = OPSorterForAngleNodes)
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
		Arf2Prototype.last_hint = h
		Arf2Prototype.hint.append(h)   # Hints in the Arf2Protorype class will be sorted in the compling process.
		self.__mhints.append(h)
		# self.__mhints.sort(key = OPSorter)   # Overlapped Hints will be removed automatically in the compilation

		return self

	def set_of_layer2(self, of_layer2:bool) -> Self:
		'''
		Set which layer the WishGroup belongs to.

		Args:
			of_layer2 (bool): Whether the WishGroup belongs to Layer2.

		Returns:
			Self (WishGroup): for Method Chaining Usage.
		'''
		self.__of_layer2 = bool(of_layer2)
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

	def try_interpolate(self, bar:float, nmr:int = 0, dnm:int = 1, apply_to_anglenodes:bool = False) -> Self:
		'''
		Try to add a PosNode based on the interpolation result,
		accoring to the Bartime input and the current PosNode list.

		When the interpolation fails, no modification will be applied to the calling WishGroup.
		Generally used to correct the trajectory of Wishes under BPM changes.

		Args:
			bar (float): Bartime integer or the Original Bartime
			nmr (int): Numerator to specify the internal position in a bar. Example 5/16 -> 5
			dnm (int): Denominator to specify the internal position in a bar. Example 5/16 -> 16
			apply_to_anglenodes(bool): If true, the interpolation will be applied to AngleNodes
									   of WishChilids belonging to the calling WishGroup.

		Returns:
			Self (WishGroup): for Method Chaining Usage.
		'''
		bartime = float(bar) + float(nmr) / float(dnm)
		if bartime < 0:
			raise ValueError("Bartime(bar+nmr/dnm) must be larger than 0.")

		# AngleNode Process
		if apply_to_anglenodes:
			for c in self.__childs:
				current_anodes = c.anodes   # AngleNode: Tuple(Bartime, Angle, EaseType)
				ansize = len(current_anodes)
				if ansize == 1:
					current_anodes[0] = (0, current_anodes[0][1], 0)
					continue
				elif bartime < current_anodes[0][1]: continue
				elif bartime > current_anodes[-1][1]: continue

				for i in range(ansize-1):
					current_anode = current_anodes[i]
					next_anode = current_anodes[i+1]

					# bartime [t1,t2)
					t1 = current_anode[1]
					t2 = next_anode[1]
					if bartime < t1  or  bartime >= t2: continue

					ratio = (bartime - t1) / (t2 - t1)
					easetype = current_anode[2]
					if easetype > 1:
						print("\n----------------")
						print("Warning:")
						print("The partial ease support is not yet implemented for AngleNodes.")
						print("Appending AngleNodes with EaseType InQuad/OutQuad acorss the BPM Edge")
						print("is not recommended.")
						print("----------------\n")
						continue
					elif easetype == 1:
						new_angle = int(current_anode[1] + (next_anode[1] - current_anode[1]) * ratio)
						current_anodes.append( (bartime, new_angle, 1) )
						current_anodes.sort(key = lambda an: an[0])

		# PosNode Process
		i_result = self.GET(bartime)
		if i_result == None: return self
		elif i_result[5] == None: return self
		elif bartime == i_result[4].bartime  or  bartime == i_result[5].bartime: return self
		else:

			ip_x = i_result[0]
			ip_y = i_result[1]
			actual_ratio = i_result[3]
			current_node = i_result[4]
			former_ci = current_node.curve_init
			former_ce = current_node.curve_end

			if former_ci > former_ce:   # Reversed; et==3
				current_node.curve_init = actual_ratio
				return self.n(bartime,0,1, ip_x, ip_y, 4, actual_ratio, former_ci)   # former_ce < actual_ratio < former_ci
			else:
				current_node.curve_end = actual_ratio
				return self.n(bartime,0,1, ip_x, ip_y, current_node.easetype, actual_ratio, former_ce)

	def mirror_lr(self, mirror_angle:bool = True) -> Self:
		'''
		Turn the Wish mirrord along the Y-Axis.

		Args:
			mirror_angle (bool): Whether to mirror the path of Childs of this WishGroup.
								 Be sure that every AngleNode degree of each WishChild not smaller than -1620.

		Returns:
			Self (WishGroup): for Method Chaining Usage.
		'''
		for node in self.__nodes:
			node.x = 16.0 - node.x
		if mirror_angle:
			for child in self.__childs:
				a = child.anodes
				l = len(a)
				for i in range(l):
					# AngleNode: Tuple(Bartime, Angle, EaseType)
					if a[i][1] < -1620:
						raise MirrorLRAngleProhibition("Can't acquire the mirrored angle for angles in range [-1800,-1620).")
					else:
						b = a[i][0]
						d = 180 - a[i][1]
						e = a[i][2]
						a[i] = (b,d,e)
		return self

	def mirror_ud(self, mirror_angle:bool = True) -> Self:
		'''
		Turn the Wish mirrord along the X-Axis.

		Args:
			mirror_angle (bool): Whether to mirror the path of Childs of this WishGroup.

		Returns:
			Self (WishGroup): for Method Chaining Usage.
		'''
		for node in self.__nodes:
			node.y = 8.0 - node.y
		if mirror_angle:
			for child in self.__childs:
				a = child.anodes
				l = len(a)
				for i in range(l):
					# AngleNode: Tuple(Bartime, Angle, EaseType)
					b = a[i][0]
					d = -(a[i][1])
					e = a[i][2]
					a[i] = (b,d,e)

	def move(self, delta_bar:float, delta_nmr:int = 0, delta_dnm:int = 1, dx:float = 0, dy:float = 0, trim_by_interpolating:bool = True) -> Self:
		'''
		Move the calling WishGroup, and its WishChilds, AngleNodes, related Hints,
		with several delta arguments specified.

		Prototypia won't provide a explicit copy function, and we suggest you to do
		this manually.

		Example:
			NEW_VERSE()

			# Some Copied Stuff
			n1(1,0,1, 8, 4).n(2,0,1, 4, 8)   # ······
			n1(1,0,1, 7, 3).n(2,0,1, 3, 7)   # ······

			for i in VERSE:
				i.move(16,0,1)
				i.mirror_lr()

		Args:
			delta_bar (float): Delta Bartime integer or the Original Delta Bartime
			delta_nmr (int): Numerator to specify the internal position after a delta bar.
							 Example 5/16 -> 5
			delta_dnm (int): Denominator to specify the internal position after a deltabar.
							 Example 5/16 -> 16
			dx (float): The delta x-axis position of the PosNode. Range[-16,32]
			dy (float): The delta y-axis position of the PosNode. Range[-8,16]
			trim_by_interpolating (bool): Whether interpolate PosNode and AngleNodes before
										  trimming Nodes with bartime smaller than 0.

		Returns:
			Self (WishGroup): for Method Chaining Usage.
		'''
		dbt = float(delta_bar) + float(delta_nmr) / float(delta_dnm)
		dx = float(dx)
		dy = float(dy)
		if dx < -16  or  dx > 32:
			raise ValueError("X-Axis Position out of Range [-16,32].")
		if dy < -8  or  dy > 16:
			raise ValueError("Y-Axis Position out of Range [-8,16].")

		# Simple Updating
		for node in self.__nodes:
			node.bartime += dbt
			node.x += dx
			node.y += dy
			if node.x < -16  or  node.x > 32:
				raise ValueError("X-Axis Position out of Range [-16,32] after the moving.")
			if node.y < -8  or  node.y > 16:
				raise ValueError("Y-Axis Position out of Range [-8,16] after the moving.")
		for child in self.__childs:
			child.bartime += dbt
		for hint in self.__mhints:
			hint.bartime += dbt

		# Simple Checking
		if self.__nodes[0].bartime < 0:
			if trim_by_interpolating:
				self.try_interpolate(0)
			while len(self.__nodes) > 2  and  self.__nodes[0].bartime < 0:
				self.__nodes.pop(0)
			if len(self.__nodes) < 2  or  self.__nodes[0].bartime < 0:
				raise MoveError("After the Triming Process, No enough PosNode remains.")
		while len(self.__childs) > 0  and  self.__childs[0].bartime < 0:
			self.__childs.pop(0)
		while len(self.__mhints) > 0  and  self.__mhints[0].bartime < 0:
			self.__mhints.pop(0)

		# Complex Checking
		for child in self.__childs:
			a = child.anodes
			l = len(a)

			# AngleNode: Tuple(Bartime, Angle, EaseType)
			if l < 2: a[0] = ( 0, a[0][1], 0 )
			elif a[0][0] < 0:
				if trim_by_interpolating:
					for i in range(l-1):
						current_anode = a[i]
						next_anode = a[i+1]

						t1 = current_anode[0]
						t2 = next_anode[0]
						if t2 < 0: continue

						angle_0 = current_anode[1]
						d_angle = next_anode[1] - angle_0

						ratio = (0-t1) / (t2-t1)
						et = current_anode[2]
						if et == 0:   # An.STASIS
							ratio = 0
						elif et == 1:   # An.LINEAR
							pass
						elif et == 2:   # An.INQUAD
							ratio *= ratio
						else:   # An.OUTQUAD
							ratio = 1.0 - ratio
							ratio = 1.0 - ratio * ratio

						a.append( (0, angle_0 + d_angle * ratio, et) )
						break
					a.sort(key = lambda a: a[0])

				while len(a) > 1  and  a[0][0] < 0: a.pop(0)
				if l < 2: a[0] = ( 0, a[0][1], 0 )

		return self

	def input(self, *args:Tuple[float]) -> Self:
		'''
		A Shorthand to add multiple WishChild to the calling WishGroup.
		Each argument refers to an accurate Bartime, and all angle data of
		newly-created WishChild(s) will be set by default.

		Example:   # 1/8 Taterendas falling down
			CURRENT_ANGLE(90)
			n1(1,0,1, 3, 5).n(2,0,1, 7, 3).input(1.125,1.25,1.375,1.5,1.625,1.75,1.875)

		Args:
			*args (Tuple[float]): A series of accurate Bartime(s).

		Returns:
			Self (WishGroup): for Method Chaining Usage.
		'''
		tdict = {}
		for t in args:
			tfloat = float(t)
			if tfloat in tdict: continue
			else:
				tdict[tfloat] = True
				self.c( float(t),0,1 )
		return self

	def input_drm(self, text:str, *, type:Union[int,None] = None, left:Union[float,None] = None, mid:Union[float,None] = None, width:Union[float,None] = None, init:Union[float,None] = None, end:Union[float,None] = None) -> Self:
		'''
		Parse Bartimes from a chart[fumen] text created by DRMaker, and use
		these Bartimes to create WishChild(s) on the calling WishGroup.

		-- Center&End Notes will be filtered.

		-- Several optional filters are provided,
		   but you need to pass them with their keywords.

		Args:
			text (str): Chart[Fumen] text created by DRMaker
			type (int): Note Type Filter, declare it like "type=0"
			left (float): Left Position Filter, declare it like "left=0"
			mid (float): Middle Position Filter, declare it like "mid=2"
			width (float): Note Width Filter, declare it like "width=4"
			init (float): Init Bartime Filter, declare it like "init=1"
			End (float): End Bartime Filter, declare it like "end=2"

		Returns:
			Self (WishGroup): for Method Chaining Usage.
		'''
		drm_lines = text.splitlines()   # <id><type><bartime><left><width><nsc_scale><parentid><LRHP>
		drm_elems = []
		drm_bars = {}
		for l in drm_lines:
			if not l.startswith("<"): continue
			l = l.removesuffix(">")
			l = l.replace("<","")
			drm_elems.append( l.split(">") )
		for e in drm_elems:

			__bartime = float(e[2])
			if __bartime in drm_bars: continue
			else: drm_bars[__bartime] = True

			__type = int(e[1])
			if __type in drm_tails: continue

			__left = float(e[3])
			__width = float(e[4])
			__mid = __left + 0.5 * __width

			if type and  __type != type: continue
			elif left and  __left != left: continue
			elif mid and  __mid != mid: continue
			elif width and  __width != width: continue
			elif init and  __bartime < init: continue
			elif end and  __bartime > end: continue

			self.c(__bartime,0,1)
		return self
	# And other chart[fumen] makers?



# Arf2 Compiler
def UpdateBPM() -> None:
	__ms = Arf2Prototype.offset
	b = Arf2Prototype.bpms
	for i in range(len(b)):
		if i == 0:
			__new = ( b[0][0], b[0][1], __ms )
			b[0] = __new
		else:
			# delta_bartime * (60000.0 / last_bars_per_minute)
			__ms += (b[i][0] - b[i-1][0]) * (60000.0 / b[i-1][1])
			__new = ( b[i][0], b[i][1], __ms )
			b[i] = __new

def GetMS(bar:float) -> int:
	b = Arf2Prototype.bpms
	if bar < b[0][0]: return 0
	elif bar >= b[-1][0]:
		return int( b[-1][2] + (bar - b[-1][0]) * (60000.0 / b[-1][1]) )
	else:
		for i in range( len(b) - 1 ):
			c = b[i]
			n = b[i+1]
			# bar [c0,n0)
			if bar < c[0]  or  bar >= n[0]: continue
			return int( c[2] + (bar - c[0]) * (60000.0 / c[1]) )
		return 0

class MergedTimeNode:
	def __init__(self) -> None:
		self.bar = None
		self.bpm = None
		self.scale = None
		self.dt_ms = None
		self.dt_base = None
		self.dt_ratio = None

def UpdateMerged(m:list[MergedTimeNode]) -> list[MergedTimeNode]:
	def dbpmprint() -> None:
		print("\n----------------")
		print("Warning:")
		print("DBPM( BPM*Scale ) Out of Range [-2400,-0.15]&[0.15,2400] ,")
		print("Ratio will be clamped.")
		print("----------------\n")
	m.sort(key = lambda mtn: mtn.bar)   # Sort

	# Fill bpm, scale, dt_ratio
	dbpm0 = float(m[0].bpm * 4 * m[0].scale)   # Bars Per Minute
	if dbpm0 > 2400:
		dbpmprint()
		dbpm0 = 2400
	elif dbpm0 > 0  and  dbpm0 < 0.15:
		dbpmprint()
		dbpm0 = 0.15
	elif dbpm0 < 0  and  dbpm0 > -0.15:
		dbpmprint()
		dbpm0 = -0.15
	elif dbpm0 < -2400:
		dbpmprint()
		dbpm0 = -2400

	m[0].dt_ratio = dbpm0 / 15000.0
	for i in range(1, len(m)):
		__last:MergedTimeNode = m[i-1]
		__current:MergedTimeNode = m[i]
		if __current.bpm == None: __current.bpm = __last.bpm
		if __current.scale == None: __current.scale = __last.scale
		current_dbpm = float(__current.bpm * 4 * __current.scale)   # Bars Per Minute

		if current_dbpm > 2400:
			dbpmprint()
			current_dbpm = 2400
		elif current_dbpm > 0  and  current_dbpm < 0.15:
			dbpmprint()
			current_dbpm = 0.15
		elif current_dbpm < 0  and  current_dbpm > -0.15:
			dbpmprint()
			current_dbpm = -0.15
		elif current_dbpm < -2400:
			dbpmprint()
			current_dbpm = -2400

		__current.dt_ratio = current_dbpm / 15000.0

	# Deduplicate by dt_ratio  &  Calculate dt_ms
	m_d:list[MergedTimeNode] = [ m[0] ]
	has_underzero = False
	for mtnode in m[1:]:
		if mtnode.dt_ratio == m_d[-1].dt_ratio: continue
		else: m_d.append(mtnode)
	for mtnode in m_d:
		dtms = GetMS(mtnode.bar)
		if dtms < 0:
			has_underzero = True
		mtnode.dt_ms = dtms

	# Trim Nodes with dt_ms < 0
	len__m_d = len(m_d)
	if has_underzero and len__m_d > 1:
		m_d.reverse()
		index_1st = None
		for i in range( len__m_d - 1 ):
			__former = m_d[i]
			__latter = m_d[i+1]
			if __latter.dt_ms < 0:
				if __former.dt_ms > 0: index_1st = i+1   # dt_ms: >0 , <0
				else: index_1st = i						 # dt_ms: =0 , <0
				break
		m_d = m_d[0: index_1st+1 ]   # [0,index_1st+1) -> [0,index_1st]
		m_d.reverse()
	m_d[0].dt_ms = 0

	# Calculate dt_base
	m_d[0].dt_base = 0
	for i in range( 1, len(m_d) ):
		__last = m_d[i-1]
		__current = m_d[i]
		__current.dt_base = __last.dt_base + (__current.dt_ms - __last.dt_ms) * __last.dt_ratio

	return m_d

def Bar2Dt(bar:float, m:list[MergedTimeNode]) -> float:
	ms = GetMS(bar)
	if ms < m[0].dt_ms: return 0
	elif ms >= m[-1].dt_ms:
		b = m[-1].dt_base
		dms = ms - m[-1].dt_ms
		r = m[-1].dt_ratio
		return ( b + dms * r )
	else:   # ms [dt_ms_1, dt_ms_2)
		for i in range( len(m)-1 ):
			__former = m[i]
			__latter = m[i+1]
			if ms < __former.dt_ms  or  ms >= __latter.dt_ms: continue
			b = __former.dt_base
			dms = ms - __former.dt_ms
			r = __former.dt_ratio
			return ( b + dms * r )
		return 0

@functools.cmp_to_key
def WishGroupSorter(a:WishGroup, b:WishGroup) -> int:
	# 1st_ms -> 1st_ydist -> 1st_xdist -> length
	a_nodes:list[PosNode] = a()["nodes"]
	b_nodes:list[PosNode] = b()["nodes"]
	a_1st:PosNode = a_nodes[1]
	b_1st:PosNode = b_nodes[1]
	if a_1st._ms < b_1st._ms: return -1
	elif a_1st._ms > b_1st._ms: return 1
	else:
		a_ydist = abs(0.5 - a_1st.y)
		b_ydist = abs(0.5 - b_1st.y)
		if a_ydist < b_ydist: return -1
		elif a_ydist > b_ydist: return 1
		else:
			a_xdist = abs(8.0 - a_1st.x)
			b_xdist = abs(8.0 - b_1st.x)
			if a_xdist < b_xdist: return -1
			elif a_xdist > b_xdist: return 1
			else:
				a_length = a_nodes[-1]._ms - a_1st._ms
				b_length = b_nodes[-1]._ms - b_1st._ms
				if a_length < b_length: return -1
				elif a_length > b_length: return 1
				else: return 0

@functools.cmp_to_key
def HintSorter(a:Hint, b:Hint) -> int:
	# ms -> ydist -> xdist
	if a._ms < b._ms: return -1
	elif a._ms > b._ms: return 1
	else:
		a_ydist = abs(0.5 - a._y)
		b_ydist = abs(0.5 - b._y)
		if a_ydist < b_ydist: return -1
		elif a_ydist > b_ydist: return 1
		else:
			a_xdist = abs(8.0 - a._x)
			b_xdist = abs(8.0 - b._x)
			if a_xdist < b_xdist: return -1
			elif a_xdist > b_xdist: return 1
			else: return 0

def RL(x:list) -> list:
	x.reverse()
	return x


def Arf2Compile() -> None:
	'''
	This function processes the data contained in the Arf2Prototype class,
	And then encode it into a *.arf file.

	Don't raise any Exception within, since it's an "atexit" function.
	'''
	# Do BPM Related Stuff
	if len(Arf2Prototype.bpms) == 0:
		print("\n----------------")
		print("Please provide a BPM List of the Arf2 chart[fumen]")
		print('''using the function "BARS_PER_MINUTE" or "BEATS_PER_MINUTE".''')
		print("\nNo file change happened.")
		print("----------------\n")
		return
	UpdateBPM()

	# Interpolation at the BPM Edges
	if len(Arf2Prototype.bpms) > 1:
		for b in Arf2Prototype.bpms:
			if(bpmbar := b[0]):   # Optimization
				for w in Arf2Prototype.wish:
					w.try_interpolate(bpmbar, 0, 1, True)

	# Merge Bartimes and Dts
	dict_layer1:dict[float,MergedTimeNode] = {}
	dict_layer2:dict[float,MergedTimeNode] = {}

	for b in Arf2Prototype.bpms:   # (bartime, BPM, base_ms)
		if b[0] in dict_layer1:
			dict_layer1[ b[0] ].bpm = b[1]
			dict_layer2[ b[0] ].bpm = b[1]
		else:
			m1 = MergedTimeNode()
			m1.bar = b[0]
			m1.bpm = b[1]
			dict_layer1[ b[0] ] = m1

			m2 = MergedTimeNode()
			m2.bar = b[0]
			m2.bpm = b[1]
			dict_layer2[ b[0] ] = m2

	for s in Arf2Prototype.scales_layer1:   # (bartime, scale)
		if s[0] in dict_layer1:
			dict_layer1[ s[0] ].scale = s[1]
		else:
			m = MergedTimeNode()
			m.bar = s[0]
			m.scale = s[1]
			dict_layer1[ s[0] ] = m

	for s in Arf2Prototype.scales_layer2:   # Same
		if s[0] in dict_layer2:
			dict_layer2[ s[0] ].scale = s[1]
		else:
			m = MergedTimeNode()
			m.bar = s[0]
			m.scale = s[1]
			dict_layer2[ s[0] ] = m

	m_layer1:list[MergedTimeNode] = []
	m_layer2:list[MergedTimeNode] = []

	for m in dict_layer1.values(): m_layer1.append( m )
	for m in dict_layer2.values(): m_layer2.append( m )
	dict_layer1 = None
	dict_layer2 = None

	m_layer1 = UpdateMerged(m_layer1)   # DeltaNodes sorted here.
	m_layer2 = UpdateMerged(m_layer2)

	# Add WishChilds-Related Hints
	# Hint(Bartime, Ref)
	for wg in Arf2Prototype.wish:
		wg_dict:dict = wg()

		'''
		{
			"childs" : self.__childs,
			"useless" : self.__useless
		}
		'''

		if wg_dict["useless"] :
			mhints:list[Hint] = wg_dict["mhints"]
			for mh in mhints: mh.ref = None
			continue

		childs_AWCRH:list[WishChild] = wg_dict["childs"]
		for c in childs_AWCRH:
			new_hint = Hint( c.bartime, wg )
			Arf2Prototype.hint.append(new_hint)

	# Discard Useless WishGroups & WishGroups that has less than 2 PosNodes
	new_wg = []
	for wg in Arf2Prototype.wish:
		if wg()["useless"]: pass
		elif len( wg()["nodes"] ) < 2: pass
		else: new_wg.append(wg)
	Arf2Prototype.wish = new_wg
	new_wg = None

	# Calculate Hint Params, and Deduplicate
	hlist:list[Hint] = Arf2Prototype.hint
	h_dict:dict[Tuple[int,float,float], Hint] = {}
	for h in hlist:
		if h.ref == None: continue   # Trim I: Hint that has no Ref
		elif type(h.ref) != WishGroup:
			print("\n----------------")
			print("Wrong Hint Reference Discovered.")
			print('''Please Don't modify the value of a Hint instance's "ref" member.''')
			print("\nNo file change happened.")
			print("----------------\n")
			return
		href:WishGroup = h.ref

		bt = h.bartime
		g_result = href.GET(bt)
		if g_result == None: continue   # Trim I: Hint that has no Interpolation Result

		__ms = GetMS(bt)
		if __ms >= 0:   # Trim I: Hint that mstime < 0
			__x = g_result[0]
			__y = g_result[1]

			h._ms = __ms
			h._x = __x
			h._y = __y

			# Trim I: Hint that overlapped on another Hint
			h_key = (__ms, __x, __y)
			if not h_key in h_dict:
				h_dict[h_key] = h
	Arf2Prototype.hint = []
	for h in h_dict.values(): Arf2Prototype.hint.append(h)
	h_dict = None
	hlist = None

	# Calculate Object Params: Other mstimes & _dt for WishChilds
	for wg in Arf2Prototype.wish:
		wg_dict:dict = wg()

		'''
		{
			"nodes" : self.__nodes,
			"childs" : self.__childs,
			"of_layer2" : self.__of_layer2
		}
		'''

		nodes_COP:list[PosNode] = wg_dict["nodes"]
		childs_COP:list[WishChild] = wg_dict["childs"]
		ofl2_COP:bool = wg_dict["of_layer2"]

		for n in nodes_COP:
			n._ms = GetMS(n.bartime)
		for c in childs_COP:
			c._dt = Bar2Dt(c.bartime, m_layer2 if ofl2_COP else m_layer1)
			for a in c.anodes:
				c._final_anodes.append(
					( GetMS(a[0]), a[1], a[2] )
				)
			if len( c._final_anodes ) == 1:
				__deg = c._final_anodes[0][1]
				c._final_anodes[0] = (0, __deg, 0)

		# Trim II: WishChilds that _dt < 0
		# WishChilds sorted here
		if len(childs_COP) > 0:
			childs_COP.sort(key = lambda c:c._dt, reverse = True )
			while childs_COP[-1]._dt < 0: childs_COP.pop()
			childs_COP.reverse()

		# Trim III: AngleNodes that ms < 0
		# AngleNodes sorted here
		for c in childs_COP:
			a_t3:list[Tuple[int,int,int]] = c.anodes   # (ms,deg,et)
			a_t3.sort( key = lambda a: a[0] )
			for i in range( len(a_t3)-1 ):
				__current_a = a_t3[i]   # ca.ms <= na.ms
				__next_a = a_t3[i+1]

				nams = __next_a[0]
				if nams < 0: continue   # <0, <0
				elif nams == 0: break   # <0, =0
				else:   # ?, >0
					cams = __current_a[0]
					if cams >= 0: break   # >=0, >0
					else:   # <0, >0
						et = __current_a[2]
						ratio = float(0 - cams) / float(nams - cams)
						deg_0 = __current_a[1]
						deg_delta = __next_a[1]

						if et == 0: ratio = 0
						# elif et == 1: pass
						elif et == 2: ratio *= ratio
						elif et == 3:
							ratio = 1.0 - ratio
							ratio = 1.0 - ratio * ratio
						a_t3.append( (0, int(deg_0 + ratio * deg_delta), et) )
						break

			if len(a_t3) > 0:
				a_t3.sort( key = lambda a: a[0] , reverse = True)
				while a_t3[-1][0] < 0: a_t3.pop()
				a_t3.reverse()

		# Trim IV: PosNodes that ms < 0
		# PosNodes sorted here
		nodes_COP.sort( key = lambda p: p._ms )
		for i in range( len(nodes_COP)-1 ):
			__current_p:PosNode = nodes_COP[i]
			__next_p:PosNode = nodes_COP[i+1]

			npms = __next_p._ms
			if npms < 0: continue
			elif npms == 0: break
			else:
				cpms = __current_p._ms
				if cpms >= 0: break
				else:
					# Interpolation
					IP_X = None
					IP_Y = None
					IP_A = None

					o_ratio = float(0 - cpms) / float(npms - cpms)
					et = __current_p.easetype
					if et:
						x0 = y0 = dx = dy = 0
						ci = __current_p.curve_init
						ce = __current_p.curve_end
						x1 = __current_p.x
						y1 = __current_p.y
						x2 = __next_p.x
						y2 = __next_p.y

						if (ci == 0  and  ce == 1)  or  (ci == 1  and  ce == 0  and  et == 3):
							dx = x2 - x1
							dy = y2 - y1
							IP_A = o_ratio

							if et == 1:
								IP_X = x1 + dx * ESIN(IP_A)
								IP_Y = y1 + dy * ECOS(IP_A)
							elif et == 2:
								IP_X = x1 + dx * ECOS(IP_A)
								IP_Y = y1 + dy * ESIN(IP_A)
							elif ci > ce:
								O = OutQuad(IP_A)
								IP_X = x1 + dx * O
								IP_Y = y1 + dy * O
							else:
								I = InQuad(IP_A)
								IP_X = x1 + dx * I
								IP_Y = y1 + dy * I

						elif et == 1:
							x0,dx = get_original(x1, x2, ci, ce, ESIN)
							y0,dy = get_original(y1, y2, ci, ce, ECOS)
							IP_A = ci + o_ratio * ( ce - ci )
							IP_X = x0 + dx * ESIN(IP_A)
							IP_Y = y0 + dy * ECOS(IP_A)
						elif et == 2:
							x0,dx = get_original(x1, x2, ci, ce, ECOS)
							y0,dy = get_original(y1, y2, ci, ce, ESIN)
							IP_A = ci + o_ratio * ( ce - ci )
							IP_X = x0 + dx * ECOS(IP_A)
							IP_Y = y0 + dy * ESIN(IP_A)
						elif ci > ce:
							x0,dx = get_original(x1, x2, ce, ci, OutQuad)
							y0,dy = get_original(y1, y2, ce, ci, OutQuad)
							IP_A = ce + o_ratio * ( ci - ce )
							IP_X = x0 + dx * OutQuad(IP_A)
							IP_Y = y0 + dy * OutQuad(IP_A)
						else:
							x0,dx = get_original(x1, x2, ci, ce, InQuad)
							y0,dy = get_original(y1, y2, ci, ce, InQuad)
							IP_A = ci + o_ratio * ( ce - ci )
							IP_X = x0 + dx * InQuad(IP_A)
							IP_Y = y0 + dy * InQuad(IP_A)

					# Inserting
					# PosNode(Bartime:float, X:float, Y:float, EaseType:int, CurveInit:float, CurveEnd:float)
					f_ci = __current_p.curve_init
					f_ce = __current_p.curve_end

					np = None   # Notice that __current_p will be discarded
					if f_ci > f_ce:  np = PosNode(0, IP_X, IP_Y, 4, IP_A, f_ci)
					else:  np = PosNode(0, IP_X, IP_Y, et, IP_A, f_ce)
					nodes_COP.append(np)
					break

		nodes_COP.sort( key = lambda p: p._ms, reverse = True)
		while nodes_COP[-1]._ms < 0: nodes_COP.pop()
		nodes_COP.reverse()

	# Sort WishGroups & Hints
	Arf2Prototype.wish.sort(key = WishGroupSorter)
	Arf2Prototype.hint.sort(key = HintSorter)

	# Produce Group Indexes
	wlist_final:list[WishGroup] = Arf2Prototype.wish
	hlist_final:list[Hint] = Arf2Prototype.hint

	before:int = 0
	for w in wlist_final:
		last_node:PosNode = w()["nodes"][-1]
		if last_node._ms > before: before = last_node._ms
	for h in hlist_final:
		hendms = h._ms + 470
		if hendms > before: before = hendms
	if before > 512000:
		print("\n----------------")
		print("Limit breached:")
		print("Object exists later than 512000ms.")
		print("--  Make sure the last PosNode EARLIER than 512000ms,")
		print("    And the last Hint EARLIER than 511530ms.")
		print("\nNo file change happened.")
		print("----------------\n")
		return

	widx:list[list[int]] = []
	hidx:list[list[int]] = []
	has_special:bool = False
	for i in range( before//512 + 1 ):
		widx.append([])
		hidx.append([])

	for i in range( len(wlist_final) ):
		w_widx:WishGroup = wlist_final[i]
		f_node:PosNode = w_widx()["nodes"][0]
		l_node:PosNode = w_widx()["nodes"][-1]
		for g in range( f_node._ms//512, l_node._ms//512 + 1 ):
			widx[g].append(i)
	for i in range( len(hlist_final) ):
		h_hidx:Hint = hlist_final[i]
		hidx[h_hidx._ms//512].append(i)
		if h_hidx.is_special:
			Arf2Prototype.special_hint = i
			has_special = True

	# Check special_hint & hgo_required
	if has_special  and  Arf2Prototype.special_hint == 0:
		print("\n----------------")
		print("Warning:")
		print("The earliest Hint is set to be the Special Hint,")
		print('''which will cause the "Special Hint" lose its effect.''')
		print("----------------\n")

	hr = 0
	hidxlast = len(hidx) - 1
	for i in range( len(hidx) ):
		current_hr = len(hidx[i])
		if i > 0: current_hr += len(hidx[i-1])
		if i < hidxlast: current_hr += len(hidx[i+1])
		if current_hr > hr: hr = current_hr
	if hr > 255:
		print("\n----------------")
		print("Limit breached:")
		print("More than 255 Hints may pop up within 1536ms.")
		print("--  Try to reduce the density of Hints.")
		print("\nNo file change happened.")
		print("----------------\n")
		return
	else: Arf2Prototype.hgo_required = hr


	'''
	Usage of Flatbuffers:
	(0) Serialized Stream:
		builder = flatbuffers.Builder(0)
		# Create Elements······, then the Root Table
		roottype_end = RootType.End(builder)
		builder.Finish(roottype_end)
		result:bytearray = builder.Output()

	(1) Vector:
		table_the_vec_belongs_to.StartXXXVector(builder, size)
		builder.PrependXXX( some_value )   # for Flatbuffers Builtin Scalar Types
		builder.PrependUOffsetTRelative( serialized_table )   # for Tables defined manually.
		vec = builder.EndVector()

	(2) Table:
		TableType.Start(builder)
		TableType.AddXXX(builder, sth)   # sth: scalar value, or serialized Vector / Table
		table = TableType.End(builder)

	(3) Tables CANNOT be created in a nested way.
		Remind to Manually Reverse the Original lists, since Buffers are built back to front.
	'''

	# Encode, Serialize & Assemble the Final binary data
	'''
	wish, hint, wgo_required, special_hint -> Arf2Prototype
	dts_layer1, dts_layer2 -> m_layer1, m_layer2
	before, index, hgo_required -> (Indexes made in this Func)
	'''
	b = flatbuffers.Builder(0)   # Builder

	## Scalars
	Arf2Serialized.before = before   # Checked
	Arf2Serialized.wgo_required = Arf2Prototype.wgo_required   # Checked
	Arf2Serialized.hgo_required = Arf2Prototype.hgo_required   # Checked
	Arf2Serialized.special_hint = Arf2Prototype.special_hint   # Checked

	## 1D Structures / dts_layer1, dts_layer2, hint
	Arf2Fb.StartDtsLayer1Vector(b, len(m_layer1))
	for mtn in RL(m_layer1):
		ratio_x105:int = int( abs(mtn.dt_ratio) * 100000 ) << 50   # Ratio Checked
		half_init_ms:int = int(mtn.dt_ms * 0.5) << 32   # Checked
		half_base_x105:int = int(mtn.dt_base * 0.5 * 100000)
		if half_base_x105 < 0:
			print("\n----------------")
			print("Limit breached:")
			print("Base DTime value of DeltaNode somewhere got smaller than 0.")
			print("--  Try to reduce the negative Speed Scale.")
			print("\nNo file change happened.")
			print("----------------\n")
			return
		b.PrependUint64(ratio_x105 + half_init_ms + half_base_x105)
	Arf2Serialized.dts_layer1 = b.EndVector()

	Arf2Fb.StartDtsLayer2Vector(b, len(m_layer2))
	for mtn in RL(m_layer2):
		ratio_x105:int = int( abs(mtn.dt_ratio) * 100000 ) << 50   # Ratio Checked
		half_init_ms:int = int(mtn.dt_ms * 0.5) << 32   # Checked
		half_base_x105:int = int(mtn.dt_base * 0.5 * 100000)
		if half_base_x105 < 0:
			print("\n----------------")
			print("Limit breached:")
			print("Base DTime value of DeltaNode somewhere got smaller than 0.")
			print("--  Try to reduce the negative Speed Scale.")
			print("\nNo file change happened.")
			print("----------------\n")
			return
		b.PrependUint64(ratio_x105 + half_init_ms + half_base_x105)
	Arf2Serialized.dts_layer2 = b.EndVector()

	Arf2Fb.StartHintVector(b, len(hlist_final))
	for h in RL(hlist_final):
		ms = int(h._ms) << 25   # Checked
		y = int( (h._y + 8.0) * 128 ) << 13   # Checked
		x = int( (h._x + 16.0) * 128 )   # Checked
		b.PrependUint64(ms + y + x)
	Arf2Serialized.hint = b.EndVector()

	## 2D Structure / index
	idxlen = len(widx)
	for i in range( idxlen ):

		current_widx = RL(widx[i])
		widx_len = len(current_widx)
		if widx_len > 255:
			print("\n----------------")
			print("Warning:")
			print("More than 255 Wishes may exist within 512ms,")
			print("which may make several Wishes hidden.\n")
			print("--  Try to reduce the density of Wishes / WishChilds.")
			print("----------------\n")

		Arf2Index.StartWidxVector(b, widx_len)
		for value in current_widx:
			if value > 65535:
				print("\n----------------")
				print("Limit breached:")
				print("More than 65535 Wishes included in the Chart[Fumen].")
				print("--  Try to reduce the amount of Wishes.")
				print("\nNo file change happened.")
				print("----------------\n")
				return
			b.PrependUint16(value)
		current_widx_serialized = b.EndVector()

		current_hidx = RL(hidx[i])
		Arf2Index.StartHidxVector(b, len(current_hidx))
		for value in current_hidx:
			if value > 65535:
				print("\n----------------")
				print("Limit breached:")
				print("More than 65535 Hints included in the Chart[Fumen].")
				print("--  Try to reduce the amount of Hints.")
				print("\nNo file change happened.")
				print("----------------\n")
				return
			b.PrependUint16(value)
		current_hidx_serialized = b.EndVector()

		Arf2Index.Start(b)
		Arf2Index.AddWidx(b, current_widx_serialized)
		Arf2Index.AddHidx(b, current_hidx_serialized)
		Arf2Serialized.index.append( Arf2Index.End(b) )

	Arf2Fb.StartIndexVector(b, idxlen)
	for tbl in RL(Arf2Serialized.index): b.PrependUOffsetTRelative(tbl)
	Arf2Serialized.index = b.EndVector()

	## Complex Structure / WishGroup
	for wg in RL(wlist_final):
		wgd:dict = wg()
		'''
		{
			"nodes" : self.__nodes,
			"childs" : self.__childs,
			"of_layer2" : self.__of_layer2,
			"max_visible_distance" : self.__max_visible_distance,
		}
		'''
		__s_childs = []   # Temporary list to store serialized WishChilds

		# WishChild: list[AngleNode] -> F_VECTOR[AngleNode] -> F_TABLE[WishChild]
		childs_S:list[WishChild] = wgd["childs"]
		for ch in RL(childs_S):

			# "WishChildFb" is an alias of class[WishChild.py -> WishChild],
			# rather than class[Arf2.py -> WishChild].
			# The code analysis of Pylance is erroneous here.
			WishChildFb.StartAnodesVector( b, len(ch._final_anodes) )
			for an in RL(ch._final_anodes):   # (ms, angle, et)
				degree = int( an[1] + 1800 ) << 20
				easetype = int( an[2] ) << 18
				halfms = int( an[0] / 2 )
				b.PrependUint32( degree + easetype + halfms )
			__anodes = b.EndVector()

			# Checked:
			# ms[0,512000], ratio_x105[-16000, 16000], Negative dts Excluded
			# max = 512000*16000 / 2 = 4096000000 < 4294967295 = 2**32 - 1
			__dt = int(ch._dt * 100000 * 0.5)

			# Serialize and Store
			WishChildFb.Start(b)
			WishChildFb.AddAnodes(b, __anodes)
			WishChildFb.AddDt(b, __dt)
			WishChildFb.AddP(b, 0)   # Different from the Default Value
			__s_childs.append( WishChildFb.End(b) )

		# WishChild: list[F_TABLE[WishChild]] -> F_VECTOR[WishChild]
		WishGroupFb.StartChildsVector(b, len(childs_S) )
		for c_serialized in __s_childs: b.PrependUOffsetTRelative(c_serialized)   # No Reversing Here
		__s_childs = b.EndVector()

		# PosNode: list[PosNode] -> F_VECTOR[PosNode]
		nodes_S:list[PosNode] = wgd["nodes"]
		WishGroupFb.StartNodesVector(b, len(nodes_S) )
		for pn in RL(nodes_S):
			curve_init = int(pn.curve_init * 511) << 55   # Checked
			curve_end = int(pn.curve_end * 511) << 46   # Checked
			_easetype = int(pn.easetype) << 44   # Checked
			_x = int( (pn.x + 16) * 128 ) << 31   # Checked
			_y = int( (pn.y + 8) * 128 ) << 19   # Checked
			b.PrependUint64( curve_init + curve_end + _easetype + _x + _y + pn._ms )
		__s_nodes = b.EndVector()

		# Encode Info
		ofl2int = int(1 if wgd["of_layer2"] else 0) << 13
		mvdint = int(wgd["max_visible_distance"] * 1024)   # Checked

		# Serialize & Store the Whole WishGroup
		WishGroupFb.Start(b)
		WishGroupFb.AddNodes(b, __s_nodes)
		WishGroupFb.AddChilds(b, __s_childs)
		WishGroupFb.AddInfo(b, ofl2int + mvdint)
		Arf2Serialized.wish.append( WishGroupFb.End(b) )

	## WishGroup: list[F_TABLE[WishGroup]] -> F_VECTOR[WishGroup]
	Arf2Fb.StartWishVector(b, len(wlist_final))
	for wg_serialized in Arf2Serialized.wish: b.PrependUOffsetTRelative(wg_serialized)   # No Reversing Here
	Arf2Serialized.wish = b.EndVector()

	## Serialize the Root Table
	Arf2Fb.Start(b)

	Arf2Fb.AddBefore(b, Arf2Serialized.before)
	Arf2Fb.AddDtsLayer1(b, Arf2Serialized.dts_layer1)
	Arf2Fb.AddDtsLayer2(b, Arf2Serialized.dts_layer2)
	Arf2Fb.AddIndex(b, Arf2Serialized.index)

	Arf2Fb.AddWish(b, Arf2Serialized.wish)
	Arf2Fb.AddWgoRequired(b, Arf2Serialized.wgo_required)

	Arf2Fb.AddHint(b, Arf2Serialized.hint)
	Arf2Fb.AddHgoRequired(b, Arf2Serialized.hgo_required)
	Arf2Fb.AddSpecialHint(b, Arf2Serialized.special_hint)

	b.Finish( Arf2Fb.End(b) )


	# File Saving & Backup
	## Get the Directory & Filename of calling *.py file(without extension)
	fnm:str = os.path.basename( sys.argv[0] ) .removesuffix(".py")
	dir:str = os.path.dirname( sys.argv[0] )

	## If the *.ar file exists, backup it
	path:str = os.path.join(dir, fnm + ".ar")
	if os.path.exists(path):
		_ctime = time.ctime( os.path.getatime(path) ).replace(":", "·")
		new_path:str = os.path.join(dir, fnm + " --" + _ctime + "-- .ar")
		shutil.copy(path, new_path)
		print("\n----------------")
		print("Former Data Backup Completed.")
		print("Filename: " + os.path.basename(new_path) )
		print("----------------\n")

	## Transfer the Buf into the *.ar file
	with open( path, mode = "wb") as buf_file:
		buf_file.write( b.Output() )
		print("\n----------------")
		print("Arf2 Generation Completed.")
		print("Filename: " + os.path.basename(path) )
		print("----------------\n")


# Automating the Compiler Function
atexit.register(Arf2Compile)
ORIG_EH = sys.excepthook
def EH(arg1, arg2, arg3) -> None:
	atexit.unregister(Arf2Compile)
	ORIG_EH(arg1, arg2, arg3)
sys.excepthook = EH
sys.exit = None   # Ban the SystemExit Exception.