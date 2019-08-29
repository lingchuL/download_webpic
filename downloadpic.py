# -*-coding:utf-8 -*-

#关于本程序的初步想法：辅助爬虫 实现下载页面内图片的功能 未来可重复使用

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
from urllib.parse import urljoin	
	
i=0

#最基本的下载保存图片/视频操作 Original Download
# html 目标网址 （确保最后得到完整地址） | link 得到的目标文件地址（有可能是相对地址）
# type 最后要得到的文件类型 | name 最后文件名字 | num 文件名后跟的序号
def oridown(html,link,type,name,num):
	global i
	if name!="":
		imgname=name+"_"+str(i+num)+"."+type
		i+=1
	else:
		imgname=link[(link.rfind('/')+1):]
	#print(imgname)
	f=open(r"F:\SomePythonProjects\images\\"+imgname,"wb+")
	#得到的有可能是相对路径 先用urllib.parse.urljoin得到绝对路径
	link=urljoin(html,link)
	img=requests.get(link)
	f.write(img.content)
	f.close()
	img.close()
	
# html 目标网址 （确保最后得到完整地址） | link 得到的目标文件地址（有可能是相对地址） | name 最后文件名字 | num 文件名后跟的序号
def download(html,type,name,num):
	#f=open(r"F:\SomePythonProjects\fordownload.txt","w+",encoding="utf-8")		#规定文件的编码方式 否则无法保存源文件
	#r=requests.get(/picture/zipai/192228.html")
	
	if html.startswith("//"):
		html="http:"+html
	if type=="":
		type="jpg"
	
	#如果链接本身就是要下载的文件 那就直接下载
	print("Running 0...")
	
	if html.endswith(type):
		oridown(html,html,type,name,num)
		
		#实际保存了1张图片 偏移量为1
		return 1
	
	#是个网址 那么就从不同地方获取图片 可以添加更多匹配方式
	else:
		
		r=requests.get(html)
		soup=BeautifulSoup(r.content.decode('utf-8'),"lxml")
		
		#1 检索所有有img标签的地方 获取其src属性的链接
		print("Running 1...")
		results=soup.find_all("img")
		
		if results:
			print("过程1下载中")
		
		for result in tqdm(results):
			link=result['src']
			
			if link.endswith(type):
				
				oridown(html,link,type,name,num)

		r.close()

		#2 检索所有href属性 判断是否有(jpg)图片
		print("Running 2...")
		
		results=soup.find_all(href=re.compile(type))
		
		for result in tqdm(results):
			link=result['href']
			if link.endswith(type):
				oridown(html,link,type,name,num)
		
		r.close()
		
		#返回实际保存图片数量
		return len(results)

if __name__=="__main__":
	html=input("目标网址:")
	type=input("想要下载的图片格式:")
	name=input("想要保存的图片名称:")
	check=downloadpic(html,type,name,0)