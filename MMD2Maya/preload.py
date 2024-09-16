# -*- encoding: utf-8 -*-
import importlib
import maya.cmds as cmds
import MD2MayaShelfTab as MDShelf
import MD2MayaEditor as MDEditor
importlib.reload(MDShelf)
importlib.reload(MDEditor)
def loadDependencyPlugin():
    if not cmds.pluginInfo('MD2MayaSolver.mll', query=True, loaded=True):
        cmds.loadPlugin('MD2MayaSolver.mll')
        cmds.pluginInfo('MD2MayaSolver.mll', edit=True, autoload=True)
    if not cmds.pluginInfo('shaderFXPlugin.mll', query=True, loaded=True):
        cmds.loadPlugin('shaderFXPlugin.mll')
        cmds.pluginInfo('shaderFXPlugin.mll', edit=True, autoload=True)
    if not cmds.pluginInfo('bullet.mll', query=True, loaded=True):
        cmds.loadPlugin('bullet.mll')
        cmds.pluginInfo('bullet.mll', edit=True, autoload=True)
MdOveTool=None
def createMMD2MayaWindow():
    #传入实例名,供runTimeCommand调用
    global  MdOveTool
    MdOveTool = MDShelf.MDShelfTab('MdOveTool')
    MdOveTool.createToolShelf()
    MDEditor.CreateMenu()
cmds.evalDeferred('loadDependencyPlugin()')
cmds.evalDeferred('createMMD2MayaWindow()')
#createToolShelf()