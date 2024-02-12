'''
Methods Provided:   # See also  GitHub.com/1dealGas/Prototypia  .
    "An", "Pn", "VERSE", "NEW_VERSE", "REQUIRE",
    "OFFSET", "BEATS_PER_MINUTE", "BARS_PER_MINUTE", "SC_LAYER1", "SC_LAYER2",
    "CURRENT_ANGLE", "specialize_last_hint", "w", "n1", "n2", "i1", "i2",
    "m", "Origin", "AngleSet", "ApplyAngleSet", "MoveAngleNodes", "CollideTo"
'''

from .Arf2 import *
__all__ = [
	"An", "Pn", "VERSE", "NEW_VERSE", "REQUIRE",
	"OFFSET", "BEATS_PER_MINUTE", "BARS_PER_MINUTE", "SC_LAYER1", "SC_LAYER2",
	"CURRENT_ANGLE", "specialize_last_hint", "w", "n1", "n2", "i1", "i2",
	"m", "Origin", "AngleSet", "ApplyAngleSet", "MoveAngleNodes", "CollideTo"
]


# Functional Classes
class An:
	'''EaseType Enums for AngleNodes.'''
	STASIS = 0
	LINEAR = 1
	INQUAD = 2
	OUTQUAD = 3
class Pn:
	'''EaseType Enums for PosNodes.'''
	LINEAR = 0
	LCIRC = 1
	RCIRC = 2
	INQUAD = 3
	OUTQUAD = 4
class __R:
	'''An internal class managing wgo_required & hgo_required.'''
	def __getitem__(self, idx):
		__idx = int(idx)
		if __idx < 0 or __idx > 255: raise ValueError("""Don't require less than 0 objects or more than 255 objects.""")
		Arf2Prototype.wgo_required = __idx
		return self
REQUIRE = __R()
"""
After Debugging your Arf2 chart[fumen] in the viewer,
Play the chart[fumen] entirely, and then Add this line at the end of your *.py file:
	REQUIRE[w]
Param "w" is shown in the title of the viewer window.
"""


# Environmental Configs
def OFFSET(ms:int) -> None:
	'''
	Set the offset(the ms time of the Bar 0) of the Arf2 chart[fumen].

	Args:
		ms (int): the ms time of the Bar 0.

	Returns:
		None
	'''
	Arf2Prototype.offset = int(ms)

def BEATS_PER_MINUTE(*args) -> None:
	'''
	Provide the BPM info in 4/4 beats-per-minute form.
	Recommended for 4/4-time tracks.

	Example:
		BEATS_PER_MINUTE(
			0,	200,   # in Bar 0~50, the tempo of the song is 200(in 4/4 beats-per-minute form).
			50,	190    # since Bar 50, the tempo of the song is 190(in 4/4 beats-per-minute form).
		)

	Args:
		*args (float): Pass BarPosition & Tempo(in 4/4 beats-per-minute form) alternately.

	Returns:
		None
	'''
	__len = len(args)
	if __len == 0  or  __len % 2 == 1 :
		raise BPMInvalidError("Pass BarPosition & Tempo(in 4/4 beats-per-minute form) alternately.")
	Arf2Prototype.bpms = []
	for i in range(0, __len, 2):
		__bar = float(args[i])
		__bpm = float(args[i+1]) / 4
		if __bar < 0:
			raise ValueError("BarTime cannot be smaller than 0.")
		elif __bar > 0 and i == 0:
			raise ValueError("The 1st BarTime must be 0.")
		if __bpm <= 0:
			raise ValueError("BPM must be larger than 0.")
		Arf2Prototype.bpms.append( (__bar,__bpm) )
	Arf2Prototype.bpms.sort(key = lambda bpmtpl: bpmtpl[0])

def BARS_PER_MINUTE(*args) -> None:
	'''
	Provide the BPM info in bars-per-minute form.
	Recommended for non-4/4-time tracks.

	Example:
		BEATS_PER_MINUTE(
			0,	50,   # in Bar 0~50, the tempo of the song is 50(in bars-per-minute form).
			50,	47.5   # since Bar 50, the tempo of the song is 47.5(in bars-per-minute form).
		)

	Args:
		*args (float): Pass BarPosition & Tempo(in bars-per-minute form) alternately.

	Returns:
		None
	'''
	__len = len(args)
	if __len == 0  or  __len % 2 == 1 :
		raise BPMInvalidError("Pass BarPosition & Tempo(in bars-per-minute form) alternately.")
	Arf2Prototype.bpms = []
	for i in range(0, __len, 2):
		__bar = float(args[i])
		__bpm = float(args[i+1])
		if __bar < 0:
			raise ValueError("BarTime cannot be smaller than 0.")
		elif __bar > 0 and i == 0:
			raise ValueError("The 1st BarTime must be 0.")
		if __bpm <= 0:
			raise ValueError("BPM must be larger than 0.")
		Arf2Prototype.bpms.append( (__bar,__bpm) )
	Arf2Prototype.bpms.sort(key = lambda bpmtpl: bpmtpl[0])

