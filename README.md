# soul_autoLike
automatically tap likes on Soul APP
声明：python自学还没多久，程序比较简陋

该程序旨在实现SoulApp自动点赞，基本功能有如下：
  
  首先打开soulApp进入广场，或最新，然后开启程序 【必须先打开soul并进入广场】
  
  程序初始化，自动根据屏幕生成应该点击的坐标
  
  设定点赞数，点赞目标达到则退出程序
  
  点赞如果出现点击错误直接重启程序并进入到最新界面
  
  如果出现网络延迟（一直显示加载中），则清除当前程序，重新打开soulApp
  
注意事项：
1、必须先自行安装adb及uiautomator，如何安装请自行搜索，并确保能在cmd命令中使用所有命令，可参照https://blog.csdn.net/L_201607/article/details/78150107
2、程序运行前需先用数据线连接手机，并保证手机的usb调试已经打开，在cmd使用命令adb devices查看是否连接成功
3、进入指定页面开始运行程序
4、需要自行安装mysql数据库，并在analyze_planet.py中去修改或者运行中输入自己的用户名及密码，若不需要souler数据可忽略该步骤
5、有引入多线程点赞，但是在测试中经常出错，于是注释掉了，有人能解决这个问题嘛^_^
 
