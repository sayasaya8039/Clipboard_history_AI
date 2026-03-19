# CSV Import/Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 設定画面に既存 UI と整合する `出力/取込` タブを追加し、履歴データと定型文データを CSV で出力・取込できるようにする。

**Architecture:** `database.py` に定型文永続化 API を追加し、CSV 入出力は新規サービスモジュールへ分離する。設定ダイアログはそのサービスを呼び出す薄い UI 層に留め、`MainWindow` は定型文を DB から読む構成へ移す。

**Tech Stack:** Python 3.10+, PyQt6, sqlite3, csv, unittest

---

### Task 1: 設定タブ追加の失敗テスト

**Files:**
- Modify: `D:/NEXTCLOUD/Windows_app/Coppy/tests/test_settings_dialog.py`

- [ ] **Step 1: Write the failing test**

```python
def test_load_settings_adds_import_export_tab(self) -> None:
    dialog = SettingsDialog()
    tab_widget = dialog.findChild(QTabWidget, "settingsTabs")
    assert [tab_widget.tabText(index) for index in range(tab_widget.count())] == [
        "一般", "履歴", "アイテム", "ショートカット", "外観", "出力/取込",
    ]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_settings_dialog.py::SettingsDialogTests::test_load_settings_adds_import_export_tab -v`
Expected: FAIL because the tab does not exist yet.

- [ ] **Step 3: Write minimal implementation**

`ui/settings_dialog.py` に `出力/取込` タブ構築処理を追加する。

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_settings_dialog.py::SettingsDialogTests::test_load_settings_adds_import_export_tab -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_settings_dialog.py ui/settings_dialog.py
git commit -m "test: cover import export settings tab"
```

### Task 2: 定型文永続化の失敗テスト

**Files:**
- Modify: `D:/NEXTCLOUD/Windows_app/Coppy/tests/test_settings_dialog.py`
- Modify: `D:/NEXTCLOUD/Windows_app/Coppy/database.py`

- [ ] **Step 1: Write the failing test**

```python
def test_save_and_load_snippets_round_trip():
    save_snippet(...)
    snippets = list_snippets()
    assert snippets[0]["name"] == "署名"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_settings_dialog.py -k snippet -v`
Expected: FAIL because snippet storage API does not exist yet.

- [ ] **Step 3: Write minimal implementation**

`snippets` テーブル作成と CRUD 補助関数を追加する。

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_settings_dialog.py -k snippet -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add database.py tests/test_settings_dialog.py
git commit -m "feat: persist snippets in database"
```

### Task 3: CSV サービスの失敗テスト

**Files:**
- Create: `D:/NEXTCLOUD/Windows_app/Coppy/tests/test_csv_transfer.py`
- Create: `D:/NEXTCLOUD/Windows_app/Coppy/csv_transfer.py`
- Modify: `D:/NEXTCLOUD/Windows_app/Coppy/database.py`

- [ ] **Step 1: Write the failing test**

```python
def test_export_history_csv_writes_expected_headers(tmp_path):
    export_history_csv(tmp_path / "history.csv", encoding="utf-8")
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_csv_transfer.py -v`
Expected: FAIL because service module does not exist yet.

- [ ] **Step 3: Write minimal implementation**

履歴 / 定型文の CSV 出力取込関数と結果集計型を追加する。

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_csv_transfer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add csv_transfer.py database.py tests/test_csv_transfer.py
git commit -m "feat: add csv transfer service"
```

### Task 4: メインウィンドウの定型文 DB 移行

**Files:**
- Modify: `D:/NEXTCLOUD/Windows_app/Coppy/ui/main_window.py`
- Modify: `D:/NEXTCLOUD/Windows_app/Coppy/tests/test_main_window.py`

- [ ] **Step 1: Write the failing test**

```python
def test_main_window_reads_persisted_snippets():
    save_snippet(...)
    window = MainWindow()
    assert any(item["name"] == "署名" for item in window._snippet_items())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_main_window.py -k persisted_snippets -v`
Expected: FAIL because the window still uses memory-only snippets.

- [ ] **Step 3: Write minimal implementation**

`MainWindow` の定型文読込 / 追加 / 編集 / 削除 / お気に入り切替を DB ベースへ切り替える。

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_main_window.py -k persisted_snippets -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ui/main_window.py tests/test_main_window.py
git commit -m "feat: load snippets from database"
```

### Task 5: 設定ダイアログの操作接続

**Files:**
- Modify: `D:/NEXTCLOUD/Windows_app/Coppy/ui/settings_dialog.py`
- Modify: `D:/NEXTCLOUD/Windows_app/Coppy/tests/test_settings_dialog.py`

- [ ] **Step 1: Write the failing test**

```python
def test_history_export_button_invokes_csv_service():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_settings_dialog.py -k export_button -v`
Expected: FAIL because handlers are not wired.

- [ ] **Step 3: Write minimal implementation**

ファイルダイアログ、文字コードコンボ、メッセージボックス、サービス呼び出しを接続する。

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_settings_dialog.py -k export_button -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ui/settings_dialog.py tests/test_settings_dialog.py
git commit -m "feat: wire csv import export settings actions"
```

### Task 6: 総合検証

**Files:**
- Modify: `D:/NEXTCLOUD/Windows_app/Coppy/config.py`
- Modify: `D:/NEXTCLOUD/Windows_app/Coppy/README.md`

- [ ] **Step 1: Update version and docs**

`APP_VERSION` を上げ、README に CSV 出力 / 取込機能を追記する。

- [ ] **Step 2: Run targeted tests**

Run: `pytest tests/test_settings_dialog.py tests/test_csv_transfer.py tests/test_main_window.py -v`
Expected: PASS

- [ ] **Step 3: Run full test suite**

Run: `pytest -v`
Expected: PASS

- [ ] **Step 4: Run build verification**

Run: `python -m compileall .`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add config.py README.md
git commit -m "feat: add csv import export for history and snippets"
```
