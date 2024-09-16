# -*- encoding: utf-8 -*-
import maya.mel as mel
import maya.cmds as cmds
from functools import partial
import MMD2MayaScript.Utils as Util

'''
因为maya自动生成的shelfTab会带入默认popup的设置
    所以这个脚本由userSetup.py调用
    这样实例会在maya运行周期保存,还可以直接通过实例调用内部函数
        *比如:runTimeCommand
    
'''
class MDShelfTab:
    def __init__(self,name):
        self.Instance=name
        self.MoveOverride=False
        self.RotateOverride=False
        self.TToolButtonPath=''
        self.TNameComCache=None
        self.RNameComCache=None
    def buildMnTranslateMM(self):
        if Util.ExistsActivateObject('MnTranslate'):
            #这里必须使用tempMM,以便内置的destroySTRSMarkingMenu执行MarkingMenuPopDown
            # 否则需要重写在按键松开的事件来销毁
            if (cmds.popupMenu('tempMM',exists=True )):
                cmds.deleteUI('tempMM')
            if (cmds.currentCtx()!='ManipMnTranslate'):
                cmds.setToolTo("ManipMnTranslate")
            popuParent = Util.findPanelPopupParent()
            popupPath=cmds.popupMenu('tempMM',button=1,markingMenu=True,parent=popuParent)
            #这个函数···不知道用来干嘛的,还没啃下来(′⌒`)，定义在drInit的2421,2723
            #ref:[\···\Maya2022\scripts\others\buildToolOptionsMM.mel]
            cmds.setParent('..', menu=True)
            if mel.eval('exists("DRUseModelingToolkitMM")') and mel.eval('DRUseModelingToolkitMM("{}")'.format(popupPath)):
                return
            self.MnTranslateManipPopupMenu(popupPath,popuParent)
            cmds.setParent('..', menu=True)
        else:
            mel.eval("buildTranslateMM")
    def buildMnRotateMM(self):
        if Util.ExistsActivateObject('MnRotate'):
            #这里必须使用tempMM,以便内置的destroySTRSMarkingMenu执行MarkingMenuPopDown
            # 否则需要重写在按键松开的事件来销毁
            if (cmds.popupMenu('tempMM',exists=True )):
                cmds.deleteUI('tempMM')
            if (cmds.currentCtx()!='ManipMnRotate'):
                cmds.setToolTo("ManipMnRotate")
            popuParent = Util.findPanelPopupParent()
            popupPath=cmds.popupMenu('tempMM',button=1,markingMenu=True,parent=popuParent)
            #这个函数···不知道用来干嘛的,还没啃下来(′⌒`)，定义在drInit的2421,2723
            #ref:[\···\Maya2022\scripts\others\buildToolOptionsMM.mel]
            cmds.setParent('..', menu=True)
            if mel.eval('exists("DRUseModelingToolkitMM")') and mel.eval('DRUseModelingToolkitMM("{}")'.format(popupPath)):
                return
            self.MnRotateManipPopupMenu(popupPath,popuParent)
            cmds.setParent('..', menu=True)
        else:
            mel.eval("buildRotateMM")
    def TranslateHotKeyOverride(self,value):
        #maya内置TranslateManip换出命令
        NameC='TranslateToolWithSnapMarkingMenuNameCommand'
        count = cmds.assignCommand(query=True, numElements=True)
        for index in range(1, count+1):
            nCom=cmds.assignCommand(index, query=True, name=True)
            if(nCom==NameC):
                #keys=cmds.assignCommand(index, query=True, keyString=True)
                if cmds.runTimeCommand('MnTranslatToolPopupMenu',exists=True):
                    cmds.runTimeCommand('MnTranslatToolPopupMenu',edit=True,delete=True)
                #runtime不能用this指针调用，需要使用Global或者明确的路径调用,也可以写个.mel调用.py文件来启动
                #这里使用创建时候的实例名调用实例的函数，其中：实例是在userSetup定义的Global变量
                cmds.runTimeCommand('MnTranslatToolPopupMenu',commandLanguage='python',command='%s.buildMnTranslateMM()'%self.Instance)
                if value:
                    self.TNameComCache=cmds.assignCommand(index, query=True, command=True)
                    cmds.assignCommand(index=index, edit=True, command='MnTranslatToolPopupMenu')
                else:
                    cmds.assignCommand(index=index, edit=True, command=self.TNameComCache)
                self.MoveOverride=value
                break
	        	#cmds.assignCommand(index=index, edit=True, command='TestRTCommand')
    def RotateHotKeyOverride(self,value):
        #maya内置TranslateManip换出命令
        NameC='RotateToolWithSnapMarkingMenuNameCommand'
        count = cmds.assignCommand(query=True, numElements=True)
        for index in range(1, count+1):
            nCom=cmds.assignCommand(index, query=True, name=True)
            if(nCom==NameC):
                #keys=cmds.assignCommand(index, query=True, keyString=True)
                if cmds.runTimeCommand('MnRotateToolPopupMenu',exists=True):
                    cmds.runTimeCommand('MnRotateToolPopupMenu',edit=True,delete=True)
                #runtime不能用this指针调用，需要使用Global或者明确的路径调用
                #这里使用创建时候的实例名调用实例的函数，其中：实例是在userSetup定义的Global变量
                cmds.runTimeCommand('MnRotateToolPopupMenu',commandLanguage='python',command='%s.buildMnRotateMM()'%self.Instance)
                if value:
                    self.RNameComCache=cmds.assignCommand(index, query=True, command=True)
                    cmds.assignCommand(index=index, edit=True, command='MnRotateToolPopupMenu')
                else:
                    cmds.assignCommand(index=index, edit=True, command=self.RNameComCache)
                self.RotateOverride=value
                break
	        	#cmds.assignCommand(index=index, edit=True, command='TestRTCommand')
    def settingManipState(self,SpaceValue,value):
        '''
        defaultValue:
            value=checkBoxState
        '''
        if SpaceValue=="world":
            cmds.MnTranslateController("ManipMnTranslate", e=True, space=SpaceValue)
            texPath = Util.getResourcePath('MnTwsManip.png')
            cmds.shelfButton(self.TToolButtonPath, edit=True, image=texPath)
        elif SpaceValue=="object":
            cmds.MnTranslateController("ManipMnTranslate", e=True, space=SpaceValue)
            texPath = Util.getResourcePath('MnTosManip.png')
            cmds.shelfButton(self.TToolButtonPath, edit=True, image=texPath)
        else:
            return
    def MnTranslateManipPopupMenu(self,popupPath,popupParent):
        '''
        这个函数在按下鼠标右键执行创建自定义popupMenu
        defaultValue:
            popupPath,popupParent
        SpaceValue = OpenMaya.MSpace.enum:
            Object=2,World=4;
        '''
        SpaceValue=cmds.MnTranslateController('ManipMnTranslate', q=True, space=True)
        if(cmds.popupMenu(popupPath, query=True ,exists=True)):
            cmds.popupMenu(popupPath, edit=True, deleteAllItems=True)
        else:
            return
        cmds.setParent(popupPath, menu = True)
        cmds.menuItem(  label="object",
                        radialPosition="E",
                        checkBox=(1 if SpaceValue == 2 else 0),
                        command=partial(self.settingManipState,'object'))
        cmds.menuItem(label="World",radialPosition="SE",checkBox=(1 if SpaceValue == 4 else 0),command=partial(self.settingManipState,'world'))
        cmds.menuItem(label="覆写",radialPosition="S",checkBox=self.MoveOverride,command=partial(self.TranslateHotKeyOverride))
    def MnRotateManipPopupMenu(self,popupPath,popupParent):
        if(cmds.popupMenu(popupPath, query=True ,exists=True)):
            cmds.popupMenu(popupPath, edit=True, deleteAllItems=True)
        else:
            return
        cmds.setParent(popupPath, menu = True)
        cmds.menuItem(label="覆写",radialPosition="S",checkBox=self.RotateOverride,command=partial(self.RotateHotKeyOverride))

    def createToolShelf(self):
        # 检查是否已经存在同名的工具架
        if cmds.shelfLayout('MMD2MayaTool', exists=True):
            cmds.deleteUI('MMD2MayaTool', layout=True)
        # 创建新的工具架
        cmds.shelfLayout('MMD2MayaTool', parent='ShelfLayout')
        TTexPath = Util.getResourcePath('MnTosManip.png')
        # 添加按钮到工具架，并指定图标路径
        self.TToolButtonPath=cmds.shelfButton('MnTranslateTool',
                                                label='MnTranslateTool',
                                                noDefaultPopup=True,
                                                command='cmds.setToolTo("ManipMnTranslate")',
                                                image=TTexPath)
        cmds.popupMenu( parent='MnTranslateTool',markingMenu=True,postMenuCommand=partial(self.MnTranslateManipPopupMenu))
        RTexPath = Util.getResourcePath('MnRManip.png')
        cmds.shelfButton('MnRotateTool',
                        label='MnRotateTool',
                        noDefaultPopup=True,
                        command='cmds.setToolTo("ManipMnRotate")',
                        image=RTexPath)
        cmds.popupMenu( parent='MnRotateTool',markingMenu=True,postMenuCommand=partial(self.MnRotateManipPopupMenu))
        

# 调用函数创建工具架
#MDShelfTab().createToolShelf()