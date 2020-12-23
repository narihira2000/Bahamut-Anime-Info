import requests
from bs4 import BeautifulSoup 
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import *
import time
import csv


#建立視窗
window=tk.Tk()
window.title("動畫瘋動畫資訊 by narihira2000")
window.geometry("690x300")
window.resizable(0,0)
#window.iconbitmap("icon.ico")

#將第一頁抓下來
url = "https://ani.gamer.com.tw/animeList.php"
r = requests.get(url)
soup=BeautifulSoup(r.text,"html.parser")

#得知全部頁數
pgSel=soup.select("div.page_number a")
pageNum=(int)(pgSel[4].text)
#List初始化
animeInfo=[]
titleList=[]
viewList=[]
yearList=[]
monthList=[]
epList=[]

#將每頁中的資料抓下來並存入List
for count in range(pageNum):
    #抓取特定頁數的資料
    url = "https://ani.gamer.com.tw/animeList.php?page="+(str)(count+1)+"&c=0&sort=0"
    r = requests.get(url)
    soup=BeautifulSoup(r.text,"html.parser")
    
	#分別抓取標題、總觀看數、年份資訊、集數
    sel=soup.select("p.theme-name")
    sel2=soup.select("div.show-view-number p")
    sel3=soup.select("p.theme-time")
    sel4=soup.select("span.theme-number")
    for s in sel:
        titleList.append(s.text)
    for s2 in sel2:
        if(s2.text.find("萬")!=-1 or s2.text.find("統計中")!=-1 or s2.text.isnumeric() ):
            viewList.append(s2.text)
    for s3 in sel3:
		#因為抓下來的格式是"年份：2019/04 共10集"，因此要進行字串分割處理
        yearStr=(s3.text).split("年份：",1)
        
        yearr=yearStr[1].split("/",1)
        yearInt=(int)(yearr[0])
        
        monthInt=(int)(yearr[1])

        yearList.append(yearInt)
        monthList.append(monthInt)
    for s4 in sel4:
        epp=(s4.text).split("第",1)
        epp=epp[1].split("集",1)
        epInt=(int)(epp[0])
        
        
        epList.append(epInt)
    
#因為觀看數破萬會寫成中文(ex.2.2萬)，因此需要判斷是否有中文參雜其中並進行處理
for i in range(len(titleList)):
    avgView=0
    allView=0

	#查詢是否有"萬"字參雜其中
    s=viewList[i].find("萬")
    if(s!=-1):
		#將有"萬"字的處理成整數
        vstr=viewList[i].split("萬",1)
        vint=(float)(vstr[0])
        vint*=10000
        allView=(int)(vint)        
        avgView=(float)(vint/epList[i])

    elif(viewList[i].find("統計中")!=-1):
		#剛上架的動畫尚未有觀看數，因此要做例外處理
        allView=-1
        avgView=-1

    else:
		#低於10000觀看數的可以直接直轉換成整數
        allView=(int)(viewList[i])        
        avgView=((float)(viewList[i]))/epList[i]
    
    #將所有資料打包進animeInfo這個dict list
    animeInfo.append({"title":titleList[i],"view":allView,"year":yearList[i],"month":monthList[i],"episode":epList[i],"avgView":avgView})

#整理出不重複的年份及月份，以顯示在GUI上
yearSort=list(set(yearList))
yearSort.sort()
monthSort=list(set(monthList))
monthSort.sort()

#若在GUI上按下"重整"按鈕，即會觸發該function
def resetData():
	#先將所有結果刪除
    x=result.get_children()
    for i in x:
        result.delete(i)
	#再將抓取的資料放進要顯示的結果list中
    for i in range(len(animeInfo)):
        result.insert('',i,values=(animeInfo[i].get("title"),animeInfo[i].get("year"),animeInfo[i].get("month"),animeInfo[i].get("episode"),animeInfo[i].get("view"),(int)(animeInfo[i].get("avgView"))))
    #列出的動畫數量
    animeCountLabel=ttk.Label(window,text="目前總共有%d部動畫，列出%d部動畫　　"%(len(titleList),len(result.get_children()))).place(x=10,y=275)

    
