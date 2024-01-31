'''
Methods Provided:   # See also  GitHub.com/1dealGas/Prototypia  .
    "An", "Pn", "REQUIRE",
    "OFFSET", "BEATS_PER_MINUTE", "BARS_PER_MINUTE", "SC_LAYER1", "SC_LAYER2",
    "CURRENT_ANGLE", "specialize_last_hint", "w", "n1", "n2",

'''

from .Arf2 import *
__all__ = [
	"An", "Pn", "REQUIRE",
	"OFFSET", "BEATS_PER_MINUTE", "BARS_PER_MINUTE", "SC_LAYER1", "SC_LAYER2",
	"CURRENT_ANGLE", "specialize_last_hint", "w", "n1", "n2",

]


# Functional Classes
class An:
	'''EaseType Enums for AngleNodes.'''
	STASIS = 0
	LINEAR = 1
	ESIN = 2
	ECOS = 3
class Pn:
	'''EaseType Enums for PosNodes.'''
	LINEAR = 0
	LCIRC = 1
	RCIRC = 2
	INQUAD = 3
	OUTQUAD = 4
class __R:
	'''An internal class managing wgo_required & hgo_required.'''
	__cnt = 0
	def __getitem__(self, idx):
		if __R.__cnt == 0:
			__idx = int(idx)
			if __idx < 0 or __idx > 255: raise ValueError("""Don't require less than 0 objects or more than 255 objects.""")
			Arf2Prototype.wgo_required = __idx
			__R.__cnt = 1
		elif __R.__cnt == 1:
			__idx = int(idx)
			if __idx < 0 or __idx > 255: raise ValueError("""Don't require less than 0 objects or more than 255 objects.""")
			Arf2Prototype.hgo_required = __idx
			__R.__cnt = 2
		return self
REQUIRE = __R()
"""
After Debugging your Arf2 chart[fumen] in the viewer,
Play the chart[fumen] entirely, and then Add this line at the end of your *.py file:
	REQUIRE[w][h]
Param "w" & "h" are provided in the title of the viewer window.
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
		max_visible_distance (float): The max visible distance for WishChilds, Range [0,8].

	Returns:
		new_wish (WishGroup): The newly-created WishGroup.
	'''
	max_visible_distance = float(max_visible_distance)
	if max_visible_distance < 0  or  max_visible_distance > 8:
		raise ValueError("MaxVisibleDistance out of Range [0,8].")
	elif max_visible_distance > 7.9990234375:
		max_visible_distance = 7.9990234375
	_w = WishGroup(of_layer2, max_visible_distance)
	Arf2Prototype.wish.append(_w)
	return _w

def n1(bar:float, nmr:int=0, dnm:int=1, x:float=0, y:float=0, easetype:int=0, curve_init:float=0, curve_end:float=1, max_visible_distance:float = 7) -> WishGroup:
	'''
	A shorthand to create a Wish in layer 1 and then attach a PosNode with given arguments.

	Example:
		wn1(some_bartime,x=1,y=1)

	Args:
		bar (float): Bartime integer or the Original Bartime
		nmr (int): numerator to specify the internal position in a bar. Example 5/16 -> 5
		dnm (int): denominator to specify the internal position in a bar. Example 5/16 -> 16
		x (float): The x-axis position of the PosNode. Range[-16,32]
		y (float): The y-axis position of the PosNode. Range[-8,16]
		easetype (int): EaseType of the AngleNode. Use Pn.* Series.
		curve_init (float): The initial ratio of the easing curve. Range[0,1]
		curve_end (float): The end ratio of the easing curve. Range[0,1]
		max_visible_distance (float): The max visible distance for WishChilds.

	Returns:
		new_wish (WishGroup): The newly-created WishGroup.
	'''
	return w(False, max_visible_distance).n(bar, nmr, dnm, x, y, easetype, curve_init, curve_end)

def n2(bar:float, nmr:int=0, dnm:int=1, x:float=0, y:float=0, easetype:int=0, curve_init:float=0, curve_end:float=1, max_visible_distance:float = 7) -> WishGroup:
	'''
	A shorthand to create a Wish in layer 2 and then attach a PosNode with given arguments.

	Example:
		wn2(some_bartime,x=1,y=1)

	Args:
		bar (float): Bartime integer or the Original Bartime
		nmr (int): numerator to specify the internal position in a bar. Example 5/16 -> 5
		dnm (int): denominator to specify the internal position in a bar. Example 5/16 -> 16
		x (float): The x-axis position of the PosNode. Range[-16,32]
		y (float): The y-axis position of the PosNode. Range[-8,16]
		easetype (int): EaseType of the AngleNode. Use Pn.* Series.
		curve_init (float): The initial ratio of the easing curve. Range[0,1]
		curve_end (float): The end ratio of the easing curve. Range[0,1]
		max_visible_distance (float): The max visible distance for WishChilds.

	Returns:
		new_wish (WishGroup): The newly-created WishGroup.
	'''
	return w(True, max_visible_distance).n(bar, nmr, dnm, x, y, easetype, curve_init, curve_end)


# Official Tools & Patterns