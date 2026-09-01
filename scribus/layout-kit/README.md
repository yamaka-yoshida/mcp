# scribus-layout-kit

Scribus `.sla` の座標キャリブレーションをプロジェクト横断で使う CLI 群。

## 前提

- Scribus 1.7.x（環境変数 `SCRIBUS_BIN`）
- `scribus-mcp`（Cursor MCP、`~/.cursor/mcp.json`）
- 各プロジェクトに `design/*.calibration.json` + `*.sla`

## 他プロジェクトへの導入（3 ステップ）

### 1. MCP（一度だけ・グローバル）

`~/.cursor/mcp.json` に `scribus` サーバを登録済みであること。`SCRIBUS_LAYOUT_KIT` を本フォルダに向ける。

### 2. calibration 作成

```powershell
cd 新プロジェクト\design
python C:\work\RustProject\Tool\scribus-layout-kit\sla_tool.py init `
  --name 帳票名 --output 帳票名.calibration.json --sla 帳票名.sla
```

### 3. プロジェクトラッパー

`project_sla_tool.py.template` を `design/sla_tool.py` にコピーし、`CALIBRATION_JSON` を変更。

```powershell
copy project_sla_tool.py.template design\sla_tool.py
# CALIBRATION_JSON = "帳票名.calibration.json" に編集
```

任意: `.cursor/skills/scribus-<プロジェクト名>-design/SKILL.md` にパスを記載（`scribus-unko-design` を参考）。

## コマンド

| コマンド | 用途 |
|----------|------|
| `info` | バウンディングボックスと余白矩形を表示 |
| `shift --dx-mm 35` | 全オブジェクトをシフト（位置キャリブレーション） |
| `fit --percent 98` | 余白内にスケール（`--dry-run` で倍率のみ） |
| `normalize` | A4 ページサイズ修正・ガイド・headless オフセット除去 |
| `layers` | レイヤー標準（`LAYERS.md`）との照合 |
| `init` | `calibration.template.json` から新規作成 |

```powershell
python sla_tool.py info --calibration design\運行指示書.calibration.json
python sla_tool.py fit --calibration design\運行指示書.calibration.json --percent 100 --dry-run
```

プロジェクトラッパー経由なら `--calibration` 省略可:

```powershell
python design\sla_tool.py info
```

## 環境変数

| 変数 | 意味 |
|------|------|
| `SCRIBUS_LAYOUT_KIT` | 本フォルダのパス（MCP / Skill から参照） |
| `SCRIBUS_BIN` | Scribus 実行ファイル |

## 関連

- Cursor Skill: `~/.cursor/skills/scribus-mcp-layout/SKILL.md`
- **マニュアル（図解 HTML）**: `C:\work\MCP\scribus\manual\index.html`
- レイヤー標準: [LAYERS.md](LAYERS.md)
- scribus-mcp: https://github.com/caewa/scribus-mcp