def SC_LAYER1(*args) -> None:
	'''
	Provide the Speed Scale info of the Arf2 chart[fumen].
	To be applied to WishChilds in the layer 1.

	Example:
		SC_LAYER1(
			0,	1,   # in Bar 0~50, the Speed Scale of layer 1 is 1.
			50,	1.05   # since Bar 50, the Speed Scale of layer 1 is 1.05 .
		)

	Args:
		*args (float): Pass BarPosition & SpeedScale alternately.

	Returns:
		None
	'''
	__len = len(args)
	if __len == 0  or  __len % 2 == 1 :
		raise ScaleInvalidError("Pass BarPosition & Scale alternately.")
	Arf2Prototype.scales_layer1 = []
	for i in range(0, __len, 2):
		__bar = float(args[i])
		__scl = float(args[i+1])
		if __bar < 0:
			raise ValueError("BarTime cannot be smaller than 0.")
		elif __bar > 0 and i == 0:
			raise ValueError("The 1st BarTime must be 0.")
		if __scl <= 0 and i == 0:
			raise ValueError("The 1st SpeedScale must be larger than 0.")
		Arf2Prototype.scales_layer1.append( (__bar,__scl) )
	Arf2Prototype.scales_layer1.sort(key = lambda sctpl: sctpl[0])
	if Arf2Prototype.scales_layer1[-1][1] < 0:
		raise ValueError("The Last SpeedScale must not be smaller than 0.")

def SC_LAYER2(*args) -> None:
	'''
	Provide the Speed Scale info of the Arf2 chart[fumen].
	To be applied to WishChilds in the layer 2.

	Example:
		SC_LAYER1(
			0,	1,   # in Bar 0~50, the Speed Scale of layer 2 is 1.
			50,	1.05   # since Bar 50, the Speed Scale of layer 2 is 1.05 .
		)

	Args:
		*args (float): Pass BarPosition & SpeedScale alternately.

	Returns:
		None
	'''
	__len = len(args)
	if __len == 0  or  __len % 2 == 1 :
		raise ScaleInvalidError("Pass BarPosition & Scale alternately.")
	Arf2Prototype.scales_layer2 = []
	for i in range(0, __len, 2):
		__bar = float(args[i])
		__scl = float(args[i+1])
		if __bar < 0:
			raise ValueError("BarTime cannot be smaller than 0.")
		elif __bar > 0 and i == 0:
			raise ValueError("The 1st BarTime must be 0.")
		if __scl <= 0 and i == 0:
			raise ValueError("The 1st SpeedScale must be larger than 0.")
		Arf2Prototype.scales_layer2.append( (__bar,__scl) )
	Arf2Prototype.scales_layer2.sort(key = lambda sctpl: sctpl[0])
	if Arf2Prototype.scales_layer2[-1][1] < 0:
		raise ValueError("The Last SpeedScale must not be smaller than 0.")


# Composational Functions
def CURRENT_ANGLE(degree:int) -> None:
	'''
	Set the default angle degree value for WishChilds followed.

	Example:
		CURRENT_ANGLE(90)
		some_wish.c(some_bartime).c(some_bartime)···   # Angle degree of these 2 WishChilds will be 90
		CURRENT_ANGLE(0)
		some_wish.c(some_bartime)···   # Angle degree of the newly-created WishChild will be 0

	Args:
		degree (int): The angle degree value.

	Returns:
		None
	'''
	degree = int(degree)
	if degree < -1800  or  degree > 1800:
		raise ValueError("Degree of AngleNode out of Range [-1800,1800].")
	Arf2Prototype.current_angle = degree

def specialize_last_hint() -> None:
	'''
	Tag the last Hint as a Special Hint.
	Each Arf2 chart[fumen] contains 0 or 1 Special Hint for some special usages.

	Example:
		some_wish.               c(some_bartime)
		specialize_last_hint()   ^  The Hint referring this WishChild won't be the Special Hint, due to the shadowing below.
		some_wish.               c(some_bartime)
		specialize_last_hint()   ^  The Hint referring this WishChild will be the Special Hint.

	Args:
		None

	Returns:
		None
	'''
	Arf2Prototype.last_hint.is_special = True

