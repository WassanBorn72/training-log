# GYMLOG Development Guide

GYMLOG の開発・ビルド・リリースに関する情報です。アプリ利用者向けの説明は [README.md](README.md) を参照してください。

## 技術構成

GYMLOG は Capacitor を利用した Android アプリです。アプリ本体は `www/index.html` にあり、Android WebView 内でローカル実行されます。

- App ID: `com.wassanborn72.gymlog`
- App name: `GYMLOG`
- Current version: `1.1.0`
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

### 種目メモ・履歴・タイマー

- 種目共通メモは既存の `exercises[].notes` を使用します。記録画面と種目編集画面から編集でき、シートの高さなどを次回以降も参照できます。日付ごとのメモではなく、過去の履歴にメモのスナップショットは追加しません。
- 履歴画面は日付別と種目別を切り替えられます。種目別では `exerciseId` で記録をまとめ、名称変更後も同じ種目の履歴を表示します。ID のない古い記録は保存された種目名でまとめます。履歴データ自体は変更しません。
- レストタイマーは全画面で下部ナビゲーションの上に固定表示します。時間設定は開閉式で、`ResizeObserver` により表示の高さに合わせてコンテンツ下部の余白とトースト位置を調整します。Android の safe area を含めて配置します。
- `drafts` のない旧バックアップを復元した場合は空の下書きを補完します。保存キー、App ID、バックアップのバージョンは維持します。

変更時は既存データの読み込み、メモ保存後の再読み込み、名称変更前の種目別履歴、タイマーの開始・一時停止・設定、旧バックアップの復元を確認してください。画面幅 320 / 360 / 412px と safe area のある表示で、タイマー・ナビゲーション・最下部の操作が重ならないことも確認します。Android 実機と署名済み APK / AAB の確認はリリース前に別途必要です。

上記のブラウザ確認は、Python の Playwright と `/usr/bin/chromium` がある環境で、リポジトリのルートから `python tests/check_ui.py` を実行できます。Android WebView の実機確認を代替するものではありません。

## Android リリース

GitHub Actions の **Build Android Release** を手動実行すると、署名済み APK / AAB を生成します。

現在の出力ファイル:

- `GYMLOG-v1.1.0.apk`: Android 端末への直接インストール用
- `GYMLOG-v1.1.0.aab`: Google Play 配布用

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


## v1.1.0 のリリース確認

versionCode は 2、versionName は 1.1.0 です。package.json、README、生成ファイル名、Release タグ／タイトルを揃えています。README は利用者向けに限定し、技術構成・署名・検証はこの文書で管理します。main 反映後に `gh workflow run android-apk.yml --ref main` を実行します。公開前に APK の App ID・バージョン・署名、AAB の署名、両方に含まれる HTML を検証し、v1.0.0 と署名証明書を比較します。公開後はタグのコミット、添付ファイル、README のリンクを確認します。実機での更新・キーボード・システムナビゲーションの確認は別途必要です。