#gui

#result為treeview，負責顯示結果
columns=("標題","年份","月份","集數","總觀看數","平均觀看數")
result=ttk.Treeview(window,height=10,columns=columns,show='headings')

titleSearchStr=tk.StringVar()
titleSerchLabel=ttk.Label(window,text="搜尋標題：").place(x=10,y=10)
titleSerchEntry=ttk.Entry(window,textvariable=titleSearchStr).place(x=75,y=10)

yearStr=tk.StringVar()
yearLabel=ttk.Label(window,text="搜尋年份：").place(x=235,y=10)
yearCombobox=ttk.Combobox(window,values=yearSort,width=5,textvariable=yearStr).place(x=300,y=10)

monthStr=tk.StringVar()
monthLabel=ttk.Label(window,text="搜尋月份：").place(x=370,y=10)
monthCombobox=ttk.Combobox(window,values=monthSort,width=4,textvariable=monthStr).place(x=435,y=10)

#若在GUI上按下"搜尋"按鈕，即會觸發該function
def search():
	#由於有三個搜尋欄位，因此針對其進行分析，若有一個欄位不為空，就進入裡面尋找
    if(titleSearchStr.get()!='' or yearStr.get()!='' or monthStr.get()!=''):
		#先將所有結果刪除
        x=result.get_children()
        for i in x:
            result.delete(i)
            
		#標題為空，年份為空，月份不為空的狀況
        if(titleSearchStr.get()=='' and yearStr.get()=='' and monthStr.get()!=''):
            for i in range(len(animeInfo)):
                if((int)(monthStr.get())==animeInfo[i].get("month")):
                    result.insert('',i,values=(animeInfo[i].get("title"),animeInfo[i].get("year"),animeInfo[i].get("month"),animeInfo[i].get("episode"),animeInfo[i].get("view"),(int)(animeInfo[i].get("avgView"))))
             
		#標題為空，年份不為空，月份為空的狀況
        elif(titleSearchStr.get()=='' and yearStr.get()!='' and monthStr.get()==''):
            for i in range(len(animeInfo)):
                if((int)(yearStr.get())==animeInfo[i].get("year")):
                    result.insert('',i,values=(animeInfo[i].get("title"),animeInfo[i].get("year"),animeInfo[i].get("month"),animeInfo[i].get("episode"),animeInfo[i].get("view"),(int)(animeInfo[i].get("avgView"))))
            
		#標題為空，年份不為空，月份不為空的狀況
        elif(titleSearchStr.get()=='' and yearStr.get()!='' and monthStr.get()!=''):
            for i in range(len(animeInfo)):
                if((int)(yearStr.get())==animeInfo[i].get("year") and (int)(monthStr.get())==animeInfo[i].get("month")):
                    result.insert('',i,values=(animeInfo[i].get("title"),animeInfo[i].get("year"),animeInfo[i].get("month"),animeInfo[i].get("episode"),animeInfo[i].get("view"),(int)(animeInfo[i].get("avgView"))))
 
		#標題不為空，年份為空，月份為空的狀況
        elif(titleSearchStr.get()!='' and yearStr.get()=='' and monthStr.get()==''):
            for i in range(len(animeInfo)):
                if(animeInfo[i].get("title").find(titleSearchStr.get())!=-1):
                    result.insert('',i,values=(animeInfo[i].get("title"),animeInfo[i].get("year"),animeInfo[i].get("month"),animeInfo[i].get("episode"),animeInfo[i].get("view"),(int)(animeInfo[i].get("avgView"))))
			
		#標題不為空，年份為空，月份不為空的狀況
        elif(titleSearchStr.get()!='' and yearStr.get()=='' and monthStr.get()!=''):
            for i in range(len(animeInfo)):
                if(animeInfo[i].get("title").find(titleSearchStr.get())!=-1 and (int)(monthStr.get())==animeInfo[i].get("month")):
                    result.insert('',i,values=(animeInfo[i].get("title"),animeInfo[i].get("year"),animeInfo[i].get("month"),animeInfo[i].get("episode"),animeInfo[i].get("view"),(int)(animeInfo[i].get("avgView"))))
 
		#標題不為空，年份不為空，月份為空的狀況
        elif(titleSearchStr.get()!='' and yearStr.get()!='' and monthStr.get()==''):
            for i in range(len(animeInfo)):
                if(animeInfo[i].get("title").find(titleSearchStr.get())!=-1 and (int)(yearStr.get())==animeInfo[i].get("year")):
                    result.insert('',i,values=(animeInfo[i].get("title"),animeInfo[i].get("year"),animeInfo[i].get("month"),animeInfo[i].get("episode"),animeInfo[i].get("view"),(int)(animeInfo[i].get("avgView"))))
 
		#標題不為空，年份不為空，月份不為空的狀況
        elif(titleSearchStr.get()!='' and yearStr.get()!='' and monthStr.get()!=''):
            for i in range(len(animeInfo)):
                if(animeInfo[i].get("title").find(titleSearchStr.get())!=-1 and (int)(yearStr.get())==animeInfo[i].get("year") and (int)(monthStr.get())==animeInfo[i].get("month")):
                    result.insert('',i,values=(animeInfo[i].get("title"),animeInfo[i].get("year"),animeInfo[i].get("month"),animeInfo[i].get("episode"),animeInfo[i].get("view"),(int)(animeInfo[i].get("avgView"))))
            
		#列出的動畫數量
        animeCountLabel=ttk.Label(window,text="目前總共有%d部動畫，列出%d部動畫　　"%(len(titleList),len(result.get_children()))).place(x=10,y=275)

	#若所有欄位為空，就呼叫resetData將資料重整
    else:
        resetData()        
 
