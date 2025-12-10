# Clipboard History AI

コピーした内容をAIが自動でカテゴリ分けして保存するWindowsアプリ

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 概要

クリップボードにコピーした内容を自動で監視し、ルールベース（+ オプションでAI）によるカテゴリ分類を行い、履歴として保存するシステムトレイ常駐型アプリケーションです。

## 機能

- **自動カテゴリ分類**
  - URL（http/https/file://、ドメイン形式）
  - メールアドレス
  - コード（Python、JavaScript、HTML等）
  - 電話番号
  - ファイルパス
  - 画像（サムネイル表示対応）
  - テキスト

- **AI分類（オプション）**
  - OpenAI GPT
  - Google Gemini

- **履歴管理**
  - 検索機能（インクリメンタル検索）
  - カテゴリフィルター
  - お気に入り登録
  - ワンクリックでクリップボードにコピー
  - URLクリックでブラウザ起動

- **UI**
  - システムトレイ常駐
  - ダークモード / ライトモード対応（システム設定連動）
  - 近未来的なトレイアイコン

## スクリーンショット

（準備中）

## インストール

### 必要条件

- Python 3.10以上
- Windows 10/11

### セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/sayasaya8039/Clipboard_history_AI.git
cd Clipboard_history_AI

# 依存関係をインストール
pip install -r requirements.txt
```

### AI機能を使用する場合（オプション）

1. `.env.example` を `.env` にコピー
2. 使用するAIプロバイダーのAPIキーを設定

```bash
cp .env.example .env
```

```env
# AI API設定
AI_PROVIDER=openai  # または gemini

# OpenAI API キー
OPENAI_API_KEY=sk-your-api-key

# Google Gemini API キー
GEMINI_API_KEY=your-gemini-api-key
```

## 使い方

### 起動

```bash
python main.py
```

起動するとシステムトレイにアイコンが表示されます。

### 操作方法

| 操作 | 動作 |
|------|------|
| トレイアイコン左クリック | 履歴ウィンドウを表示 |
| トレイアイコン右クリック | メニューを表示 |
| 履歴アイテムダブルクリック | クリップボードにコピー |
| URLクリック | ブラウザで開く |
| ⭐ボタン | お気に入り登録/解除 |
| 📋ボタン | クリップボードにコピー |
| 🗑ボタン | 履歴から削除 |

### 設定

トレイアイコン右クリック → 「設定」から以下を設定できます：

- AIプロバイダー（無効/OpenAI/Gemini）
- APIキー
- テーマ（システム/ライト/ダーク）

## プロジェクト構造

```
Clipboard_history_AI/
├── main.py                 # エントリーポイント
├── config.py               # 設定管理
├── database.py             # SQLite操作
├── categorizer.py          # ルールベース分類
├── ai_client.py            # AI APIクライアント
├── clipboard_monitor.py    # クリップボード監視
├── ui/
│   ├── main_window.py      # メインウィンドウ
│   ├── settings_dialog.py  # 設定ダイアログ
│   ├── tray_icon.py        # システムトレイ
│   └── styles.py           # テーマ/スタイル
├── requirements.txt
├── .env.example
└── README.md
```

## 技術スタック

- **言語**: Python 3.10+
- **GUI**: PyQt6
- **データベース**: SQLite
- **AI API**: OpenAI / Google Gemini（オプション）

## ライセンス

MIT License

## 作者

sayasaya8039

---

Built with Claude Code
