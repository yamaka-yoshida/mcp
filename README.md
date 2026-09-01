# MCP 配布資源ハブ

Cursor 用 MCP サーバの**配布資源・設定テンプレート・ドキュメント**を一箇所に集約するリポジトリです。  
GitHub（または Cursor ホスト）にプッシュしておけば、自宅 PC・会社 PC などで `git clone` + セットアップスクリプトだけで同じ環境を再現できます。

## なぜこの構成か

| 従来 | このリポジトリ |
|------|----------------|
| `mcp.json` がマシンごとにバラバラ | `configs/mcp.json.template` から自動生成 |
| layout-kit / マニュアルが散在 | `scribus/` 以下に同梱 |
| pip パッケージのバージョンが不明 | `manifest.json` + `install.ps1` で一覧化 |
| 新 PC で手作業コピー | `clone` → `install.ps1` → `apply-config.ps1` |

## フォルダ構成

```
C:\work\MCP\
├── manifest.json           # 各 MCP の一覧・依存関係
├── configs\
│   └── mcp.json.template   # ~/.cursor/mcp.json の雛形
├── scripts\
│   ├── install.ps1         # pip パッケージ一括インストール
│   └── apply-config.ps1    # mcp.json を生成・配置
├── scribus\
│   ├── layout-kit\         # 座標キャリブレーション CLI
│   └── manual\             # 図解 HTML マニュアル
├── excel\
│   └── README.md           # Excel 系 MCP（外部リポジトリ参照）
└── docs\
    └── getting-started.md
```

## 新しい PC でのセットアップ

```powershell
cd C:\work
git clone <your-repo-url> MCP
cd MCP\scripts
.\install.ps1
.\apply-config.ps1 -PdfFormsDocs "C:\path\to\your\project\docs"
```

Cursor を再起動すると MCP が読み込まれます。

### 前提ソフト

- Python 3.13 / 3.14（MCP ごとに使い分け）
- Scribus 1.7.3（scribus MCP 利用時）
- Microsoft Excel（Excel 系 MCP 利用時）

## 同梱 vs 外部

| 種別 | 扱い |
|------|------|
| **同梱**（このリポジトリ内） | scribus layout-kit、HTML マニュアル、設定テンプレート |
| **pip インストール** | scribus-mcp, excellm, mcp-excel, mcp-pdf-forms |
| **外部リポジトリ参照** | ExcelVBAproject の excel-automation / vba-skills スクリプト |
| **プロジェクト固有** | pdf-forms の docs パス、各プロジェクトの `*.calibration.json` |

## マニュアル

ブラウザで開く:

```
C:\work\MCP\scribus\manual\index.html
```

## GitHub にプッシュする場合

```powershell
cd C:\work\MCP
git init -b main
git add -A
git commit -m "Initial MCP distribution hub"
git remote add origin <url>
git push -u origin main
```

**注意**: `configs/mcp.local.json` や `.env` は `.gitignore` 済み。マシン固有パスは `apply-config.ps1` の引数で渡してください。

## 関連

- 汎用 Skill: `%USERPROFILE%\.cursor\skills\scribus-mcp-layout\`
- scribus-mcp: https://github.com/caewa/scribus-mcp
