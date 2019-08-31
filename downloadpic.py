# -*-coding:utf-8 -*-

#关于本程序的初步想法：辅助爬虫 实现下载页面内图片的功能 未来可重复使用

#想要添加的功能：1.获取页面内视频地址并下载视频文件
#				2.未来能方便地添加任意格式的代码 这很可能需要面向对象封装

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
from urllib.parse import urljoin	
	
i=0

#设置代理
proxy_dict={
	"http":"http://127.0.0.1:2080",
	"https":"https://127.0.0.1:2080"
}

#最基本的下载保存图片/视频操作 Original Download
# html 目标网址 （确保最后得到完整地址） | link 得到的目标文件地址（有可能是相对地址）
# type 最后要得到的文件类型 | name 最后文件名字 | num 文件名后跟的序号
def oridown(html,link,type,name,num):
	global i
	global proxy_dict
	if name!="":
		imgname=name+"_"+str(i+num)+"."+type
		i+=1
	else:
		imgname=link[(link.rfind('/')+1):]
	#print(imgname)
	f=open(r"F:\SomePythonProjects\images\\"+imgname,"wb+")
	#得到的有可能是相对路径 先用urllib.parse.urljoin得到绝对路径
	link=urljoin(html,link)
	img=requests.get(link,proxies=proxy_dict)
	f.write(img.content)
	f.close()
	img.close()
	
# html 目标网址 （确保最后得到完整地址） | link 得到的目标文件地址（有可能是相对地址） 
# name 最后文件名字 | num 文件名后跟的序号 | webcontent 可选 直接传递网页源码
def download(html,type,name,num,webcontent=""):
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
		oridown(html,html,type,name,num)
		
		#实际保存了1张图片 偏移量为1
		return 1
	
	#是个网址 那么就从不同地方获取图片 可以添加更多匹配方式
	else:
		r=requests.get(html,proxies=proxy_dict)
		soup=BeautifulSoup(r.content.decode('utf-8'),"lxml")
		
		#-----------------1 检索所有有img标签的地方 获取其src属性的链接---------------------
		print("Running 1...")
		results=soup.find_all("img")
		
		if results:
			print("过程1下载中--正在下载有图片标签的文件")
			
		tq=tqdm(results,ncols=60)
		try:
			for result in tq:
				link=result['src']
				
				if link.endswith(type):
					
					oridown(html,link,type,name,num)
		except:
			print("过程1出现错误")

		tq.close()
		r.close()

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
					oridown(html,link,type,name,num)
		except:
			print("Process 2 Error")
		tq.close()
		r.close()
		
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
					oridown(csshtml,link,type,name,num)

			tq.close()
			rcss.close()
		
		#返回实际保存图片数量
		print(i)
		return i

if __name__=="__main__":
	html=input("目标网址:")
	type=input("想要爬取的文件格式:")
	name=input("想要保存的文件名称:")
	check=download(html,type,name,0)
