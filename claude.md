# 🛠️ アプリ開発ガイドライン（cloud.md）

このドキュメントは、Claudeでアプリを作成する際の標準ガイドラインです。  
Webアプリ、Chrome拡張機能、デスクトップアプリなど、あらゆる種類のアプリ開発に適用されます。

---

## 📋 基本方針

### 全体の原則
- **シンプルで分かりやすいコード**を心がける
- **日本語ユーザー**を第一に考えた設計
- **白・黒・グレー**を基調としたモノトーンデザイン
- **ダークモード / ライトモード両対応**
- 過度な装飾を避け、**機能性重視**

---

## 🎨 デザインガイドライン

### カラーパレット

```
【ライトモード】
- 背景（メイン）: #FFFFFF
- 背景（サブ）  : #F5F5F5, #EEEEEE
- テキスト（メイン）: #1A1A1A
- テキスト（サブ）  : #666666
- ボーダー: #E0E0E0, #D0D0D0
- アクセント: #333333

【ダークモード】
- 背景（メイン）: #1A1A1A
- 背景（サブ）  : #2D2D2D, #3D3D3D
- テキスト（メイン）: #F5F5F5
- テキスト（サブ）  : #A0A0A0
- ボーダー: #404040, #505050
- アクセント: #E0E0E0

【共通アクセントカラー（必要な場合のみ）】
- 成功: #4CAF50（緑）
- エラー: #F44336（赤）
- 警告: #FF9800（オレンジ）
- 情報: #2196F3（青）
```

### タイポグラフィ

```css
/* 推奨フォントスタック */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Hiragino Sans', 
             'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif;

/* フォントサイズ目安 */
- 見出し（大）: 24px - 32px
- 見出し（中）: 18px - 20px
- 本文: 14px - 16px
- 補足テキスト: 12px - 13px
```

### スペーシング

```
/* 基本単位: 4px */
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px
```

### ボーダー・角丸

```
- 角丸（小）: 4px - ボタン、入力欄
- 角丸（中）: 8px - カード、モーダル
- 角丸（大）: 12px - 大きなコンテナ
- ボーダー幅: 1px（基本）
```

### シャドウ

```css
/* ライトモード */
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

/* ダークモード */
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
```

---

## ⚛️ 技術スタック

### React（Artifacts）

```jsx
// 基本構成
import React, { useState, useEffect, useCallback, useMemo } from 'react';

// 状態管理: useState を中心に使用
const [state, setState] = useState(initialValue);

// 副作用: useEffect
useEffect(() => {
  // 処理
}, [dependencies]);

// パフォーマンス最適化（必要な場合のみ）
const memoizedValue = useMemo(() => computeValue(a, b), [a, b]);
const memoizedCallback = useCallback(() => doSomething(a), [a]);
```

### 使用可能なライブラリ（Artifacts内）

```jsx
// アイコン - Lucide React を標準使用
import { Settings, Check, X, ChevronDown, Search, Plus, Trash2 } from 'lucide-react';

// チャート（必要な場合）
import { LineChart, BarChart, PieChart, XAxis, YAxis, Tooltip } from 'recharts';

// 数学計算（必要な場合）
import * as math from 'mathjs';

// データ処理（必要な場合）
import _ from 'lodash';
```

### スタイリング - Tailwind CSS

```jsx
// 基本的なTailwindクラスを使用
// ※ カスタムカラーは使用不可、インラインstyleで対応

// ダークモード対応の例
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">

// ただしArtifactsではdark:が効かない場合があるため、
// 状態管理でテーマを切り替える方式を推奨
```

### ダークモード実装パターン

```jsx
const App = () => {
  const [isDark, setIsDark] = useState(false);
  
  // システム設定を検出（初回のみ）
  useEffect(() => {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setIsDark(true);
    }
  }, []);

  const theme = {
    bg: isDark ? '#1A1A1A' : '#FFFFFF',
    bgSub: isDark ? '#2D2D2D' : '#F5F5F5',
    text: isDark ? '#F5F5F5' : '#1A1A1A',
    textSub: isDark ? '#A0A0A0' : '#666666',
    border: isDark ? '#404040' : '#E0E0E0',
  };

  return (
    <div style={{ backgroundColor: theme.bg, color: theme.text }}>
      {/* コンテンツ */}
    </div>
  );
};
```

