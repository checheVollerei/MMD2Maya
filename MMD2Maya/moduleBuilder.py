# -*- encoding: utf-8 -*-

import os
import sys
import shutil
import maya.cmds as cmds

class module:

    def __init__(self,name='Name',path='Path'):
        self.Entry={
                    'MAYAVERSION':None,
                    'PLATFORM':None,
                    'LOCALE':None
                    }
        self.additional=[]
        self.ModuleName=name
        self.ModuleVersion='0.0'
        self.ModulePath=path
    def setEntry(self,line1):
        subEn=line1.split()
        for en in range(1,len(subEn)-3):
            sen=subEn[en].split(':')
            self.Entry[sen[0]]=sen[1]
            print(subEn[en].split(':'))
        self.ModuleName=subEn[len(subEn)-3]
        self.ModuleVersion=subEn[len(subEn)-2]
        self.ModulePath=subEn[len(subEn)-1]
        print(str(self.Entry))
    def setAdditional(self,Desc):
        if Desc==[]:
            self.additional.append('')
        else:
            self.additional.append(Desc)
    def setVersion(self,ves):
        self.Entry['MAYAVERSION']=ves
    def setPlatform(self,PF):
        self.Entry['PLATFORM']=PF
    def createModuleText(self):
        print(str(self.Entry))
        keyTab=['MAYAVERSION','PLATFORM','LOCALE']
        space=' '
        result='+'
        for kt in keyTab:
            if self.Entry[kt]:
                result+=space+kt+':'+self.Entry[kt]
        result+=space+self.ModuleName
        result+=space+self.ModuleVersion
        result+=space+self.ModulePath
        result+='\n'
        for a in self.additional:
            result+=a+'\n'
        result+='\n'
        return result


def createModuleFile(path,file):
    '''
    通过mel执行的文件无法获取__file__,(?
        所以这个文件的所有函数统一由这个函数调用
    '''
    ver22=module('MMD2Maya',path)
    ver22.setVersion('2022')
    ver22.setPlatform('win64')
    ver22.setAdditional('plug-ins: plug-ins/2022')

    ver23=module('MMD2Maya',path)
    ver23.setVersion('2023')
    ver23.setPlatform('win64')
    ver23.setAdditional('plug-ins: plug-ins/2023')

    ver24=module('MMD2Maya',path)
    ver24.setVersion('2024')
    ver24.setPlatform('win64')
    ver24.setAdditional('plug-ins: plug-ins/2024')

    ver25=module('MMD2Maya',path)
    ver25.setVersion('2025')
    ver25.setPlatform('win64')
    ver25.setAdditional('plug-ins: plug-ins/2025')

    modFile=os.path.join(path, file)
    with open(modFile, 'w') as MF:
        MF.write(ver22.createModuleText())
        MF.write(ver23.createModuleText())
        MF.write(ver24.createModuleText())
        MF.write(ver25.createModuleText())
    MGMP=getModulePath()
    print(str(MGMP))
    if MGMP:
        shutil.copy2(modFile, MGMP)
    preload(path)

def getModulePath():
    AP=os.getenv('MAYA_APP_DIR')
    gloMP=os.path.join(AP,'modules')
    norGloMP=os.path.normpath(gloMP)
    mps=os.getenv('MAYA_MODULE_PATH').split(';')
    norMPs=[]
    for mp in mps:
        nmp=os.path.normpath(mp)
        norMPs.append(nmp)
    if norGloMP in norMPs:
        if not os.path.exists(norGloMP):
            os.makedirs(norGloMP)
        return norGloMP
    else:
        return None
#在安装的时候加载
def preload(filePath):
    
    actiVersion = cmds.about(version=True)
    pluginPath  = os.path.join(filePath,'plug-ins')
    pluginPath  = os.path.normpath(os.path.join(pluginPath,actiVersion))
    if os.path.isdir(pluginPath):
        defaultPPath    = os.environ.get('MAYA_PLUG_IN_PATH')
        dPlugPathArray  = defaultPPath.split(';')
        dPlugNPathArray=[]
        for path in dPlugPathArray:
            dPlugNPathArray.append(os.path.normpath(path))
        if pluginPath not in dPlugNPathArray:
            if not dPlugPathArray[-1]:#path;path2;path3;
                newPlugPath=defaultPPath+pluginPath+';'
            else:#path;path2;path3
                newPlugPath=defaultPPath+';'+pluginPath
            os.environ['MAYA_PLUG_IN_PATH'] = newPlugPath
    scriptPath  = os.path.normpath(os.path.join(filePath,'scripts'))
    defaultSPath    = os.environ.get('MAYA_SCRIPT_PATH')
    dScriptPathArray  = defaultSPath.split(';')
    dScriptNPathArray=[]
    for path in dScriptPathArray:
        dScriptNPathArray.append(os.path.normpath(path))
    
    if scriptPath not in dScriptNPathArray:
        if not dScriptPathArray[-1]:#path;path2;path3;
            newScriptPath=defaultSPath+scriptPath+';'
        else:
            newScriptPath=defaultSPath+';'+scriptPath
        if scriptPath not in sys.path:
            sys.path.append(scriptPath)
        os.environ['MAYA_SCRIPT_PATH'] = newScriptPath