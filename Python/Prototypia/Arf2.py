# Common Imports
from ast import *
from math import *
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
class MoveError						(E):pass
class BPMInvalidError				(E):pass
class ScaleInvalidError				(E):pass
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

		bartime = float(bartime)
		if bartime < 0:
			raise ValueError("Bartime(bar+nmr/dnm) must be larger than 0.")
		elif bartime < self.__nodes[0].bartime: return
		elif bartime >= self.__nodes[-1].bartime: return

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
				if ci == 0 and ce == 1:
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
						return_x = x1 + dx * OutQuad(actual_ratio)
						return_y = y1 + dy * OutQuad(actual_ratio)
					else:
						return_x = x1 + dx * InQuad(actual_ratio)
						return_y = y1 + dy * InQuad(actual_ratio)

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
					return_x = x0 + dx * OutQuad(actual_ratio)
					return_y = y0 + dy * OutQuad(actual_ratio)
				else:
					x0,dx = get_original(x1, x2, ci, ce, InQuad)
					y0,dy = get_original(y1, y2, ci, ce, InQuad)
					actual_ratio = ci + original_ratio * ( ce - ci )
					return_x = x0 + dx * InQuad(actual_ratio)
					return_y = y0 + dy * InQuad(actual_ratio)

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

		# Hint(s) will be added in the compiling process.
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
		Arf2Prototype.last_hint = h
		Arf2Prototype.hint.append(h)   # Hints in the Arf2Protorype class will be sorted in the compling process.

		self.__mhints.append(h)
		self.__mhints.sort(key = lambda ht: ht.bartime)

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

	def try_interpolate(self, bar:float, nmr:int=0, dnm:int=1) -> Self:
		'''
		Try to add a PosNode based on the interpolation result,
		accoring to the Bartime input and the current PosNode list.

		When the interpolation fails, no modification will be applied to the calling WishGroup.
		Generally used to correct the trajectory of Wishes under BPM changes.

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

		i_result = self.GET(bartime)
		if i_result == None: return self
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
				raise MoveError("After the Triming Process, No enough PosNode(s) remain(s).")
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
			n1(1,,, 3, 5).n(2,,, 7, 3).input(1.125,1.25,1.375,1.5,1.625,1.75,1.875)

		Args:
			*args (Tuple[float]): A series of accurate Bartime(s).

		Returns:
			Self (WishGroup): for Method Chaining Usage.
		'''
		for t in args: self.c( float(t),0,1 )
		return self

	def input_drm(self, text:str, *, type:Union[int,None] = None, left:Union[float,None] = None, mid:Union[float,None] = None, width:Union[float,None] = None, init:Union[float,None] = None, end:Union[float,None] = None) -> Self:
		'''
		Parse Bartimes from a chart[fumen] text created by DRMaker, and use
		these Bartimes to create WishChild(s) on the calling WishGroup.

		-- Center&End Notes will be filtered.

		-- Several optional filters are provided,
		   but you need to pass them with their keywords.

		Args:
			text (str): Chart[fumen] text created by DRMaker
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
		for l in drm_lines:
			if not l.startswith("<"): continue
			l.removesuffix(">")
			l.replace("<","")
			drm_elems.append( l.split(">") )
		for e in drm_elems:
			if int(e[6]) != 0: continue

			__type = int(e[1])
			__bartime = float(e[2])
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



# Arf2 Compiler Function
def Arf2Compile() -> None:
	'''
	This function processes the data contained in the Arf2Prototype class,
	And then encode it into a *.arf file.
	'''
	# Merge Bartimes and Dts
	# Add WishChilds-related Hints
	# Calculate Object Params
	# Final Sortings
	# Produce Group Indexes
	# Encode the Flatbuffers binary data
	# File Backup & Export
	pass


# Automating the Compiler Function
atexit.register(Arf2Compile)
ORIG_EH = sys.excepthook
def EH(arg1, arg2, arg3) -> None:
	atexit.unregister(Arf2Compile)
	ORIG_EH(arg1, arg2, arg3)
sys.excepthook = EH
sys.exit = None   # Ban the SystemExit Exception.