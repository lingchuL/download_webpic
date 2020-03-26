# -*-coding:utf-8 -*-

#关于本程序的初步想法：辅助爬虫 实现下载页面内图片的功能 未来可重复使用

#想要添加的功能：1.未来能方便地添加任意格式的代码 这很可能需要面向对象封装

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
from urllib.parse import urljoin	

import winreg
import os

i=0

#---------------------------------设置代理------------------------------------------
#通过注册表获取代理设置
def getproxyip():
	key=winreg.OpenKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
	try:
		proxy=winreg.QueryValueEx(key,"AutoConfigURL")
		ip=proxy[0]
		
		rule=re.compile(r"//.*?/")
		proxyip=rule.search(ip)
		proxyip=proxyip[0][2:-1]
		
		return proxyip
	
	except BaseException as e:
		proxyip="127.0.0.1:2080"
		print("使用默认代理")
		return proxyip


proxyip=getproxyip()
'''
if proxyip!=-1:
	proxy_dict={
		"http":"http://"+proxyip,
		"https":"https://"+proxyip
	}
else:
	proxy_dict={}
'''
proxy_dict={
	"http":"http://"+proxyip,
	"https":"https://"+proxyip
}
print(proxy_dict)
#-------------------------------------------------------------------------------------

#最基本的下载保存图片/视频操作 Original Download
# html 目标网址 （确保最后得到完整地址） | link 得到的目标文件地址（有可能是相对地址）
# type 最后要得到的文件类型 | name 最后文件名字 | num 文件名后跟的序号
# path 用于保存的文件夹
def oridown(html,link,type,name,num,path):
	global i
	global proxy_dict
	if name!="":
		imgname=name+"_"+str(i+num)+"."+type
		i+=1
	else:
		imgname=link[(link.rfind('/')+1):]
	#print(imgname)
	f=open(path+imgname,"wb+")
	#得到的有可能是相对路径 先用urllib.parse.urljoin得到绝对路径
	link=urljoin(html,link)
	header={
		"referer": html,
		"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3741.400 QQBrowser/10.5.3863.400"
	}
	img=requests.get(link,proxies=proxy_dict,headers=header)
	f.write(img.content)
	f.close()
	img.close()
	
# html 目标网址 （确保最后得到完整地址） | link 得到的目标文件地址（有可能是相对地址） 
# name 最后文件名字 | num 文件名后跟的序号 | webcontent 可选 直接传递网页源码
# path 保存文件夹
def download(html,type,name,num,path,webcontent=""):
	#f=open(r"F:\SomePythonProjects\fordownload.txt","w+",encoding="utf-8")		#规定文件的编码方式 否则无法保存源文件
	#r=requests.get(/picture/zipai/192228.html")
	
	global proxy_dict
	
	if html.startswith("//"):
		html="http:"+html
	if type=="":
		type="jpg"
	
	
	#如果链接本身就是要下载的文件 那就直接下载
	if html.endswith(type):
		print("Running 0...")
		oridown(html,html,type,name,num,path)
		
		#实际保存了1张图片 偏移量为1
		return 1
	
	#是个网址 那么就从不同地方获取图片 可以添加更多匹配方式
	else:
		if webcontent=="":
			r=requests.get(html,proxies=proxy_dict)
			soup=BeautifulSoup(r.content.decode('utf-8'),"lxml")
		else:
			soup=BeautifulSoup(webcontent,"lxml")
		
		#-----------------1 检索所有有img标签的地方 获取其src属性的链接---------------------
		print("Running 1...")
		results=soup.find_all("img")
		
		if results:
			#print(results)
			print("过程1下载中--正在下载有图片标签的文件")
			
		tq=tqdm(results,ncols=60)
		try:
			for result in tq:
				link=result['src']
				
				if link.endswith(type):
					
					oridown(html,link,type,name,num,path)
		except:
			print("过程1出现错误")

		tq.close()
		#r.close()

		#-----------------2 检索所有href属性 判断是否有(jpg)图片----------------------------
		print("Running 2...")
		
		results=soup.find_all(href=re.compile(type))
		if results:
			print("过程2下载中--正在下载所有链接中的指定文件")
		#print("Process 2 Results: ",results)
		tq=tqdm(results,ncols=60)
		try:
			for result in tq:
				link=result['href']
				if link.endswith(type):
					oridown(html,link,type,name,num,path)
		except:
			print("过程2出现错误")
		tq.close()
		#r.close()
		
		#-----------------3 有的网站会在样式表中引入图片！------------------------------------
		print("Running 3...")
		
		cssfiles=soup.find_all(href=re.compile("css"))
		#print(cssfiles)
		if cssfiles:
			print("过程3下载中--正在下载样式表中的指定文件")
		for css in cssfiles:
			csshtml=urljoin(html,css['href'])
			rcss=requests.get(csshtml,proxies=proxy_dict)
			#匹配并得到css中的文件地址
			rerule=re.compile(r"(?:url).*?\)")
			cssresults=rerule.findall(rcss.text)
			
			tq=tqdm(cssresults,ncols=60)
			for cssresult in tq:
				link=cssresult[4:-1]
				if link.endswith(type):
					#要传入csshtml 因为这里的link是相对css而言的
					oridown(csshtml,link,type,name,num,path)

			tq.close()
			rcss.close()
		
		#返回实际保存图片数量
		print("共下载",i,"份指定文件")
		
		if webcontent=="":
			r.close()
		
		return i

if __name__=="__main__":
	html=input("目标网址:")
	type=input("想要爬取的文件格式:")
	name=input("想要保存的文件名称:")
	
	picpath=r"F:\SomePythonProjects\images\\"+name
	
	if not os.path.exists(picpath):
		os.mkdir(picpath)
	picpath+=r"\\"
	
	check=download(html,type,name,0,picpath)
