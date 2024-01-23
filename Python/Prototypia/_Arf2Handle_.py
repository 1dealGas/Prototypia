# Common Imports
import sys
import atexit
import flatbuffers

# Flatbuffers Related Imports
import Arf2 as FB_Arf2
import Arf2Index as FB_Index
import WishChild as FB_WishChild
import WishGroup as FB_WishGroup


# Error Handling & Tools
E = Exception
class                                		Prohibited(E):
	def __str__(self) -> str: return 	''' The "new method is prohibited to call in the __main__ script. '''

def NonManual(f) -> function:
	def decorated(*args, **kwargs) -> None:
		if __name__ == "__main__": raise Prohibited
		return f(*args, **kwargs)
	return decorated


# Arf2 Elements
# AngleNode: Tuple(Bartime, Angle, EaseType)
class WishChild:
	'''
	WishChild refers a WishGroup's position and the current DTime to determine its position
	in a polar-coordinate-like way.
	'''
	# EaseType Enums
	STASIS = 0
	LINEAR = 1
	ESIN = 2
	ECOS = 3

	@NonManual
	def __init__(self, Bartime:float) -> None:
		self.bartime = Bartime
		self.is_default_angle = True
		self.anodes = [(0, Arf2Prototype._current_angle, WishChild.STASIS)]

class PosNode:
	'''
	Class of Nodes that a Wish passes by.
	'''
	# EaseType Enums
	LINEAR = 0
	LCIRC = 1
	RCIRC = 2
	INQUAD = 3
	OUTQUAD = 4

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

class WishGroup:
	'''
	Class of Wishes in an Arf2 chart[fumen].
	In Aerials, Wish guides the player to light the Hint.
	'''
	@NonManual
	def __init__(self, ofLayer2:bool = False, MaxVisibleDistance:float = 7):
		self.nodes = []
		self.childs = []
		self.of_layer2 = ofLayer2
		self.max_visible_distance = MaxVisibleDistance
	
	# Several Tool Functions for the WishGroup instance


class Hint:
	'''
	Hint represents the Tap Note of Aerials.
	The position(x,y) will be determined in the compiling progress.
	'''
	@NonManual
	def __init__(self, Bartime:float, Ref:WishGroup) -> None:
		self.bartime = Bartime
		self.ref = Ref
		self.is_special = False


# Arf2 Prototype Data & Compiler Function
class Arf2Prototype:
	'''
	A rough Singeleton class of the Prototype Data of an Arf2 chart[fumen].
	'''
	_wish:list[WishGroup]						= []
	_hint:list[Hint]							= []
	_offset:int									= 0		# A ms value (>=0)
	_current_angle:int							= 90	# Degree [-1800,1800]
	_last_hint:Hint								= None
	_bpms:list[tuple(float,float)]				= []	# (Bartime, BPM)
	_scales_layer1:list[tuple(float,float)]		= []	# (Bartime, Scale)
	_scales_layer2:list[tuple(float,float)]		= []	# Bartime>=0   BPM>0

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