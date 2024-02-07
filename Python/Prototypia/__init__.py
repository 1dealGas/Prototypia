'''
Methods Provided:   # See also  GitHub.com/1dealGas/Prototypia  .
    "An", "Pn", "VERSE", "NEW_VERSE", "REQUIRE",
    "OFFSET", "BEATS_PER_MINUTE", "BARS_PER_MINUTE", "SC_LAYER1", "SC_LAYER2",
    "CURRENT_ANGLE", "specialize_last_hint", "w", "n1", "n2", "i1", "i2",
    "Origin", "collide_to", "m"
'''

from .Arf2 import *
__all__ = [
	"An", "Pn", "VERSE", "NEW_VERSE", "REQUIRE",
	"OFFSET", "BEATS_PER_MINUTE", "BARS_PER_MINUTE", "SC_LAYER1", "SC_LAYER2",
	"CURRENT_ANGLE", "specialize_last_hint", "w", "n1", "n2", "i1", "i2",
	"Origin", "collide_to", "m"
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
		max_visible_distance (float): The max visible distance for WishChilds.

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
		max_visible_distance (float): The max visible distance for WishChilds.

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
		max_visible_distance (float): The max visible distance for WishChilds.
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
		max_visible_distance (float): The max visible distance for WishChilds.
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


def collide_to(target:WishGroup, at_bar:float, at_nmr:int = 0, at_dnm:int = 1, easetype:int = 0, curve_init:float = 0, curve_end:float = 1, with_a_hint:bool = True) -> FunctionType:
	'''
	A PseudoDecorator function to let multiple WishGroups collide.

	Example:
		# Suppose there are 3 WishGroups: wish_1, wish_2 and wish_3 .
		wish_1 / collide_to(wish_2, 6,9,16) / collide_to(wish_3, 7,0,1)

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

	def rtn(w:WishGroup) -> None:
		w.n(at_bartime,0,1, target_x, target_y, easetype, curve_init, curve_end)
		if with_a_hint: w.manual_hint(at_bartime,0,1)
	return rtn


def m(bar:float, nmr:int = 0, dnm:int = 1, x:float = 0, y:float = 0, *args, **kwargs) -> None:
	# easetype:int = 0, curve_init:float = 0, curve_end:float = 1
	pass