---

## 📝 コーディング規約

### 命名規則

```javascript
// コンポーネント: PascalCase
const UserProfile = () => { ... };
const SettingsModal = () => { ... };

// 関数・変数: camelCase
const handleClick = () => { ... };
const userName = 'さやさや';

// 定数: UPPER_SNAKE_CASE
const MAX_ITEMS = 100;
const API_ENDPOINT = 'https://...';

// ブール値: is/has/can/should プレフィックス
const isLoading = true;
const hasError = false;
const canSubmit = true;
```

### コンポーネント構成

```jsx
const ComponentName = ({ prop1, prop2 }) => {
  // 1. useState
  const [state, setState] = useState(initialValue);
  
  // 2. useMemo / useCallback（必要な場合）
  
  // 3. useEffect
  useEffect(() => {
    // 処理
  }, []);
  
  // 4. イベントハンドラ
  const handleClick = () => {
    // 処理
  };
  
  // 5. 早期リターン（ローディング、エラー等）
  if (isLoading) return <Loading />;
  
  // 6. メインのJSX
  return (
    <div>
      {/* コンテンツ */}
    </div>
  );
};
```

### JSX記述ルール

```jsx
// 条件付きレンダリング
{condition && <Component />}
{condition ? <ComponentA /> : <ComponentB />}

// リストレンダリング - 必ずkeyを付ける
{items.map((item) => (
  <Item key={item.id} data={item} />
))}

// イベントハンドラ
<button onClick={handleClick}>クリック</button>
<button onClick={() => handleDelete(id)}>削除</button>

// インラインスタイル（テーマ対応時）
<div style={{ backgroundColor: theme.bg, padding: '16px' }}>
```

---

## 🌏 日本語対応

### テキスト

```jsx
// UIテキストは全て日本語で記述
<button>保存する</button>
<label>名前を入力してください</label>
<p>データが見つかりませんでした</p>

// エラーメッセージも日本語で分かりやすく
const errorMessages = {
  required: '入力必須です',
  invalidEmail: 'メールアドレスの形式が正しくありません',
  tooLong: '文字数が上限を超えています',
  networkError: '通信エラーが発生しました。もう一度お試しください',
};
```

### 日付・数値フォーマット

```javascript
// 日付フォーマット
const formatDate = (date) => {
  return new Intl.DateTimeFormat('ja-JP', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);
};
// 結果: "2024年12月9日"

// 数値フォーマット（カンマ区切り）
const formatNumber = (num) => {
  return new Intl.NumberFormat('ja-JP').format(num);
};
// 結果: "1,234,567"

// 通貨フォーマット
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('ja-JP', {
    style: 'currency',
    currency: 'JPY',
  }).format(amount);
};
// 結果: "¥1,234"
```

---

## ⚠️ エラーハンドリング

### 基本パターン

```jsx
const App = () => {
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('データの取得に失敗しました');
      }
      const data = await response.json();
      // データ処理
    } catch (err) {
      setError(err.message || '予期せぬエラーが発生しました');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      {isLoading && <p>読み込み中...</p>}
      {error && (
        <div style={{ color: '#F44336', padding: '8px' }}>
          ⚠️ {error}
        </div>
      )}
      {/* メインコンテンツ */}
    </div>
  );
};
```

### 入力バリデーション

```jsx
const validateInput = (value, rules) => {
  const errors = [];
  
  if (rules.required && !value.trim()) {
    errors.push('入力必須です');
  }
  
  if (rules.minLength && value.length < rules.minLength) {
    errors.push(`${rules.minLength}文字以上で入力してください`);
  }
  
  if (rules.maxLength && value.length > rules.maxLength) {
    errors.push(`${rules.maxLength}文字以内で入力してください`);
  }
  
  if (rules.pattern && !rules.pattern.test(value)) {
    errors.push('形式が正しくありません');
  }
  
  return errors;
};
```

---

## ♿ アクセシビリティ（基本）

### 必須対応項目

