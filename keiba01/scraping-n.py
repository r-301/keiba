from bs4 import BeautifulSoup
import requests
import urllib.request
import pandas as pd
auth = "https://race.netkeiba.com/race/result.html"
html = requests.get("https://race.netkeiba.com/race/result.html?race_id=202005021211")
soup = BeautifulSoup(html.text,"lxml")

urls = []
for n in range(101,201):
    l = "?race_id=202005" + str(n).zfill(4)
    for i in range(1,13):
        u = auth + l + str(i).zfill(2)
        urls.append(u)

print(urls)
box_list = []
def scraping(url):
    html = urllib.request.urlopen(url)
    soup = BeautifulSoup(html,"lxml")
    
    boxes = soup.find_all("tr",class_="HorseList")
    for box in boxes:
        box = box.text
        box_list.append(box.split())

    return box_list

for url in urls:
    print(scraping(url))
col = ["着順","枠","馬番","馬名","性齢","斤量","騎手","タイム","着差","人気",
        "単勝オッズ","後3F","コーナー通過順","厩舎","馬体重（増減）"]
df = pd.DataFrame(box_list,columns=col)
print(df.head())
df.to_csv("keiba1.csv",index=False,encoding="utf-8-sig")