import maya.cmds as cmds
    


def RegisterCCDIK(*args):
    #long == fullPath=True
    selectTab = cmds.ls(selection=True,long=True)
    print(selectTab)
    if (len(selectTab)!=3):
        return
    for  act in reversed(selectTab):
        print(cmds.nodeType(act))
        if (cmds.nodeType(act)!='transform') and (cmds.nodeType(act)!='joint'):
            return
    
    rot=selectTab[0]
    target=selectTab[1]
    handle=selectTab[2]
    handleMD2M=cmds.listConnections(handle+'.message', type="MD2MayaNode")
    if not handleMD2M:
        return
    LinkTab=[]
    linkTabMD2=[]
    current_node = target
    temp=cmds.listConnections(target+'.message', type="MD2MayaNode")
    targetMD2=None
    if temp:
        targetMD2=temp[0]
    else:
        return
    while True:
    #{
        parent = cmds.listRelatives(current_node, fullPath=True,parent=True)
        linked_nodes = cmds.listConnections(parent[0]+'.message', type="MD2MayaNode")
        if linked_nodes or ((cmds.nodeType(parent[0])!='transform') and (cmds.nodeType(parent[0])!='joint')):
            LinkTab.append(parent[0])
            linkTabMD2.append(linked_nodes[0])
        else:
            print(parent[0]+'未注册MD2MayaNode')
            return
        if parent[0] == rot:
            break
            # 如果没有父级，结束遍历
        if not parent:
            print('未找到rot')
            return
        current_node=parent[0]
    #}
    #这里应该需要updateIKTabComponent（）他根据给定名称刷新节点上的列表
    #cmds.textScrollList(CCDTableComponent,edit=True,removeAll=True)
    cmds.connectAttr( targetMD2  + ".MDnOutRotate", handleMD2M[0] + ".TargetRotate",force=True)
    cmds.connectAttr( targetMD2  + ".MDnOutTranslate", handleMD2M[0] + ".TargetTranslate",force=True)
    
    for i in range(len(LinkTab)):
        cmds.connectAttr( linkTabMD2[i]  + ".MDnOutRotate", handleMD2M[0] + ".MDnIKTable[%i].MDnTabRotate"%i,force=True)
        cmds.connectAttr( linkTabMD2[i]  + ".MDnOutTranslate", handleMD2M[0] + ".MDnIKTable[%i].MDnTabTranslate"%i,force=True)
        cmds.connectAttr( linkTabMD2[i]  + ".MDnOutJointOrient", handleMD2M[0] + ".MDnIKTable[%i].MDnTabJointOrient"%i,force=True)

        cmds.connectAttr( handleMD2M[0] + ".MDnOutIK[%i].MDnOutIKTranslate"%i, LinkTab[i]  + ".translate",force=True)
        cmds.connectAttr( handleMD2M[0] + ".MDnOutIK[%i].MDnOutIKRotate"%i, LinkTab[i]  + ".rotate",force=True)
        #cmds.textScrollList(CCDTableComponent,edit=True,append=linkTabMD2[i])

    rotIndex = len(LinkTab)-1
    cmds.connectAttr( LinkTab[rotIndex]  + ".parentMatrix[0]", handleMD2M[0] + ".MDnIKTable[%i].MDnTabParentMatrix"%rotIndex,force=True)
    

def LimitButtonCommand(attr):
#{
    getState = cmds.getAttr(attr)
    setState = not getState
    backColor = [0.35,0.35,0.35]
    if setState:
        backColor = [0.1,0.1,0.1]
    cmds.button('CCDLimitButton',edit=True,backgroundColor=backColor)
    cmds.setAttr(attr,setState)
#} 
#这个应该在CCDTableComponent选择列表发生改变的时候触发
def updateLimitComponent(nodeName):
#{
    indexItem=cmds.textScrollList('CCDTableComponent',query=True, selectIndexedItem=True)
    if indexItem:
        index=indexItem[0]-1
    else:
        index=0
    cmds.connectControl("LimitMaxX",nodeName+".MDnIKTable[%i].MDnAxisLimitMax%i"%(index,0))
    cmds.connectControl("LimitMaxY",nodeName+".MDnIKTable[%i].MDnAxisLimitMax%i"%(index,1))
    cmds.connectControl("LimitMaxZ",nodeName+".MDnIKTable[%i].MDnAxisLimitMax%i"%(index,2))

    cmds.connectControl("LimitMinX",nodeName+".MDnIKTable[%i].MDnAxisLimitMin%i"%(index,0))
    cmds.connectControl("LimitMinY",nodeName+".MDnIKTable[%i].MDnAxisLimitMin%i"%(index,1))
    cmds.connectControl("LimitMinZ",nodeName+".MDnIKTable[%i].MDnAxisLimitMin%i"%(index,2))
    AttrName = nodeName+".MDnIKTable[%i].MDnEnableAxisLimit"%index
    #获取当前选择列表的limit值，这个值与button的颜色相关
    enbleLimit = cmds.getAttr(AttrName) 
    backColor = [0.35,0.35,0.35]
    if enbleLimit:
        backColor = [0.1,0.1,0.1]
        
    cmds.button('CCDLimitButton',edit=True,backgroundColor=backColor,command=lambda *args:LimitButtonCommand(AttrName))
