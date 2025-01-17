import time
import os
import sys
import framebuf
import network
import gc
import time
import urequests
import json
import SeniorOS
from machine import unique_id
from SeniorOS.system.devlib import *
import SeniorOS.system.log_manager as LogManager
LogManager.Output("system/core.mpy", "INFO")

# 适用于 data/ 下 .sros 扩展名文件的信息读写操作
# 将大部分使用了 init_file write_file 类函数而只对 data 文件夹下的数据作读写的代码替换为此处代码

# 初始化函数
class DataCtrl:
    # 初始化函数，传入文件夹路径
    def __init__(self,dataFolderPath): # 文件夹传参结尾必须要有反斜杠！！！
        self.data={}
        self.dataFolderPath=dataFolderPath
        LogManager.Output("SystemData initial", "INFO")
        eval("[/EnableDebugMsg('Core.DataCtrl.__init__')/]")
        for i in [f for f in os.listdir(dataFolderPath) if f.endswith('.sros')]:
            with open(dataFolderPath+i,'r',encoding='utf-8')as f:
                self.data[i.strip('.sros')]=f.read().strip('\r')
                eval("[/EnableDebugMsg('Core.DataCtrl.__init__')/]");print(self.data[i.strip('.sros')])
        # 反正几乎是内部API 所以编码 命名规则 换行符采用 自己手动改改（
        eval("[/EnableDebugMsg('Core.DataCtrl.__init__')/]")

    # 获取数据
    def GetOriginal(self,dataName):
        return self.data[dataName]
    # 写入数据
    def WriteOriginal(self,dataName,dataValue,singleUseSet=False,needReboot=False):
        if singleUseSet: # singleUseSet参数:一次性设置 不会实际写入文件 此选参为True时 needReboot不生效
            self.data[dataName]=dataValue
            return
        with open(self.dataFolderPath+dataName+'.sros','w',encoding='utf-8') as f:
            f.write(dataValue)
            self.data[dataName]=dataValue
        if not needReboot: #needReboot参数:当该值为True时 不修改实际运行值 特别适用于类似 开机需要根据config作init的程序使用
            self.data[dataName]=dataValue

    def Get(self, controls, dataName):
        ConfigRead = Data.GetOriginal(controls)
        Config=ConfigRead.split('\n')
        data=[]
        TSList2=[]
        # 遍历Config列表
        for i in range(len(Config)):
            TSList1=Config[i].split(':')
            TSList2.append(TSList1[0])
            data.append(TSList1[1])
        try: index = TSList2.index(dataName)
        except: index = 0
        if controls == "text":
            return data[index].strip("\r")
        elif controls == "list":
            return data[index].split(';')
    def Write(self, controls, dataName, dataValue):
        ConfigRead = Data.GetOriginal(controls)
        Config=ConfigRead.split('\n')
        TSList2=[]
        for i in range(len(Config)):
            TSList1=Config[i].split(':')
            TSList2.append(TSList1[0])
        try: index = TSList2.index(dataName)
        except: index = 0
        Config[index] = dataName + ":" + dataValue
        
        with open(self.dataFolderPath + 'text' + '.sros','w') as f:
            f.write('\n'.join(Config))
            self.data[controls]='\n'.join(Config)
            print(Config)
        with open(self.dataFolderPath + 'text' + '.sros','r') as f:
            print(f.read())
        return

Data=DataCtrl("/SeniorOS/data/")

# 文件/路径 格式工厂
class File_Path_Factory:

    # 将所有的斜杠替换为反斜杠 便于统一路径
    def Replace2Backslash(path):
        return path.replace("\\","/")

    # 判断文件是否存在
    # 传入一绝对路径 返回1布尔值
    def FileIsExist(filePath:str)->bool:
        filePath=File_Path_Factory.Format.Replace2Backslash(filePath)
        if filePath[-1] in os.listdir("/"+filePath[:-1]):return True
        else:return False

    # 判断路径指向的文件对象是否是目录
    # 传入一绝对路径 返回1布尔值
    def IsDir(filePath:str)->bool:
        # 检查st_mode(第一项)中文件类型位
        try:return os.stat(filePath)[0] & 0o170000 == 0o040000
        # 如异常代表路径无效或不是目录
        except:return False

