# -*- encoding: utf-8 -*-
import os
import sys
import importlib
import maya.mel as mel
import maya.cmds as cmds
from MMD2MayaScript import PmxEditor as Pmx
from MMD2MayaScript import VmdEditor as Vmd
from MMD2MayaScript import JointDynamicEditor as dyna
importlib.reload(Vmd)
importlib.reload(Pmx)
importlib.reload(dyna)

def CreateMenu():
    """ Creates Menu in Maya's Window """   
    #在Maya的窗口中创建菜单
    cmds.setParent(mel.eval("$temp1=$gMainWindow"))
    #Menu=cmds.menu(parent="MayaWindow",label="插件入口")
    if cmds.control("MMDE", exists=True):
        cmds.deleteUI("MMDE", menu=True)
    menu = cmds.menu("MMDE", label= "MMD2Maya",tearOff=True)
    cmds.menuItem(label= "载入PMX文件...", command=lambda x:Pmx.PmxEditor())
    cmds.menuItem(divider=True)
    cmds.menuItem(label= "载入VMD文件...", command=lambda x:Vmd.VmdEditor())
    cmds.menuItem(divider=True)
    cmds.menuItem(divider=True)
    cmds.menuItem(label= "动力骨骼...", command=lambda x:dyna.DynamicEditor())
    #cmds.menuItem(divider=True)
    #cmds.menuItem(divider=True)
    #cmds.menuItem(label= "删除脚本",command=lambda x:Delete_Script())
    #cmds.evalDeferred('createToolShelf()')
#def initializePlugin(plugin):
#	CreateMenu()
#
#def uninitializePlugin(plugin):
#    if cmds.shelfLayout('MikuDanceTool', exists=True):
#        cmds.deleteUI('MikuDanceTool', layout=True)
#    if cmds.control("MMDE", exists=True):
#        cmds.deleteUI("MMDE", menu=True)