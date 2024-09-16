# -*- encoding: utf-8 -*-
import os
import math
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

from MMD2MayaScript import Resource as res
import maya.app.mayabullet.BulletUtils as BulletUtils


def Cross(V1,V2):
    X=V1[1]*V2[2]-V1[2]*V2[1]
    Y=V1[2]*V2[0]-V1[0]*V2[2]
    Z=V1[0]*V2[1]-V1[1]*V2[0]
    Result=[X,Y,Z]
    return Result
def QuatDot(q1,q2):
    cosOmega=q1[0]*q2[0]+q1[1]*q2[1]+q1[2]*q2[2]+q1[3]*q2[3]
    return cosOmega

def QuatNormalize(q):
    length = QuatDot(q,q)
    x=q[0]*length
    y=q[1]*length
    z=q[2]*length
    w=q[3]*length
    Result=[x,y,z,w]
    return Result

def AverageQuat(QuatList):
    """_summary_
    ref:[https://www.cnblogs.com/21207-iHome/p/6952004.html]
        这个网址还分享了一个matlab的平均加权,但是和maya的平均模式算法不同
    """
    Result = [0,0,0,1]
    firstQuat=QuatList[0]
    lastQuat=[0,0,0,1]
    weight=1.0/len(QuatList)
    for i in range(1,len(QuatList)):
        NextQuat=QuatList[i]
        cos = QuatDot(NextQuat,firstQuat)
        if (cos<0):
            NextQuat[0]=-NextQuat[0]
            NextQuat[1]=-NextQuat[1]
            NextQuat[2]=-NextQuat[2]
            NextQuat[3]=-NextQuat[3]

        lastQuat[0]+=NextQuat[0]
        lastQuat[1]+=NextQuat[1]
        lastQuat[2]+=NextQuat[2]
        lastQuat[3]+=NextQuat[3]
        Result[0]=lastQuat[0]*weight
        Result[1]=lastQuat[1]*weight
        Result[2]=lastQuat[2]*weight
        Result[3]=lastQuat[3]*weight

    return QuatNormalize(Result)

def computeOffsetValue(constraint,newTarget,nodeB):
    targetCount = cmds.getAttr(constraint + '.target', size=True)
    QuatArray=[]
    nodeBRot = cmds.xform(nodeB, query=True, worldSpace=True, rotation=True)
    BQuat = OpenMaya.MEulerRotation(nodeBRot[0]*(3.1415926/180), nodeBRot[1]*(3.1415926/180), nodeBRot[2]*(3.1415926/180)).asQuaternion()
    for ti in range(targetCount-1):#获取所有已连接目标的四元数
        target = cmds.listConnections( constraint+'.target[%i].targetRotateOrder'%ti, d=False, s=True)[0]
        rot = cmds.xform(target, query=True, worldSpace=True, rotation=True)
        Orient= OpenMaya.MEulerRotation(rot[0]*(3.1415926/180), rot[1]*(3.1415926/180), rot[2]*(3.1415926/180)).asQuaternion()
        QuatArray.append([Orient[0],Orient[1],Orient[2],Orient[3]])
    rot2 = cmds.xform(newTarget, query=True, worldSpace=True, rotation=True)
    Orient2= OpenMaya.MEulerRotation(rot2[0]*(3.1415926/180), rot2[1]*(3.1415926/180), rot2[2]*(3.1415926/180)).asQuaternion()
    QuatArray.append([Orient2[0],Orient2[1],Orient2[2],Orient2[3]])
    outQuat = AverageQuat(QuatArray)
    outQuat2 = OpenMaya.MQuaternion(outQuat[0],outQuat[1],outQuat[2],outQuat[3])
    differ = (BQuat*outQuat2.inverse()).asEulerRotation()
    offsetValue = [differ[0]*(180/3.1415926),differ[1]*(180/3.1415926),differ[2]*(180/3.1415926)]
    return offsetValue
def QuatSlerp(Quat1,Quat2,t):
    #result=[0,0,0,0]
    if t>1:
        print('t值错误')
    #四元数插值函数来自《3D数学基础：图形和游戏开发》==>四元数插值
    #X  Y  Z  W 四元数点积：各分量的乘积和 cosθ
    cosOmega=Quat1[0]*Quat2[0] + Quat1[1]*Quat2[1] + Quat1[2]*Quat2[2] + Quat1[3]*Quat2[3]
    #两个旋转矢量大于90°，角度为负
    if cosOmega<0.0:
        Quat2[0]=-Quat2[0]
        Quat2[1]=-Quat2[1]
        Quat2[2]=-Quat2[2]
        Quat2[3]=-Quat2[3]
        cosOmega=-cosOmega
    k0=0.0
    k1=0.0
    if cosOmega>0.9999:
        k0=1-t
        k1=t
    else:
        sinOmega=math.sqrt(1.0-cosOmega*cosOmega)
        Omega=math.atan2(sinOmega,cosOmega)
        #Omega=math.acos(cosOmega)
        inverseSin=1.0/sinOmega
        k0=math.sin((1.0-t)*Omega)*inverseSin
        k1=math.sin(t*Omega)*inverseSin
    x=Quat1[0]*k0+Quat2[0]*k1
    y=Quat1[1]*k0+Quat2[1]*k1
    z=Quat1[2]*k0+Quat2[2]*k1
    w=Quat1[3]*k0+Quat2[3]*k1
    result=[x,y,z,w]
    return result

