**ioc_tweet**  
This script allows you to gather Indicator of Compromise (IoCs) from Twitter and send them to MISP
for Threat Intelligence analysis. The script uses the [Tweepy](https://docs.tweepy.org) and [PyMISP](https://github.com/MISP/PyMISP) 
Python libraries.

The script needs the following configuration:
* config->**config.ini**: Twitter API configuration, MISP url and MISP API key.
* config->**keywords.txt**: The terms that you to want to monitor on Twitter.
* config->**filters.txt**: The filters for avoiding false positives in your alerts. The script
checks if the tweets gathered contain any of these keywords.

**How it works?**

It's very simple.

1) The script reads your keywords.txt file, and it searches the keywords of the file 
   one by one on Twitter.

2) If you have **typed -a option**, the script will read your filters.txt file, and it will
check if the tweets gathered contain any of your filters. 

3) If you have typed **-m option together with -a**, you will send the alerts to
your MISP instance.
   
**Usage**

Gathering IoCs on Twitter.
```bash 
python main.py
```
Output example
``` bash
[*] Searching IoC's on Twitter:
[*] Checking if the tweets gathered contain any keyword of your list.
[+] Tweet containing: opendir
	[!] Tweet by beefyspace on 2021-05-17 08:17:14:
	[!] #phishing
	[!] #opendir
	[!] #fastdomain
	[!]Tweet content:
		RT @ecarlesi: Possible threat on hxxps://goldfieldcatering[.]com/wordpress-5[.]7[.]1[.]zip #phishing #opendir  #fastdomain
[*] Number of tweets gathered: 1
```
Gathering IoCs on Twitter and checking if there are tweets containing any of your filters words.
```bash 
python main.py -a
```
Output example (same as above)
``` bash
[*] Searching IoC's on Twitter:
[*] Checking if the tweets gathered contain any keyword of your list.
[+] Tweet containing: opendir
	[!] Tweet by beefyspace on 2021-05-17 08:17:14:
	[!] #phishing
	[!] #opendir
	[!] #fastdomain
	[!]Tweet content:
		RT @ecarlesi: Possible threat on hxxps://goldfieldcatering[.]com/wordpress-5[.]7[.]1[.]zip #phishing #opendir  #fastdomain
[*] Number of tweets gathered: 1
```
Sending alerts detected to **your MISP instance**.

```bash 
python main.py -a -m
```
``` bash
[*] Searching IoC's on Twitter:
[*] Checking if the tweets gathered contain any keyword of your list.
[+] Tweet containing: opendir
	[!] Tweet by beefyspace on 2021-05-17 08:17:14:
	[!] #phishing
	[!] #opendir
	[!] #fastdomain
	[!]Tweet content:
		RT @ecarlesi: Possible threat on hxxps://goldfieldcatering[.]com/wordpress-5[.]7[.]1[.]zip #phishing #opendir  #fastdomain
[*] Number of tweets gathered: 1
[*] Sending alerts to MISP
	 [*] Event with ID 1355 has been successfully stored.

```