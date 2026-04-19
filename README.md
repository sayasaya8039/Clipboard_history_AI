# Coppy - Clipboard History

<p align="center">
  <img src="resources/icon.png" alt="Coppy" width="128" height="128">
</p>

コピーした内容を自動でカテゴリ分けして保存する Windows アプリです。

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-green.svg)
![Version](https://img.shields.io/badge/Version-1.2.0-brightgreen.svg)
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
- データ入出力
  - 履歴データの CSV 出力 / 取込
  - 定型文データの CSV 出力 / 取込
  - UTF-8 / Shift_JIS 対応
  - 定型文をすべてクリア後に取り込むオプション
- 永続保存
  - 設定 / 履歴 / 定型文を `%APPDATA%\Coppy` 配下に保存
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

### ビルド（EXE 生成）

```bash
python -m PyInstaller ClipboardHistory.spec --noconfirm
```

`dist/coppy.exe` が生成されます。

## 使い方

### 起動

```bash
python main.py
# または
dist/coppy.exe
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
- 出力 / 取込

## プロジェクト構造

```text
Coppy/
├── main.py                 # エントリーポイント
├── config.py               # 設定管理
├── database.py             # SQLite 操作
├── csv_transfer.py         # 履歴 / 定型文の CSV 出力・取込
├── categorizer.py          # ルールベース分類
├── clipboard_monitor.py    # クリップボード監視
├── startup.py              # Windows スタートアップ登録
├── create_icon.py          # アイコン生成スクリプト
├── ui/
│   ├── main_window.py      # メインウィンドウ
│   ├── detail_panels.py    # 詳細パネル
│   ├── dialogs.py          # ダイアログ
│   ├── iconography.py      # アイコンフォント
│   ├── settings_dialog.py  # 設定ダイアログ
│   ├── tray_icon.py        # システムトレイ
│   ├── widgets.py          # 共通ウィジェット
│   ├── styles.py           # テーマ / スタイル
│   └── sample_data.py      # サンプルデータ
├── resources/
│   ├── icon.ico            # アプリアイコン (ICO)
│   └── icon.png            # アプリアイコン (PNG)
├── tests/                  # テスト
├── ClipboardHistory.spec   # PyInstaller ビルド設定
├── requirements.txt
└── README.md
```

## 技術スタック

- 言語: Python 3.10+
- GUI: PyQt6
- データベース: SQLite
- ビルド: PyInstaller

## ライセンス

MIT License

## 作者

sayasaya8039

---

Built with Claude Code
