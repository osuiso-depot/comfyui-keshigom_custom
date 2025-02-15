
class a_AlwaysEqualProxy(str):
    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False

any_type = a_AlwaysEqualProxy("*")


class StringNodeClass:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "raw_text": ("STRING", {"multiline": True})
            }
        }
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("output", )
    FUNCTION = "run"
    OUTPUT_NODE = True

    CATEGORY = "sample_node"


    def run(self, raw_text):
        return (raw_text, )


import re

class RegExTextChopper:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
                "regex": ("STRING", {})
            },
            "optional": {}
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("Part 1", "Part 2", "Part 3", "Part 4", "All parts")

    FUNCTION = "run"
    CATEGORY = "KANI-NODES"

    @staticmethod
    def is_valid_regex(regex_from_user: str) -> bool:
        try:
            re.compile(regex_from_user)  # 修正: `re.escape` を削除
            return True
        except re.error:
            return False

    def run(self, text, regex):
        if self.is_valid_regex(regex):
            obj = re.compile(regex, re.MULTILINE)
            result = obj.findall(text)

            # キャプチャグループがある場合、findall はタプルのリストを返す
            if result and isinstance(result[0], tuple):
                result = [match[0] for match in result]

            # 必要な個数だけ取り出す
            text1, text2, text3, text4 = (result + ["", "", "", ""])[:4]
            text_all = "\n".join(result)
        else:
            text1 = text2 = text3 = text4 = ""
            text_all = text

        return text1, text2, text3, text4, text_all


