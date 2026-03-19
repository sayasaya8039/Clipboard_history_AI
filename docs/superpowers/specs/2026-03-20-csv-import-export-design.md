# CSV Import/Export Design

**Goal:** 設定画面に既存 UI と整合する `出力/取込` タブを追加し、履歴データと定型文データを CSV で出力・取込できるようにする。

## Background

- 現在の設定ダイアログは `一般 / 履歴 / アイテム / ショートカット / 外観` の 5 タブ構成。
- 履歴データは `clipboard_history` テーブルに保存されている。
- 定型文データは `ui.main_window.MainWindow` のメモリ上でのみ管理され、再起動後に残らない。
- ユーザー要件は「設定内に出力/取込タブボタンを設置し、CSV で保存できること」。

## Scope

### In Scope

- 設定ダイアログに `出力/取込` タブを追加する
- 履歴データの CSV 出力 / 取込
- 定型文データの DB 永続化
- 定型文データの CSV 出力 / 取込
- 文字コード `UTF-8` / `Shift_JIS` の選択
- 既存設定 UI と整合するレイアウトとスタイル
- 定型文取込前の全件クリアオプション
- 設定 / 履歴 / 定型文を `%APPDATA%\\Coppy` に永続保存

### Out of Scope

- 設定値の出力 / 取込
- 画像ファイル本体のエクスポート
- 「既存データを全消去してから取込」などの破壊的操作
- 複数ファイル一括取込

## UX

- 設定ダイアログに 6 つ目のタブ `出力/取込` を追加する。
- タブ内部は既存設定ページと同じ縦積みレイアウト、見出し、区切り線、ボタンスタイルを使う。
- `履歴データ` と `定型文データ` の 2 セクションを配置する。
- 各セクションに以下を置く。
  - `CSV出力` 行: 文字コードコンボボックス + 出力ボタン
  - `CSV取込` 行: 文字コードコンボボックス + 取込ボタン
- 定型文セクションには `定型文をすべてクリア後に取り込む` トグルを置く。
- 操作完了 / 失敗は `QMessageBox` で通知する。

## Data Model

### Existing History Table

- `clipboard_history` は既存のまま使う。
- CSV 出力列:
  - `content_type`
  - `content`
  - `image_path`
  - `category`
  - `app`
  - `is_favorite`
  - `created_at`
- CSV 取込時は `content_hash` を再計算する。
- 重複判定は `content_hash` による。

### New Snippets Table

- `snippets` テーブルを追加する。
- 想定列:
  - `id INTEGER PRIMARY KEY AUTOINCREMENT`
  - `name TEXT NOT NULL`
  - `content TEXT NOT NULL`
  - `description TEXT`
  - `tags TEXT NOT NULL DEFAULT ''`
  - `favorite BOOLEAN DEFAULT FALSE`
  - `created_at DATETIME DEFAULT CURRENT_TIMESTAMP`
- `tags` はカンマ区切り文字列で保存し、UI では `list[str]` に変換する。
- 重複判定は `name + content` の組み合わせ。
- 重複時は `description`, `tags`, `favorite`, `created_at` を更新する。

## CSV Format

### History CSV

- 1 行目はヘッダー固定。
- 画像履歴は `image_path` の文字列のみを保存し、画像本体は含めない。
- `created_at` は文字列として保存し、取込時にそのまま保持する。

### Snippet CSV

- 1 行目はヘッダー固定。
- 列:
  - `name`
  - `content`
  - `description`
  - `tags`
  - `favorite`
  - `created_at`

## Error Handling

- ファイル選択キャンセル時は何もしない。
- CSV の必須列不足、デコード失敗、読み書き失敗は警告ダイアログで伝える。
- 取込完了時は `追加件数 / 更新件数 / スキップ件数` を表示する。
- `clear_existing` が有効な場合は確認ダイアログを経由し、`snippets` テーブルを空にしてから取り込む。
- 永続データの保存先は `%APPDATA%\\Coppy` とし、旧 `data/`, `images/` が存在する場合は初回起動時に移行する。
- 部分成功は許可するが、行単位で不正データはスキップする。

## Testing

- 設定ダイアログのタブ数とタブ名を更新するテストを追加する。
- `出力/取込` タブ内の主要 UI 要素の存在を検証する。
- 履歴 CSV の出力 / 取込 / 重複スキップを検証する。
- 定型文 DB 永続化を検証する。
- 定型文 CSV の出力 / 取込 / 重複更新を検証する。
- `UTF-8` と `Shift_JIS` の双方で round-trip を確認する。

## Risks

- 定型文のメモリ管理から DB 管理への移行で UI の選択状態更新に不整合が出る可能性がある。
- `Shift_JIS` で表現できない文字はエクスポート時に失敗する可能性があるため、例外を UI に返す。
- 既存ワークツリーに未整理ファイルがあるため、今回の変更対象以外は触らない。