def SLerpOffsetValue(constraint,newTarget,nodeB):
    targetCount = cmds.getAttr(constraint + '.target', size=True)

    nodeBRot = cmds.xform(nodeB, query=True, worldSpace=True, rotation=True)
    nodeBQuat=OpenMaya.MEulerRotation(nodeBRot[0]*(3.1415926/180), nodeBRot[1]*(3.1415926/180), nodeBRot[2]*(3.1415926/180)).asQuaternion()
    tempQuat = OpenMaya.MQuaternion(0.0,0.0,0.0,1.0)
    weight = 1.0/targetCount
    for ti in range(targetCount-2):#获取所有已连接目标的四元数
        target = cmds.listConnections( constraint+'.target[%i].targetRotateOrder'%ti, d=False, s=True)[0]
        rot = cmds.xform(target, query=True, worldSpace=True, rotation=True)
        Quat= OpenMaya.MEulerRotation(rot[0]*(3.1415926/180), rot[1]*(3.1415926/180), rot[2]*(3.1415926/180)).asQuaternion()

        target2 = cmds.listConnections( constraint+'.target[%i].targetRotateOrder'%(ti+1), d=False, s=True)[0]
        rot2 = cmds.xform(target2, query=True, worldSpace=True, rotation=True)
        QuatNext= OpenMaya.MEulerRotation(rot2[0]*(3.1415926/180), rot2[1]*(3.1415926/180), rot2[2]*(3.1415926/180)).asQuaternion()
        tempQuat=QuatSlerp(Quat,QuatNext,weight)
        
    rot2 = cmds.xform(newTarget, query=True, worldSpace=True, rotation=True)
    Orient2= OpenMaya.MEulerRotation(rot2[0]*(3.1415926/180), rot2[1]*(3.1415926/180), rot2[2]*(3.1415926/180)).asQuaternion()
    SlerpValue = QuatSlerp(tempQuat,Orient2,weight)
    SlerpQuat = OpenMaya.MQuaternion(SlerpValue[0],SlerpValue[1],SlerpValue[2],SlerpValue[3])
    differ = (nodeBQuat*SlerpQuat.inverse()).asEulerRotation()
    offsetValue = [differ[0]*(180/3.1415926),differ[1]*(180/3.1415926),differ[2]*(180/3.1415926)]
    return offsetValue
    
def orientConstraint(nodeA,nodeB,outPlug):
    """
    其中oQ,所有四元数插值后的输出值
    平均模式：
        结果上和AverageQuat相同,但是AverageQuat在四元数相差过大会有跳变
        
    最短路径：
        是一个多级SLerp,其中权重w=1/targetCount
        q=slerp(slerp(q1,q2,w),q3,w)
    最长路径：
        同样的slerp,但是cos取反
    """


    """
    connection=True
    linklist=cmds.listConnections( nodeB+'.%s'%outPlug, d=False, s=True)
    if linklist:
        if cmds.nodeType(linklist[0]) == 'orientConstraint':
            constraint=linklist[0]
            connection=False
            offset = SLerpOffsetValue(constraint,nodeA,nodeB)
            cmds.setAttr(constraint+'.offset',offset[0],offset[1],offset[2],type='double3')
        else:
            constraint = cmds.createNode( 'orientConstraint', parent=nodeB )
            cmds.setAttr(constraint+'.interpType',2)
            rot1 = cmds.xform(nodeA, query=True, worldSpace=True, rotation=True)
            rot2 = cmds.xform(nodeB, query=True, worldSpace=True, rotation=True)
            Quat1 = OpenMaya.MEulerRotation(rot1[0]*(3.1415926/180), rot1[1]*(3.1415926/180), rot1[2]*(3.1415926/180)).asQuaternion()
            Quat2 = OpenMaya.MEulerRotation(rot2[0]*(3.1415926/180), rot2[1]*(3.1415926/180), rot2[2]*(3.1415926/180)).asQuaternion()
            differ = (Quat2*Quat1.inverse()).asEulerRotation()
            offsetValue = [differ[0]*(180/3.1415926),differ[1]*(180/3.1415926),differ[2]*(180/3.1415926)]
            cmds.setAttr(constraint+'.offset',offsetValue[0],offsetValue[1],offsetValue[2],type='double3')
    else:
        constraint = cmds.createNode( 'orientConstraint', parent=nodeB )
        cmds.setAttr(constraint+'.interpType',2)
        rot1 = cmds.xform(nodeA, query=True, worldSpace=True, rotation=True)
        rot2 = cmds.xform(nodeB, query=True, worldSpace=True, rotation=True)
        Quat1 = OpenMaya.MEulerRotation(rot1[0]*(3.1415926/180), rot1[1]*(3.1415926/180), rot1[2]*(3.1415926/180)).asQuaternion()
        Quat2 = OpenMaya.MEulerRotation(rot2[0]*(3.1415926/180), rot2[1]*(3.1415926/180), rot2[2]*(3.1415926/180)).asQuaternion()
        differ = (Quat2*Quat1.inverse()).asEulerRotation()
        offsetValue = [differ[0]*(180/3.1415926),differ[1]*(180/3.1415926),differ[2]*(180/3.1415926)]
        cmds.setAttr(constraint+'.offset',offsetValue[0],offsetValue[1],offsetValue[2],type='double3')
    # 获取数组属性的大小
    NextIndex = cmds.getAttr(constraint + '.target', size=True)

    cmds.connectAttr(nodeA+'.rotate', constraint+'.target[%i].targetRotate'%NextIndex)
    cmds.connectAttr(nodeA+'.parentMatrix[0]', constraint+'.target[%i].targetParentMatrix'%NextIndex)
    cmds.connectAttr(nodeA+'.rotateOrder', constraint+'.target[%i].targetRotateOrder'%NextIndex)
    if connection:
        cmds.connectAttr(nodeB+'.parentInverseMatrix[0]', constraint+'.constraintParentInverseMatrix')
        cmds.connectAttr(nodeB+'.rotateOrder', constraint+'.constraintRotateOrder')
        cmds.connectAttr(constraint+'.constraintRotate', nodeB+'.%s'%outPlug)

    """
    rot=cmds.listConnections( nodeB+'.rotate', d=False, s=True ,plugs=True)
    if rot:
        cmds.disconnectAttr(rot[0],nodeB+'.rotate')
    trans=cmds.listConnections( nodeB+'.translate', d=False, s=True ,plugs=True)
    if trans:
        cmds.disconnectAttr(trans[0],nodeB+'.translate')    
    cmds.orientConstraint(nodeA,nodeB,maintainOffset=True)
    