class ResolutionSelector:
    """
    A node to provide a drop-down list of resolutions and returns two int values (width and height).
    """

    # クラス変数として BASE_RESOLUTIONS を定義
    BASE_RESOLUTIONS = [
        (1024, 1024),
        (704, 1408),
        (704, 1344),
        (768, 1344),
        (768, 1280),
        (832, 1216),
        (832, 1152),
        (896, 1152),
        (896, 1088),
        (960, 1088),
        (960, 1024),
        (1088, 960),
        (1088, 896),
        (1152, 896),
        (1152, 832),
        (1216, 832),
        (1280, 768),
        (1344, 768),
        (1408, 704),
        (1472, 704),
        (1536, 640),
        (1600, 640),
        (1664, 576),
        (1728, 576)
    ]


    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """
        Return a dictionary which contains config for all input fields.
        """
        # Create a list of resolution strings for the drop-down menu
        resolution_strings = [
            f"{width} x {height}" for width, height in cls.BASE_RESOLUTIONS
        ]

        return {
            "required": {
                "base_resolution": (resolution_strings,),
                "base_adjustment": (["SDXL (None)", "SD21 (75%)", "SD15 (50%)"],),
                "FLIP": ("BOOLEAN", {"default": False})
            }
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "select_resolution"
    CATEGORY = "KANI-NODES"

    def select_resolution(self, base_resolution: str, base_adjustment: str, FLIP: bool) -> tuple[int, int]:
        """
        Returns the width and height based on the selected resolution and adjustment.

        Args:
            base_resolution (str): Selected resolution in the format "width x height".
            base_adjustment (str): Selected adjustment (resolution value reduction) based on SD version.
            FLIP (bool): Whether to swap width and height.

        Returns:
            Tuple[int, int]: Adjusted width and height.
        """
        try:
            width, height = map(int, base_resolution.split(' x '))
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid base_resolution format: {base_resolution}")

        # 調整係数を定義
        adjustment_factors = {
            "SDXL (None)": 1.0,
            "SD21 (75%)": 0.75,
            "SD15 (50%)": 0.5
        }

        factor = adjustment_factors.get(base_adjustment)
        if factor is None:
            raise ValueError(f"Invalid base_adjustment value: {base_adjustment}")

        # 計算後に整数変換
        adjusted_width = int(width * factor)
        adjusted_height = int(height * factor)

        return (adjusted_height, adjusted_width) if FLIP else (adjusted_width, adjusted_height)


class ResolutionSelectorConst:
    """
    A node to provide a constant int of resolutions and returns two int values (width and height).
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 1, "max": 65536}),  # 最小値を1に変更
                "height": ("INT", {"default": 1024, "min": 1, "max": 65536}), # 同上
                "base_adjustment": (["SDXL (None)", "SD21 (75%)", "SD15 (50%)"],),
                "FLIP": ("BOOLEAN", {"default": False})
            }
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "select_resolution"
    CATEGORY = "KANI-NODES"

    def select_resolution(self, width: int, height: int, base_adjustment: str, FLIP: bool) -> tuple[int, int]:
        """
        Returns the width and height based on the selected resolution and FLIP.

        Args:
            width (int): Input width.
            height (int): Input height.
            base_adjustment (str): Resolution adjustment type.
            FLIP (bool): Whether to flip width and height.

        Returns:
            Tuple[int, int]: Adjusted width and height.
        """
        adjustment_factors = {
            "SDXL (None)": 1.0,
            "SD21 (75%)": 0.75,
            "SD15 (50%)": 0.5
        }

        factor = adjustment_factors.get(base_adjustment)
        if factor is None:
            raise ValueError(f"Invalid base_adjustment value: {base_adjustment}")

        # ここで整数化する（先に調整を行い、その後intにキャスト）
        adjusted_width = int(width * factor)
        adjusted_height = int(height * factor)

        return (adjusted_height, adjusted_width) if FLIP else (adjusted_width, adjusted_height)

class KANI_TextFind:
    """
    This class performs string search using either a substring or a regular expression pattern.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True }),
                "substring": ("STRING", {"default": '', "multiline": False}),
                "pattern": ("STRING", {"default": '', "multiline": False}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("found",)
    FUNCTION = "execute"

    CATEGORY = "KANI-NODES"

    def execute(self, text: str, substring: str, pattern: str) -> tuple[bool]:
        if substring:
            return (substring in text,)  # タプルとして返す

        return (bool(re.search(pattern, text)),)  # タプルとして返す

import os
import folder_paths as comfy_paths
import comfy.sd

class KANI_Checkpoint_Loader_From_String:
    """
    NODE for loading checkpoints from a string.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "ckpt_str": ("STRING", {"default": "", "multiline": False}),
                "output_vae": ("BOOLEAN", {"default": True}),
                "output_clip": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "STRING")
    RETURN_NAMES = ("MODEL", "CLIP", "VAE", "NAME_STRING")
    FUNCTION = "load_checkpoint"

    CATEGORY = "KANI-NODES"

    def load_checkpoint(self, ckpt_str, output_vae=True, output_clip=True):
        # 空文字やNoneのチェック
        if not ckpt_str:
            raise ValueError("Checkpoint name cannot be empty.")

        # 拡張子がない場合、自動で .safetensors を補完
        _, ext = os.path.splitext(ckpt_str)
        if ext == "":
            ckpt_str += ".safetensors"

        # .safetensors または .pt 以外の拡張子はエラー
        valid_extensions = (".safetensors", ".ckpt")
        if not ckpt_str.endswith(valid_extensions):
            raise ValueError(f"Invalid checkpoint extension: '{ckpt_str}'. Only .safetensors and .ckpt are allowed.")

        # チェックポイントのパスを取得
        ckpt_path = comfy_paths.get_full_path("checkpoints", ckpt_str)

        # パスがNoneまたは存在しない場合のエラーハンドリング
        if ckpt_path is None or not os.path.exists(ckpt_path):
            raise FileNotFoundError(f"Checkpoint '{ckpt_str}' not found in 'checkpoints' directory.")

        # .ckpt の場合、警告を表示（処理は続行）
        if ckpt_str.endswith(".ckpt"):
            print(f"⚠ Warning: Loading a .ckpt model '{ckpt_str}'. This format is less secure than .safetensors.")

        # チェックポイントをロード
        out = comfy.sd.load_checkpoint_guess_config(
            ckpt_path, output_vae=output_vae, output_clip=output_clip,
            embedding_directory=comfy_paths.get_folder_paths("embeddings")
        )

        # チェックポイントの名前を返す（拡張子なし）
        return out[0], out[1], out[2], os.path.splitext(os.path.basename(ckpt_str))[0]

import random

class KANI_TrueorFalse:
    """input をそのまま出力し、50% の確率で True/False を返す"""
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "input": (any_type, {"tooltip": "The input flows directly to the output."})  # 任意の型の入力を受け付ける
            },
        }

    RETURN_TYPES = (any_type, "BOOLEAN")  # 順序を修正（signal が最初）
    RETURN_NAMES = ("output", "50%/50%")  # 戻り値の名前を定義
    FUNCTION = "execute"

    CATEGORY = "KANI-NODES"

    def execute(self, input, **kwargs):
        """
        signal をそのまま出力し、True か False をランダムに返す
        """
        result = random.random() < 0.5  # 50% の確率で True/False を返す
        return input, result

    @classmethod
    def IS_CHANGED(cls, input, **kwargs):
        """
        常に再評価を行う
        """
        return float("NaN")


import json


class KANI_ShowAnything:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {"anything": (any_type, {})},  # 何でも受け入れる
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            }
        }

    RETURN_TYPES = (any_type,)  # 何でも返せる
    RETURN_NAMES = ("output",)
    INPUT_IS_LIST = True  # `anything` はリストとして受け取る
    OUTPUT_NODE = True
    FUNCTION = "log_input"
    CATEGORY = "KANI-NODES/Logic"

    def log_input(self, unique_id=None, extra_pnginfo=None, **kwargs):
        """
        何でも受け取り、それをノード上に表示する。
        """
        values = []
        if "anything" in kwargs:
            for val in kwargs["anything"]:
                try:
                    # 文字列・数値・辞書などを適切に処理
                    if isinstance(val, str):
                        values.append(val)
                    elif isinstance(val, (int, float, bool)):
                        values.append(str(val))  # 数値を文字列に変換
                    elif isinstance(val, (list, dict, set, tuple)):
                        values.append(json.dumps(val, ensure_ascii=False))
                    else:
                        values.append(str(val))
                except Exception as e:
                    print(f"Error processing value: {val}, Exception: {e}")
                    values.append(str(val))

        # ワークフロー情報を取得してノードにデータをセット
        if not extra_pnginfo:
            print("Error: extra_pnginfo is empty")
        elif not isinstance(extra_pnginfo[0], dict) or "workflow" not in extra_pnginfo[0]:
            print("Error: extra_pnginfo[0] is not a dict or missing 'workflow' key")
        else:
            workflow = extra_pnginfo[0]["workflow"]
            node = next((x for x in workflow["nodes"] if str(x["id"]) == unique_id[0]), None)
            if node:
                node["widgets_values"] = [values]

        # 単一要素なら `values[0]` を返す、それ以外は `values` のまま
        if isinstance(values, list) and len(values) == 1:
            return {"ui": {"text": values}, "result": (values[0],), }
        else:
            return {"ui": {"text": values}, "result": (values,), }



class KANI_Multiplexer:
    """
    flag (制御信号): これがONの場合、inputがoutput1に流れます。
    flag (制御信号): これがOFFの場合、inputがoutput2に流れます。
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "flag": ("BOOLEAN", {"default": True}),  # `bool` を避ける
                "input": (any_type, {"tooltip": "This input flows to either output1 or 2."}),  # 何でも受け入れる
            }
        }

    # 出力1,2どちらかに signal を流す
    RETURN_TYPES = (any_type, any_type)
    RETURN_NAMES = ("output_1", "output_2")  # 出力名を明確に

    FUNCTION = "execute"

    CATEGORY = "KANI-NODES/Logic"

    def execute(self, flag, input):
        if flag:
            return (input, "")
        else:
            return ("", input)