def w(of_layer2:bool = False, max_visible_distance:float = 7) -> WishGroup:
	'''
	Write an Empty Wish into the Arf2 chart[fumen].
	You may add PosNodes & WishChilds in a method-chaining form.

	Example:
		w().n(some_bartime,x=1,y=1).c(some_bartime)

	Args:
		of_layer2 (bool): Is this WishGroup belongs to layer 2?  By default, newly-created WishGroup belongs to layer 1.
		max_visible_distance (float): The max visible distance for WishChilds, Range (0,8].

	Returns:
		new_wish (WishGroup): The newly-created WishGroup.
	'''
	max_visible_distance = float(max_visible_distance)
	if max_visible_distance <= 0  or  max_visible_distance > 8:
		raise ValueError("MaxVisibleDistance out of Range (0,8].")
	elif max_visible_distance > 7.9990234375:
		max_visible_distance = 7.9990234375
	_w = WishGroup(of_layer2, max_visible_distance)
	Arf2Prototype.wish.append(_w)
	VERSE.append(_w)
	return _w

def n1(bar:float, nmr:int=0, dnm:int=1, x:float=0, y:float=0, easetype:int=0, curve_init:float=0, curve_end:float=1, max_visible_distance:float = 7) -> WishGroup:
	'''
	A shorthand to create a Wish in layer 1 and then attach a PosNode with given arguments.

	Example:
		n1(some_bartime,x=1,y=1)

	Args:
		bar (float): Bartime integer or the Original Bartime
		nmr (int): numerator to specify the internal position in a bar. Example 5/16 -> 5
		dnm (int): denominator to specify the internal position in a bar. Example 5/16 -> 16
		x (float): The x-axis position of the PosNode. Range[-16,32]
		y (float): The y-axis position of the PosNode. Range[-8,16]
		easetype (int): EaseType of the PosNode. Use Pn.* Series.
		curve_init (float): The initial ratio of the easing curve. Range[0,1]
		curve_end (float): The end ratio of the easing curve. Range[0,1]
		max_visible_distance (float): The max visible distance for WishChilds, Range (0,8].

	Returns:
		new_wish (WishGroup): The newly-created WishGroup.
	'''
	# Args checking are finished in the method "w" and "h".
	return w(False, max_visible_distance).n(bar, nmr, dnm, x, y, easetype, curve_init, curve_end)

def n2(bar:float, nmr:int=0, dnm:int=1, x:float=0, y:float=0, easetype:int=0, curve_init:float=0, curve_end:float=1, max_visible_distance:float = 7) -> WishGroup:
	'''
	A shorthand to create a Wish in layer 2 and then attach a PosNode with given arguments.

	Example:
		n2(some_bartime,x=1,y=1)

	Args:
		bar (float): Bartime integer or the Original Bartime
		nmr (int): numerator to specify the internal position in a bar. Example 5/16 -> 5
		dnm (int): denominator to specify the internal position in a bar. Example 5/16 -> 16
		x (float): The x-axis position of the PosNode. Range[-16,32]
		y (float): The y-axis position of the PosNode. Range[-8,16]
		easetype (int): EaseType of the PosNode. Use Pn.* Series.
		curve_init (float): The initial ratio of the easing curve. Range[0,1]
		curve_end (float): The end ratio of the easing curve. Range[0,1]
		max_visible_distance (float): The max visible distance for WishChilds, Range (0,8].

	Returns:
		new_wish (WishGroup): The newly-created WishGroup.
	'''
	return w(True, max_visible_distance).n(bar, nmr, dnm, x, y, easetype, curve_init, curve_end)

def i1(bar:float, nmr:int=0, dnm:int=1, x:float=0, y:float=0, easetype:int=0, curve_init:float=0, curve_end:float=1, max_visible_distance:float = 7, ahead:Union[float,None] = None) -> WishGroup:
	'''
	A shorthand to create a Wish in layer 1, attach a PosNode with given arguments and its prefix PosNode,
	And then create a WishChild with the default angle degree on the newly-created WishGroup.

	Example:
		i1(some_bartime,x=1,y=1)

	Args:
		bar (float): Bartime integer or the Original Bartime
		nmr (int): numerator to specify the internal position in a bar. Example 5/16 -> 5
		dnm (int): denominator to specify the internal position in a bar. Example 5/16 -> 16
		x (float): The x-axis position of the PosNode. Range[-16,32]
		y (float): The y-axis position of the PosNode. Range[-8,16]
		easetype (int): EaseType of the PosNode. Use Pn.* Series.
		curve_init (float): The initial ratio of the easing curve. Range[0,1]
		curve_end (float): The end ratio of the easing curve. Range[0,1]
		max_visible_distance (float): The max visible distance for WishChilds, Range (0,8].
		ahead (Union[float,None]): Specify the ahead-visible-bartime
								   before the Wish and its WishChild collide.

	Returns:
		new_wish (WishGroup): The newly-created WishGroup.
	'''
	# Args checking are finished in the method "w" and "h".
	if ahead == None:
		ahead = float(max_visible_distance) / 16.0
	return w(False, max_visible_distance).n(bar-ahead, nmr, dnm, x, y).n(bar, nmr, dnm, x, y, easetype, curve_init, curve_end).c(bar, nmr, dnm)

