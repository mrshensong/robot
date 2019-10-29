# robot

> 代码运行  
1.下载工程  
2.创建虚拟环境  
3.pip install -r packages.txt(安装需要用到的包)  
4.直接运行robot.py  

> exe运行  
1.pyinstaller -F -w robot.py(在dist文件夹中生成可执行文件)  
2.拷贝虚拟环境venv\Lib\site-packages\cv2\opencv_videoio_ffmpeg411_64.dll文件  
3.将配置文件目录(config), 第2步中拷贝的文件, 生成的可执行文件放置于同一目录下即可运行