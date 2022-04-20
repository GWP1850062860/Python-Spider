import requests
import re
import csv
import pandas as pd
from bs4 import BeautifulSoup
import cn2an
import os
import time
import sys


class Novel(object):
    def __init__(self, novel_name, novel_url=""):
        """
        :param novel_name: 小说名称————必填项.  例如：逆天邪神
        :param novel_url:  小说url ————选填.  例如:https://www.quge3.com/book/1030/ 
                            tips:一般不用填写,可以自动识别并填充.
                            当你给小说名取别名时请务必附上url.
                例如：
                novel = Novel(novel_name="小三", novel_url="https://www.quge3.com/book/1030/")  
        :param kwargs: 若还有其他的参数，使用可变参数字典形式进行传递————无效,之后优化升级再说.
        :return:
        """
        print("initialization...")
        self.novel_name = novel_name
        self.novel_url = novel_url
        self.latest_chapter = None  # --str 小说章节.     ex:  逆天邪神第1936章 灾厄奏鸣
        self.latest_chapter_num = None  # --int 下载小说时马夹对应的章节数.  ex:   1936
        # sometime your latest_chapter_num != latest_html_num,  ex:1936 != 1937
        # for matching latest_chapter to download.
        self.novel_chapter_list = None  # --list 章节全部名单
        # 下载小说时填充html的数字1937 ex:下载第1936章时html实际是1937
        self.latest_html_num = None  # --str
        # history about you had created novel_name.
        self.novel_list_csv = "novel_list.csv"
        # search novel_name from www.quge3.com
        self.inquire_url = "https://www.quge3.com/s?q="
        self.__mkdir("novel_downloads")
        self.__creat_file(self.novel_list_csv)
        self.initialization = self.__initialization()

    def __initialization(self):
        ret = self.__load_url()
        if ret is False:
            """
            1.name+url
                根据url未在小说网站(www.quge3.com)中找到对应小说!
            2.name
                一般有根据用户名自动填充url失败(1.不在本地列表能找到 2.同时联网查找也找不到,也可能是request的状态码不对(没出现过))

            """
            print(".........ERROR:initialization failed..............")
            return False
        else:
            text = self.__getHTMLText(self.novel_url)
            resp_chapter = re.findall(r'<a href =.*?>(.*?)</a>', text)
            self.novel_chapter_list = resp_chapter
            self.latest_chapter = resp_chapter[-1]
            self.latest_html_num = re.findall(r'<a href ="/\w+/\w+/(\d+).html">{}</a>'.format(self.latest_chapter), text)[0]
            try:
                output = self.__cn2an_novel(self.latest_chapter)
                self.latest_chapter_num = int(re.findall(r'\d+', output)[0])
            except IndexError as e:
                print("my_warning:列表的list[0]为空.{} 原因是cn2an转换失败,只影响小说名下载格式而已！".format(e))
            except:
                print("my_error:异常: cn2an")
            # print(self.latest_chapter)
            # print(self.latest_chapter_num)
            # print(self.novel_chapter_list)
            # print(self.latest_html_num)
            print("..............loading finished!..............")
            return True

    def __load_url(self):
        # case 1: 用户自定义小说名称和url.这种情况url必给.
        #       1.1 从网站中检查用户提供的url是否有对应的小说
        if self.novel_url != "":
            status_code = self.__getUrlStatus_code(self.novel_url)
            if status_code == 200:
                pass
            elif status_code == 404:
                print("初始化失败!你提供的url不能在网站中找到对应小说!请重新赋值url")
                return False
            else:
                print("line:"+str(sys._getframe().f_lineno)+"\n初始化失败!status_code:"+str(status_code))
                return False
            # 1.2 确认url存在对应小说,开始在本地novel_list_csv中查找是否已存在用户输入的小说名.
            # 如果存在————替换小说名+更新小说的url+并将小说的阅读记录清0
            flag_ret = self.__inquire_and_deal_in_list(novel_name=self.novel_name, novel_url=self.novel_url,novel_list_csv=self.novel_list_csv)
            if flag_ret is True:
                print("msg_success:从网站(www.quge3.com)中成功找到对应小说的URL(provided by user)")
                return True
            else:
                print("line:"+str(sys._getframe().f_lineno)+"请重新提供小说的url")
                return False
        # case 2: 未提供url. 
        # ------2.1 首先本地novel_list_csv中查找novel_name.如果找到就赋值给self.novel_url用于初始化实例变量
        with open(self.novel_list_csv, "r", encoding="utf-8") as f:
            lines = csv.reader(f)
            for line in lines:
                # format: line[0] --小说名   line[1] --url   line[2] --小说上次更新记录章节
                try:
                    if line[0] == self.novel_name:
                        self.novel_url = line[1]
                        print("Found novel URL(from local),novel_url loading completed!")
                        return True
                        break
                except IndexError as e:
                    # 针对novel_list_csv中存在空白行时的出错处理.
                    print("my_error:{}".format(e))
                    self.__rm_null_line()
                    print("my_error:solve {} successfully!".format(e))
                    continue
        # ------2.2如果在本地小说列表novel_list_csv中找不到用户小说对应的url,则开始联网查找.
        try:
            # inquire_url = "https://www.quge3.com/s?q="+"小说名"
            inquire_url = self.inquire_url+self.novel_name
            resp_text = self.__getHTMLText(inquire_url)
            # 判断小说在网站中是否有.
            if not re.findall(r'<a href="/book/(.*?)">', resp_text):
                print("my_error:在www.quge3.com中,没有找到你说的小说!")
                print("自动填充URL失败!")
                print("   |___@error case:请检查你的小说名是否正确.")
                print("   |___@tips:你可以主动给小说名附上一个URL链接来创建类!(from www.quge3.com)")
                return False
            else:
                # 小说在网站中能找到,选取第一个作为我们小说的url.
                # 再将相关信息写入novel_list_csv,方便下次读取和存档.从而不需要再次进行联网查询而耗时.
                resp_url = "https://www.quge3.com/book/" + \
                    re.findall(r'<a href="/book/(.*?)">', resp_text)[0]
                self.novel_url = resp_url
                with open(self.novel_list_csv, "a+", encoding="utf-8") as f:
                    w = csv.writer(f)
                    content_temp = [self.novel_name, self.novel_url, "0"]
                    w.writerow(content_temp)
                    print("联网查找...\n===>自动找到对应小说的URL(from www.quge3.com), novel_url loading completed!")
                return True
        except:
            print("line:"+str(sys._getframe().f_lineno)+"-----URL错误!\n")
            return False

    def __mkdir(self, path):
        folder = os.path.exists("./"+path)
        if not folder:                   # 判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(path)            # makedirs 创建文件时如果路径不存在会创建这个路径
            print("---  new folder...  ---")
            print("---  OK  ---")
        else:
            pass
            # print("---  There is this folder!  ---")

    def __creat_file(self, filename):
        flag = os.path.exists("./"+filename)
        if flag is False:
            fp = open(filename, mode="w", encoding="utf-8")
            fp.close()
        else:
            pass    
            # print("filename:"+filename+" exists already!")

    def __download_tool(self, gap_num, novel_url=""):
        if novel_url == "":  # 想的是之后升级接口用,目前没有用.就当novel_url = self.novel_url来处理
            novel_url = self.novel_url
        if gap_num == 0:
            pass
            print("小说不需要下载！")
        elif gap_num >= 1:
            for i in range(1, gap_num+1, 1):
                print(i)  # 指示作用————好看!同时可以看到下载进度
                download_cursor = int(self.latest_html_num)-(i-1)
                # print(download_cursor)
                download_url = novel_url+str(download_cursor)+'.html'
                print(download_url)
                # resp = requests.get(download_url)
                resp_text = self.__getHTMLText(download_url)
                soup = BeautifulSoup(resp_text, 'lxml')
                soup.select('#chaptercontent')
                mytxt = soup.text[soup.text.find(
                    '下一章'):soup.text.rfind('『点此报错')]
                mytxt = mytxt[3:]
                mytxt = mytxt.strip()
                mytxt = mytxt.replace('　　', '\n')
                novel_save_location = "./novel_downloads/"+self.novel_name+self.__cn2an_novel(self.novel_chapter_list[-(i)]).strip()+".txt"
                with open(novel_save_location, "w", encoding='utf-8') as f:
                    f.write(mytxt)
                print("本章节下载完毕!----下载进度:"+'{:.2%}'.format(i/gap_num))
                # 避免被反爬机制针对,add delay 2s
                if i >= 10:
                    time.sleep(2)
            print("全部下载完成!我是最棒的,yeah!")
        else:
            print("invalid parameter!")

    def is_update(self):
        """
        返回值：-1  表示初始化类失败
                gap_num 更新章节数：0 --表示未更新  value --更新章节值(距离历史记录)
        """
        if self.initialization is False:
            print("my_error:initialization failed. Please create a correct class!")
            return -1
        print("____________________________________________________")
        print("Starting is_update()...                             |")
        resp_text = self.__getHTMLText(self.novel_url)
        resp_chapter = re.findall(r'<a href =.*?>(.*?)</a>', resp_text)
        print("msg:小说"+self.novel_name+",爬虫爬取的最新一章是:"+resp_chapter[-1])
        self.novel_chapter_list = resp_chapter
        self.latest_chapter = resp_chapter[-1]
        self.latest_html_num = re.findall(r'<a href ="/\w+/\w+/(\d+).html">{}</a>'.format(self.latest_chapter), resp_text)[0]
        try:
            output = self.__cn2an_novel(self.latest_chapter)
            # print(output)
            self.latest_chapter_num = int(re.findall(r'\d+', output)[0])
            # print("msg:latest_chapter_num:"+str(self.latest_chapter_num))
        except IndexError as e:
            print("my_error:列表的list[0]为空.{}".format(e))
        except:
            print("my_error:异常: cn2an")
        with open(self.novel_list_csv, "r", encoding="utf-8") as f:
            lines = csv.reader(f)
            for line in lines:
                # line[0] 小说名  line[2] 小说上次更新记录章节
                try:
                    if line[0] == self.novel_name:
                        num_record = re.findall(
                            r'\d+', self.__cn2an_novel(line[2]))[0]
                        gap_num = self.latest_chapter_num-int(num_record)  # 更新章节数
                        break
                except IndexError as e:
                    print("my_error:{}".format(e))
                    self.__rm_null_line()
                    continue

        if gap_num != 0:
            # 保存爬取到的最新的章节数  例如：第1936章 灾厄奏鸣
            print("\ndata(novel_list_csv) start writing back....")
            file = open(self.novel_list_csv, "r", encoding="utf-8")
            content = file.read()
            file.close()
            temp_old = self.novel_name+","+self.novel_url+","+line[2]
            print("msg:what is written:"+resp_chapter[-1])
            temp_new = self.novel_name+","+self.novel_url+","+resp_chapter[-1]
            content = content.replace(temp_old, temp_new)
            # print(content)
            # 通过观察print(content)的结果来看with部分的内容不能算是内部变量，在with外面也能使用（line[2]）。
            with open(self.novel_list_csv, "w", encoding='utf-8') as f:
                f.write(content)
            print("data(novel_list_csv) writing back successfully.\n")
            print("msg_success:total is "+str(gap_num)+"章更新！")
        else:
            print("小说({})尚未更新！".format(self.novel_name))
        return gap_num
  
    def download_novel(self, download_num=""):
        """
        传参值download_num:
            空  ---下载已更新章节(距离是历史记录章节)
            value ---手动下载多少章！从最后章节开始下载,(value--),直到为0.
            -1   ---下载小说全部章节
        """
        if self.initialization is False:
            print("my_error:initialization failed. Please create a correct class!")
            return -1
        if download_num == "":
            # 初始值未传递,自动下载小说最新更新章节的内容.(result = latest_chapter - num_record)
            gap_num = self.is_update()
            if gap_num != -1:
                download_num = gap_num
                self.__download_tool(download_num)
            else:
                print("line:"+str(sys._getframe().f_lineno)+"初始化类失败!")
        else:
            # 手动下载多少章！   -1  --表示所有章节全部下载
            if download_num == -1:
                self.__download_tool(self.latest_chapter_num)
            else:
                self.__download_tool(download_num)

    def __getHTMLText(self, url):
        heards = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
        }
        counter = 0
        flag = False
        while(flag is False):
            try:
                r = requests.get(url, heards)
                r.raise_for_status()
                r.encoding = r.apparent_encoding
                return r.text
            except:
                flag = False
                counter = counter + 1
                print("__getHTMLText()请求出现问题,status_code:"+str(r.status_code)+",正在自救处理...\n自救次数:"+str(counter))
                if counter <= 10:
                    time.sleep(5)
                elif counter >= 11 and counter <= 50 :
                    time.sleep(60)
                else:
                    break
                # if r.status_code == 404:
                #     return 404
                # else:
                #     print("my_error:getHTMLResp() status_code:"+str(r.status_code))
                #     return -1

    def __getUrlStatus_code(self, url):
        heards = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
        }
        r = requests.get(url, heards)
        return r.status_code

    def __inquire_and_deal_in_list(self, novel_name, novel_url, novel_list_csv):
        """
            判断小说novel_name是否在novel_list_csv已存在,如果存在,使用新的url替换已经存在的url
            存在：替换并返回True
            不存在：1.联网查找,判断小说网站中是否有这本小说,如果有则添加这组信息到novel_list_csv.返回True
                   2.联网找不到,返回False
        """
        fp = open(novel_list_csv, "r", encoding="utf-8")
        content = fp.read()  # str
        fp.close()
        new_novel_info = novel_name + "," + novel_url + ",0"
        content_temp = [novel_name, novel_url, "0"]
        # 保证小说名处于novel_list开头和中间的行首时能匹配到,同时保证小说名中不包含其他字符串.
        re_str1 = r'(^|\n){},.*,.*'.format(novel_name)
        result_temp = re.search(re_str1, content)
        if result_temp is None:
            print("line:"+str(sys._getframe().f_lineno)+". inquire_in_list(),小说不在本地列表中,开始联网查找...")
            status_code = self.__getUrlStatus_code(novel_url)
            if status_code == 200:
                print("小说已在小说网站(www.quge3.com)中找到!\nStarting write novel info to novel_list_csv...")
                with open(novel_list_csv, "w", encoding='utf-8') as f:
                    f.write(content)
                with open(novel_list_csv, "a+", newline="", encoding='utf-8') as f:
                    w = csv.writer(f, dialect="excel")
                    content_temp = [self.novel_name, self.novel_url, "0"]
                    w.writerow(content_temp)
                    # f.write(content)
                    # f.write(new_novel_info)
                    print("msg_success:(case1:)update data(novel_list_csv) successfully.")
                    return True
            else:
                print("my_error:小说未在小说网站(www.quge3.com)中找到! status_code:"+str(status_code))
                return False
        # 因为上面的匹配结果处于中间的行首时，前面会存在一个'\n',由于找不到其他办法,所有暂时先对上面的处理结果再提取一次.
        re_str2 = r'{},.*,.*'.format(novel_name)
        result = re.search(re_str2, result_temp.group(0))
        # print(result.group(0))      
        content = content.replace(result.group(0), new_novel_info)
        with open(novel_list_csv, "w", encoding='utf-8') as f:
            f.write(content) 
        print("msg_success:(case2:)update data(novel_list_csv) successfully.")
        return True

    @classmethod
    def hello(cls):
        print("i am ok")

    def __rm_null_line(self):
        # 去除csv文件的空白行
        try:
            df = pd.read_csv(self.novel_list_csv)
            df.to_csv(self.novel_list_csv, index=False)
            print("my_error:list index out of range dealed successfully!")
        except:
            pass

    def __cn2an_novel(self, str_chapter):
        re_str1 = r'第.*千.*章.*'
        re_str2 = r'第.*(百|零).*章.*'
        resp = re.search(re_str1, str_chapter)
        if resp is not None:   
            resp = re.search(re_str2, str_chapter)
            if resp is not None:
                pass
            else:
                str_chapter = str_chapter.split("千", 1)
                str_chapter = str_chapter[0] + "千零" + str_chapter[1]
        return cn2an.transform(str_chapter)


if __name__ == '__main__':

    # 小说类创建
    # novel = Novel(novel_name="逆天邪神")
    novel = Novel(novel_name="小三", novel_url="https://www.quge3.com/book/1030/")
    # novel = Novel(novel_name="小sizi", novel_url="https://www.quge3.com/book/1392/")
    # novel = Novel(novel_name="小san", novel_url="https://www.quge3.com/book/1031/") #url汉字转化失败

    # novel = Novel(novel_name="剑来")
    # novel = Novel(novel_name="我怎么还活着")
    # novel = Novel(novel_name="不存在的小说名")
    # novel = Novel(novel_name="万古神帝")
    # novel2 = Novel(novel_name="极品全能学生")
    
    # 检查是否更新
    novel.is_update()

    # 小说下载
    novel.download_novel(3)
    # novel.download_novel(-1)