def i2(bar:float, nmr:int=0, dnm:int=1, x:float=0, y:float=0, easetype:int=0, curve_init:float=0, curve_end:float=1, max_visible_distance:float = 7, ahead:Union[float,None] = None) -> WishGroup:
	'''
	A shorthand to create a Wish in layer 2, attach a PosNode with given arguments and its prefix PosNode,
	And then create a WishChild with the default angle degree on the newly-created WishGroup.

	Example:
		i2(some_bartime,x=1,y=1)

	Args:
		bar (float): Bartime integer or the Original Bartime
		nmr (int): numerator to specify the internal position in a bar. Example 5/16 -> 5
		dnm (int): denominator to specify the internal position in a bar. Example 5/16 -> 16
		x (float): The x-axis position of the PosNode. Range[-16,32]
		y (float): The y-axis position of the PosNode. Range[-8,16]
		easetype (int): EaseType of the PosNode. Use Pn.* Series.
		curve_init (float): The initial ratio of the easing curve. Range[0,1]
		curve_end (float): The end ratio of the easing curve. Range[0,1]
		max_visible_distance (float): The max visible distance for WishChilds, Range (0,8].
		ahead (Union[float,None]): Specify the ahead-visible-bartime
								   before the Wish and its WishChild collide.

	Returns:
		new_wish (WishGroup): The newly-created WishGroup.
	'''
	# Args checking are finished in the method "w" and "h".
	if ahead == None:
		ahead = float(max_visible_distance) / 16.0
	return w(True, max_visible_distance).n(bar-ahead, nmr, dnm, x, y).n(bar, nmr, dnm, x, y, easetype, curve_init, curve_end).c(bar, nmr, dnm)

