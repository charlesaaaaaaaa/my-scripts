* 该用例要用到chrome
## 下载chrome linux版本及对应的驱动、依赖库
```
https://gitee.com/liu-liangcheng/Tools/blob/master/google-chrome-pkg/chromedriver_linux64.zip
for i in `seq 0 2`
do
	wget https://gitee.com/liu-liangcheng/Tools/blob/master/google-chrome-pkg/google-chrome-stable_current_x86_64.rpm-0$i
done
cat google-chrome-stable_current_x86_64.rpm-0* > google-chrome-stable_current_x86_64.rpm
rm -rf google-chrome-stable_current_x86_64.rpm-0*
yum install pango.x86_64 libXcomposite.x86_64 libXcursor.x86_64 libXdamage.x86_64 libXext.x86_64 libXi.x86_64 libXtst.x86_64 cups-libs.x86_64 libXScrnSaver.x86_64 libXrandr.x86_64 GConf2.x86_64 alsa-lib.x86_64 atk.x86_64 gtk3.x86_64 -y
```

## 安装chrome
`sudo yum install google-chrome-stable_current_x86_64.rpm -y`
`unzip chromedriver_linux64.zip`
* driver放在当前目录下就可以了，尽量不要改变系统环境

## 运行Xvfb
* 这个软件是用来模拟windows浏览器的ui界面，要用到这个软件去欺骗selenium
  * selenium为linux专门开发的无头模式不好用，各种出错，所以只能用这个软件绕过selenium
* 安装：
  * `sudo yum install Xvfb`
* 启动：
  * `Xvfb -ac :7 -screen 0 1280x1024x8 -nolisten tcp &`
  * `export DISPLAY=:7`
  * 运行selenium脚本 
* 关闭：
  * `killall Xvfb`
