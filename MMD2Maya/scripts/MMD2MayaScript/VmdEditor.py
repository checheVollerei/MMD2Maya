# -*- encoding: utf-8 -*-
import os
import importlib
import maya.cmds as cmds
from functools import partial
from MMD2MayaScript.VmdEditorScript import VmdRead as VMD
from MMD2MayaScript.VmdEditorScript import BuildAction as anim
importlib.reload(VMD)
importlib.reload(anim)
#def onMayaDroppedPythonFile(paths):
#    pass
#
class VmdEditor:
    TimeMap={
        'game':'15fps',
        'film':'24fps',
        'pal':'25fps',
        'ntsc':'30fps',
        'show':'48fps',
        'palf':'50fps',
        'ntscf':'60fps'
        }
    def __init__(self):

        #{组件路径
        self.fileFieldPath=None
        self.BriefingFieldPath=None
        self.JGTextFPath=None
        self.MGTextFPath=None
        #}
        self.CreateWindow()
        self.FrameRate=0#maya面板帧速率
        self.Vmdfile=None#解码文件
        self.jointGroup=None#骨骼组
        self.MorphGroup=None#融合变形控制器
    def CreateWindow(self):
    #{
        if cmds.window('VmdWindow', exists=True):
            cmds.deleteUI('VmdWindow')
        window = cmds.window('VmdWindow' ,title="Vmd文件载入", widthHeight=(300, 200),resizeToFitChildren=True )
        form = cmds.formLayout()
        layout1=cmds.columnLayout( adjustableColumn=True )
        cmds.rowLayout(numberOfColumns=2,columnAttach2=('left','left'))
        fpsS = cmds.currentUnit(query=True, time=True)
        if fpsS in self.TimeMap:
            fpsS=self.TimeMap[fpsS]
        cmds.text(label='帧速率',width=110)
        cmds.textField(text=str(fpsS)+'\t(推荐30fps)',editable=False,width=200,backgroundColor=[0.2,0.2,0.2])
        cmds.setParent( '..' )#rowLayout| to layout1|
        r1=cmds.rowLayout(numberOfColumns=3,adjustableColumn=2,columnAttach3=('left','left','left'))
        cmds.text(label='文件路径:',width=110)
        self.fileFieldPath = cmds.textField(height=30,width=200)
        cmds.button(label='😋',width=30,command=partial(self.loadingFile))
        cmds.setParent(form)
        FileName=cmds.text('FileName',label='未载入动画文件',height=30, width=300,backgroundColor=[0.2,0.2,0.2])
        BuildButton = cmds.button(label='动画导入',height=50,command=partial(self.CreateAnimation))
        child1 =cmds.formLayout(backgroundColor=[0.18,0.18,0.18])
        p1=cmds.paneLayout( configuration='vertical2' )
        self.BriefingFieldPath=cmds.text(label='文件简介')
        cmds.columnLayout( adjustableColumn=True,backgroundColor=[0.25,0.25,0.25])
        cmds.frameLayout('jointline1', label='骨骼动画 :' )
        self.JGTextFPath=cmds.textField(placeholderText='载体待写入..',
                        height=30,width=110,
                        textChangedCommand=partial(self.JointFieldChange),
                        backgroundColor=[0.15,0.15,0.15])
        cmds.setParent( '..' )
        cmds.frameLayout('morphline1', label='表情动画 :' )
        self.MGTextFPath=cmds.textField(placeholderText='载体待写入..',
                        height=30,width=110,
                        textChangedCommand=partial(self.MorphFieldChange),
                        backgroundColor=[0.15,0.15,0.15])
        cmds.setParent( '..' )
        cmds.frameLayout( label='相机动画 :' )
        cmds.textField(placeholderText='(暂不支持)',editable=False,height=30,width=110,backgroundColor=[0.2,0.15,0.15])
        cmds.setParent( '..' )
        cmds.frameLayout( label='灯光动画 :' )
        cmds.textField(placeholderText='(暂不支持)',editable=False,height=30,width=110,backgroundColor=[0.2,0.15,0.15])
        cmds.setParent( '..' )
        cmds.frameLayout( label='阴影动画 :' )
        cmds.textField(placeholderText='(暂不支持)',editable=False,height=30,width=110,backgroundColor=[0.2,0.15,0.15])
        cmds.setParent( '..' )
        cmds.frameLayout( label='IK动画 :' )
        cmds.textField(placeholderText='载体由骨骼数据同步写入',editable=False,height=30,width=110,backgroundColor=[0.3,0.25,0.2])


        cmds.formLayout(child1, 
                        edit=True, 
                        attachForm=[
                                    (p1, 'top',5),(p1, 'bottom', 5), (p1, 'left',5),(p1, 'right', 5)
                                    ]
                        )

        cmds.formLayout(form,
                        edit=True,
                        attachForm=[
                                    (layout1, 'top', 5), (layout1, 'left',5),(layout1, 'right', 5),
                                    (FileName, 'top',66),(FileName, 'left',150),(FileName, 'right', 150),
                                    (BuildButton, 'bottom', 10), (BuildButton, 'left',15),(BuildButton, 'right', 15),
                                    (child1, 'top',100),(child1, 'bottom',70),(child1, 'left',15),(child1, 'right', 15)
                                    ]
                        )

        cmds.showWindow()
    #}
    def loadingFile(self,value):
        '''
        value:
            buttonDefaultValue:
        '''
        multipleFilters = "VMD File (*.vmd);;All Files (*.*)"
        filePaths= cmds.fileDialog2(
            fileFilter=multipleFilters,
            dialogStyle=2,
            fileMode=1)
        if not filePaths:
            return
        filePath=filePaths[0]
        filename = os.path.splitext(os.path.basename(filePath))
        if filename[1]!='.vmd':
            cmds.text('FileName',edit=True,label='不支持的文件类型')
            return
        cmds.textField(self.fileFieldPath,edit=True,text=filePath)
        self.Vmdfile=VMD.DecodeVMD(filePath)
        cmds.text(self.BriefingFieldPath,edit=True,label=self.Vmdfile.Briefing)
        cmds.text('FileName',edit=True,label=filename[0])
    def JointFieldChange(self,value):
        if not value or value=='':
            cmds.frameLayout('jointline1',edit=True, label='骨骼动画 :')
            self.jointGroup=None
            return
        if cmds.objExists(value):
            if cmds.objectType(value, isType='transform') or cmds.objectType(value, isType='joint'):
                cmds.frameLayout('jointline1',edit=True, label='骨骼动画 :\t⭕')
                self.jointGroup=value
                #✔✖
                return
        cmds.frameLayout('jointline1',edit=True, label='骨骼动画 :\t❌')
        self.jointGroup=None
    def MorphFieldChange(self,value):
        if not value or value=='':
            cmds.frameLayout('morphline1',edit=True, label='表情动画 :')
            self.MorphGroup=None
        if cmds.objExists(value):
            if cmds.objectType(value, isType='transform'):
                cmds.frameLayout('morphline1',edit=True, label='表情动画 :\t⭕')
                self.MorphGroup=value
                #✔✖
                return
        cmds.frameLayout('morphline1',edit=True, label='表情动画 :\t❌')
        self.MorphGroup=None
    def CreateAnimation(self,value):
        if not self.Vmdfile or ((self.jointGroup==None)and(self.MorphGroup==None)):
            return
        if self.jointGroup:
            self.jointGroup = cmds.textField(self.JGTextFPath,query=True,text=True)
        if self.MorphGroup:
            self.MorphGroup = cmds.textField(self.MGTextFPath,query=True,text=True)
        anim.Action(self.Vmdfile,self.jointGroup,self.MorphGroup)
        