# Official Tools & Patterns
def m(bar:float, nmr:int, dnm:int, x:float, y:float, *args, **kwargs) -> list[WishGroup]:
	# easetype:int = 0, curve_init:float = 0, curve_end:float = 1
	# ahead_bar, ahead_nmr, ahead_dnm
	'''
	Create multiple WishGroups and make them collide at the provided position & time.

	Mandatory Args:
		bar (float): Bartime integer or the Original Bartime
		nmr (int): numerator to specify the internal position in a bar. Example 5/16 -> 5
		dnm (int): denominator to specify the internal position in a bar. Example 5/16 -> 16
		x (float): The x-axis position of the PosNode. Range[-16,32]
		y (float): The y-axis position of the PosNode. Range[-8,16]

	Args:
		when you pass the kwarg "with_distances_alternated = True",
		Pass degree(s) & distance(s) alternately; Pass only degree(s) else.
		-- If you pass nothing, "args" will be [90] or [90,default_distance].

	Keyword Args:
		ahead_bar (float): Bartime integer or the Original Bartime, representing the time before the collision.
						   This Argument is Nullable.
		ahead_nmr (int): numerator to specify the internal position in a bar. Example 5/16 -> 5
		ahead_dnm (int): denominator to specify the internal position in a bar. Example 5/16 -> 16
		easetype (int): EaseType of the PosNode. Use Pn.* Series.
		curve_init (float): The initial ratio of the easing curve. Range[0,1]
		curve_end (float): The end ratio of the easing curve. Range[0,1]
		default_distance (float): Set the default distance, 7.0 if not specified.
		with_distances_alternated (bool): Whether "Args" includes degree(s) & distance(s) alternately,
										  or only includes degree(s).
		with_a_stationary_wish (bool): If True, the function creates an extra stationary WishGroup.
		of_layer2 (bool): If True, all WishGroup(s) created will be of Layer 2.
		max_visible_distance (float): The max visible distance for WishChilds, Range (0,8].

	Returns:
		Wishes (list[WishGroup]): The list of newly-created WishGroups.
	'''
	# Create Variables
	__easetype:int = 0
	__curve_init:float = 0
	__curve_end:float = 1
	__default_distance:float = 7.0
	__ahead_bartime:float = None
	__wda:bool = False
	__wsw:bool = False
	__ofl2:bool = False
	__mvb:float = 7.0

	# Check Mandatory Args
	bartime = float(bar) + float(nmr) / float(dnm)
	if bartime < 0:
		raise ValueError("Bartime(bar+nmr/dnm) must be larger than 0.")

	x = float(x)
	y = float(y)
	if x < -16  or  x > 32:
		raise ValueError("X-Axis Position out of Range [-16,32].")
	if y < -8  or  y > 16:
		raise ValueError("Y-Axis Position out of Range [-8,16].")

	# Check kwargs
	if "easetype" in kwargs:
		__easetype = int(kwargs["easetype"])
		if __easetype < 0  or  __easetype > 4:
			raise TypeError("Invalid EaseType. Use Pn.* Series.")

	if "curve_init" in kwargs:
		__curve_init = float(kwargs["curve_init"])
	if "curve_end" in kwargs:
		__curve_end = float(kwargs["curve_end"])
	if __curve_init < 0  or  __curve_init > 1:
			raise ValueError("CurveInit out of Range [0,1].")
	if __curve_end < 0  or  __curve_end > 1:
			raise ValueError("CurveEnd out of Range [0,1].")
	if __curve_init >= __curve_end:
			raise ValueError("CurveEnd Value must be larger than CurveInit Value.")

	if "default_distance" in kwargs:
		__default_distance = float(kwargs["default_distance"])
	if "with_distances_alternated" in kwargs:
		__wda = bool(kwargs["with_distances_alternated"])
	if "with_a_stationary_wish" in kwargs:
		__wsw = bool(kwargs["with_a_stationary_wish"])

	if "of_layer2" in kwargs:
		__ofl2 = bool(kwargs["of_layer2"])
	if "max_visible_distance" in kwargs:   # No Range Checking Here
		__mvb = float(kwargs["max_visible_distance"])

	if "ahead_bar" in kwargs:
		__ab = kwargs["ahead_bar"]
		__an = 0
		__ad = 1
		if "ahead_nmr" in kwargs: __an = kwargs["ahead_nmr"]
		if "ahead_dnm" in kwargs: __ad = kwargs["ahead_dnm"]
		__ahead_bartime = float( __ab ) + float( __an ) / float( __ad )
		if __ahead_bartime < 0:
			raise ValueError("Bartime Ahead must be larger than 0.")
	else:
		__ahead_bartime = __default_distance / 16.0

	# Arrange args
	if len(args) == 0:
		if __wda: args = (90, __default_distance)
		else: args = (90,)
	deg_dist:list[Tuple[float,float]] = []
	if __wda:
		for i in range( 0, len(args), 2 ):
			__deg = float(args[i])
			__dist = float(args[i+1])
			deg_dist.append( (__deg, __dist) )
	else:
		for deg in args:
			__deg = float(deg)
			deg_dist.append( (__deg, __default_distance) )

	# Manipulate
	rtn:list[WishGroup] = []
	for t in deg_dist:
		__rad = t[0] * pi / 180.0
		__dx = t[1] * cos(__rad)
		__dy = t[1] * sin(__rad)
		rtn.append(
			w(__ofl2, __mvb).n(bartime - __ahead_bartime,0,1, x+__dx, y+__dy, __easetype, __curve_init, __curve_end).n(bartime,0,1, x, y, 0, 0, 1)
		)
	if __wsw: rtn.append(
		w(__ofl2, __mvb).n(bartime - __ahead_bartime,0,1, x, y, 0, 0, 1).n(bartime,0,1, x, y, 0, 0, 1)
	)
	rtn[-1].manual_hint(bartime)

	return rtn


