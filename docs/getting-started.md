# はじめに — 新しい PC への展開

## 1. リポジトリを取得

```powershell
cd C:\work
git clone <repo-url> MCP
```

## 2. 依存パッケージをインストール

```powershell
cd C:\work\MCP\scripts
.\install.ps1
```

Python のパスが標準と違う場合:

```powershell
.\install.ps1 -Python313 "D:\Python313\python.exe" -Python314 "D:\Python314\python.exe"
```

## 3. Cursor MCP 設定を生成

```powershell
.\apply-config.ps1 `
  -WorkRoot "C:\work" `
  -PdfFormsDocs "C:\work\YourProject\docs"
```

## 4. Scribus（帳票レイアウト利用時）

1. Scribus 1.7.3 をインストール
2. `scribus-mcp --print-bridge-path` で bridge を確認
3. マニュアル: `C:\work\MCP\scribus\manual\index.html`

## 5. Skills（任意）

汎用 Skill は Cursor の個人フォルダに置く:

```
%USERPROFILE%\.cursor\skills\scribus-mcp-layout\
```

プロジェクト固有 Skill は各リポジトリの `.cursor/skills/` に置く。

## トラブルシューティング

| 問題 | 対処 |
|------|------|
| MCP が表示されない | Cursor 再起動、`~/.cursor/mcp.json` の JSON 構文確認 |
| scribus-mcp が見つからない | `install.ps1` 再実行、Python314 Scripts を PATH に |
| layout-kit が見つからない | `SCRIBUS_LAYOUT_KIT` が `C:\work\MCP\scribus\layout-kit` か確認 |
