描述
===

我用python脚本实现了fetch多个url的文本内容，并分析这些文本数据，统计出每个单词的次数，然后将结果集存在指定的目录下。

1. 显然，这是一个典型得`IO-bound`，或者`network-bound`问题，所以我们不会受限于python得GIL锁。
2. 另外，所用的urls被存在了一个文本文件中，这里我假设文本文件不会太大，也就是10多M，所以脚本一次性读取urls到内存中。
3. 程序获取到html内容后，将会对它进行简单的清洗，这里我利用`正则匹配`只提取了字符A-Za-z0-9对应的内容，可以考虑利用stopword list进行进一步清洗。

实际操作中遇到的问题：

1. 访问某些url遭遇403 Forbidden， 通过添加headers到request中，设置线程delay避免频繁访问已经解决了一部分，其余的估计得通过实现设置代理来达到。
2. 不能以url作为结果集的文件名，因为在linux下'/'不能出现在文件名中，通过hash(url)解决了这个问题。
3. 特殊字符导致结果集很丑陋，这里我只提取了字符A-Za-z0-9对应的内容来绕过问题。
4. 重复的url，或者去重问题， 没有解决。


用法
===

最简单的运行方式是：

1. 把脚本`crawl_and_word_count.py`, `run.sh`和测试数据文件`test_urls`从github上pull或者wget下来，并放到同一个文件夹下
2. 在终端运行命令

    chmod a+x run.sh

3. 在终端运行命令
 
   ./run.sh

4. 你将会在程序看到运行状况,运行完毕,你可以运行

    ls output

   这将会输出所有的结果文件


功能
===

运行`python crawl_and_word_count.py`将会输出usage，

\<urls_input_file\>: 输入文件，也即目标urls所在的文件， 注意： url必须逐行存储在文件中

\<target_dir\>: 结果集所在目录，确保该目录存在，并有相应权限

\<thread_num\>： 线程数

\<thread_delay\>： url request delay， 避免过快访问导致服务器拒绝

\<timeout\>： socket访问超时限制

1. 支持多线程， 通过参数`thread_num`设置线程数
2. 支持超时设置
3. 支持线程delay设置


不支持设置proxy
不支持提取非拉丁系的其他语言