#}
def updateIKTabComponent(nodeName):
#{
    #print("组件名称："+CCDTableComponent)
    cmds.textScrollList('CCDTableComponent',edit=True,removeAll=True)
    AttrSize = cmds.getAttr(nodeName + '.MDnIKTable', size=True)
    if (AttrSize>0):
        for index in range(AttrSize):
            attr = nodeName+".MDnIKTable[%i].MDnTabRotate"%index
            source=cmds.listConnections(attr,plugs=False)
            if source:
                cmds.textScrollList('CCDTableComponent',edit=True,append=source[0])
                cmds.textScrollList('CCDTableComponent',edit=True,selectIndexedItem=1,selectCommand=lambda *args:updateLimitComponent(nodeName))
        updateLimitComponent(nodeName) #手动执行一次
        targetSource=cmds.listConnections(nodeName+".MDnIKTarget.TargetRotate",plugs=False)
        if targetSource:
            cmds.textField('MDtargetField',edit=True,text=str(targetSource[0]),)
    else:
        updateLimitComponent(nodeName)
        cmds.textField('MDtargetField',edit=True,text='空')
#}
def createUITemplate(nodeName):
    if cmds.uiTemplate( 'CCDIKTemplate', exists=True ):
    	cmds.deleteUI( 'CCDIKTemplate', uiTemplate=True )

    cmds.uiTemplate( 'CCDIKTemplate' )
    #{模板预设
    cmds.button( defineTemplate='CCDIKTemplate', width=100, height=30, align='left' )
    cmds.floatField(defineTemplate='CCDIKTemplate',width=60,precision=3 )
    cmds.intField(defineTemplate='CCDIKTemplate',width=50)
    cmds.frameLayout( defineTemplate='CCDIKTemplate', borderVisible=True, labelVisible=False )
    #}
    cmds.setUITemplate( 'CCDIKTemplate', pushTemplate=True )
    cmds.columnLayout(adjustableColumn=True)
    cmds.rowLayout(numberOfColumns=4,columnAttach=[(1,'left',100),(2,'left',5),(3,'left',40),(4,'left',5)])
    cmds.text(label='循环:')
    cmds.intField("loop",value=3)
    cmds.text(label='单位角:')
    cmds.floatField("planeAngle",value=0.0,width=70,precision=4)
    cmds.setParent('..')#rowLayout->columnLayout
    cmds.rowLayout(numberOfColumns=2,columnAttach=[(1,'left',100),(2,'left',5)])
    cmds.text(label='目标:')
    cmds.textField('MDtargetField',text='空', editable=False,annotation="此组件仅用以可视化",backgroundColor=(0.3,0.45,0.9))
    cmds.setParent('..')#rowLayout->columnLayout
    cmds.rowLayout(numberOfColumns=1,adjustableColumn=2,columnAttach=(1,'left',100))
    cmds.text(label='连接列表:')
    cmds.setParent('..')#rowLayout->columnLayout
    cmds.rowLayout(numberOfColumns=3,adjustableColumn=3,columnAttach=(1,'left',100),columnAlign3=('left','left','left'))
    # 创建一个文本滚动列表
    cmds.textScrollList('CCDTableComponent',numberOfRows=8, allowMultiSelection=False,
    			append=['空',],width=100,selectCommand=lambda *args:updateLimitComponent(nodeName))
    cmds.separator(width=10, height=135,style='single')
    cmds.columnLayout(adjustableColumn=True)
    cmds.rowLayout(numberOfColumns=2,adjustableColumn=3,columnAttach2=('left','left'))
    CCDLimitButton=cmds.button('CCDLimitButton',label='轴限制',width=110)
    cmds.button(label='😋',width=30)
    cmds.setParent('..')
    cmds.rowLayout(numberOfColumns=2,adjustableColumn=3,columnAttach2=('left','left'),columnOffset2=(10,50))
    cmds.text(label='最大值')
    cmds.text(label='最小值')
    cmds.setParent('..')
    cmds.rowLayout(numberOfColumns=3,adjustableColumn=4,columnAlign3=('left','left','left'))
    cmds.floatField('LimitMaxX',value=0.0)
    cmds.text(label='| X |')
    cmds.floatField('LimitMinX',value=0.0)
    cmds.setParent('..')
    cmds.rowLayout(numberOfColumns=3,adjustableColumn=4,columnAlign3=('left','left','left'))
    cmds.floatField('LimitMaxY',value=0.0)
    cmds.text(label='| Y |')
    cmds.floatField('LimitMinY',value=0.0)
    cmds.setParent('..')
    cmds.rowLayout(numberOfColumns=3,adjustableColumn=4,columnAlign3=('left','left','left'))
    cmds.floatField('LimitMaxZ',value=0.0)
    cmds.text(label='| Z |')
    cmds.floatField('LimitMinZ',value=0.0)
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.rowLayout(columnAttach=(1,'left',100))
    cmds.button(label='载入ik',width=100,command=RegisterCCDIK)
    cmds.setParent('..')#toColumnLayout1
    cmds.setUITemplate( popTemplate=True )
    #通过connectControl链接的组件可以直接用右键锁定的那些东西
    cmds.connectControl("loop",nodeName+".MDnIKLoop")
    cmds.connectControl("planeAngle",nodeName+".MDnIKAngle")
    updateIKTabComponent(nodeName)

def updateUITemplate(nodeName):
    cmds.connectControl("loop",nodeName+".MDnIKLoop")
    cmds.connectControl("planeAngle",nodeName+".MDnIKAngle")#,index=2
    updateIKTabComponent(nodeName)
