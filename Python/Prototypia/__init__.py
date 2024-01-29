from .Arf2 import *
__all__ = [
	"An", "Pn",
    "OFFSET", "BEATS_PER_MINUTE", "BARS_PER_MINUTE", "SC_LAYER1", "SC_LAYER2",
    "CURRENT_ANGLE", "specialize_last_hint", "w",

	"REQUIRE"
]


class An:   # EaseType Enums
	STASIS = 0
	LINEAR = 1
	ESIN = 2
	ECOS = 3
class Pn:   # EaseType Enums
	LINEAR = 0
	LCIRC = 1
	RCIRC = 2
	INQUAD = 3
	OUTQUAD = 4
class _R:   # Managing wgo_required & hgo_required
	cnt = 0
	def __getitem__(self, idx):
		if _R.cnt == 0:
			Arf2Prototype._wgo_required = idx
			_R.cnt = 1
		elif _R.cnt == 1:
			Arf2Prototype._hgo_required = idx
			_R.cnt = 2
		return self
REQUIRE = _R()


def OFFSET(ms:int) -> None:
	Arf2Prototype._offset = ms

def BEATS_PER_MINUTE(*args) -> None:
	pass

def BARS_PER_MINUTE(*args) -> None:
	pass

def SC_LAYER1(*args) -> None:
	pass

def SC_LAYER2(*args) -> None:
	pass


# Under Construction
def CURRENT_ANGLE(degree:int) -> None:
	if degree<-1800 or degree>1800:
		raise ValueError("Degree of AngleNode out of Range [-1800,1800].")
	Arf2Prototype._current_angle = degree

def specialize_last_hint() -> None:
	Arf2Prototype._last_hint.is_special = True

def w(of_layer2:bool = False, max_visible_distance:float = 7) -> WishGroup:
	_w = WishGroup(of_layer2, max_visible_distance)
	Arf2Prototype._wish.append(_w)