# プロジェクト用 MCP ひな型

ワーク方針: `C:\work\docs\developer\cursor-mcp-project-policy.md`  
参照実装: `C:\work\RustProject\tool-launcher\.cursor\`（空 `mcp.json` + スコープ用 `.mdc`）

## ファイル一覧

| ファイル | 用途 |
|----------|------|
| `project.cursor.mcp.json.template` | 新規製品の `.cursor/mcp.json`（**空の `mcpServers`** — MCP 不要な製品向け） |
| `project.cursor.mcp.with-servers.example.json` | MCP を載せるときの記述例（コピーして不要ブロックを削除） |
| `mcp-project-rule.mdc.template` | `{{PLACEHOLDER}}` 付きルール。製品ごとに置換して `.cursor/rules/mcp-<slug>.mdc` へ |
| `examples/tool-launcher.*` | tool-launcher 適用済みの実例（テンプレ置換後の見本） |
| `mcp.json.template` | **グローバル** `~/.cursor/mcp.json` 用（従来・マシン横断インフラ） |

## 新規プロジェクトへの配置

```powershell
$Repo = "C:\work\RustProject\my-product"
New-Item -ItemType Directory -Force -Path "$Repo\.cursor\rules" | Out-Null
Copy-Item "C:\work\MCP\configs\project.cursor.mcp.json.template" "$Repo\.cursor\mcp.json"
```

MCP 付きの製品では、代わりに `project.cursor.mcp.with-servers.example.json` を起点に編集する。

## ルール（スコープ制限）

1. `mcp-project-rule.mdc.template` をコピーし `mcp-my-product.mdc` などにリネーム。
2. プレースホルダを置換:

| プレースホルダ | 例（tool-launcher） |
|----------------|---------------------|
| `{{PROJECT_SLUG}}` | `tool-launcher` |
| `{{PROJECT_TITLE}}` | `tool-launcher` |
| `{{MCP_JSON_POLICY}}` | **製品専用 MCP は登録しない**（空） |
| `{{GLOBAL_SERVERS_TO_AVOID}}` | `scribus / dart / penpot` |
| `{{AGENT_TOOL_ROWS}}` | 利用可・不可の表の行（markdown 表のセル） |
| `{{SCOPE_BOUNDARY_NOTES}}` | 他リポジトリでやる作業の一文 |

実例は `examples/tool-launcher.mcp-project-rule.mdc` をそのまま見る。

## MCP が不要な製品（tool-launcher 型）

- `mcp.json` は **空**のまま。
- 代わりに **ルールで**「使ってよい手段（シェル・browser）」と「他製品 MCP 禁止」を明示する。
- グローバルに残っている scribus / excel 等は、マージされるため **ルールで使わない**と書く。

## MCP が必要な製品

`project.cursor.mcp.with-servers.example.json` を参考に、この repo の `mcp.json` にのみサーバーを定義する。グローバルと **同名を避ける**（プロジェクト優先でも二重管理になる）。

## グローバル設定

マシン横断の少数 MCP だけ `mcp.json.template` → `scripts\apply-config.ps1` で `~/.cursor/mcp.json` を生成する（プロジェクト用テンプレとは別）。