import ast
import math
import random
import operator as op

operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Pow: op.pow,
    ast.BitXor: op.xor,
    ast.USub: op.neg,
    ast.Mod: op.mod,
    ast.BitAnd: op.and_,
    ast.BitOr: op.or_,
    ast.Invert: op.invert,
    ast.And: lambda a, b: 1 if a and b else 0,
    ast.Or: lambda a, b: 1 if a or b else 0,
    ast.Not: lambda a: 0 if a else 1,
    ast.RShift: op.rshift,
    ast.LShift: op.lshift
}


functions = {
    "round": {
        "args": (1, 2),
        "call": lambda a, b = None: round(a, b),
        "hint": "number, dp? = 0"
    },
    "ceil": {
        "args": (1, 1),
        "call": lambda a: math.ceil(a),
        "hint": "number"
    },
    "floor": {
        "args": (1, 1),
        "call": lambda a: math.floor(a),
        "hint": "number"
    },
    "min": {
        "args": (2, None),
        "call": lambda *args: min(*args),
        "hint": "...numbers"
    },
    "max": {
        "args": (2, None),
        "call": lambda *args: max(*args),
        "hint": "...numbers"
    },
    "randomint": {
        "args": (2, 2),
        "call": lambda a, b: random.randint(a, b),
        "hint": "min, max"
    },
    "randomchoice": {
        "args": (2, None),
        "call": lambda *args: random.choice(args),
        "hint": "...numbers"
    },
    "sqrt": {
        "args": (1, 1),
        "call": lambda a: math.sqrt(a),
        "hint": "number"
    },
    "int": {
        "args": (1, 1),
        "call": lambda a = None: int(a),
        "hint": "number"
    },
    "iif": {
        "args": (3, 3),
        "call": lambda a, b, c = None: b if a else c,
        "hint": "value, truepart, falsepart"
    },
}

