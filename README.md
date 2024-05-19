# bangumi-cv-character-list  

bangumi cv character list (in descending order by time)  

读取bangumi的cv列表存在本地,为excel添加图片、超链接，默认按时间倒序

本项目request相关代码来自于 <https://github.com/jerrylususu/bangumi-takeout-py> ,相关警告请查阅该项目

**如遇网络问题请更换网络或手动删除目录下.bgm_token，网络问题与本项目无关**

**如果令牌过期（默认有效期为一周）手动删除.bgm_token**



参考时间：单人300个词条约10min

因单个样本测试周期较长，本项目还未经大量测试来提升应对api对不同项目返回多种变量类型的泛化性能，欢迎提交issue帮助改进

使用样例:(test on windows)  

功能追加：
实例：python .\main.py --id 34198  7575 --game_only 1
批量保存获取cv信息，支持仅查看游戏相关的工作（--game_only 1），默认值为0

![效果](assets/example1.png)

to do list:

因bangumi api原因大量词条出现开发项信息缺失，该问题暂时未能解决

针对多个id使用多线程并行获取信息（）
