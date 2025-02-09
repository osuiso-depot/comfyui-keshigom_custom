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
    A node to provide a constanct int of resolutions and returns two int values (width and height).
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """
        Return a dictionary which contains config for all input fields.
        """
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

class KANI_Checkpoint_Loader_Simple:
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
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "signal": ("*",)  # 任意の型の入力を受け付ける
            },
        }

    RETURN_TYPES = ("*", "BOOLEAN")  # 順序を修正（signal が最初）
    RETURN_NAMES = ("signal", "result")  # 戻り値の名前を定義
    FUNCTION = "execute"

    CATEGORY = "KANI-NODES"

    def execute(self, signal=None):
        """
        signal をそのまま出力し、True か False をランダムに返す
        """
        result = random.random() < 0.5  # 50% の確率で True/False を返す
        return signal, result

    @classmethod
    def IS_CHANGED(cls, signal=None, **kwargs):
        """
        常に再評価を行う
        """
        return float("NaN")


import json


class a_AlwaysEqualProxy(str):
    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False

any_type = a_AlwaysEqualProxy("*")

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
    入力2 (制御信号): これがONの場合、入力1が出力1に流れます。
    入力2 (制御信号): これがOFFの場合、入力1が出力2に流れます。
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


NODE_CLASS_MAPPINGS = {
    "RegExTextChopper": RegExTextChopper,
    "ResolutionSelector": ResolutionSelector,
    "ResolutionSelectorConst": ResolutionSelectorConst,
    "KANI_TextFind": KANI_TextFind,
    "KANI_Checkpoint_Loader_Simple": KANI_Checkpoint_Loader_Simple,
    "KANI_TrueorFalse": KANI_TrueorFalse,
    "KANI_ShowAnything": KANI_ShowAnything,
    "KANI_Multiplexer": KANI_Multiplexer,
    "StringNodeClass": StringNodeClass
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RegExTextChopper":"KANI🦀RegexpChopper",
    "ResolutionSelector":"KANI🦀FLIP-W/H Selector",
    "ResolutionSelectorConst":"KANI🦀FLIP-W/H SelectorConst",
    "KANI_TextFind":"KANI🦀TextFind",
    "KANI_Checkpoint_Loader_Simple":"KANI🦀ckpt_Loader_Simple",
    "KANI_TrueorFalse":"KANI🦀True-or-False",
    "KANI_ShowAnything":"KANI🦀showAnything",
    "KANI_Multiplexer":"KANI🦀Multiplexer",
    "StringNodeClass":"myStringNode"
}
