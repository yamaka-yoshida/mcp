# Scribus MCP 資源

| パス | 内容 |
|------|------|
| `layout-kit/` | `.sla` 座標・レイヤー・スケール CLI（`sla_tool.py`） |
| `manual/` | 図解 HTML マニュアル（`manual/index.html`） |

## 環境変数

`mcp.json` の scribus サーバで設定:

```
SCRIBUS_LAYOUT_KIT=C:\work\MCP\scribus\layout-kit
SCRIBUS_BIN=C:\Program Files\Scribus 1.7.3\scribus.exe
```

## プロジェクト側

各リポジトリの `design/sla_tool.py` ラッパーは `SCRIBUS_LAYOUT_KIT` を参照する。  
未設定時のフォールバックを `C:\work\MCP\scribus\layout-kit` に合わせて更新すること。
