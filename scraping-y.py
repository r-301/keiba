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
sel = []
box_list = []
box_lists = []
def scraping(url):
    html = urllib.request.urlopen(url)
    num = 0
    soup = BeautifulSoup(html,"lxml")
    sets = soup.find_all("div",class_="RaceData01")
    for se in sets:
        se = se.text
        sel.insert(0,se.split())
        fields = sel[0][2]
        field = fields[:1]
        dist = fields[1:]
    
        cli = sel[0][5]
        cli =cli[3:]
        baba = sel[0][7]
        baba =baba[3:]
        boxes = soup.find_all("tr",class_="HorseList")
        for box in boxes:
            box = box.text
            box = box.split()
            box += [field,dist,cli,baba]
            box_list.append(box)
            
    for i in box_list:
        
        if len(i) == 18:
            i.insert(8,"0")
        
        elif len(i) < 18:
            del box_list[num]
            

    num += 1
    return box_list


    
    

for url in urls:
    print(scraping(url))
col = ["着順","枠","馬番","馬名","性齢","斤量","騎手","タイム","着差","人気",
        "単勝オッズ","後3F","コーナー通過順","厩舎","馬体重（増減）","芝ダート","距離","天候","馬場"]
df = pd.DataFrame(box_list,columns=col)
print(df.head())
df.to_csv("keiba2.csv",index=False,encoding="utf-8-sig")