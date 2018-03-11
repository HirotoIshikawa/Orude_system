# Orude_system  
LineとTwitterを駆使して、部員に情報を提供  
センサーを使って部室に仲間が「おるのか？」をお知らせ!  




Raspberry piとTSL2516(照度センサー)を使用

#Orude.py  
部室が解錠、施錠した時にLineへ通知メッセージを送信  
Line notifyを使用->accesstoken取得が必要  
センサーの反応により施錠、解錠を検知->任意のメッセージをポスト    

#train_delayInformation.py  
大学周辺の電車の遅延情報を取得  
Beautiful Soupによるスクレイピング  
スクレイピング先はYahoo路線情報  
遅延を検知->TwitterとLineにメッセージをポスト  

#Weather_info.py  
大学周辺の天気予報を取得  
livedoorのapiを活用  
午前->当日の天気予報  
午後->明日の天気予報  
Twitterへのポスト
