# scheinefuervereine
Scraper für die Scheine für Vereine 2024, stündlich der JSON Output der API sowie der Spendenstand als Textdatei in einem S3 Bucket.

## Hintergrund

Einmal im Jahr veranstaltet REWE eine Spendenaktion für Vereine, dabei wird pro 15 € Einkaufswert ein Aktionscoupon ausgegeben. Dieser kann vom Kunden für den eigenen Verein eingelöst werden und dieser Verein kann davon am Ende der Aktion Prämien bestellen. 

Ich wollte für unseren Verein mal eine Übersicht haben, wie die Aktion sich entwickelt und dafür einfach täglich einmal den Stand ablegen. Dazu kam der Wunsch den aktuellen Stand auf unserer Webseite anzuzeigen, jedoch ohne die Seite einzubetten.

Der Code ist in python gehackt, wahrscheinlich nicht der optimalste Code aber das soll mich jetzt nicht stören. Für die Webseite habe ich ebenso ein einfaches PHP Plugin gebaut, dieses holt einfach den Inhalt einer angegebenen URL. 

Der Stand wird als JSON in einem S3 Bucket abgelegt, dazu nur der numerische Stand extra in einer Textdatei, diese kann zB für das Wordpress Plugin aber auch jede andere Platform genutzt werden (, sofern der Bucket public ist oder sich um Auth gekümmert wird, versteht sich).

Zusätzlich liegt jetzt auch Auswertungsscript bereit, dazu später mehr.

## Installation

Ich empfehle ein venv für Python zu nutzen, falls noch nicht geschehen kann es so installiert werden:
```bash
python3 -m pip install --user virtualenv
```

Falls noch nicht geschehen, den `.venv` Ordner anlegen und diesen aktivieren
```bash
python3 -m venv env
source .venv/bin/activate
which python
```

Zuletzt die notwendigen Pakete installieren
```bash
pip install -r requirements.txt
```

## Konfiguration

Da alles recht simpel in Python gehackt wurde, einfach in die `scrape.py` wechseln, dort die Daten des S3 Bucket einstellen, die Vereins ID eintragen und ggf die Benennung der Dateien anpassen.

## Cronjob

Crontab öffnen mit dem Editor der Wahl
```bash
crontab -e
```

Cronjob anlegen, `0 0 * * *` bedeutet [täglich um 0 Uhr ausführen](https://crontab.guru/#0_0_*_*_*).
```bash
0 0 * * * /home/USER/scheine-fuer-vereine-2024/.venv/bin/python /home/USER/scheine-fuer-vereine-2024/scrape.py >> /root/scheine/log.txt 2>&1
```

Bedenke, dass so ein Server ja auch nur ein Rechner irgendwo ist und jemand für den Traffic bezahlen muss. Sei so fair und denke daran, wenn du den Cronjob einstellst. Täglich und Stündlich sollte kein Problem sein, öfter abrufen macht keinen Sinn! 

## Wordpress

Um mit Wordpress simpel den aktuellen Stand anzuzeigen, habe ich ein kleines Wordpress Plugin geschrieben. Es ruft lediglich den Inhalt einer URL/verlinkten Datei ab und zeigt es an. 

Zur Installation einfach per FTP einen Ordner im Plugin Verzeichnis von Wordpress erstellen und die functions.php hochladen. Im Webinterface unter Plugins dann aktivieren, und in einem Beitrag einfach den Shortcode `[load_text url=…]` verwenden. 

## Auswertung

Bei uns gab es von einzelnen den Wunsch zu sehen, wie sich die Abgabe / Einlösung von Scheinen zeitlich entwickelt hat. Seitens REWE gibts diese Funktion nicht, praktischerweise gibt es aber ein S3 Bucket voller Datenpunkte. Je nach Auswertungstool müssen die Daten noch in ein anderes Format gebracht werden. Da CSV am verbreitesten ist und ehrlich gesagt die meisten Felder uninteressant sind, bietet `analyze.py` einen Download aller gescrapten Datenpunkte und fügt die Felder `timestamp, totalBalance, redeemed, Customer_Registered, WishList, availableBalance, LatestOrder, disabled` dort ein.

Viel Fehlerbehandlung gibt es nicht, da diese Auswertung auch nur einmal pro Aktion benötigt wird. Zu Anfang wird die `count.txt` aus der Liste genommen, im Durchlauf die fehlgeschlagenen Scrapes ignoriert. Wenn das Script wegen Timeouts zum S3 abbricht, muss es neu gestartet werden - sorry!