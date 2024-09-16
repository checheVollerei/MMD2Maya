# encoding: utf-8
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import math
import binascii #变形节点以16进制命名

# t = (CurrentTime-startTime)/(endTime-startTime)
#   endTime > CurrentTime > startTime
# endTime：当前帧
# startTime:前一帧

#X：Keyframe
#Y：算前一帧四元数和当前帧四元数的平面角（第一帧假设为《单位四元数》的）

#P0:当前帧(keyframe,value)
#P3:后一帧(keyframe,value)
#P1:outTargent*(P3-P0)+P0
#P2:inTargent*(P3-P0)+P0
#outTargent ：采样后一帧补间曲线.xy, 这个值对应ainmCurve中前一帧的outTargent
#inpTargent ：采样后一帧补间曲线.zw, 这个值对应ainmCurve中当前帧的inpTargent
#其中，补间曲线坐标是归一化后的，既：value/=127 0<=value<=1
class vec2:
    def __init__(self,xValue,yValue):
        self.x = xValue
        self.y = yValue
    def length(self):
        return math.sqrt(self.x*self.x+self.y*self.y)

    def normalize(self):
        l=self.length()
        if l <= 0.0001:
            l=1.0
        return vec2(self.x/l,self.y/l)
    def dot(self,other):
        return self.x*other.x+self.y*other.y
    def RAngle(self,other):
        
        cos = self.normalize().dot(other.normalize())
        r = math.acos(cos)
        return r

    def __add__(self, other):
        return vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return vec2(self.x * other.x, self.y * other.y)

    def __truediv__(self, other):
        return vec2(self.x / other.x, self.y / other.y)

def BezierSample(startTime,endTime,CurrentTime,P0Value,P3Value,Tweened):
    P0=vec2(startTime,P0Value)
    P3=vec2(endTime,P3Value)
    P1=vec2((Tweened[0]/127.0)*(P3.x-P0.x)+P0.x,(Tweened[1]/127.0)*(P3.y-P0.y)+P0.y)
    P2=vec2((Tweened[2]/127.0)*(P3.x-P0.x)+P0.x,(Tweened[3]/127.0)*(P3.y-P0.y)+P0.y)
    t=(CurrentTime-startTime)/(endTime-startTime)#startTime-endTime==>0-1
    u=math.pow(1.0-t,3)*P0.x+3*t*math.pow((1.0-t),2)*P1.x+3*math.pow(t,2)*(1.0-t)*P2.x+math.pow(t,3)*P3.x
    v=math.pow(1.0-t,3)*P0.y+3*t*math.pow((1.0-t),2)*P1.y+3*math.pow(t,2)*(1.0-t)*P2.y+math.pow(t,3)*P3.y
    mapingX=(u-P0.x)/(P3.x-P0.x)
    mapingY=(v-P0.y)/(P3.y-P0.y)
    Value=[mapingX,mapingY]
    return Value

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

class data:

    def __init__(self,mayaNodePath,MD2MayaNodePath,PM,T,R,Orient):
        self.MayaNode       =   mayaNodePath    #string
        self.MdNode         =   MD2MayaNodePath #string
        self.ParentMatrix   =   PM              #MMatrix
        self.staticTranslate=   T               #[0,0,0]
        self.staticRotate   =   R               #[0,0,0]
        self.JointOrient    =   Orient          #MEulerRotation

