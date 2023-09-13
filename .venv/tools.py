from asyncio.windows_events import NULL
from subprocess import check_output
import sys
import re

from bson import ObjectId
from db import database
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from time import sleep

db=database()


def gospider(url):
	try:
		new_url= "https://{}".format(url)
		r=requests.get(new_url,verify=False)
	except:
		new_url = "http://{}".format(url)
	url=new_url
	urls=[]
	data = check_output(["gospider.exe","-s" ,url ,"-t" ,"20" ,"-d", "2" ,"--sitemap" ,"--robots" ,"-w" ,"-r"])
	data = data.splitlines()
	for i in data:
		try:
			e = re.search("(?P<url>https?://[^\s]+)", str(i)).group(1).split("]")[0].split("'")[0]
			urls.append(e)
		except Exception as e:
			print(e)
	db.insert({"category":"URL Extraction","result":urls,"project":sys.argv[3]},"Result") 
	
	return urls

def recursive_gospider(url):
	all_urls = gospider(url)
	for i in all_urls:
		try:
			if url in i:
				all_urls += gospider(i)
		except Exception as e:
			print(e)
	clean_urls = []
	for i in list(set(all_urls)):
		if url in i:
			clean_urls.append(i)
	db.insert({"category":"URL Extraction","result":clean_urls,"project":sys.argv[3]},"Result") 


	return clean_urls

def subfinder(target):
    z=[]
    output = check_output(["subfinder","-d",target])
    output =  output.splitlines()
    for i in output:
        z.append(str(i.decode("utf-8")))
    db.insert({"category":"subdomains","result":z,"project":sys.argv[3]},"Result")
    
    return z

def assetfinder(target):
    z=[]
    output = check_output(["assetfinder",target])
    output =  output.splitlines()
    for i in output:
        z.append(str(i.decode("utf-8")))
    db.insert({"category":"subdomains","result":z,"project":sys.argv[3]},"Result")		
    return z

def clear_subdomains(subs):
	for sub in subs:
		subs[subs.index(sub)] = sub.split("://")[1].split("/")[0]
	return list(set(subs))

def whoisrequest(target):
	try:
		r=requests.get("https://whoisrequest.com/whois/{}".format(target))
		print(r.text)
		a = r.text.split("<pre>")[1].split("</pre>")[0].splitlines()
		db.insert({"category":"Who,is","result":a,"project":sys.argv[3]},"Result")

		return a
	except Exception as e:
		print(str(e))

def query_google(query):
	result = []
	try:
		for j in search(query, num=150, stop=150, pause=10):
			result.append(j)
	except Exception as e:
		print(e)
	return result

def google_dorking(target):
	dorks = {
	"sub_domains" : "site:*.{}".format(target),
	"directory_listing" : "site:*.{} intitle:index.of".format(target),
	"juicy_files" : "site:*.{} ext:xml | ext:conf | ext:cnf | ext:reg | ext:inf | ext:rdp | ext:cfg | ext:txt | ext:ora | ext:ini | ext:sql | ext:dbf | ext:mdb | ext:log | ext:bkf | ext:bkp | ext:bak | ext:old | ext:backup | ext:doc | ext:docx | ext:odt | ext:pdf | ext:rtf | ext:sxw | ext:psw | ext:ppt | ext:pptx | ext:pps | ext:csv ".format(target),
	"login" : "site:*.{} login".format(target),
	"admin_login" : "site:*.{} admin login".format(target),
	"phpinfo" : "site:*.{} intitle:phpinfo \"published by the PHP Group\"".format(target),
	"pastbin" : "site:pastebin.com {}".format(target),
	}
	result={}
	for dork in dorks:
		print("[+]Grabbing {}".format(dork))
		result[dork] = query_google(dorks[dork])
		sleep(20)
	db.insert({"category":"search engine","result":result,"project":sys.argv[3]},"Result")
	return result

def crt(target):
	result = []
	r = requests.get("https://crt.sh/?q=%25.{}".format(target))
	soup = BeautifulSoup(r.text,features="html.parser")
	k = soup.findAll("td")
	for i in k:
		if i is not None:
			if len(i.findAll())==0:
				if "." in i.text and ":" not in i.text:
					result.append(i.text)
					print(i.text)
	if len(result)>0:
		db.insert({"category":"subdomains","result":result,"project":sys.argv[3]},"Result")
		return result
	
	return result

def censys(target):
	result=[]
	draft ={}

	params = {
	    'resource': 'hosts',
	    'sort': 'RELEVANCE',
	    'per_page': '25',
	    'virtual_hosts': 'EXCLUDE',
	    'q': target,
	}

	r = requests.get('https://search.censys.io/_search', params=params)
	soup = BeautifulSoup(r.text,features="html.parser")
	infos = soup.findAll("div",{"class":"SearchResult"})
	for info in infos:
		draft ={}
		draft["ip"] = info.find("a").find("strong").text
		services = info.findAll("div",{"class":"service SearchResult__metadata-value"})
		details = info.find("span",{"class":"SearchResult__metadata-value detail"})
		draft["details"] = details.text.replace("\n","")
		s = []
		for service in services:
			s.append(service.find("a").text)
		draft["services"] = s
		result.append(draft)
	db.insert({"category":"search engine","result":result,"project":sys.argv[3]},"Result")

	return result

def gau(url):
	try:
		new_url= "https://{}".format(url)
		r=requests.get(new_url,verify=False)
	except Exception as e:
		open("error.txt","w").write(str(e))
		new_url = "http://{}".format(url)
	url=new_url
	output = check_output(["gau","--subs",url])
	output =  output.splitlines()
	for i in range(len(output)):
		output[i]=output[i].decode("utf-8")
	db.insert({"category":"URL Extraction 1","result":output,"project":sys.argv[3]},"Result") 

	return(output)

def subdomains(target):
	z=subfinder(target)
	k=assetfinder(target)
	x=crt(target)
	
	return print("done")




found=db.find("Tools",{"_id":ObjectId(sys.argv[1]) })
eval("{}('{}')".format(found['Toolname'],sys.argv[2]))
exit()