class Origin:
	'''
	Predefine an Origin Point, and you may chain PosNodes on the Origin Point Instance.

	Args:
		x (float): The x-axis position of the Origin. Range[-16,32]
		y (float): The y-axis position of the Origin. Range[-8,16]
		ahead_bar (float): Bartime integer or the Original Bartime, representing the time ahead the 1st attached PosNode.
						   This Argument is Nullable.
		ahead_nmr (int): numerator to specify the internal position in a bar. Example 5/16 -> 5
		ahead_dnm (int): denominator to specify the internal position in a bar. Example 5/16 -> 16
		easetype (int): EaseType of the Origin. Use Pn.* Series.
		curve_init (float): The initial ratio of the Origin's easing curve. Range[0,1]
		curve_end (float): The end ratio of the Origin's easing curve. Range[0,1]
		of_layer2 (bool): Is WishGroup(s) generated by the Origin belong(s) to layer 2?  By default, newly-created WishGroup belongs to layer 1.
		max_visible_distance (float): Max visible distance of WishChilds for WishGroup(s) generated by the Origin.
	'''
	def __init__(self, x:float, y:float, ahead_bar:Union[float, None] = None, ahead_nmr:int = 0, ahead_dnm:int = 1, easetype:int = 0, curve_init:float = 0, curve_end:float = 1, of_layer2:bool = False, max_visible_distance:float = 7) -> None:
		self.__x = float(x)
		self.__y = float(y)
		self.__et = int(easetype)
		self.__ci = float(curve_init)
		self.__ce = float(curve_end)
		self.__mvd = float(max_visible_distance)
		self.__ofl2 = bool(of_layer2)
		self.__ahead = None
		if ahead_bar:
			self.__ahead = float(ahead_bar) + float(ahead_nmr) / float(ahead_dnm)

	def n(self, bar:float, nmr:int = 0, dnm:int = 1, x:float = 0, y:float = 0, easetype:int = 0, curve_init:float = 0, curve_end:float = 1) -> WishGroup:
		'''
		Create a WishGroup with the Origin Info, and attach a PosNode with arguments passed in.

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
			Result (WishGroup): for Method Chaining Usage.
		'''
		if self.__ahead == None:
			self.__ahead = sqrt( (x-self.__x)**2 + (y-self.__y)**2 ) / 16.0
		return w(self.__ofl2, self.__mvd).n(bar - self.__ahead, nmr, dnm, self.__x, self.__y, self.__et, self.__ci, self.__ce).n(bar, nmr, dnm, x, y, easetype, curve_init, curve_end)

	def to(self, target:WishGroup, at_bar:float, at_nmr:int = 0, at_dnm:int = 1, easetype:int = 0, curve_init:float = 0, curve_end:float = 1, with_a_hint:bool = True) -> WishGroup:
		'''
		Create a WishGroup with the Origin Info, and let it collide to the target WishGroup.

		Args:
			target (WishGroup): The collision target.
			at_bar (float): Bartime integer or the Original Bartime, representing the collision timing.
			at_nmr (int): Numerator to specify the internal position in a bar. Example 5/16 -> 5
			at_dnm (int): Denominator to specify the internal position in a bar. Example 5/16 -> 16
			easetype (int): EaseType of the AngleNode. Use Pn.* Series.
			curve_init (float): The initial ratio of the easing curve. Range[0,1]
			curve_end (float): The end ratio of the easing curve. Range[0,1]
			with_a_hint (bool): If True, attach a Hint to the "calling" WishGroup with the bartime the
								collision timing and the angle the default.

		Returns:
			Result (WishGroup): for Method Chaining Usage.
		'''
		if type(target) != "WishGroup":
			raise ValueError('''The type of argument "target" must be "WishGroup".''')

		at_bartime = float(at_bar) + float(at_nmr) / float(at_dnm)
		if at_bartime < 0:
			raise ValueError("Bartime(bar+nmr/dnm) must be larger than 0.")

		target_get_result = target.GET(at_bartime)
		if target_get_result == None:
			raise RuntimeError("Failed to get the Position of the Collide Target.")
		target_x = target_get_result[0]
		target_y = target_get_result[1]

		if self.__ahead == None:
			self.__ahead = sqrt( (target_x-self.__x)**2 + (target_y-self.__y)**2 ) / 16.0

		if with_a_hint: target.manual_hint(at_bartime)
		return w(self.__ofl2, self.__mvd).n(at_bartime - self.__ahead, 0, 1, self.__x, self.__y, self.__et, self.__ci, self.__ce).n(at_bartime, 0, 1, target_x, target_y, easetype, curve_init, curve_end)