#若在GUI上按下"匯出.csv"按鈕，即會觸發該function
def saveFile():
	#或取目前時間
    nowTime=time.strftime("%Y%m%d_%H%M%S", time.localtime())

	#使用asksaveasfilename得知存檔位置
    filename =  filedialog.asksaveasfilename(initialdir = "/",title = "儲存檔案",initialfile=nowTime+".csv",filetypes = (("csv files","*.csv"),("all files","*.*")))
       
	#進行寫檔
    with open(filename,'w',newline='',encoding='cp950',errors='ignore') as csvfile:
        writer=csv.writer(csvfile)
        writer.writerow(['標題','年份','月份','集數','總觀看數','平均觀看數'])
        for i in result.get_children():
            item_text=result.item(i,"values")
            writer.writerow(item_text)

#GUI
searchBtn=ttk.Button(window,text="搜尋",command=search).place(x=500,y=8)

resetBtn=ttk.Button(window,text="重整",command=resetData).place(x=593,y=8)

outputBtn=ttk.Button(window,text="匯出.csv",command=saveFile).place(x=590,y=271)

#treeview結果的欄位
result.column('標題',width=358,anchor='w')
result.column('年份',width=50,anchor='center')
result.column('月份',width=40,anchor='center')
result.column('集數',width=40,anchor='center')
result.column('總觀看數',width=80,anchor='center')
result.column('平均觀看數',width=80,anchor='center')
result.heading('標題',text="標題")
result.heading('年份',text="年份")
result.heading('月份',text="月份")
result.heading('集數',text="集數")
result.heading('總觀看數',text="總觀看數")
result.heading('平均觀看數',text="平均觀看數")

#將結果顯示出來
resetData()

#列出的動畫數量
animeCountLabel=ttk.Label(window,text="目前總共有%d部動畫，列出%d部動畫　　"%(len(titleList),len(result.get_children()))).place(x=10,y=275)

result.place(x=10,y=40)

#設置滑動條
vbar=ttk.Scrollbar(window,orient='vertical',command=result.yview)
result.configure(yscrollcommand=vbar.set)
vbar.place(x=660,y=39,height=229)

#排序function
def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(key=lambda t: int(t[0]), reverse=reverse)

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    tv.heading(col,
               command=lambda: treeview_sort_column(tv, col, not reverse))

#點擊除了標題以外的欄位都會進行排序
for col in columns[1:]:
    result.heading(col,text=col,command=lambda _col=col: treeview_sort_column(result, _col, False))

#運行視窗
window.mainloop()
