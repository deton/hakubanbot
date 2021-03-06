# ホワイトボードに文字を書くロボット

ホワイトボード前につり下げる、文字を書くロボットです。
書く文字列、大きさ、位置を、Wi-Fi経由HTTPで指示可能。

* Type1: [YouTube動画](https://youtu.be/4IXlrD8SohQ)、
  [ニコニコ動画](http://www.nicovideo.jp/watch/sm25818606)
* Type2: [YouTube動画](https://youtu.be/-9cJXXc-xhg)、
  [ニコニコ動画](http://www.nicovideo.jp/watch/sm25957377)

![hakubanbot写真(Type2)](https://github.com/deton/hakubanbot/raw/img/hakubanbot2.jpg)
![hakubanbot写真(Type1)](https://github.com/deton/hakubanbot/raw/img/hakubanbot.jpg)

## 特長
[Makelangelo](http://www.makelangelo.com/)をベースにしていますが、
以下の違いがあります。

* 書く文字を指示可能なので、
  文字を構成する線分のリストを指示するのに比べて利用が容易。漢字にも対応。
* Wi-Fi接続でHTTPで描画する文字列の指示を受け付けるので、
 * シリアル接続でコマンドを受け付けるのに比べて専用の制御用PCの設置が不要。
 * 制御用PC上でJava GUIアプリを使って操作するのに比べて、
   自動化や他サービスとの連携が容易。
* ホワイトボードイレーザ付き。文字を書く前にイレーズ可能。
* (Type1)紐でつるすゴンドラ側に全ハードウェアを持っているので、
  ホワイトボード側にモータ等を固定するのに比べて設置が容易(GarabatoBOT同様)。

## 用途
* Microsoft Exchangeサーバから各人の予定を取得して、
  罫線入り行動予定表ホワイトボードを自動更新。
  予定はExchangeに登録しているのに、ホワイトボードにも手で書くのは面倒なので。
  Aさんの予定「3/16休み」、Bさんの予定「3/17出張」等。
  ([Exchangeサーバからの予定取得](https://github.com/deton/ExchangeAppointmentBot))
* 出退勤表示の自動更新。
  PCが起動中かどうかをもとに「3/13 8:20出勤」「3/13 18:00退勤」等を書く。
  ([LED点滅](https://github.com/deton/presenceled)だけだと、
  ぱっと見ではわかりにくいので)
* 手で描いた線をそのままhakubanbotで描画するスマートフォン用アプリ。
  遠隔の(複数)ホワイトボードに字や絵を描く。
  (ただし、現状のHTTP APIは文字列指定のみなのでAPI追加要)
* ホワイトボード自動掃除機。窓ふきロボット相当。
  ただし、消去だけが目的なら、別の構造にする方が良さそう。
  ([うおーるぼっとBLE](http://wallbot.org/)等)

## ハードウェア
Type1は、GarabatoBOTを参考に作成。
3Dプリンタによる部品でなく、入手しやすい部品を使用。

* Type1: ゴンドラ側にモータ等を全て載せるタイプ。
    + 利点: 設置が容易
    + 欠点: 安定動作のためのセッティングが難しい
* Type2: ゴンドラ側にはペンとペン上げ下げ用サーボモータのみ載せるタイプ。
    + 利点: Type1に比べて、安定動作するセッティングが容易
    + 欠点: 設置が少し面倒

* (Type1)モバイルバッテリをぶらさげているのは、
  糸巻き部分がホワイトボードに平行になるようにするため。
  斜めになっていると、回転時に紐がひっかかって外れるので。

* サーボモータは両面テープで固定。
* イレーザは、ゼムクリップを切断したもので、消しゴムをサーボアームに固定。
  消しゴムにティッシュペーパやフェルト等を貼り付け。

![hakubanbot裏側写真(Type1)](https://github.com/deton/hakubanbot/raw/img/hakubanbot-back.jpg)

* (Type2.1)糸巻きから紐が外れないように、糸巻き部分にカバーを取り付けた版。
  単3電池は重し。ゴンドラが軽すぎると、イレーズができないのと、
  ペン上げ下げ時に揺れが大きくて書く線が揺れるので。

![カバー付き糸巻き](https://github.com/deton/hakubanbot/raw/img/hakubanbot2-spoolcover.jpg)

## ソフトウェア
Linino ONE(Linux+Arduino)で、HTTP受け付け(Linux)と、モータ制御(Arduino)。

    HTTP(書く文字列) → CGIスクリプト@Linux → Bridge(G-Code) → Arduino

### Linino ONEのOSを、LininoIOからLinino OSに変更

    linup latest master

LininoIOだとLinuxメインで、Linux側からMCU経由でI/O制御する形になるが、
モータドライバ等を使用する独自スケッチをArduino側で動かしたかったので。

(MCUとLinuxを仲介するbridge.pyが落ちたり、安定しない場合は、
[python-firmataとpyserialを削除する](https://groups.google.com/forum/#!msg/linino/-rSmpjX4UOM/Cnjv-uzrlfgJ)
と良いかも。)

### モータ制御
モータ制御はArduino。
[Makelangeloのfirmware_ams.inoベース](https://github.com/deton/Makelangelo)。
SerialからNC加工等で使われるG-Codeを読んで動作。

変更点:

+ SerialからG-Codeコマンドを読むかわりに、
  Linino ONEのLinux側から読むように変更(SerialをConsoleに変更等)。
+ ULN2003モータドライバに対応

### Pythonスクリプト
hakubanbot.htmlとcgi-bin/は、Linino ONEの/www/に配置。
hakubanbot/*は/usr/lib/python2.7/site-packages/hakubanbot/に配置。

* hakubanbot.html: 書く文字列を入力するFORM等。
* cgi-bin/nph-hakubanbot.py: CGIスクリプト。
  ホワイトボードの特定位置に文字を書きたい場合は、
  ホワイトボードの大きさに合わせて、XMIN等の値を変更する必要あり。
  不正確な値だと、ペン座標指定と実際の位置のずれが発生する。
  例えば、(0,0)→(0,25)→(0,0)と移動した際、元の位置に戻らず1cm程度ずれる等。
  細かい位置にこだわらなければ、適当な値でもだいたいは問題なし(例:上述の動画)。
* hakubanbot/kst2gcode.py: 指定された文字列をG-Code化。
* hakubanbot/gcode2mcu.py: G-CodeをArduino(MCU)側に送信。
* hakubanbot/eraseg.py: イレーズ動作を行うG-Codeを生成。

#### 文字のG-Code化(kst2gcode.py)
[ストロークフォントKST32B](http://www.vector.co.jp/soft/data/writing/se119277.html)
をそのままG-Code化。
[KSTストロークフォントを展開するPythonスクリプト](http://boxheadroom.com/2009/06/03/kst)
をベースに、G-Code対応。

## 部品
* [Linino ONE](http://akizukidenshi.com/catalog/g/gM-08902/)。
  Arduino+Linux。Arduino Yunの小型版。
  Wi-Fi接続できてArduinoスケッチが使えて小型。
* [ステッピングモータ(モータドライバ付き)](http://www.sengoku.co.jp/mod/sgk_cart/detail.php?code=EEHD-4JT3) 2個
* スプールというか糸巻き2個。ダイソーのクリアカラー リールホルダーを分解して
  取り出したもの。紐もそのまま使用。
  ケースも穴を開けて軸を取り除いて流用(Type2.1)。
* サーボモータ。手元にあったプチロボS2のものを流用。サーボホーンの形がT字形で、
  ペン上げとイレーザを使い分けやすいので今回の用途には便利。
* タミヤのユニバーサルプレート
* 目玉クリップ。ホワイトボードペン固定用
* ねじ8個。ステッピングモータ(Type1)や目玉クリップをユニバーサルプレートに固定。
  タミヤのユニバーサルアームセットのものを使用。
* (Type2)タミヤのユニバーサルアームセットのスペーサーQ4 4個、目玉クリップ4個。
  ステッピングモータをホワイトボード側に固定。
* はさみで切れるユニバーサル基板
* ピンソケット。ステッピングモータ接続用に最低24口
* モータ電源用USBケーブル。切断して5V電源をモータ用に接続
* Linino ONE用microUSBケーブル
* (Type1)モバイルバッテリもしくは単3形ニッケル水素充電池4本。
  USB出力2つ、Qi充電対応で、在庫処分になっていたQE-PL202を購入。

## 課題
Type1の場合、安定して自動的な書き消しができるようにするのはなかなか大変そう。
Type2にして、ホワイトボード側にステッピングモータを配置すると、
だいぶ安定して動作する印象。

* イレーズがきれいにできない。
  ホワイトボードによっては、手で消す場合も少し力を入れないといけないものがあり、
  hakubanbotでの自動イレーズがきれいにできない。少しかすれた形になる程度。
  ゴンドラ部分が軽すぎると、
  ホワイトボード上をすべるだけでイレーズができないので、
  重しとして単3電池4本を載せたが(Type2.1)、まだ軽すぎる模様。

* イレーズに時間がかかる。

* G-Codeの最適化。
  [polargraphの最適化ツール](https://github.com/ezheidtmann/polargraph-optimizer)
  と同様に、移動量やペンの上げ下げを減らす。
* 移動速度の高速化。モータ制御パラメータのチューニングや、
  polargraph同様にAccelStepperライブラリの使用等。

* (Type1)ペンの上げ下げを確実にする。
 * モバイルバッテリが先にホワイトボードに接触して、ペンが接触しない場合あり。
 * ホワイトボード上部と下部で調整し直さないと駄目な場合あり。
 * ホワイトボード端の方だとペンの上げ下げがうまくいかない場合あり。
* セッティングによっては、ゴンドラ移動時に糸巻きから糸が外れることが頻発する。
 * (Type1)モバイルバッテリが先にホワイトボードに接触して、
   糸巻きが斜めになっている場合。

## TODO
* ペン先が乾かないようキャップをはめる。描画終了時に特定位置に移動して。
  少し試してみた感じでは、
  特定位置に移動するとティッシュペーパーを当てる形にする程度で良さそう。
* ~~モバイルバッテリをQi充電できるように、描画終了時に特定位置に移動。~~
  QE-PL202は、給電中の充電に対応していない。

## 参考
* [Makelangelo](https://github.com/MarginallyClever/Makelangelo)。
  なお、kst2gcode.pyで生成したG-Codeは、Makelangeloでも描画可能なはず。
  (ペンの上げ下げは変換が必要かも)
* [GarabatoBOT](https://github.com/astromaf/GarabatoBOT)
* [polargraph](https://github.com/euphy/polargraphcontroller)
* [mDrawBotのmSpider](https://github.com/Makeblock-official/mDrawBot)
* [gocupi](https://github.com/brandonagr/gocupi)
