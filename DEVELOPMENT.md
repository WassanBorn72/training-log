# GYMLOG Development Guide

GYMLOG の開発・ビルド・リリースに関する情報です。アプリ利用者向けの説明は [README.md](README.md) を参照してください。

## 技術構成

GYMLOG は Capacitor を利用した Android アプリです。アプリ本体は `www/index.html` にあり、Android WebView 内でローカル実行されます。

- App ID: `com.wassanborn72.gymlog`
- App name: `GYMLOG`
- Current version: `1.0.0`
- Web directory: `www`
- Capacitor: 8.x
- Android プロジェクトはビルド時に生成

GitHub Pages、Service Worker、Web App Manifest などの PWA 用構成は使用していません。

## リポジトリ構成

```text
training-log/
├─ www/
│  └─ index.html
├─ assets/
│  └─ icon.svg
├─ capacitor.config.json
├─ package.json
├─ README.md
├─ DEVELOPMENT.md
└─ .github/
   └─ workflows/
      └─ android-apk.yml
```

## ローカル開発

Node.js が利用できる環境では、以下のコマンドで Android プロジェクトを生成・同期できます。

```bash
npm install
npx cap add android
npx cap sync android
npx cap open android
```

アプリ本体の変更は基本的に `www/` 以下で行います。

## データ保存

トレーニングデータは WebView の localStorage に保存しています。

内部ストレージキー `ironlog-v1` は旧名称から引き継いだデータ形式との互換性維持のため、そのまま使用しています。表示上のアプリ名は GYMLOG です。

バックアップは JSON 形式でエクスポート・インポートできます。

## Android リリース

GitHub Actions の **Build Android Release** を手動実行すると、署名済み APK / AAB を生成します。

現在の出力ファイル:

- `GYMLOG-v1.0.0.apk`: Android 端末への直接インストール用
- `GYMLOG-v1.0.0.aab`: Google Play 配布用

ビルド完了後、Actions artifact に保存するとともに GitHub Release に公開します。

## 署名

リリースビルドには以下の GitHub Actions Repository Secrets が必要です。

```text
GYMLOG_KEYSTORE_BASE64
GYMLOG_KEYSTORE_PASSWORD
GYMLOG_KEY_ALIAS
GYMLOG_KEY_PASSWORD
```

署名用 `.jks`、Base64 化した鍵、パスワードなどの秘密情報はリポジトリへコミットしないでください。

同じ App ID のアプリを将来アップデートするには同じ署名鍵が必要です。キーストアと認証情報は、GitHub とは別の安全な場所にもバックアップしてください。

## GitHub Actions

ワークフロー:

```text
.github/workflows/android-apk.yml
```

**Build Android Release** は次の処理を行います。

1. Node.js / Java 環境を準備
2. Capacitor Android プロジェクトを生成
3. Android アイコンを生成
4. Web アプリを同期
5. Repository Secrets から署名鍵を復元
6. versionCode / versionName と release signing を設定
7. APK / AAB を release build
8. Actions artifact を保存
9. GitHub Release に APK / AAB を公開

## バージョン更新時

新しいバージョンをリリースする際は、少なくとも Android の `versionCode`、`versionName`、生成ファイル名、GitHub Release のタグ・タイトル、および README のバージョン表記を更新してください。

現在はこれらの一部をワークフロー内で指定しています。
