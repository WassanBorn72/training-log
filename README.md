# GYMLOG

GYMLOG は、Android 端末でローカル動作する筋トレ記録アプリです。Capacitor を利用したネイティブ Android アプリとして構成されており、ブラウザや PWA、外部サーバーへの接続を前提とせず、オフラインで使用できます。

## リリース

現在のリリース版は **GYMLOG v1.0.0** です。

- App ID: `com.wassanborn72.gymlog`
- App name: `GYMLOG`
- Version: `1.0.0`
- Android 向け署名付き release APK / AAB
- APK: `GYMLOG-v1.0.0.apk`
- AAB: `GYMLOG-v1.0.0.aab`

APK は Android 端末への直接インストール用、AAB は Google Play での配布に利用できる形式です。

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

## アプリ構成

アプリ本体は `www/index.html` にあり、Capacitor の Android WebView 内でローカル実行されます。

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

Android プロジェクト自体はリポジトリに固定保存せず、GitHub Actions のビルド時に生成します。GitHub Pages、Service Worker、Web App Manifest などの PWA 用構成は使用していません。

## データ保存とバックアップ

トレーニング記録は Android アプリ内のローカルストレージに保存され、サーバーには送信されません。

アプリのデータ消去、アンインストール、端末変更などで記録が失われる可能性があるため、必要なデータはアプリ内の JSON バックアップ機能で保存してください。バックアップした JSON はアプリから復元できます。

## リリースビルド

GitHub Actions の **Build Android Release** を手動実行すると、署名済みの APK と AAB を生成します。

ビルドには次の Repository Secrets が必要です。

- `GYMLOG_KEYSTORE_BASE64`
- `GYMLOG_KEYSTORE_PASSWORD`
- `GYMLOG_KEY_ALIAS`
- `GYMLOG_KEY_PASSWORD`

署名用キーストアやパスワードそのものはリポジトリには保存しません。同じ App ID の GYMLOG を今後アップデートするため、署名鍵は継続して安全に保管する必要があります。

### v1.0.0 のビルド

`Build Android Release #17` で、署名付き `GYMLOG-v1.0.0.apk` と `GYMLOG-v1.0.0.aab` の生成を確認済みです。

## 開発

Node.js が利用できる環境では、以下のコマンドで Android プロジェクトを生成・同期できます。

```bash
npm install
npx cap add android
npx cap sync android
npx cap open android
```

アプリ本体の変更は基本的に `www/` 以下で行います。
