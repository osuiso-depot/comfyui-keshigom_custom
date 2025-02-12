# comfyui-keshigom_custom

### 概要
このカスタムノードは個人的によく使うノードを移植・機能追加・機能削除・再開発してまとめたものです。

### 目的
重厚すぎる傾向にある人気カスタムノード群から気に入った機能だけを抽出し、アプリケーション全体の動作を軽量にすることです。

### 注意事項
しばしば、予告なくアップデートが入ります。


---


# ノード一覧


---

## 🦀SetNode
- **説明**: 入力した値に名前をつけて保存します。
- **入力**:
  - `*`: 任意の型の入力
- **出力**:
  - `*`: 任意の型の出力

## 🦀GetNode
- **説明**: 保存した値を出力します。
- **出力**:
  - `*`: 保存した値の出力

## KANI🦀RegexpChopper
- **説明**: 正規表現を使用してテキストを分割します。
- **入力**:
  - `text`: 分割対象の文字列
  - `regex`: 使用する正規表現
- **出力**:
  - `Part 1`, `Part 2`, `Part 3`, `Part 4`, `All parts`: 分割されたテキスト

## KANI🦀FLIP-W/H Selector
- **説明**: 解像度のドロップダウンリストを提供し、選択された解像度に基づいて幅と高さを返します。
- **入力**:
  - `base_resolution`: 基本解像度
  - `base_adjustment`: 解像度の調整
  - `FLIP`: 幅と高さを入れ替えるかどうか
- **出力**:
  - `width`, `height`: 調整された幅と高さ

## KANI🦀FLIP-W/H SelectorConst
- **説明**: 定数の解像度を提供し、選択された解像度に基づいて幅と高さを返します。
- **入力**:
  - `width`: 幅
  - `height`: 高さ
  - `base_adjustment`: 解像度の調整
  - `FLIP`: 幅と高さを入れ替えるかどうか
- **出力**:
  - `width`, `height`: 調整された幅と高さ

## KANI🦀TextFind
- **説明**: 部分文字列または正規表現パターンを使用して文字列検索を行います。
- **入力**:
  - `text`: 検索対象の文字列
  - `substring`: 検索する部分文字列
  - `pattern`: 検索する正規表現パターン
- **出力**:
  - `found`: 検索結果（真偽値）

## KANI🦀ckpt_Loader_From_String
- **説明**: 文字列からチェックポイントをロードします。
- **入力**:
  - `ckpt_str`: チェックポイントの名前
  - `output_vae`: VAEを出力するかどうか
  - `output_clip`: CLIPを出力するかどうか
- **出力**:
  - `MODEL`, `CLIP`, `VAE`, `NAME_STRING`: ロードされたモデルとその名前

## KANI🦀True-or-False
- **説明**: 入力をそのまま出力し、50%の確率でTrue/Falseを返します。
- **入力**:
  - `input`: 任意の型の入力
- **出力**:
  - `output`: 入力された値
  - `50%/50%`: 50%の確率でTrue/False

## KANI🦀showAnything
- **説明**: 任意の入力を受け取り、それをノード上に表示します。
- **入力**:
  - `anything`: 任意の型の入力
- **出力**:
  - `output`: 入力された値

## KANI🦀Multiplexer
- **説明**: フラグに基づいて入力を2つの出力のいずれかに流します。
- **入力**:
  - `flag`: 制御信号
  - `input`: 任意の型の入力
- **出力**:
  - `output_1`, `output_2`: フラグに基づいて流される出力

## KANI🦀Math Expression
- **説明**: 数式を評価し、結果を返します。
- **入力**:
  - `expression`: 評価する数式
  - `a`, `b`, `c`: 任意の型の入力
- **出力**:
  - `INT`, `FLOAT`: 評価結果

### myStringNode(デバッグ用)
- **説明**: 文字列を入力として受け取り、そのまま出力します。
- **入力**:
  - `raw_text`: 入力文字列
- **出力**:
  - `output`: 入力された文字列


---

### 🦀とは？
蟹。

---

## 参考(謝辞)
[ComfyUI-Custom-Scripts](https://github.com/pythongosssss/ComfyUI-Custom-Scripts)
[ComfyUI-KJNodes](https://github.com/kijai/ComfyUI-KJNodes)
[was-node-suite-comfyui](https://github.com/WASasquatch/was-node-suite-comfyui)
[ComfyUI_ResolutionSelector](https://github.com/bradsec/ComfyUI_ResolutionSelector)
