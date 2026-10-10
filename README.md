# GYMLOG

GYMLOG は、Android 端末内で動作する筋トレ記録アプリです。Capacitor で構成したネイティブ Android アプリとして APK を生成し、ブラウザや PWA のインストール状態には依存しません。

## 主な機能

- セットごとの重量・回数の記録
- kg / lbs の切り替え
- セットの追加・削除
- 前回の重量・回数、前回メニューのコピー
- レストタイマー（30 / 60 / 90 / 120 秒、自由入力）
- 日付別のトレーニング記録
- 履歴検索・詳細表示
- 部位別の種目ライブラリ（追加・編集）
- トレーニングメニューの保存・呼び出し
- JSON バックアップ・復元
- 端末内保存
- オフライン動作

## Android アプリとしての構成

アプリ本体は `www/index.html` にあり、Capacitor の Android WebView 内でローカル実行されます。

- App ID: `com.wassanborn72.gymlog`
- App name: `GYMLOG`
- Web directory: `www`
- Android プロジェクトはビルド時に生成
- APK は GitHub Actions で自動ビルド

GitHub Pages、Service Worker、Web App Manifest などの PWA 用構成は使用しません。

## リリースビルド

GitHub Actions の **Build Android Release** を手動実行すると、署名付きの正式リリースビルドを生成します。

必要な Repository Secrets:

- `GYMLOG_KEYSTORE_BASE64`
- `GYMLOG_KEYSTORE_PASSWORD`
- `GYMLOG_KEY_ALIAS`
- `GYMLOG_KEY_PASSWORD`

ビルド成果物 `GYMLOG-v1.0.0` には、端末へ直接インストールできる `GYMLOG-v1.0.0.apk` と、Google Play 配布用の `GYMLOG-v1.0.0.aab` が含まれます。

署名鍵は今後のアップデートでも同じものを使う必要があります。キーストアとパスワードは安全な場所に保管してください。

## 開発

Node.js が利用できる環境では、以下で Android プロジェクトを生成・同期できます。

```bash
npm install
npx cap add android
npx cap sync android
npx cap open android
```

アプリ本体を変更する場合は、基本的に `www/` 以下を編集します。

## データとプライバシー

トレーニング記録はアプリ内のローカルストレージに保存され、サーバーには送信されません。

アプリのデータ消去、アンインストール、端末変更などで記録が失われる可能性があります。必要なデータはアプリ内の JSON バックアップ機能で定期的に保存してください。

## リポジトリ構成

```text
training-log/
├─ www/
│  └─ index.html
├─ assets/
│  └─ icon.svg
├─ capacitor.config.json
├─ package.json
└─ .github/
   └─ workflows/
      └─ android-apk.yml
```
