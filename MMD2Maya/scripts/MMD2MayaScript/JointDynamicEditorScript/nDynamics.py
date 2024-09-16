import maya.cmds as cmds
import maya.mel as mel

def makeCurveDynamic(curve,hairSys,nucl):
    curveShape = cmds.listRelatives(curve, shapes=True)[0]
    if cmds.objectType( curveShape, isType='nurbsCurve' ):
    #{
        if not hairSys:
        #{
            #立场系统
            nucleus = cmds.createNode( 'nucleus', n=('nucleus_#') )
            #毛发系统
            hairSystem = cmds.createNode( 'hairSystem', n=('hairSystemShape_#') )
            cmds.setAttr((hairSystem+'.active'),1)#使用立场解算器
            cmds.setAttr((hairSystem+'.bendResistance'),0)#弯曲阻力，直接从根部解算
            cmds.setAttr((hairSystem+'.stretchDamp'),10)#拉伸阻力，防止运动过大产生离谱的拉伸解算效果

            # Connect time to hair system and nucleus
            # 为立场和毛发系统接入time
            cmds.connectAttr('time1.outTime', (nucleus + '.currentTime'))
            cmds.connectAttr('time1.outTime', (hairSystem + '.currentTime'))

            # Connect hair system and nucleus together
            cmds.connectAttr((hairSystem + '.currentState'), (nucleus + '.inputActive[0]'))
            cmds.connectAttr((hairSystem + '.startState'), (nucleus + '.inputActiveStart[0]'))
            cmds.connectAttr((nucleus + '.outputObjects[0]'), (hairSystem + '.nextState'))
            cmds.connectAttr((nucleus + '.startFrame'), (hairSystem + '.startFrame'))

            #{ 非必要，引入变量的情况下不需要更改
            hairSystemTransformNode=cmds.listRelatives(hairSystem, parent=True)[0]
            HairSystem_TNode=cmds.rename(hairSystemTransformNode,'HairSystem#')
            #立场是个类似transform&Group的东西？
            #nucleusTransformNode=cmds.listRelatives(nucleus, parent=True)[0]
            #Nucleus=cmds.rename(nucleusTransformNode,'Nucleus')
            #}
            cmds.parent(HairSystem_TNode,nucleus)
        #}
        else :
        #{
            hairSystem=hairSys
            #获取指定节点上的链接目标
            nucleus = nucl
            #cmds.listConnections(hairSystem, type='nucleus')[0]
        #}

        #毛囊系统
        follicle = cmds.createNode( 'follicle', n=('follicleShape#') )
        cmds.setAttr((follicle + '.restPose'), 1)#静止姿势
        cmds.setAttr((follicle+'.startDirection'),1)#解算方向：开始点
        cmds.setAttr((follicle+'.pointLock'),1)#点锁定：起点锁定
        cmds.setAttr((follicle+'.degree'),1)#输出曲线阶数
        #输出曲线
        outputCurve = cmds.createNode( 'nurbsCurve', n=('outputCurve#') )
        #outputCurve = cmds.duplicate(curve,name=('outputCurve_' + curve))[0]
        #outputCurve = cmds.listRelatives(outputCurve, shapes=True)[0]

        # 变换节点和形状节点
        cmds.connectAttr((curve + '.worldMatrix[0]'), (follicle + '.startPositionMatrix'))
        cmds.connectAttr((curveShape + '.local'), (follicle + '.startPosition'))

        # Connect follicle to output curve
        cmds.connectAttr((follicle + '.outCurve'), (outputCurve + '.create'))

        outHairIndex = cmds.getAttr(hairSystem + '.outputHair', size=True)

        # Connect hair system to follicle
        cmds.connectAttr((hairSystem + '.outputHair[{}]'.format(outHairIndex)), (follicle + '.currentPosition'))
        cmds.connectAttr((follicle + '.outHair'), (hairSystem + '.inputHair[{}]'.format(outHairIndex)))
        #
        #
        outCurveTransformNode=cmds.listRelatives(outputCurve, parent=True)[0]
        dynamicCurve=cmds.rename(outCurveTransformNode,'dynamicCurve#')


        follicleTransformNode=cmds.listRelatives(follicle, parent=True)[0]
        Follicle=cmds.rename(follicleTransformNode,'Follicle#')

        staticCurveTransformNode=cmds.listRelatives(curveShape, parent=True)[0]
        staticCurve=cmds.rename(staticCurveTransformNode,'staticCurve#')

        #{整理子父级
        cmds.parent(dynamicCurve,Follicle)
        cmds.parent(staticCurve,Follicle)
        hairSystemTransformNode=cmds.listRelatives(hairSystem, parent=True)[0]
        cmds.parent(Follicle,hairSystemTransformNode)
        
        #}
        # Return all created objects from simulation.
        # 运动曲线，毛发系统，立场系统，毛囊系统，静止曲线
        return [dynamicCurve, hairSystem, nucleus, Follicle, staticCurve]
    #{
    else:
    #{
        raise RuntimeError('makeCurveDynamic()函数输入曲线变量为空')
    #}
