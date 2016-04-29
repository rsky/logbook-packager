# logbook-packager

## これは何?

[sanaehirotaka](https://github.com/sanaehirotaka)さんの[航海日誌 (logbook-kai)](https://github.com/sanaehirotaka/logbook-kai)をOS Xのアプリケーションパッケージ(.app)にしてダブルクリックで起動できるようにするツールです。

## システム要件

* OS X
* logbook-kaiが動作するバージョンのJava
* Python 2.7+

## パッケージの作り方

```sh
$ python package.py /path/to/logbook-kai_x.y.z.zip
```

上記コマンドを実行すると *build* ディレクトリに *航海日誌* アプリケーションが作成されます。 (言語の優先順位によってはアプリケーション名が *LogBook* になります)

## ログ等の保存先

全てのファイルは *~/Library/Application Support/LogBook* ディレクトリ以下に保存されます。  
Dropbox等でログを同期するなら、ここに同期したいファイルのシンボリックリンクを作成してください。

## ライセンス

あまりこだわりはないのですが、ライセンスが明記されている方が安心なので[MITライセンス](LICENSE)とします。

## 謝辞

一提督としてlogbook-kaiの前身であるlogbook時代からお世話になっております。sanaehirotakaさんにはこの場を借りてお礼申し上げます。  
また、アイコンはlogbook-kaiに含まれる *icon.svg* を1024x1024サイズに書き出したものを使わせていただきました。