class MathExpression:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "expression": ("STRING", {"multiline": True, "dynamicPrompts": False}),
            },
            "optional": {
                "a": (any_type, {}),
                "b": (any_type, {}),
                "c": (any_type, {}),
            },
            "hidden": {"extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT"},
        }

    RETURN_TYPES = ("INT", "FLOAT")
    FUNCTION = "evaluate"
    CATEGORY = "KANI-NODES/Math"
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, expression, **kwargs):
        """ランダム関数が含まれる場合は、常に再評価を行う"""
        return float("NaN") if "random" in expression else expression

    # widgetの値を取得するためのメソッド
    def get_widget_value(self, extra_pnginfo, prompt, node_name, widget_name):
        workflow = extra_pnginfo["workflow"] if "workflow" in extra_pnginfo else { "nodes": [] }
        node_id = None
        for node in workflow["nodes"]:
            name = node["type"]
            if "properties" in node:
                if "Node name for S&R" in node["properties"]:
                    name = node["properties"]["Node name for S&R"]
            if name == node_name:
                node_id = node["id"]
                break
            if "title" in node:
                name = node["title"]
            if name == node_name:
                node_id = node["id"]
                break
        if node_id is not None:
            values = prompt[str(node_id)]
            if "inputs" in values:
                if widget_name in values["inputs"]:
                    value = values["inputs"][widget_name]
                    if isinstance(value, list):
                        raise ValueError("Converted widgets are not supported via named reference, use the inputs instead.")
                    return value
            raise NameError(f"Widget not found: {node_name}.{widget_name}")
        raise NameError(f"Node not found: {node_name}.{widget_name}")

    # image,lantentのサイズを取得するためのメソッド
    def get_size(self, target, property):
        if isinstance(target, dict) and "samples" in target:
            # Latent
            if property == "width":
                return target["samples"].shape[3] * 8
            return target["samples"].shape[2] * 8
        else:
            # Image
            if property == "width":
                return target.shape[2]
            return target.shape[1]


    def evaluate(self, expression, prompt, extra_pnginfo={}, a=None, b=None, c=None):
        expression = expression.replace('\n', ' ').replace('\r', '')
        # ノードが空の場合は適切に処理(0を返す)
        if not expression:
            return {"ui": {"value": [""]}, "result": (0, 0.0)}
        node = ast.parse(expression, mode='eval').body
        lookup = {"a": a, "b": b, "c": c}

        def eval_op(node, l, r):
            l = eval_expr(l)
            r = eval_expr(r)
            l = l if isinstance(l, int) else float(l)
            r = r if isinstance(r, int) else float(r)
            return operators[type(node.op)](l, r)

        def eval_expr(node):
            if isinstance(node, ast.Constant):  # 数値リテラル
                return node.value
            elif isinstance(node, ast.Name):  # 変数
                if node.id in lookup:
                    val = lookup[node.id]
                    if isinstance(val, (int, float, complex)):
                        return val
                    else:
                        raise TypeError(
                            f"Compex types (LATENT/IMAGE) need to reference their width/height, e.g. {node.id}.width")
                raise NameError(f"Name not found: {node.id}")
            elif isinstance(node, ast.BinOp):  # 二項演算 (+, -, *, /)
                left, right = eval_expr(node.left), eval_expr(node.right)
                return operators[type(node.op)](left, right)
            elif isinstance(node, ast.UnaryOp):  # 単項演算 (-, ~, not)
                return operators[type(node.op)](eval_expr(node.operand))
            elif isinstance(node, ast.BoolOp):  # `and` / `or`
                return eval_op(node, node.values[0], node.values[1])
            elif isinstance(node, ast.Compare):  # 比較演算 (x < y < z)
                l = eval_expr(node.left)
                r = eval_expr(node.comparators[0])
                if isinstance(node.ops[0], ast.Eq):
                    return 1 if l == r else 0
                if isinstance(node.ops[0], ast.NotEq):
                    return 1 if l != r else 0
                if isinstance(node.ops[0], ast.Gt):
                    return 1 if l > r else 0
                if isinstance(node.ops[0], ast.GtE):
                    return 1 if l >= r else 0
                if isinstance(node.ops[0], ast.Lt):
                    return 1 if l < r else 0
                if isinstance(node.ops[0], ast.LtE):
                    return 1 if l <= r else 0
                raise NotImplementedError(
                    "Operator " + node.ops[0].__class__.__name__ + " not supported.")
            elif isinstance(node, ast.Call):  # 関数呼び出し
                func_name = node.func.id
                if func_name in functions:
                    func = functions[func_name]
                    args = [eval_expr(arg) for arg in node.args]
                    if len(args) < func["args"][0] or (func["args"][1] is not None and len(args) > func["args"][1]):
                        raise ValueError(f"関数 '{func_name}' の引数の数が不正です")
                    return func["call"](*args)
                raise ValueError(f"関数 '{func_name}' は未定義です")
            # 属性参照 (widget の値取得)
            elif isinstance(node, ast.Attribute):
                if node.value.id in lookup:
                    if node.attr == "width" or node.attr == "height":
                        return self.get_size(lookup[node.value.id], node.attr)
                return self.get_widget_value(extra_pnginfo, prompt, node.value.id, node.attr)
            else:
                raise TypeError(f"未対応のノードタイプ: {type(node).__name__}")

        result = eval_expr(node)
        return {"ui": {"value": [result]}, "result": (int(result), float(result))}