class Action:

    
    def __init__(self,VmdFile,JG=None,MG=None):
        self.FPS=OpenMaya.MTime.uiUnit()
        if JG:
            self.jointArray=self.searchMD2MayaNode(JG)
            self.buildCurveNode(VmdFile,self.jointArray)
            self.buildIkCurve(VmdFile,self.jointArray)
        if MG:
            self.buildBlendShapeCurve(VmdFile,MG)
        

    def searchMD2MayaNode(self,jointGroup):
    #{
        selectArray = cmds.listRelatives(jointGroup ,fullPath=True,type=['transform','joint'], allDescendents = True)
        selectArray.append(jointGroup)
        NodeTab={}
        for bone in selectArray:
        #{
                handleMD2M=cmds.listConnections(bone+'.message', type="MD2MayaNode")
                if not handleMD2M:
                    continue
                mdName = cmds.getAttr(handleMD2M[0]+'.MDnBoneName')
                if not mdName:
                    continue
                if (mdName not in NodeTab):
                    pmArray =cmds.getAttr(bone+'.parentMatrix[0]')
                    ParentMatrix = OpenMaya.MMatrix()
                    #这是openmaya1.0的M矩阵在python中的读写方式
                    for r in range(4):
                        for f in range(4):
                            #ref:[https://groups.google.com/g/python_inside_maya/c/Gou02IHsYKA]
                            OpenMaya.MScriptUtil.setDoubleArray(ParentMatrix[r], f, pmArray[r*4+f])
                    Translate=cmds.getAttr(bone+'.MnTranslate')[0]
                    Rotate=cmds.getAttr(bone+'.MnRotate')[0]
                    Orient=OpenMaya.MEulerRotation(0,0,0)
                    if cmds.objExists(bone + '.jointOrient'):
                        orValue=cmds.getAttr(bone + '.jointOrient')[0]
                        Orient= OpenMaya.MEulerRotation(orValue[0]*(3.1415926/180), orValue[1]*(3.1415926/180), orValue[2]*(3.1415926/180))
                    NodeTab[mdName]=data(bone,handleMD2M[0],ParentMatrix,Translate,Rotate,Orient)
        #}
        return NodeTab
    #}
    def buildCurveNode(self,flie,jTab):
        for key in flie.BoneMotionData:
        #{
            if(key in jTab):
                da      = jTab[key]
                path1   = da.MayaNode
                selectList  = OpenMaya.MSelectionList()
                selectList.add(path1)
                jointObj=OpenMaya.MObject()
                selectList.getDependNode(0,jointObj)

                Action.disconnectPlug(str(path1)+'.MnTranslateX')
                Action.disconnectPlug(str(path1)+'.MnTranslateY')
                Action.disconnectPlug(str(path1)+'.MnTranslateZ')
                Action.disconnectPlug(str(path1)+'.MnRotateX')
                Action.disconnectPlug(str(path1)+'.MnRotateY')
                Action.disconnectPlug(str(path1)+'.MnRotateZ')

                TranslateX = OpenMaya.MPlug( OpenMaya.MFnDependencyNode(jointObj).findPlug('MnTranslateX',True))
                TranslateY = OpenMaya.MPlug( OpenMaya.MFnDependencyNode(jointObj).findPlug('MnTranslateY',True))
                TranslateZ = OpenMaya.MPlug( OpenMaya.MFnDependencyNode(jointObj).findPlug('MnTranslateZ',True))

                RotateX = OpenMaya.MPlug( OpenMaya.MFnDependencyNode(jointObj).findPlug('MnRotateX',True))
                RotateY = OpenMaya.MPlug( OpenMaya.MFnDependencyNode(jointObj).findPlug('MnRotateY',True))
                RotateZ = OpenMaya.MPlug( OpenMaya.MFnDependencyNode(jointObj).findPlug('MnRotateZ',True))

                #帧数组
                TimeArray    = OpenMaya.MTimeArray()
                #平移数组
                xTransformValue = OpenMaya.MDoubleArray()
                yTransformValue = OpenMaya.MDoubleArray()
                zTransformValue = OpenMaya.MDoubleArray()
                #旋转数组
                xRotateValue  = OpenMaya.MDoubleArray()
                yRotateValue  = OpenMaya.MDoubleArray()
                zRotateValue  = OpenMaya.MDoubleArray()
                #{初始姿态
                TimeArray.append(OpenMaya.MTime(1,self.FPS))
                xTransformValue.append(da.staticTranslate[0])
                yTransformValue.append(da.staticTranslate[1])
                zTransformValue.append(da.staticTranslate[2])
                xRotateValue.append(0.0)
                yRotateValue.append(0.0)
                zRotateValue.append(0.0)
                #}
                #平移补间曲线【[lastox,lastoy,currentix,currentiy],[],[]】
                TTweened = {}
                #根据帧获取原始的四元数和补间曲线
                #frame:[quat,Tweene]
                QuatTable={}
                for motion in (flie.BoneMotionData[key]):
                #{  
                    #worldPos = OpenMaya.MPoint(motion.Translation[0],motion.Translation[1],-motion.Translation[2],1)
                    #localPos=worldPos*da.ParentMatrix.inverse()
                    worldPos = OpenMaya.MVector(motion.Translation[0],motion.Translation[1],-motion.Translation[2])
                    #Point*MMatrix在脚本里行不通,以矩阵构建TM，然后以w写入点以o读取
                    boneMatrix  = OpenMaya.MTransformationMatrix(da.ParentMatrix)
                    boneMatrix.setTranslation(worldPos,OpenMaya.MSpace.kWorld)
                    localPos=boneMatrix.getTranslation(OpenMaya.MSpace.kObject)
                    #ref:[https://mikumikudance.fandom.com/wiki/VMD_file_format]
                    #这篇文章描述了动画位置和静态姿势的偏移关系
                    localPos.x=localPos[0]+da.staticTranslate[0]
                    localPos.y=localPos[1]+da.staticTranslate[1]
                    localPos.z=localPos[2]+da.staticTranslate[2]

                    quaternion =    [   -motion.Rotation[0],
                                        -motion.Rotation[1],
                                        motion.Rotation[2],
                                        motion.Rotation[3]
                                    ]
                    MQuat = OpenMaya.MQuaternion(quaternion[0],quaternion[1],quaternion[2],quaternion[3])

                    worldRotateEuler=MQuat.asEulerRotation()
                    #把世界空间的旋转转到父级空间下，旋转值是直立坐标空间的变换，所以还要抵消骨骼旋转轴
                    offsetMatrix=da.JointOrient.asMatrix()*da.ParentMatrix
                    pRotate=offsetMatrix*worldRotateEuler.asMatrix()*offsetMatrix.inverse()
                    LRotate=OpenMaya.MTransformationMatrix(pRotate).rotation()
                    localRotate =LRotate.asEulerRotation()
                    #补间曲线
                    QuatTweene=(motion.QuatLerp)
                    #帧
                    frameTime= motion.FrameTime+50
                    time=OpenMaya.MTime(frameTime,self.FPS)

                    TimeArray.append(time)
                    xTransformValue.append(localPos[0])
                    yTransformValue.append(localPos[1])
                    zTransformValue.append(localPos[2])
                    xRotateValue.append(localRotate[0])
                    yRotateValue.append(localRotate[1])
                    zRotateValue.append(localRotate[2])
                    TableValue=[quaternion,QuatTweene]
                    QuatTable[time.value()]=TableValue

                    lastOX = vec2(motion.TweenedX[0]/127.0,motion.TweenedX[1]/127.0)
                    currentiIX= vec2(motion.TweenedX[2]/127.0,motion.TweenedX[3]/127.0)
                    lastOY = vec2(motion.TweenedY[0]/127.0,motion.TweenedY[1]/127.0)
                    currentiIY= vec2(motion.TweenedY[2]/127.0,motion.TweenedY[3]/127.0)
                    lastOZ = vec2(motion.TweenedZ[0]/127.0,motion.TweenedZ[1]/127.0)
                    currentiIZ= vec2(motion.TweenedZ[2]/127.0,motion.TweenedZ[3]/127.0)

                    tweenedXYZ=[lastOX,lastOY,lastOZ,currentiIX,currentiIY,currentiIZ]
                    TTweened[time.value()]=tweenedXYZ
                #}
                if not (cmds.getAttr(path1 + '.MnTranslateX', lock = True)):
                    # 创建动画曲线TL:Linear 
                    TranslateCurveFn_x = OpenMayaAnim.MFnAnimCurve()
                    animCurveT_x = TranslateCurveFn_x.create(TranslateX, OpenMayaAnim.MFnAnimCurve.kAnimCurveTL)
                    TranslateCurveFn_y = OpenMayaAnim.MFnAnimCurve()
                    animCurveT_y = TranslateCurveFn_y.create(TranslateY, OpenMayaAnim.MFnAnimCurve.kAnimCurveTL)
                    TranslateCurveFn_z = OpenMayaAnim.MFnAnimCurve()
                    animCurveT_z = TranslateCurveFn_z.create(TranslateZ, OpenMayaAnim.MFnAnimCurve.kAnimCurveTL)
                    TranslateCurveFn_x.setIsWeighted(True)
                    TranslateCurveFn_y.setIsWeighted(True)
                    TranslateCurveFn_z.setIsWeighted(True)
                    TranslateCurveFn_x.addKeys(TimeArray,xTransformValue,OpenMayaAnim.MFnAnimCurve.kTangentLinear ,OpenMayaAnim.MFnAnimCurve.kTangentLinear )
                    TranslateCurveFn_y.addKeys(TimeArray,yTransformValue,OpenMayaAnim.MFnAnimCurve.kTangentLinear ,OpenMayaAnim.MFnAnimCurve.kTangentLinear )
                    TranslateCurveFn_z.addKeys(TimeArray,zTransformValue,OpenMayaAnim.MFnAnimCurve.kTangentLinear ,OpenMayaAnim.MFnAnimCurve.kTangentLinear )
                    AnimCurveList=[TranslateCurveFn_x,TranslateCurveFn_y,TranslateCurveFn_z]

                    for index in range(len(AnimCurveList)):
                    #{
                        Action.SampleCuverTangent(AnimCurveList[index],TTweened,index)
                    #}
                    #函数（animCurve,tweened,）
                    
                #try:
                if not (cmds.getAttr(path1 + '.MnRotateX', lock=True)):
                    # 创建动画曲线TA:Angle
                    RotateCurveFn_x = OpenMayaAnim.MFnAnimCurve()
                    animCurveR_x = RotateCurveFn_x.create(RotateX, OpenMayaAnim.MFnAnimCurve.kAnimCurveTA)
                    RotateCurveFn_y = OpenMayaAnim.MFnAnimCurve()
                    animCurveR_y = RotateCurveFn_y.create(RotateY, OpenMayaAnim.MFnAnimCurve.kAnimCurveTA)
                    RotateCurveFn_z = OpenMayaAnim.MFnAnimCurve()
                    animCurveR_z = RotateCurveFn_z.create(RotateZ, OpenMayaAnim.MFnAnimCurve.kAnimCurveTA)
                    #添加关键帧
                    RotateCurveFn_x.addKeys(TimeArray,xRotateValue,OpenMayaAnim.MFnAnimCurve.kTangentLinear ,OpenMayaAnim.MFnAnimCurve.kTangentLinear )
                    RotateCurveFn_y.addKeys(TimeArray,yRotateValue,OpenMayaAnim.MFnAnimCurve.kTangentLinear ,OpenMayaAnim.MFnAnimCurve.kTangentLinear )
                    RotateCurveFn_z.addKeys(TimeArray,zRotateValue,OpenMayaAnim.MFnAnimCurve.kTangentLinear ,OpenMayaAnim.MFnAnimCurve.kTangentLinear )
                    RotateKeyNumber=RotateCurveFn_x.numKeys()
                    LerpTimeArray=OpenMaya.MTimeArray()
                    lerpXR=OpenMaya.MDoubleArray()
                    lerpYR=OpenMaya.MDoubleArray()
                    lerpZR=OpenMaya.MDoubleArray()
                    for twk in range(1,RotateKeyNumber-1):
                    #{
                        at=int(RotateCurveFn_x.time(twk).value())
                        nt=int(RotateCurveFn_x.time(twk+1).value())
                        if at+1 != nt:
                            Quat1   =   QuatTable[at][0]
                            Quat2   =   QuatTable[nt][0]
                            Tweened =   QuatTable[nt][1]
                            for twt in range(at+1,nt):
                                bezierValue=BezierSample(float(at),float(nt),float(twt),10,20,Tweened)
                                #t=(float(twt-at))/(float(nt-at))
                                t=bezierValue[1]
                                TwQuat=QuatSlerp(Quat1,Quat2,t)
                                MtwQuat = OpenMaya.MQuaternion(TwQuat[0],TwQuat[1],TwQuat[2],TwQuat[3])
                                lerpEuler=MtwQuat.asEulerRotation()
                                #把世界空间的旋转转到父级空间下
                                #pRotate=lerpEuler.asMatrix()*da.ParentMatrix.inverse()
                                offsetMatrix=da.JointOrient.asMatrix()*da.ParentMatrix
                                pRotate=offsetMatrix*lerpEuler.asMatrix()*offsetMatrix.inverse()
                                LRotate=OpenMaya.MTransformationMatrix(pRotate).rotation()
                                #现在的pRotate应该就是正常的旋转值了
                                localRotate = LRotate.asEulerRotation()
                                lerpXR.append(localRotate[0])
                                lerpYR.append(localRotate[1])
                                lerpZR.append(localRotate[2])
                                MLerpTime=OpenMaya.MTime(twt,self.FPS)
                                LerpTimeArray.append(MLerpTime)
                    if(LerpTimeArray.length()>0):
                        RotateCurveFn_x.addKeys(LerpTimeArray,lerpXR,OpenMayaAnim.MFnAnimCurve.kTangentLinear ,OpenMayaAnim.MFnAnimCurve.kTangentLinear,True )
                        RotateCurveFn_y.addKeys(LerpTimeArray,lerpYR,OpenMayaAnim.MFnAnimCurve.kTangentLinear ,OpenMayaAnim.MFnAnimCurve.kTangentLinear,True )
                        RotateCurveFn_z.addKeys(LerpTimeArray,lerpZR,OpenMayaAnim.MFnAnimCurve.kTangentLinear ,OpenMayaAnim.MFnAnimCurve.kTangentLinear,True )
                        #print('总帧数'+str(keys))
                #}
                #except Exception as e:
                   # traceback.print_exc()
                    #嵌入表达式和已经链接过的节点不能嵌入曲线
                  #  print('旋转节点创建失败：'+str(e))
                

        #}
    def buildBlendShapeCurve(self,flie,MorphNode):
        selectList  = OpenMaya.MSelectionList()
        selectList.add(MorphNode)
        HandleObj=OpenMaya.MObject()
        selectList.getDependNode(0,HandleObj)
        for MorphName in flie.MorphMotionData:
            deStr =  binascii.hexlify(MorphName.encode())
            hexStr =str('Morph')+str(deStr.decode()) #控制BlendShape的权重属性名称
            #查询这个节点是否拥有给定属性
            hasAttr =  cmds.objExists(MorphNode + '.' + hexStr)
            if hasAttr:
                Action.disconnectPlug(MorphNode + '.' + hexStr)
                plug = OpenMaya.MPlug( OpenMaya.MFnDependencyNode(HandleObj).findPlug(hexStr,True))
                TimeArray = OpenMaya.MTimeArray()
                ValueArray = OpenMaya.MDoubleArray()
                for frame in flie.MorphMotionData[MorphName]:
                #{
                    frameTime= frame.FrameTime
                    time=OpenMaya.MTime(frameTime,self.FPS)
                    TimeArray.append(time)

                    weight = frame.weight
                    ValueArray.append(weight)
                #}
                blendShapeCurve = OpenMayaAnim.MFnAnimCurve()
                animCurveObj = blendShapeCurve.create(plug, OpenMayaAnim.MFnAnimCurve.kAnimCurveTU)
                blendShapeCurve.addKeys(
                                        TimeArray,
                                        ValueArray,
                                        OpenMayaAnim.MFnAnimCurve.kTangentLinear,
                                        OpenMayaAnim.MFnAnimCurve.kTangentLinear,True )

    def buildIkCurve(self,file,jTab):
        for ikName in file.IKMotionData:
        #{
            if (ikName in jTab):
            #{
                nodeData = jTab[ikName]
                selectList  = OpenMaya.MSelectionList()
                selectList.add(nodeData.MdNode)
                nodeObj=OpenMaya.MObject()
                selectList.getDependNode(0,nodeObj)
                Action.disconnectPlug(nodeData.MdNode + '.' + 'MDnIKState')
                ikStatePlug = OpenMaya.MPlug(OpenMaya.MFnDependencyNode(nodeObj).findPlug('MDnIKState',True))
                TimeArray = OpenMaya.MTimeArray()
                ValueArray = OpenMaya.MDoubleArray()
                for keys in file.IKMotionData[ikName]:
                    frameTime = OpenMaya.MTime(keys.FrameTime,self.FPS)
                    value =float(keys.Eanble)
                    TimeArray.append(frameTime)
                    ValueArray.append(value)
                ikCurve = OpenMayaAnim.MFnAnimCurve()
                animCurveObj = ikCurve.create(ikStatePlug, OpenMayaAnim.MFnAnimCurve.kAnimCurveTU)
                ikCurve.addKeys(TimeArray,ValueArray,OpenMayaAnim.MFnAnimCurve.kTangentLinear ,OpenMayaAnim.MFnAnimCurve.kTangentLinear,True )
            #}
        #}
    @staticmethod
    def disconnectPlug(plugName):
        #获取这个属性的链接列表
        if not cmds.connectionInfo(plugName,isDestination=True):
            return
        sNode=cmds.listConnections( plugName, d=False, s=True ,plugs=False)
        if sNode and (cmds.nodeType(sNode[0],inherited=True)[0]=='animCurve'):
            cmds.delete(sNode[0])
        elif sNode :
            sPlug = cmds.listConnections( plugName, d=False, s=True ,plugs=True)[0]
            cmds.disconnectAttr(sPlug,plugName)

        
    @staticmethod
    def SampleCuverTangent(AnimaCurve,TweenedList,AxisIndex):
    #{
        """
        AxisIndex: 
            input:  X,Y,Z:0,1,2
            output: X,Y,Z:3,4,5
        """
        KeyNumber=AnimaCurve.numKeys()
        #看起来三通道帧数一致，就先这么写着
        #设置当前帧的出射切线和下一帧的入射切线
        for act in range(1,KeyNumber-1):
        #{
            #第一个帧的帧位置
            #30/1
            CurTime    = int(AnimaCurve.time(act).value())
            NextTime   = int(AnimaCurve.time(act+1).value())
            #出射区间=下一帧值-当前值
            CurValue = AnimaCurve.value(act)
            NextValue = AnimaCurve.value(act+1)
            
            curTweenedoutput = TweenedList[NextTime][AxisIndex]
            nextTweenedinput = TweenedList[NextTime][AxisIndex+3]
            
            p0 = vec2(float(CurTime),float(CurValue))
            p3 = vec2(float(NextTime),float(NextValue))
            p1 = (p3-p0)*curTweenedoutput
            p2 = (p0-p3)*vec2(1.0-nextTweenedinput.x,1.0-nextTweenedinput.y)
            p1Angle =p1.RAngle(vec2(1.0,0.0)) 
            p1L = p1.length()
            p2Angle =p2.RAngle(vec2(-1.0,0.0))
            p2L = p2.length()
            if(CurValue>NextValue):
                p1Angle*=-1
                p2Angle*=-1
            p1MAngle=OpenMaya.MAngle(p1Angle,OpenMaya.MAngle.kRadians) 
            p2MAngle=OpenMaya.MAngle(p2Angle,OpenMaya.MAngle.kRadians)
            #对于出入切线分别设置的时候，要在之前将切线编辑类型设置为非统一切线
            #Angle：对于入切线=切线点到控制点向量在-x象限上基于x的角度，出切线则是+x
            #weight:出入切线点到控制点的距离(向量长度，单看这个值和p0p3的阈值区间无关)
            AnimaCurve.setTangentsLocked(act,False)
            AnimaCurve.setTangentsLocked(act+1,False)
            AnimaCurve.setTangent(act,p1MAngle,p1L,False,None,True)
            AnimaCurve.setTangent(act+1,p2MAngle,p2L,True,None,True)
        #}
    #}