```jsx
// 1. ボタンには適切なラベルを
<button aria-label="メニューを開く">
  <MenuIcon />
</button>

// 2. フォーム要素にはlabelを紐付け
<label htmlFor="username">ユーザー名</label>
<input id="username" type="text" />

// 3. 画像には代替テキスト
<img src="..." alt="プロフィール画像" />

// 4. キーボード操作対応
<div 
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
>

// 5. フォーカス可視化（削除しない）
// outline: none は避け、カスタムフォーカススタイルを使用
<button style={{ outline: 'none' }} className="focus:ring-2 focus:ring-gray-400">
```

---

## 📁 ファイル構成（参考）

### Chrome拡張機能

```
extension/
├── manifest.json
├── popup/
│   ├── popup.html
│   ├── popup.js
│   └── popup.css
├── content/
│   └── content.js
├── background/
│   └── background.js
├── options/
│   ├── options.html
│   └── options.js
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

### Webアプリ（単一ファイル - Artifacts用）

```jsx
// 全てを1つのファイルにまとめる
// コンポーネントは上部に定義、メインAppは最後に

// --- 共通コンポーネント ---
const Button = ({ children, onClick, variant = 'primary' }) => { ... };
const Input = ({ value, onChange, placeholder }) => { ... };
const Modal = ({ isOpen, onClose, children }) => { ... };

// --- 機能別コンポーネント ---
const Header = () => { ... };
const MainContent = () => { ... };
const Footer = () => { ... };

// --- メインApp ---
const App = () => {
  return (
    <div>
      <Header />
      <MainContent />
      <Footer />
    </div>
  );
};

export default App;
```

---

## 🔧 よく使うUIパターン

### ボタン

```jsx
const Button = ({ children, onClick, variant = 'primary', disabled = false }) => {
  const baseStyle = {
    padding: '8px 16px',
    borderRadius: '4px',
    border: 'none',
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
    transition: 'all 0.2s',
  };

  const variants = {
    primary: { backgroundColor: '#333', color: '#fff' },
    secondary: { backgroundColor: '#e0e0e0', color: '#333' },
    outline: { backgroundColor: 'transparent', border: '1px solid #333', color: '#333' },
  };

  return (
    <button
      style={{ ...baseStyle, ...variants[variant] }}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};
```

### 入力フィールド

```jsx
const Input = ({ value, onChange, placeholder, error }) => {
  return (
    <div>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        style={{
          width: '100%',
          padding: '8px 12px',
          borderRadius: '4px',
          border: `1px solid ${error ? '#F44336' : '#E0E0E0'}`,
          fontSize: '14px',
        }}
      />
      {error && (
        <p style={{ color: '#F44336', fontSize: '12px', marginTop: '4px' }}>
          {error}
        </p>
      )}
    </div>
  );
};
```

### モーダル

```jsx
const Modal = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: '#fff',
          borderRadius: '8px',
          padding: '24px',
          maxWidth: '480px',
          width: '90%',
          maxHeight: '80vh',
          overflow: 'auto',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
          <h2 style={{ margin: 0, fontSize: '18px' }}>{title}</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
            ✕
          </button>
        </div>
        {children}
      </div>
    </div>
  );
};
```

---

## ✅ チェックリスト

### 開発時の確認項目

- [ ] 日本語で分かりやすいUIテキストになっているか
- [ ] ダークモード / ライトモード両方で見た目を確認したか
- [ ] エラー時の表示・メッセージは適切か
- [ ] ボタンやリンクはクリック可能に見えるか
- [ ] 入力欄にはプレースホルダーやラベルがあるか
- [ ] ローディング状態の表示はあるか
- [ ] キーボードでの操作は可能か（基本的なもの）

### 納品前の確認項目

- [ ] コンソールにエラーが出ていないか
- [ ] 不要なconsole.logは削除したか
- [ ] コードにコメントは適切に入っているか
- [ ] 動作確認は完了したか

---

## 📝 備考

- このガイドラインは汎用的なものです。プロジェクトの要件に応じて柔軟に調整してください。
- 質問や追加要望があれば、いつでもお知らせください。

---

*最終更新: 2024年12月*
