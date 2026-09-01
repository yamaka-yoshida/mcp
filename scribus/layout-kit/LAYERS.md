# 帳票レイアウト — Scribus レイヤー標準

`layers.standard.json` が正本。帳票は **下→上** の 5 レイヤーで分ける。

## レイヤー一覧

| 順（下→上） | 名前 | 印刷 | 置くもの |
|------------|------|------|----------|
| 0 | **背景** | ○ | 塗り矩形、セクション背景色、ロゴ |
| 1 | **罫線** | ○ | 表枠、罫線、枠のみの矩形 |
| 2 | **見出し** | ○ | 固定ラベル、タイトル、列見出し、行番号 |
| 3 | **データ** | ○ | 入力欄プレースホルダ、サンプル値（AcroForm 位置参考） |
| 4 | **作業** | × | 余白ガイド、キャリブレーション、作業メモ |

**最小構成**（シンプルな静的帳票）: `背景` + `罫線` + `見出し` の 3 つで可。  
**データ入力あり**の帳票: `データ` を追加。  
**レイアウト調整中**: `作業` を追加（PDF には出さない）。

## オブジェクト種別 → レイヤー

| kind | レイヤー | 例 |
|------|---------|-----|
| `bg_fill`, `image` | 背景 | `section_bg` 矩形 |
| `line`, `grid`, `border_rect` | 罫線 | `createLine`, 表の外枠 |
| `label`, `title`, `header`, `row_number` | 見出し | 「運転日」「No」 |
| `field`, `placeholder`, `sample_value` | データ | 空テキストフレーム |
| `guide`, `calibration` | 作業 | 余白ガイド線 |

## Scribus スクリプト（headless）

```python
import os, sys
KIT = os.environ.get("SCRIBUS_LAYOUT_KIT", r"C:\work\RustProject\Tool\scribus-layout-kit")
sys.path.insert(0, KIT)
from scribus_layers import ensure_layers, set_layer

ensure_layers(scribus)
set_layer(scribus, "label")      # → 見出し
set_layer(scribus, "grid")       # → 罫線
set_layer(scribus, "bg_fill")    # → 背景
```

## MCP（scribus-mcp）

1. `list_layers` で現状確認
2. 不足があれば `create_layer`
3. **作成前**に `set_active_layer`（`find_objects` の layer フィルタは未対応）
4. 既存オブジェクトは `send_to_layer`
5. `作業` は `set_layer_printable` で `false`

## 検証 CLI

```powershell
python sla_tool.py layers --calibration design\帳票.calibration.json
```

`.sla` のレイヤー名・順序・印刷可否を標準と照合する。

## 新規プロジェクト

`sla_tool.py init` で作る `*.calibration.json` に `layers.profile` が入る。  
Skill `scribus-mcp-layout` も本標準を参照する。
