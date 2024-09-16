import os

import maya.cmds as cmds
import maya.mel as mel
import sys
import importlib
##自动加载脚本
#LocalRef:[C:\Program Files\Autodesk\Maya2022\Python37\Lib\site-packages\maya\app\startup]
#         [C:\Program Files\Autodesk\Maya2022\Python37\Lib\site-packages\maya\app\general\executeDroppedPythonFile.py]
def onMayaDroppedPythonFile(paths):
    #for path in paths:
    print(str(paths))
    #    cmds.evalDeferred('execfile("' + path + '")')
    pass
        

print('测试')


# 获取当前脚本文件的绝对路径
script_path = os.path.abspath(__file__)

# 获取当前脚本文件所在目录的路径
script_dir = os.path.dirname(script_path)

print(f"Script file path: {script_path}")
print(f"Script directory: {script_dir}")