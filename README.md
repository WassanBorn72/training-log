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

- App ID: `com.wassanborn72.ironlog`
- App name: `GYMLOG`
- Web directory: `www`
- Android プロジェクトはビルド時に生成
- APK は GitHub Actions で自動ビルド

GitHub Pages、Service Worker、Web App Manifest などの PWA 用構成は使用しません。

## APK の作成

`main` ブランチに対象ファイルを push すると、GitHub Actions の **Build Android APK** が実行されます。

1. GitHub の **Actions** を開く
2. **Build Android APK** の最新の成功した実行を開く
3. **Artifacts / 成果物** から `GYMLOG-apk` を取得
4. ZIP を展開
5. `GYMLOG.apk` を Android 端末にインストール

現在の配布物は GitHub Actions で生成する debug APK です。端末への直接インストールで利用できます。Google Play 等で一般配布する場合は、署名付き release APK / AAB の設定が別途必要です。

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