NODE_CLASS_MAPPINGS = {
    "RegExTextChopper": RegExTextChopper,
    "ResolutionSelector": ResolutionSelector,
    "ResolutionSelectorConst": ResolutionSelectorConst,
    "KANI_TextFind": KANI_TextFind,
    "KANI_Checkpoint_Loader_From_String": KANI_Checkpoint_Loader_From_String,
    "KANI_TrueorFalse": KANI_TrueorFalse,
    "KANI_ShowAnything": KANI_ShowAnything,
    "KANI_Multiplexer": KANI_Multiplexer,
    "KANI_MathExpression": MathExpression,
    "StringNodeClass": StringNodeClass
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RegExTextChopper":"KANI🦀RegexpChopper",
    "ResolutionSelector":"KANI🦀FLIP-W/H Selector",
    "ResolutionSelectorConst":"KANI🦀FLIP-W/H SelectorConst",
    "KANI_TextFind":"KANI🦀TextFind",
    "KANI_Checkpoint_Loader_From_String":"KANI🦀ckpt_Loader_From_String",
    "KANI_TrueorFalse":"KANI🦀True-or-False",
    "KANI_ShowAnything":"KANI🦀showAnything",
    "KANI_Multiplexer":"KANI🦀Multiplexer",
    "KANI_MathExpression": "KANI🦀Math Expression",
    "StringNodeClass":"myStringNode"
}
