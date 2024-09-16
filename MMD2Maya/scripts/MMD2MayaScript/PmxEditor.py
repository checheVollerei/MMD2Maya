# -*- encoding: utf-8 -*-

# Make a new window
import os
import re
import shutil
import binascii #变形节点以16进制命名

import maya.cmds as cmds
from functools import partial
from MMD2MayaScript.PmxEditorScript import BuildModel as model
from MMD2MayaScript.PmxEditorScript import PmxRead as PMX
from MMD2MayaScript import Utils as Util
import importlib
importlib.reload(model)
importlib.reload(PMX)

class PmxEditor():

    def __init__(self):
        self.filePath=''
        self.renderMode=Util.GetRenderingMode()
        self.DisplayLang=0#0:中&日文，1:英文
        self.PhysicsModel=0
        self.ShadingModel=0
        self.LangButtonBackColor=[[0.3,0.45,0.9],[0.35,0.35,0.35]]#0:激活,1:未激活
        self.ModelName  = ['-','*']
        self.Briefing   = ['未载入文件...','Not loading file...']
        self.AlternatePath=Util.getTempPath()
        self.TexturePath = []#这个索引必须和pmxfile.TexturePath一对一
        self.TexturePath2 = []
        self.PmxFile=None
        self.CreateWindow()


    def CreateWindow(self):
    #{
        if cmds.window('pmxWindow', exists=True):
                cmds.deleteUI('pmxWindow')
        window = cmds.window('pmxWindow',
                            title="pmx文件载入", 
                            widthHeight=(300, 200),
                            resizeToFitChildren=True )
        form = cmds.formLayout()
        layout1=cmds.columnLayout( adjustableColumn=True )
        cmds.rowLayout(numberOfColumns=2,columnAttach2=('left','left'))
        cmds.text(label='当前渲染引擎',width=110)
        cmds.textField(text=self.renderMode,editable=False,width=200)

        cmds.setParent( '..' )#rowLayout| to layout1|
        r1=cmds.rowLayout(numberOfColumns=3,adjustableColumn=2,columnAttach3=('left','left','left'))
        cmds.text(label='文件路径',width=110)
        cmds.textField('pmxFilePath',width=200)
        cmds.button(label='😋',width=30,command=lambda x:self.loadFile())

        cmds.setParent('..')#r1| to layout1|
        cmds.rowLayout(numberOfColumns=3,columnAttach3=('left','left','left'), columnAttach=[(1, 'left', 112)] )
        cmds.button('langC',label='中',width=30,height=30,backgroundColor=self.LangButtonBackColor[self.DisplayLang],command=lambda x:self.LangChange())
        cmds.textField('ModelName',text='-',width=200,height=30)
        cmds.button('langE',label='英',width=30,height=30,backgroundColor=self.LangButtonBackColor[1-self.DisplayLang],command=lambda x:self.LangChange())


        cmds.setParent(form)#rowLayout| to form|
        tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        child1 =cmds.paneLayout( configuration='single')
        text_field = cmds.text('PmxBriefing',label='未载入文件...',backgroundColor=[0.18,0.18,0.18])

        cmds.setParent( '..' )#child1| to tabs|
        child2 =cmds.formLayout()
        child2R1=cmds.rowLayout(numberOfColumns=3,adjustableColumn=2)
        cmds.text(label='备用路径',width=110)
        cmds.textField('pmxFilePath2',text=self.AlternatePath,width=200,editable=False )#,changeCommand=partial(self.FilePathChange)
        cmds.button(label='...',width=30,command=lambda x:self.SearchFilePath())

        cmds.setParent('..')
        scrollLayout = cmds.scrollLayout(childResizable=True,minChildWidth=200)

        fram1=cmds.frameLayout(collapsable=True ,label='Texture' )

        cmds.rowColumnLayout( 'TexTable',numberOfColumns=2)

        for index in range(10):
            cmds.text(label = '贴图'+str(index)+' : -> ',align='right',width=150)
            cmds.textField(width=200)
        cmds.formLayout(child2, edit=True, attachForm = [
            (child2R1, 'top',10),(child2R1, 'left', 1),(child2R1, 'right', 1),
            (scrollLayout, 'top',50),(scrollLayout, 'bottom',1),(scrollLayout, 'left', 1),(scrollLayout, 'right', 1),
        ])
        cmds.tabLayout( tabs, edit=True, tabLabel=((child1, '模型简介'), (child2, '贴图备份')) )

        cmds.setParent(form)#r1| to form|
        subform=cmds.formLayout()
        fram1=cmds.frameLayout( label='材质' )
        cmds.columnLayout()
        collection1 = cmds.radioCollection()
        shading2 = cmds.radioButton( label='ToonShading' ,select=True ,onCommand=lambda x:self.ShadingChange())
        shading1 = cmds.radioButton( label='lambert' ,onCommand=lambda x:self.ShadingChange())
        
        cmds.setParent(subform)#collection1| to form|subform|
        fram2=cmds.frameLayout( label='物理' )
        cmds.columnLayout()
        collection2 = cmds.radioCollection()
        Physics1 = cmds.radioButton( label='静态网格' ,select=True ,onCommand=lambda x:self.PhysicsChange())
        Physics2 = cmds.radioButton( label='bellet' ,onCommand=lambda x:self.PhysicsChange())
        

        cmds.setParent(subform)#collection1| to form|subform|
        BuildButton = cmds.button(label='场景构成', width=100,height=70 ,command=lambda x:self.BuildScene())

        cmds.formLayout(subform, edit=True, attachForm=[
            (BuildButton, 'top',1),(BuildButton, 'bottom',1),(BuildButton, 'right', 1),
            (fram1, 'top',1),(fram1, 'bottom',1),(fram1, 'right', 130),
            (fram2, 'top',1),(fram2, 'bottom',1),(fram2, 'right', 250),
        ])

        cmds.formLayout(form, edit=True, attachForm=[
            
            (layout1, 'top', 5), (layout1, 'left',5),(layout1, 'right', 5),
            (tabs, 'top',90),(tabs, 'bottom',80),(tabs, 'left',5),(tabs, 'right', 5),
            (subform, 'left',5),(subform, 'right', 5),(subform, 'bottom', 5),
        ])

        cmds.showWindow( window )
    #}
    def LangChange(self):
        """
        语言切换模块，按下按钮的时候修改激活按钮的颜色和[ModelName][PmxBriefing]的显示文件
        """
        self.DisplayLang=1-self.DisplayLang
        cmds.button('langC',edit=True,backgroundColor=self.LangButtonBackColor[self.DisplayLang])
        cmds.button('langE',edit=True,backgroundColor=self.LangButtonBackColor[1-self.DisplayLang])
        cmds.text('PmxBriefing',edit=True,label=self.Briefing[self.DisplayLang])
        cmds.textField('ModelName',edit=True,text=self.ModelName[self.DisplayLang])
    def PhysicsChange(self):
        """
        只有两个单选的时候可以直接 !value,
        多个单选元素的时候可以使用
        cmds.radioCollection( '', edit=True, select=True )查询当前选择的元素字符串
        """
        self.PhysicsModel=1-self.PhysicsModel
    def ShadingChange(self):
        self.ShadingModel=1-self.ShadingModel
    def CreateTexFileWidgets(self):
        parentLayout = cmds.rowColumnLayout( 'TexTable',query=True,fullPathName=True)
        children = cmds.rowColumnLayout('TexTable', query=True, childArray=True)
        self.TexturePath=[]
        # 删除所有子级组件
        if children is not None:
            for child in children:
                cmds.deleteUI(child)

        cmds.setParent(parentLayout)
        for i in range(len(self.PmxFile.TexturePaths)):
        #{
            tex=self.PmxFile.TexturePaths[i]
            Texfile = os.path.basename(tex.TexturePath)
            split=os.path.splitext(Texfile)
            texName=str(split[0])
            extension=str(split[1])
            cmds.text(label =texName +' : -> ',align='right',width=200)
            if re.search(r'[^\x00-\x7F]',texName):
                deStr =  binascii.hexlify(texName.encode())
                hexStr = deStr.decode()
                cmds.textField('texName%i'%i,text=hexStr,width=200,changeCommand=partial(self.TextureRename,i))
                self.TexturePath.append([hexStr,extension])
            else:
                cmds.textField('texName%i'%i,text=texName,width=200,changeCommand=partial(self.TextureRename,i))
                self.TexturePath.append([texName,extension])
        #}
    def TextureRename(self,index,value):
        """_summary_
        textField的changeCommand回调会隐式传递一个text值
        lambda只能用于常量传入,如果是变量他传入的始终是最后一个索引
        """
        activWidget='texName%i'%index
        changeText=value#cmds.textField(activWidget,query=True,text=True)
        lastName = self.TexturePath[index][0]
        if re.search(r'[^\x00-\x7F]',changeText):
            cmds.textField(activWidget,edit=True,text=lastName)
        else:
            self.TexturePath[index][0]=changeText
    def copyTexture2NewPath(self):
        filePath=os.path.dirname(self.filePath[0])#文件夹的绝对路径
            # 检查目标目录是否存在，如果不存在则创建
        if not os.path.isdir(self.AlternatePath):
            os.makedirs(self.AlternatePath)
        self.TexturePath2=[]
        for i in range(len(self.TexturePath)):
            relTexPath=self.PmxFile.TexturePaths[i].TexturePath
            srcPath=os.path.join(filePath, relTexPath)
            TexName =self.TexturePath[i][0]+self.TexturePath[i][1]#[0]:fileName,[1]:fileExtension
            dstPath = os.path.join(self.AlternatePath,TexName)
            self.TexturePath2.append(dstPath)
            #shutil.copy2是可以覆写的，使用scriptEditor执行都可以
            # 但是maya通过外部脚本权限不够
            if os.path.exists(dstPath):
                continue
            else:
                shutil.copy2(srcPath, dstPath)
    def SearchFilePath(self):
        value=cmds.fileDialog2(fileFilter= "All Files (*.*)", dialogStyle=2,fileMode=3)
        if not value:
            return 
        path=value[0]
        if os.path.isdir(path):
            if re.search(r'[^\x00-\x7F]',path):
                print('备用路径不能包含非英文字符;')
            else:
                cmds.textField('pmxFilePath2',edit=True,text=path)
                self.AlternatePath=path
    def FilePathChange(self,value):
        print(value)
        if os.path.isdir(value):
            if re.search(r'[^\x00-\x7F]',value):
                print('备用路径不能包含非英文字符;')
                cmds.textField('pmxFilePath2',edit=True,text=self.AlternatePath)
            else:
                self.AlternatePath=value
        else:
            cmds.textField('pmxFilePath2',edit=True,text=self.AlternatePath)
    def loadFile(self):
        multipleFilters = "PMX Files (*.pmx);;All Files (*.*)"

        self.filePath = cmds.fileDialog2(fileFilter=multipleFilters,dialogStyle=2,fileMode=1)
        if not self.filePath:
            return
        filename = os.path.splitext(os.path.basename(self.filePath[0]))
        if filename[1]!='.pmx':
            return
        cmds.textField('pmxFilePath',edit=True,text=self.filePath[0])
        self.PmxFile=PMX.DecodePMX(self.filePath[0])
        self.Briefing=self.PmxFile.Briefing
        self.ModelName=self.PmxFile.ModelName
        cmds.text('PmxBriefing',edit=True,label=self.Briefing[self.DisplayLang])
        cmds.textField('ModelName',edit=True,text=self.ModelName[self.DisplayLang])
        self.CreateTexFileWidgets()

    def BuildScene(self):
        if not self.PmxFile:
            return
        self.copyTexture2NewPath()
        shaderfile=Util.getResourcePath('PmxStandardMat.sfx')
        Scene = model.BuildScene(self.TexturePath2,shaderfile,self.PhysicsModel,self.ShadingModel)
        Scene.Execution(self.PmxFile)
        cmds.setAttr('hardwareRenderingGlobals.transparencyAlgorithm' ,3)#