class AngleSet:
	'''
	Predefine a set of AngleNodes, and then Apply them to a WishChild.

	Example:
		my_angleset = AngleSet(
		#	BartimeAhead		Degree		EaseType
			0.5,				90,			An.OUTQUAD,
			0.25,				45,			An.INQUAD,
			0,					0,			An.STASIS
		)

		some_wish / ApplyAngleSet(my_angleset)
	'''
	def __init__(self, *args) -> None:
		self.ans:list[Tuple[float,int,int]] = []

		__len = len(args)
		if __len == 0  or  __len % 3 != 0 :
			raise AnglenodeInvalidError("Pass Bartime, Degree and EaseType(An.*) alternately.")
		for i in range(0,__len,3):
			__bartime_ahead = float( args[i] )
			__degree = int( args[i+1] )
			__et = int( args[i+2] )
			if __bartime_ahead < 0:
				raise ValueError("Bartime(bar+nmr/dnm) must be larger than 0.")
			if __degree < -1800  or  __degree > 1800:
				raise ValueError("Degree of AngleNode out of Range [-1800,1800].")
			if __et < 0  or  __et > 3:
				raise TypeError("Invalid AngleNode EaseType. Use An.* Series.")
			self.ans.append( (__bartime_ahead, __degree, __et) )
		self.ans.sort( key=lambda aon: aon[0], reverse=True )

	def move(self, delta_bar:float = 0, delta_nmr:int = 0, delta_dnm:int = 1, delta_degree:int = 0, trim_by_interpolating:bool = True) -> Self:
		'''
		Move the AngleSet with several delta arguments specified.

		Args:
			delta_bar (float): Delta Bartime integer or the Original Delta Bartime
			delta_nmr (int): Numerator to specify the internal position after a delta bar.
							 Example 5/16 -> 5
			delta_dnm (int): Denominator to specify the internal position after a deltabar.
							 Example 5/16 -> 16
			delta_degree (float): The delta degree for all angle values of the AngleSet.
			trim_by_interpolating (bool): Whether interpolate AngleNodes before trimming
										  Nodes with BartimeAhead smaller than 0.

		Returns:
			Result (AngleSet): for Method Chaining Usage.
		'''
		# Delta Check
		delta_bartime = float(delta_bar) + float(delta_nmr) / float(delta_dnm)
		if delta_bartime < 0:
			raise ValueError("Bartime(bar+nmr/dnm) must be larger than 0.")
		if delta_degree < -1800  or  delta_degree > 1800:
			raise ValueError("Delta Degree out of Range [-1800,1800].")

		# Manipulation
		__len = len(self.ans)
		for i in range(__len):
			new_bt = self.ans[i][0] + delta_bartime
			new_deg = self.ans[i][1] + delta_degree
			if new_deg < -1800  or  new_deg > 1800:
				raise ValueError("Moved AngleDegree out of Range [-1800,1800].")
			et = self.ans[i][2]
			self.ans[i] = (new_bt, new_deg, et)

		# Trim
		trimed = []
		for i in range(__len-1):
			as_l = self.ans[i]
			as_r = self.ans[i+1]

			if as_l[0] < 0: break
			else: trimed.append(as_l)

			if as_r[0] < 0:
				if trim_by_interpolating:
					ratio = as_l[0] / (as_l[0] - as_r[0])
					deg0 = as_l[1]
					degd = as_r[1] - deg0
					et = as_l[2]

					if et == 0: pass   # An.STASIS
					elif et == 1:   # An.LINEAR
						trimed.append( (0, deg0 + degd * ratio, 1) )
					elif et == 2:   # An.INQUAD
						ratio *= ratio
						trimed.append( (0, deg0 + degd * ratio, 2) )
					else:   # An.OUTQUAD
						ratio = 1.0 - ratio
						ratio = 1.0 - ratio * ratio
						trimed.append( (0, deg0 + degd * ratio, 3) )
				break
			if i == __len-2  and  as_r[0] >= 0: trimed.append(as_r)

		trimed.sort( key=lambda aon: aon[0], reverse=True )
		self.ans = trimed

		return self

def ApplyAngleSet(s:AngleSet, to_all_childs:bool = False) -> FunctionType:
	'''
	A PseudoDecorator function to apply an AngleSet to the last / all
	WishChild(s) to the calling WishGroup.

	Args:
		s (AngleSet): The AngleSet to be applied.
		to_all_childs (bool): If True, the AngleSet will be applied to all
							  WishChild(s) of the calling WishGroup.

	Returns:
		rtn (FunctionType): For PseudoDecorator Usage.
	'''
	if type(s) != AngleSet:
		raise ValueError('''The type of argument "s" must be "AngleSet".''')
	if len(s.ans) == 0:
		raise RuntimeError("Please attach at least one AngleNode on the AngleSet before applying the AngleSet.")

	def rtn1(w:WishGroup) -> None:
		child:WishChild = (w()["last_child"])
		if child == None:
			raise RuntimeError("Please attach at least one WishChild on the WishGroup before applying an AngleSet.")
		child.anodes = []
		child_bar = child.bartime
		for an in s.ans:
			final_bar = child_bar - an[0]
			if final_bar < 0:
				raise RuntimeError("AngleSet Final Bartime(child_bar - anglenode_bar) smaller than 0.")
			deg = an[1]
			et = an[2]
			child.anodes.append( (final_bar,deg,et) )
		child.anodes.sort(key = lambda an: an[0])

	def rtn2(w:WishGroup) -> None:
		childlist:list[WishChild] = w()["childs"]
		if len(childlist) == 0:
			raise RuntimeError("Please attach at least one WishChild on the WishGroup before applying an AngleSet.")
		for child in childlist:
			child.anodes = []
			child_bar = child.bartime
			for an in s.ans:
				final_bar = child_bar - an[0]
				if final_bar < 0:
					raise RuntimeError("AngleSet Final Bartime(child_bar - anglenode_bar) smaller than 0.")
				deg = an[1]
				et = an[2]
				child.anodes.append( (final_bar,deg,et) )
			child.anodes.sort(key = lambda an: an[0])

	return (rtn2 if to_all_childs else rtn1)


