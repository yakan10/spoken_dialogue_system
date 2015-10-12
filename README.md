# Speech Dialogue System

無料ツールを駆使した他力本願音声対話システムです  

## 動作環境
Mac OS X 10.9.5  
python2.7.5

## 構成

以下のシステムが直列に動作します

* 音声認識システム
  * Google Speech API
  * Julius
* 対話生成システム
  * docomo 雑談対話API
* 音声合成システム
  * MacOSX付属のsayコマンド

システムは増やす予定...

## 事前準備

色々登録したりダウンロードしたり面倒くさいですが  
タダで使えるからと割り切って頑張ってください

### オーディオ設定
* マイク入力確認  
Macならシステム環境設定>サウンド>入力 から確認できます  
Windowsなら右下のスピーカアイコンを右クリック>録音デバイスから確認  
マイクを接続して、音量バーが触れていることを確認してください
* オーディオ再生確認  
Macならシステム環境設定>サウンド>出力 から確認できます  
Windowsなら右下のスピーカアイコンを右クリック>再生デバイスから確認  
適当に音楽など流して、音量バーが触れていることを確認してください

### Google Speech API
* APIキーの入手  
<http://qiita.com/mountcedar/items/be1e5d54fcef8f3a4bda>などが参考になります  
取得したAPIキーは、gapi.pyの14行目のAPI_KEY変数にセットしてください  
* soxのインストール  
音声ファイルの形式を変換するソフトです  
brewやらapt-getやらでインストールして下さい  
wav形式 &amp; flac形式が扱えるもの必須です
* pythonライブラリのインストール  
`sudo pip install pyaudio`

### Julius
* ディクテーションキットのダウンロード  
<http://julius.osdn.jp/index.php?q=dictation-kit.html>から自分のOSに合ったものをダウンロード・解凍してください
* run-gmm.shをモジュールモードに書き換え  
run-gmm.shを以下のように書き換えます  
`./bin/julius -C main.jconf -C am-gmm.jconf -demo $*`  
↓  
`./bin/julius -C main.jconf -C am-gmm.jconf -demo -module $*`  
「-module」というオプションが増えただけです

### docomo 雑談対話API
* APIキーの入手  
<https://dev.smt.docomo.ne.jp/?p=index>から新規登録して適当なAPIを作成、キーを入手しましょう  
取得したAPIキーは、docomo_chat.pyの7行目のAPI_KEY変数にセットしてください

### MacOSX付属のsayコマンド
* 音声合成のセットアップ  
システム環境設定>音声入力と読み上げ>テキスト読み上げ>システムの声  
「カスタマイズ」を選択  
日本語（日本）の「Kyoko」「Otoya」を選択  
ダウンロードが始まるのでしばらく待つ  
システムの声で「Kyoko」か「Otoya」を選択  


## 実行

### とりあえず実行
`python main.py`  
で、音声認識が始まります。  
音声を検知すると音声認識が開始し、認識結果が雑談対話に飛び、返答を音声合成システムが読み上げます。  
デフォルトでは、Google, docomo雑談, MacOSX合成 が動作します

### APIの選択
main.pyのオプションで、使うAPIを選択できます。  

* 音声認識  
-r google ... Google Speech API  
-r julius ... Julius※使うときは予め別ウィンドウで./run-gmm.shを叩いてJuliusを起動してください
* 雑談対話  
-d docomo ... ドコモの雑談対話  
* 音声合成  
-s say    ... MacOSXの音声合成

### Tips
* Google Speech APIでは動作ディレクトリ直下にaudio/というディレクトリが自動作成され、そこに音声ファイルが溜まります。  
適宜削除してください。
* Julius音声認識を使う場合は雑音にかなり弱いので静かなところで実験してください
* ラズパイではJuliusの./run-gmm.shで動作する大語彙連続音声認識はめちゃくちゃ遅いです。単語認識か文法認識がオススメです。

## 参考
* Juliusの音声認識の叩き方  
[ラズパイで作ろう！ ゼロから学ぶロボット製作教室](
http://itpro.nikkeibp.co.jp/atcl/column/15/040800081/)