# 获取日期 ByGxxk
class GetTime:
    Year=lambda:time.localtime()[0]
    Month=lambda:time.localtime()[1]
    Week=lambda:time.localtime()[6]
    Day =lambda:time.localtime()[2]
    Hour=lambda:time.localtime()[3]
    Min =lambda:time.localtime()[4]
    Sec =lambda:time.localtime()[5]

def FullCollect():
    # 反复进行collect函数直至达到极限
    # 此代码来自 TaoLiSystem
    m=gc.mem_free()
    while True:
        gc.collect()
        if m != gc.mem_free():
            m = gc.mem_free()
        else:
            return m

# 获取设备ID
def GetDeviceID(wifiStaObj=network.WLAN(network.STA_IF),
                mode=1
        ):
    if mode==0:return "".join(str(wifiStaObj.config('mac'))[2:len(str(wifiStaObj.config('mac')))-1].split("\\x"))
    elif mode==1:return "".join(str(unique_id())[2:len(str(unique_id()))-1].split("\\x"))

# 支持2算法的截图
# 分别为 直接复制缓冲区数据(CopyFrameBuf) 和 枚举缓冲区数据(Enumerate)
# 在Enumerate中 又细分为 速度优先(fast) 与 内存占用最小(ram)
# 这里Enumerate部分使用的算法取决于构建阶段 对本代码作EXPR操作时 constData["screenMethod"] 的值是 fast 还是 ram
class Screenshot:
    def CopyFramebuf(path,oledObj=__import__("SeniorOS.system.devlib")):
        bufb=bytearray(128*64)
        with open(path,"wb")as f:
            f.write(b"P4\n128 64\n")
            buf=framebuf.FrameBuffer(bufb,128,64,framebuf.MONO_HLSB)
            buf.blit(oledObj.buffer,0,0)
            f.write(bufb)
    def Enumerate(path,oledObj=__import__("SeniorOS.system.devlib")):# 以「枚举」为核心 的算法
        if eval("[/Const('screenshotMethod')/]")=="fast": # 速度优先
            with open(path, 'wb') as f:
                f.write(b'P4\n128 64\n')
                for y in range(128):
                    row_data = bytearray(8) #缓冲区
                    for x in range(64):row_data[x//8]|=(oledObj.pixel(x, y))<<7-(x%8) #循环 算偏移量 然后转格式 写到缓冲区内
                    f.write(row_data)
        elif eval("[/Const('screenshotMethod')/]")=="ram":# RAM优先
            buffer = bytearray(1024)  # 创建缓冲区
            # 获取屏幕像素状态
            for y in range(64):
                for x in range(128):
                    buffer[x//8+y*16]|=oledObj.pixel(x,y)<<7-(x%8)
            # 保存为PBM文件
            try:
                os.chdir("/SeniorOS/downloads")
            except:
                os.mkdir("/SeniorOS/downloads")
                os.chdir("/SeniorOS/downloads")
            with open('screenshot.pbm', 'wb') as f:
                # 写入PBM文件头
                f.write(b'P4\n128 64\n')
                f.write(buffer)  # 将缓冲区数据写入PBM文件

def Tree(path="/",prt=print,_tabs=0):
    lst=os.listdir(path)
    dirs=[]
    files=[]
    l=0
    for i in lst:
        pti=path+'/'+i
        if os.stat(pti)[0] & 0x4000:
            dirs.append(i)
        else:
            files.append(i)
        l+=1
    lk="├"
    ldirs=len(dirs)
    for n,i in enumerate(dirs+files,1):
        if n==l:
            lk="└"
        prt("│"*_tabs+lk+i)
        if n<ldirs:
            Tree(path+'/'+i,prt,_tabs+1)

def ListState(dispContent, selectNum):
    return (''.join([str(selectNum + 1),'/',str(len(dispContent))]))