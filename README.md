# robot

> 代码运行  
1.下载工程  
2.创建虚拟环境  
3.pip install -r config/packages.txt(安装需要用到的包)  
4.直接运行robot.py  

> exe运行  
1.pyinstaller -F -w robot.py(在dist文件夹中生成可执行文件)  
2.将exe文件放置在工作路径
3.拷贝虚拟环境venv\Lib\site-packages\cv2\opencv_videoio_ffmpeg411_64.dll到工作目录  
4.拷贝E:\software\DaHengVision\install_file\GalaxySDK\APIDll\Win64目录下DxImagePro.dll和GxIAPI.dll文件到工作目录  
5.将配置文件目录(config)拷贝到工作目录  
6.拷贝venv\Lib\site-packages\PyQt5\Qt\plugins到工作目录config文件夹中  
7.拷贝venv\Lib\site-packages\PyQt5\Qt\resources到工作目录config文件夹中  
8.拷贝venv\Lib\site-packages\PyQt5\Qt\translations到工作目录config文件夹中  
9.在cinfig目录下新建calibrate目录放置畸变校正参数模型文件  