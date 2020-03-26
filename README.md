# download_webpic
A simple crawler which can download files of the given type(default jpg) in the given website page

Maybe useful and convenient to be add into a larger and stronger crawler code:)

It can run alone to download the files as well.

For now, there're only two methods to find files in a web page. Probably working on adding more reliable methods.

-- 2019.8.31 --
Add the third method of finding file, some pictures are loaded by css style sheets maybe for copyrights. Now the code can find them out.

-- 2019.10.9 --
Now the script will create a new folder for downloaded files, using the name you give.

-- 2020.3.26 --
Added "referer" parameter into http head, which made it possible to pass the crawler detection in some websites(Such as pixiv).
