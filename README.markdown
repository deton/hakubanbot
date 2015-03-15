# ホワイトボードに文字を書くロボット

ホワイトボードに文字を書くロボットです。
書く文字列、大きさ、位置を、Wi-Fi経由HTTPで指示可能。

## 部品
* [Linino ONE](http://akizukidenshi.com/catalog/g/gM-08902/)。
  Arduino+Linux。Arduino Yunの小型版
* [ステッピングモータ(モータドライバ付き)](http://www.sengoku.co.jp/mod/sgk_cart/detail.php?code=EEHD-4JT3) 2個
* スプールというか糸巻き2個。ダイソーのクリアカラー リールホルダーを分解したもの
* サーボモータ。手元にあったプチロボS2のものを流用。サーボアームの形が好適。
* タミヤのユニバーサルプレート
* 目玉クリップ。ホワイトボードマーカペン固定用
* ねじ8個。ステッピングモータや目玉クリップをユニバーサルプレートに固定。
  タミヤのユニバーサルアームセットのものを使用。
* はさみで切れるユニバーサル基板
* ピンソケット。ステッピングモータ接続用に最低24口
* モータ電源用USBケーブル。切断して5V電源をモータ用に接続
* Linino ONE用microUSBケーブル
* モバイルバッテリもしくはNi-MH単3型4本。
  USB出力2つ、Qi充電対応で、在庫処分になっていたQE-PL202を購入。

## ハードウェア
GarabatoBotを参考に作成。

* モバイルバッテリをぶらさげているのは、
  糸巻き部分がホワイトボードに平行になるようにするため。
  斜めになっていると、回転時に紐がひっかかって外れるので。

* サーボモータは両面テープで固定。
* イレーザは、ゼムクリップを切断したもので、消しゴムをサーボアームに固定。
  消しゴムにティッシュペーパやフェルト等を貼り付け。

## ソフトウェア
### Linino ONEのOSを、LininoIOからLinino OSに変更

    linup latest master

LininoIOだとLinuxメインで、Linux側からMCU経由でI/O制御する形になるが、
モータドライバ等を使用する独自スケッチをArduino側で動かしたかったので。

### モータ制御
モータ制御はArduino。
[Makelangeloのfirmware_ams.inoベース](https://github.com/deton/Makelangelo)。
SerialからNC加工等で使われるG-Codeを読んで動作。

変更点:

+ SerialからG-Codeコマンドを読むかわりに、
  Linino ONEのLinux側から読むように変更(SerialをConsoleに変更等)。
+ ULN2003モータドライバに対応

### Pythonスクリプト
Linino ONEの/www/に配置。

* hakubanbot.html: 書く文字列を入力するFORM等。
* cgi-bin/nph-hakubanbot.py: CGIスクリプト。
* cgi-bin/kst2gcode.py: 指定された文字列をG-Code化。
* cgi-bin/gcode2mcu.py: G-CodeをArduino(MCU)側に送信。
* cgi-bin/eraseg.py: イレーズ用動作を行うG-Codeを生成。

#### 文字のG-Code化(kst2gcode.py)
[ストロークフォントKST32B](http://www.vector.co.jp/soft/data/writing/se119277.html)
をそのままG-Code化。
[KSTストロークフォントを展開するPythonスクリプト](http://boxheadroom.com/2009/06/03/kst)
をベースに、G-Code対応。

## TODO
* 文字列描画中に、次に書く文字をキューイングする機能。
* モバイルバッテリをQi充電できるように、描画終了時に特定位置に移動。
* ペン先が乾かないようキャップをはめる。描画終了時に特定位置に移動して。
* モータ電源用USBケーブルが抜けやすいので、ピンヘッダでなくDCジャック等にする。

## 課題
安定して自動的な書き消しができるようにするのはなかなか大変そう。

* ペンの上げ下げを確実にする。
 * モバイルバッテリが先にホワイトボードに接触して、ペンが接触しない場合あり。
 * ホワイトボード上部と下部で調整し直さないと駄目な場合あり。
 * ホワイトボード端の方だとペンの上げ下げがうまくいかない場合あり。
* イレーズに時間がかかる。

* G-Codeの最適化。
  [polargraphの最適化ツール](https://github.com/ezheidtmann/polargraph-optimizer)
  と同様に、移動量やペンの上げ下げを減らす。

## 用途
* Microsoft Exchangeサーバから各人の予定を取得して、
  予定表ホワイトボードを自動更新。
  予定はExchangeに登録しているのに、ホワイトボードも手で書くのは面倒なので。
  Aさんの予定「3/16休み」、Bさんの予定「3/17出張」等。
  ([Exchangeサーバからの予定取得](https://github.com/deton/ExchangeAppointmentBot))
* 出退勤表示の自動更新。
  PCが起動中かどうかをもとに「3/13 8:20出勤」「3/13 18:00退勤」等を書く。
  ([LED点滅](https://github.com/deton/presenceled)だけだと、
  ぱっと見ではわかりにくいので)
* 手で描いた線をそのままhakubanbotで描画するスマートフォン用アプリ。
  遠隔の(複数)ホワイトボードに字や絵を描く。

## 参考
* [Makelangelo](https://github.com/MarginallyClever/Makelangelo)。
  なお、kst2gcode.pyで生成したG-Codeは、Makelangeloでも描画可能なはず。
* [GarabatoBOT](https://github.com/astromaf/GarabatoBOT)
* [polargraph](https://github.com/euphy/polargraphcontroller)
* [gocupi](https://github.com/brandonagr/gocupi)