#ref:[https://github.com/alicevision/mayaAPI/blob/master/2016.sp1/linux/lib/python2.7/site-packages/maya/app/mayabullet/RigidBodyConstraint.py]
#localRef:[C:\Program Files\Autodesk\Maya2022\Python27\Lib\site-packages\maya\app\mayabullet]
# CreateRigidBodyConstraint().command()
def RigidBodyConstraint(RigidBodyA,RigidBodyB,transformNode):
#{
    solver = BulletUtils.getSolver()
    constraint = cmds.createNode( 'bulletRigidBodyConstraintShape', parent=transformNode )
    cmds.connectAttr( (solver    +".outSolverInitialized"), (constraint+".solverInitialized") )
    cmds.connectAttr( (RigidBodyA +".outRigidBodyData"),(constraint+".rigidBodyA") )
    cmds.connectAttr( (RigidBodyB  +".outRigidBodyData"), (constraint +".rigidBodyB") )
    cmds.connectAttr( (constraint+".outConstraintData"),   (solver    +".rigidBodyConstraints"), na=True )
    cmds.connectAttr( (solver    +".startTime"), (constraint+".startTime") )
    cmds.connectAttr( (solver    +".currentTime"), (constraint+".currentTime") )
    #因为mmd具有显式设置transformation，所以不要计算两个刚体的中间值
    cmds.setAttr(constraint+'.visibility',0)
    cmds.setAttr(constraint+'.lodVisibility',0)
    return constraint
#}
def ExistsActivateObject(attrName):
    selectList=cmds.ls(selection=True,type=['transform','joint'])
    if selectList:
        if cmds.objExists(selectList[-1] + '.%s'%attrName):
            return True
    return False
def findPanelPopupParent():
    '''
    ref:/..../Maya2022/scripts/others/findPanelPopupParent.mel
    '''
    current = cmds.getPanel(underPointer=True)
    if current and (cmds.panel(current,query=True,exists=True)):
        #获取该面板的paneLayout父面板
        pLayout = cmds.layout(current,query=True,parent=True)
        #如果不属于paneLayout或者workspaceControl则往上查
        while not((cmds.paneLayout(pLayout,query=True,exists=True))or(cmds.workspaceControl(pLayout,query=True,exists=True))):
            pLayout=cmds.control(pLayout,query=True,parent=True)
        if (cmds.paneLayout(pLayout,query=True,exists=True))or(cmds.workspaceControl(pLayout,query=True,exists=True)):
            return pLayout
    return "viewPanes"

def GetRenderingMode():
#{
    #ref:[C:\Users\【UserName】\Documents\maya\2022\zh_CN\prefs\userPrefs.mel]
    vp2RenderingEngine = cmds.optionVar(query='vp2RenderingEngine')
    return vp2RenderingEngine
#}
def getResourcePath(file):
    DataPath=os.path.dirname(os.path.abspath(res.__file__))
    filePath = os.path.join(DataPath,file)
    if os.path.exists(filePath):
        return filePath
    else:
        return None

def getTempPath():
    ModPath=cmds.moduleInfo(path=True, moduleName='MMD2Maya')
    if os.path.exists(ModPath):
        return os.path.normpath(os.path.join(ModPath,'TempTexture')) 
    else:
        return None