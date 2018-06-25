suyun
======

Why this is called 'suyun'? What does it mean? I wrote this spider because one of my former colleagues asked me to help her. And her name is suyun. 

# How it works

It's based on scrapy and a proxy pool named [proxy_pool](https://github.com/ruxtain/proxy_pool). It runs the proxy pool locally to get free proxies and feed it to the spider through an API.

Please note that suyun is only for Amazon US. In the future I might make it be adaptive to other European countries.

# Try it out

```
# First of one, make sure you get the proxy_pool running
python proxy_pool/Run/main.py
# Then you need set up the database in settings.py
MONGO_URI = 'mongodb://localhost:27017'
MONGO_DATABASE = 'suyun'
# Run it in command line
scrapy crawl amazon
# After it's done, you can output a spreadsheet
python suyun/cook.py
```

This spider runs relatively fast and it's completely free.