def MoveAngleNodes(delta_bar:float = 0, delta_nmr:int = 0, delta_dnm:int = 1, delta_degree:int = 0, trim_by_interpolating:bool = True, for_all_childs:bool = False) -> FunctionType:
	'''
	A PseudoDecorator function to move AngleNode(s) related to the
	calling WishGroup.

	Args:
		delta_bar (float): Delta Bartime integer or the Original Delta Bartime
		delta_nmr (int): Numerator to specify the internal position after a delta bar.
						 Example 5/16 -> 5
		delta_dnm (int): Denominator to specify the internal position after a deltabar.
						 Example 5/16 -> 16
		delta_degree (float): The delta degree for all angle values of the AngleSet.
		trim_by_interpolating (bool): Whether interpolate AngleNodes before trimming
									  Nodes with BartimeAhead smaller than 0.
		for_all_childs (bool): If False, the method applies the movement to the last
							   WishChild; else, the method applies the movement to all
							   WishChild(s) in the calling WishGroup.

	Returns:
		rtn (FunctionType): For PseudoDecorator Usage.
	'''
	# Delta Check
	delta_bartime = float(delta_bar) + float(delta_nmr) / float(delta_dnm)
	if delta_bartime < 0:
		raise ValueError("Bartime(bar+nmr/dnm) must be larger than 0.")
	if delta_degree < -1800  or  delta_degree > 1800:
		raise ValueError("Delta Degree out of Range [-1800,1800].")

	def __move(c:WishChild) -> None:
		a = c.anodes
		__len = len(a)

		for i in range(__len):
			new_bt = a[i][0] + delta_bartime
			new_deg = a[i][1] + delta_degree
			if new_deg < -1800  or  new_deg > 1800:
				raise ValueError("Moved AngleDegree out of Range [-1800,1800].")
			et = a[i][2]
			a[i] = (new_bt, new_deg, et)

		if __len < 2: a[0] = ( 0, a[0][1], 0 )
		elif a[0][0] < 0:
			if trim_by_interpolating:
				for i in range(__len-1):
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
				if __len < 2: a[0] = ( 0, a[0][1], 0 )

	if for_all_childs:
		def rtn(w:WishGroup) -> None:
			childs:list[WishChild] = w()["childs"]
			for c in childs: __move(c)
		return rtn
	else:
		def rtn(w:WishGroup) -> None:
			last_child:WishChild = w()["last_child"]
			__move(last_child)
		return rtn


def CollideTo(target:WishGroup, at_bar:float, at_nmr:int = 0, at_dnm:int = 1, easetype:int = 0, curve_init:float = 0, curve_end:float = 1, with_a_hint:bool = True) -> FunctionType:
	'''
	A PseudoDecorator function to let multiple WishGroups collide.

	Example:
		# Suppose there are 3 WishGroups: wish_1, wish_2 and wish_3 .
		wish_1 / CollideTo(wish_2, 6,9,16) / CollideTo(wish_3, 7,0,1)

	Args:
		target (WishGroup): The collision target.
		at_bar (float): Bartime integer or the Original Bartime, representing the collision timing.
		at_nmr (int): Numerator to specify the internal position in a bar. Example 5/16 -> 5
		at_dnm (int): Denominator to specify the internal position in a bar. Example 5/16 -> 16
		easetype (int): EaseType of the AngleNode. Use Pn.* Series.
		curve_init (float): The initial ratio of the easing curve. Range[0,1]
		curve_end (float): The end ratio of the easing curve. Range[0,1]
		with_a_hint (bool): If True, attach a Hint to the "calling" WishGroup with the bartime the
							collision timing and the angle the default.

	Returns:
		rtn (FunctionType): For PseudoDecorator Usage.
	'''
	if type(target) != WishGroup:
		raise ValueError('''The type of argument "target" must be "WishGroup".''')

	at_bartime = float(at_bar) + float(at_nmr) / float(at_dnm)
	if at_bartime < 0:
		raise ValueError("Bartime(bar+nmr/dnm) must be larger than 0.")

	target_get_result = target.GET(at_bartime)
	if target_get_result == None:
		raise RuntimeError("Failed to get the Position of the Collide Target.")
	target_x = target_get_result[0]
	target_y = target_get_result[1]

	def rtn(w:WishGroup) -> None:
		w.n(at_bartime,0,1, target_x, target_y, easetype, curve_init, curve_end)
		if with_a_hint: w.manual_hint(at_bartime,0,1)
	return rtn