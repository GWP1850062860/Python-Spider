# Python-Spider
这里面是用python编写的爬虫神器

目前有python笔趣阁小说爬取神器1.0，位于位于novel-1.0下。

[TOC]

## python笔趣阁小说爬取神器1.0

支持内容：

### 1.抓取小说

- 采用"小说名"来直接抓取小说——覆盖范围：笔趣阁全部小说。

- 采用"小说名+小说URL"来抓取小说，小说名可以是你小说的别称。例如："逆天邪神"改为"小三"。

  tips：此方式是以url为主要判别标准。

### 2.检查小说是否更新

- 如果有更新，显示更新情况。

  ```python
  # 检查是否更新
  novel.is_update()
  ```

  

### 3.下载小说内容到本地

- 支持只下载更新内容

  ```python
  # 小说下载——下载最新更新章节（本地对上次你看的最新章节数会有历史记录）
  novel.download_novel()
  ```

- 支持自定义下载章节数

  ```python
  # 小说下载——下载最新的3章
  novel.download_novel(3)
  ```

- 支持全本下载

  ```python
  novel.download_novel(-1)  # -1  ——表示下载全本小说
  ```

  

### example1——采用"小说名"

小说"逆天邪神"爬取日志：

```python
if __name__ == '__main__':   
    # 小说类创建
    novel = Novel(novel_name="逆天邪神")

    # 检查是否更新
    novel.is_update()

    # 小说下载——下载最新的3章
    novel.download_novel(3)
```

```
打印内容：
initialization...
---  new folder...  ---
---  OK  ---
联网查找...
===>自动找到对应小说的URL(from www.quge3.com), novel_url loading completed!
..............loading finished!..............
____________________________________________________
Starting is_update()...                             |
msg:小说逆天邪神,爬虫爬取的最新一章是:第1936章 灾厄奏鸣

data(novel_list_csv) start writing back....
msg:what is written:第1936章 灾厄奏鸣
data(novel_list_csv) writing back successfully.

msg_success:total is 1936章更新！
1
https://www.quge3.com/book/1030/1937.html
本章节下载完毕!----下载进度:33.33%
2
https://www.quge3.com/book/1030/1936.html
本章节下载完毕!----下载进度:66.67%
3
https://www.quge3.com/book/1030/1935.html
本章节下载完毕!----下载进度:100.00%
全部下载完成!我是最棒的,yeah!
[Finished in 11.4s]
```

### example1——采用"小说名"+"小说URL"

此URL内容实际上是"逆天邪神"的内容

```python
if __name__ == '__main__':   
    # 小说类创建——此URL内容实际上是"逆天邪神"的内容
    novel = Novel(novel_name="小三", novel_url="https://www.quge3.com/book/1030/")

    # 检查是否更新
    novel.is_update()

    # 小说下载——下载最新的3章
    novel.download_novel(3)
```

```
initialization...
line:330. inquire_in_list(),小说不在本地列表中,开始联网查找...
小说已在小说网站(www.quge3.com)中找到!
Starting write novel info to novel_list_csv...
msg_success:(case1:)update data(novel_list_csv) successfully.
msg_success:从网站(www.quge3.com)中成功找到对应小说的URL(provided by user)
..............loading finished!..............
____________________________________________________
Starting is_update()...                             |
msg:小说小三,爬虫爬取的最新一章是:第1936章 灾厄奏鸣
my_error:list index out of range
my_error:list index out of range dealed successfully!

data(novel_list_csv) start writing back....
msg:what is written:第1936章 灾厄奏鸣
data(novel_list_csv) writing back successfully.

msg_success:total is 1936章更新！
1
https://www.quge3.com/book/1030/1937.html
本章节下载完毕!----下载进度:33.33%
2
https://www.quge3.com/book/1030/1936.html
本章节下载完毕!----下载进度:66.67%
3
https://www.quge3.com/book/1030/1935.html
本章节下载完毕!----下载进度:100.00%
全部下载完成!我是最棒的,yeah!
[Finished in 18.5s]
```

欢迎使用！

交流邮箱：

x131421gwp@outlook.com

gwp5132@163.com