def createNucleus():
    #立场系统
    nucleus = cmds.createNode( 'nucleus', n=('nucleus_#') )
    #毛发系统
    hairSystem = cmds.createNode( 'hairSystem', n=('hairSystemShape_#') )
    cmds.setAttr((hairSystem+'.active'),1)#使用立场解算器
    cmds.setAttr((hairSystem+'.bendResistance'),0)#弯曲阻力，直接从根部解算
    cmds.setAttr((hairSystem+'.stretchDamp'),10)#拉伸阻力，防止运动过大产生离谱的拉伸解算效果
    # Connect time to hair system and nucleus
    # 为立场和毛发系统接入time
    cmds.connectAttr('time1.outTime', (nucleus + '.currentTime'))
    cmds.connectAttr('time1.outTime', (hairSystem + '.currentTime'))
    # Connect hair system and nucleus together
    cmds.connectAttr((hairSystem + '.currentState'), (nucleus + '.inputActive[0]'))
    cmds.connectAttr((hairSystem + '.startState'), (nucleus + '.inputActiveStart[0]'))
    cmds.connectAttr((nucleus + '.outputObjects[0]'), (hairSystem + '.nextState'))
    cmds.connectAttr((nucleus + '.startFrame'), (hairSystem + '.startFrame'))
    #{ 非必要，引入变量的情况下不需要更改
    hairSystemTransformNode=cmds.listRelatives(hairSystem, parent=True)[0]
    hairSystemTransformNode=cmds.rename(hairSystemTransformNode,'HairSystem#')
    #}
    cmds.parent(hairSystemTransformNode,nucleus)
    return [nucleus,hairSystemTransformNode]

def createHairSyetem(nucleus):
    #毛发系统
    hairSystem = cmds.createNode( 'hairSystem', n=('hairSystemShape_#') )
    cmds.setAttr((hairSystem+'.active'),1)#使用立场解算器
    cmds.setAttr((hairSystem+'.bendResistance'),0)#弯曲阻力，直接从根部解算
    cmds.setAttr((hairSystem+'.stretchDamp'),10)#拉伸阻力，防止运动过大产生离谱的拉伸解算效果

    cmds.connectAttr('time1.outTime', (hairSystem + '.currentTime'))
    # Connect hair system and nucleus together
    index = cmds.getAttr(nucleus + '.outputObjects', size=True)
    cmds.connectAttr((hairSystem + '.currentState'), (nucleus + '.inputActive[%i]'%index))
    cmds.connectAttr((hairSystem + '.startState'), (nucleus + '.inputActiveStart[%i]'%index))
    cmds.connectAttr((nucleus + '.outputObjects[%i]'%index), (hairSystem + '.nextState'))
    cmds.connectAttr((nucleus + '.startFrame'), (hairSystem + '.startFrame'))
    #{ 非必要，引入变量的情况下不需要更改
    hairSystemTransformNode=cmds.listRelatives(hairSystem, parent=True)[0]
    hairSystemTransformNode=cmds.rename(hairSystemTransformNode,'HairSystem#')
    #}
    cmds.parent(hairSystemTransformNode,nucleus)
    return hairSystemTransformNode
def createDynamic(joints,nucleus,hairSystem):
    jointPositions = []
    print(str(joints))
    for joint in joints:
        worldPos = cmds.xform(joint, query=True, worldSpace=True, translation=True) 
        jointPositions.append(worldPos)

    # 创建曲线 Degree默认为3
    curve_a = cmds.curve(degree=1,point = jointPositions)
    startPoint = cmds.xform(curve_a + '.cv[0]', query=True, worldSpace=True, translation=True)
    cmds.move(startPoint[0], startPoint[1], startPoint[2], curve_a + '.scalePivot', curve_a + '.rotatePivot', absolute=True)
    #cmds.select(clear=True)
    #test= mel.eval('makeCurvesDynamic 2 { "0", "0", "1", "1", "0"};')
    #print(str(test))
    hairSystemShape= cmds.listRelatives(hairSystem, shapes=True)[0]
    outCurve= makeCurveDynamic(curve_a,hairSystemShape,nucleus)
    #hairSystem=outCurve[1]
    #nucleus=outCurve[2]
    # 创建 IK 样条线控制柄
    #	parentCurve指定曲线是否自动移动到最高级骨骼的子集  通过ikSplineHandle
    ik_handle = cmds.ikHandle(sj=joints[0], ee=joints[-1], sol='ikSplineSolver', curve=outCurve[0], createCurve=False,parentCurve=False)

    #将这个IK放置在动态曲线下
    cmds.parent(ik_handle[0],outCurve[0])

    parent = cmds.listRelatives(joints[0], parent=True)
    if parent:
        firstParent = parent[0]
        cmds.parentConstraint(firstParent,outCurve[-1],maintainOffset=True,weight=1.0)
    else:
        print('The current skeleton is not linked to the parent object')