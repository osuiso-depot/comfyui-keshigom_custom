from .nodes import StringNodeClass
from .nodes import RegExTextChopper
from .nodes import ResolutionSelector
from .nodes import ResolutionSelectorConst
from .nodes import KANI_TextFind
from .nodes import KANI_Checkpoint_Loader_Simple
from .nodes import KANI_TrueorFalse

NODE_CLASS_MAPPINGS = {
    "KANI🦀RegexpChopper":RegExTextChopper,
    "KANI🦀FLIP-W/H Selector":ResolutionSelector,
    "KANI🦀FLIP-W/H SelectorConst":ResolutionSelectorConst,
    "KANI🦀TextFind":KANI_TextFind,
    "KANI🦀ckpt_Loader_Simple":KANI_Checkpoint_Loader_Simple,
    "KANI🦀True-or-False":KANI_TrueorFalse,
    "myStringNode": StringNodeClass
}
