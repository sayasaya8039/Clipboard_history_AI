# Clipboard History

コピーした内容を自動でカテゴリ分けして保存する Windows アプリです。

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 概要

クリップボードにコピーした内容を自動で監視し、ルールベースでカテゴリ分類して履歴として保存する、システムトレイ常駐型アプリケーションです。

## 機能

- 自動カテゴリ分類
  - URL
  - メールアドレス
  - コード
  - 電話番号
  - ファイルパス
  - 画像
  - テキスト
- 履歴管理
  - 検索
  - お気に入り
  - ワンクリックコピー
  - URL をブラウザで開く
- UI
  - システムトレイ常駐
  - ダーク / ライト / システムテーマ
  - Figma ベースの設定ダイアログ

## インストール

### 必要条件

- Python 3.10 以上
- Windows 10/11

### セットアップ

```bash
git clone https://github.com/sayasaya8039/Clipboard_history_AI.git
cd Clipboard_history_AI
pip install -r requirements.txt
```

## 使い方

### 起動

```bash
python main.py
```

起動するとシステムトレイにアイコンが表示されます。

### 主な操作

| 操作 | 動作 |
|------|------|
| トレイアイコン左クリック | 履歴ウィンドウを表示 |
| トレイアイコン右クリック | メニューを表示 |
| 履歴アイテムダブルクリック | クリップボードにコピー |
| URLクリック | ブラウザで開く |
| ⭐ボタン | お気に入り登録 / 解除 |
| 📋ボタン | クリップボードにコピー |
| 🗑ボタン | 履歴から削除 |

### 設定

トレイアイコン右クリックの「設定」から以下を管理できます。

- 一般
- 履歴
- アイテム
- ショートカット
- 外観

## プロジェクト構造

```text
Clipboard_history_AI/
├── main.py                 # エントリーポイント
├── config.py               # 設定管理
├── database.py             # SQLite 操作
├── categorizer.py          # ルールベース分類
├── clipboard_monitor.py    # クリップボード監視
├── ui/
│   ├── main_window.py      # メインウィンドウ
│   ├── settings_dialog.py  # 設定ダイアログ
│   ├── tray_icon.py        # システムトレイ
│   └── styles.py           # テーマ / スタイル
├── requirements.txt
└── README.md
```

## 技術スタック

- 言語: Python 3.10+
- GUI: PyQt6
- データベース: SQLite

## ライセンス

MIT License

## 作者

sayasaya8039

---

Built with Claude Code
