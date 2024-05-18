# bangumi-cv-character-list  

bangumi cv character list (in descending order by time)  

读取bangumi的cv列表存在本地,实现时间倒序 

本项目request相关代码来自于 https://github.com/jerrylususu/bangumi-takeout-py ,相关警告请查阅该项目

使用样例:(test on windows)  

python .\main.py --id 34198  

![效果](assets/example.png)

功能追加：
实例：python .\main.py --id 34198  7575 --game_only 1
批量保存获取cv信息，支持仅查看游戏相关的工作（--game_only 1），默认值为0
