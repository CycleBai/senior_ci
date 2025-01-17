from SeniorOS.system.devlib import *
import SeniorOS.system.core as Core
import SeniorOS.system.daylight as DayLight
import SeniorOS.system.pages_manager as PagesManager
import machine
import esp32


list = [eval("[/Language('网络与时间')/]"), 
        eval("[/Language('界面与动效')/]"), 
        eval("[/Language('缓存与运存')/]"), 
        eval("[/Language('系统与设备')/]")]
tip = [eval("[/Language('联网相关设置及信息')/]"), 
       eval("[/Language('界面动效参数及设置')/]"), 
       eval("[/Language('应用缓存与设备内存')/]"), 
       eval("[/Language('系统设备信息及更新')/]")]

DayLight.UITools()
import SeniorOS.system.pages as Pages
import SeniorOS.style.port as Style
time.sleep_ms(5)

Settings0 = {
    0: Pages.WifiPages,
    1: Pages.Time,
    2: Pages.Choosewifi,
    3: Pages.AutoConnectWifi
}

Settings1 = {
    0: DayLight.LightModeSet,
    1:DayLight.LuminanceSet,
    2: DayLight.VastSea.Switch,
    3: Style.homeStyleSet,
    4: Style.barStyleSet,
    5: DayLight.About,
}

Settings2 = {
    0: Pages.Collect,
    1: Pages.Collect,
}

Settings3 = {
    0: Pages.About,
    1: Pages.About,
}

def Main():
    while not button_a.value()==0:
        settingsNum = DayLight.Select.Style2(list, tip, 18, False, "设置")
        if eval("[/GetButtonExpr('th')/]"):
            options = eval('DayLight.Select.Style1(list{}, 28, True, "选择")'.format(str(settingsNum)),
                            {'list0':['重连网络', '同步时间', '新建网络配置','自动联网配置'],
                            'list1':['日光模式','亮度调节','动效开关','桌面风格','状态栏风格' '日光引擎信息'],
                            'list2':['释放内存', '内存信息'],
                            'list3':['设备信息', '系统更新'],
                            'DayLight':DayLight}
                        )
            if settingsNum == 0:
                DayLight.VastSea.Progressive(True)
                if options == None:
                    pass
                else:
                    Settings0.get(options)()
                DayLight.VastSea.Progressive(True)
            elif settingsNum == 1:
                DayLight.VastSea.Progressive(True)
                if options == None:
                    pass
                else:
                    Settings1.get(options)()
                DayLight.VastSea.Progressive(True)
            elif settingsNum == 2:
                DayLight.VastSea.Progressive(True)
                if options == None:
                    pass
                else:
                    Settings2.get(options)()
                DayLight.VastSea.Progressive(True)
            elif settingsNum == 3:
                DayLight.VastSea.Progressive(True)
                if options == None:
                    pass
                else:
                    Settings3.get(options)()
                DayLight.VastSea.Progressive(True)
            else:
                pass