# -*- encoding: utf-8 -*-

import os
import binascii #变形节点以16进制命名
import importlib
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.app.mayabullet as bullet
import maya.OpenMayaAnim as OpenMayaAnim
from MMD2MayaScript import Utils as Util
from MMD2MayaScript.PmxEditorScript import PmxRead as PMX
#每次加载这个脚本的时候重载一次，不然它不会刷新
importlib.reload(PMX)
importlib.reload(Util)

#以插件编写python的时候需要以api.OpenMaya引入文件
#注意python版本是python3

class BuildScene:
    NameTable={
        '操作中心':'viewController',
        '全ての親':'mother',
        'グルーブ':'groove',
        'センター':'center',
        '上半身':'upperBody',
        '上半身2':'upperBody2',
        '下半身':'lowerBody',
        '首':'neck',
        '頭':'head',
        '腰':'waist',
        '腰キャンセル左':'waist_amend_L',
        '腰キャンセル右':'waist_amend_R',
        '両目':'eyes',
        #上半身左边骨骼
        '左目':'eye_L',
        '左肩P':'shoulderP_L',
        '左肩':'shoulder_L',
        '左肩C':'shoulderC_L',
        '左腕':'arm_L',
        '左ひじ':'elbow_L',
        '左手首':'wrist_L',
        '左手先':'hand_tip_L',
        '左ダミー':'dummy_L',
        '左親指０':'thumb0_L',
        '左親指１':'thumb1_L',
        '左親指２':'thumb2_L',
        '左親指先':'thumb_tip_L',
        '左人指０':'fore0_L',
        '左人指１':'fore1_L',
        '左人指２':'fore2_L',
        '左人指３':'fore3_L',
        '左人指先':'fore_tip_L',
        '左中指０':'middle0_L',
        '左中指１':'middle1_L',
        '左中指２':'middle2_L',
        '左中指３':'middle3_L',
        '左中指先':'middle_tip_L',
        '左薬指０':'third0_L',
        '左薬指１':'third1_L',
        '左薬指２':'third2_L',
        '左薬指３':'third3_L',
        '左薬指先':'third_tip_L',
        '左小指０':'little0_L',
        '左小指１':'little1_L',
        '左小指２':'little2_L',
        '左小指３':'little3_L',
        '左小指先':'little_tip_L',
        
        #上半身右边骨骼
        '右目':'eye_R',
        '右肩P':'shoulderP_R',
        '右肩':'shoulder_R',
        '右肩C':'shoulderC_R',
        '右腕':'arm_R',
        '右ひじ':'elbow_R',
        '右手首':'wrist_R',
        '右手先':'hand_tip_R',
        '右ダミー':'dummy_R',
        '右親指０':'thumb0_R',
        '右親指１':'thumb1_R',
        '右親指２':'thumb2_R',
        '右親指先':'thumb_tip_R',
        '右人指０':'fore0_R',
        '右人指１':'fore1_R',
        '右人指２':'fore2_R',
        '右人指３':'fore3_R',
        '右人指先':'fore_tip_R',
        '右中指０':'middle0_R',
        '右中指１':'middle1_R',
        '右中指２':'middle2_R',
        '右中指３':'middle3_R',
        '右中指先':'middle_tip_R',
        '右薬指０':'third0_R',
        '右薬指１':'third1_R',
        '右薬指２':'third2_R',
        '右薬指３':'third3_R',
        '右薬指先':'third_tip_R',
        '右小指０':'little0_R',
        '右小指１':'little1_R',
        '右小指２':'little2_R',
        '右小指３':'little3_R',
        '右小指先':'little_tip_R',

        '左足':'leg_L',
        '左足D':'legD_L',
        '左ひざ':'knee_L',
        '左ひざD':'kneeD_L',
        '左足首':'ankle_L',
        '左足首D':'ankleD_L',
        '左足先EX':'footEX_L',
        '左つま先':'toe_L',
        '右足':'leg_R',
        '右足D':'legD_R',
        '右ひざ':'knee_R',
        '右ひざD':'kneeD_R',
        '右足首':'ankle_R',
        '右足首D':'ankleD_R',
        '右足先EX':'footEX_R',
        '右つま先':'toe_R',

        '左足IK親':'leg IKP_L',
        '左足ＩＫ':'leg_IK_L',
        '左つま先ＩＫ':'toe_IK_L',
        '右足IK親':'leg IKP_R',
        '右足ＩＫ':'leg_IK_R',
        '右つま先ＩＫ':'toe_IK_R'
    }
    ToonMaping=[
        'toon0.bmp',
        'toon01.bmp',
        'toon02.bmp',
        'toon03.bmp',
        'toon04.bmp',
        'toon05.bmp',
        'toon06.bmp',
        'toon07.bmp',
        'toon08.bmp',
        'toon09.bmp',
        'toon10.bmp',
        ]
    def __init__(self,TexFile,shaderFile,Physics,Shading):
    #{
        self.TexturePath=TexFile
        self.shaderPath=shaderFile
        self.shadingType=Shading
        self.PhysicsType=Physics
        B_transform=OpenMaya.MFnTransform()
        self.Root=B_transform.create()
        B_transform.setName('MMDGroup')
    #}
    
    def BulidMesh(self,vex,index):
    #{
        if(len(vex)<=0)or(len(index)<=0):
            return

        points = OpenMaya.MFloatPointArray()
        normals=OpenMaya.MVectorArray()
        pointId=OpenMaya.MIntArray()
        uArray = OpenMaya.MFloatArray()
        vArray = OpenMaya.MFloatArray()
        polygon_counts = OpenMaya.MIntArray(int(len(index)/3),3)
        pointIndex = OpenMaya.MIntArray()
        for i in range(len(vex)):
        #{

            points.append(vex[i].Vertex[0],vex[i].Vertex[1],-vex[i].Vertex[2])
            normal=OpenMaya.MVector(vex[i].Normal[0],vex[i].Normal[1],-vex[i].Normal[2])
            pointId.append(i)
            normals.append(normal)
            uArray.append(vex[i].Texcoord[0])
            vArray.append(1-vex[i].Texcoord[1])
        #}
        for i in range(0,len(index),3):
        #{
            #[1,2,3]==>>[3,2,1]#反转面朝向
            #改了法线不改组成顺序会导致maya内部的面朝向和法线朝向对不上
            pointIndex.append(index[i+2].Index)
            pointIndex.append(index[i+1].Index)
            pointIndex.append(index[i].Index)
        #}
        mesh_fn = OpenMaya.MFnMesh()
        MeshNode= mesh_fn.create(points.length(),polygon_counts.length(), points,polygon_counts, pointIndex,uArray,vArray)
        mesh_fn.assignUVs(polygon_counts,pointIndex)
        mesh_fn.setVertexNormals(normals,pointId,OpenMaya.MSpace.kObject)
        meshPath = OpenMaya.MDagPath()
        OpenMaya.MDagPath.getAPathTo(MeshNode,meshPath)
        return meshPath
    #}
    def BuildBlendShape(self,meshObj,MorphData):
    #{
        if(meshObj==None)or(len(MorphData)<=0):
            return
        meshPath=meshObj.fullPathName()
        MorphTransform=OpenMaya.MFnTransform()
        MorphNode=MorphTransform.create(self.Root)
        MorphTransform.setName('Morph')
        numFn=OpenMaya.MFnNumericAttribute()
        MorphDep = OpenMaya.MFnDependencyNode(MorphNode)
        #复制这个mesh
        TempMesh=[]
        for ms in range(len(MorphData)):
        #{
            shapeName=MorphData[ms].MorphName
            deStr   = binascii.hexlify(shapeName.encode())
            hexStr  = str('Morph')+str(deStr.decode())
            attr=numFn.create(hexStr,hexStr,OpenMaya.MFnNumericData.kFloat, 0)
            numFn.setReadable(True)
            numFn.setWritable(True)
            numFn.setStorable(True)
            numFn.setKeyable(False)
            numFn.setChannelBox(True)
            numFn.setNiceNameOverride(shapeName)
            numFn.setMin(0.0)#设置完clamp后maya内部会以side绘制UI
            numFn.setMax(1.0)
            MorphDep.addAttribute(attr)
            if MorphData[ms].MorphType==1:

                MorphMesh   = cmds.duplicate(meshPath,name=hexStr)[0]
                selelis     = OpenMaya.MSelectionList()
                selelis.add(MorphMesh)
                MorphMeshDagPath = OpenMaya.MDagPath()
                selelis.getDagPath(0,MorphMeshDagPath)

                #为这个path填MFnMesh，其中的所有改动会反馈到path所在的mesh
                targetMesh    = OpenMaya.MFnMesh(MorphMeshDagPath)
                MorphPointArray = OpenMaya.MFloatPointArray()
                targetMesh.getPoints(MorphPointArray,OpenMaya.MSpace.kObject)
                for i in range( MorphData[ms].DataSize):
                    index   =   MorphData[ms].VertexIndex[i]
                    offset  =   MorphData[ms].VertexOffset[i]
                    pos     =   MorphPointArray[index]

                    MorphPointArray.set(index,pos[0]+offset[0],pos[1]+offset[1],pos[2]-offset[2])

                targetMesh.setPoints(MorphPointArray,OpenMaya.MSpace.kObject)

                MorphPath   =   MorphMeshDagPath.fullPathName()

                TempMesh.append(MorphPath)
        #}
        #防止使用这个插件的时候选中物体，每次使用lelect之前clear一下
        cmds.select(clear = True)
        cmds.select(TempMesh,add=True)#选择所有的形变物体
        cmds.select(meshPath,add=True)#加选择这个物体
        BlendShapPath = cmds.blendShape(name='MMDBlendShap#')[0]
        cmds.delete(TempMesh)#删除所有的形变物体
        cmds.select(clear = True)
        #这段应该放在蒙皮之前但其他都创建之后
        for md in range(len(MorphData)):
            handlePath = MorphDep.absoluteName()
            shapeName=MorphData[md].MorphName
            deStr   =  binascii.hexlify(shapeName.encode())
            hexStr  =  str('Morph')+str(deStr.decode())
            if MorphData[md].MorphType==0:

                for lis in range(len(MorphData[md].MorphIndex)):
                    weight=cmds.shadingNode('floatMath', asUtility=True)
                    cmds.connectAttr(handlePath + "."+hexStr, weight + ".floatA")
                    cmds.setAttr(weight+'.floatB',MorphData[md].MorphInfluence[lis])
                    cmds.setAttr(weight+'.operation',2)#相乘
                    OtherIndex=MorphData[md].MorphIndex[lis]
                    otherName=MorphData[OtherIndex].MorphName
                    otherEncode =  binascii.hexlify(otherName.encode())
                    otherHexStr = str('Morph')+str(otherEncode.decode())
                    MixWeight =cmds.shadingNode('floatMath', asUtility=True)
                    cmds.setAttr(MixWeight+'.operation',0)#相加
                    cmds.connectAttr(weight + ".outFloat", MixWeight + ".floatA")
                    cmds.connectAttr(handlePath + "."+otherHexStr, MixWeight + ".floatB")
                    cmds.connectAttr(MixWeight + ".outFloat", BlendShapPath + "."+otherHexStr,force=True)
            elif MorphData[md].MorphType==1:
                if not cmds.connectionInfo( BlendShapPath + "."+hexStr, isDestination=True):
                    cmds.connectAttr(handlePath + "."+hexStr, BlendShapPath + "."+hexStr,force=False)
            else:
                cmds.setAttr(handlePath + "."+hexStr,lock=True)
    #}
    def createTextureNode(self,absTexturePath):
        if absTexturePath==None:
            return
        TextureNode=[]
        for path in absTexturePath:
            fileNode=None
            NodeName= os.path.splitext(os.path.basename(path))[0]
            print(NodeName)
            if os.path.exists(path):
                fileNode   =   cmds.shadingNode("file", asTexture=True,name=NodeName+'#')
                cmds.setAttr(fileNode + ".fileTextureName",path , type="string")
            TextureNode.append(fileNode)
        return TextureNode
        
    def LambertMaterial(self,meshObj,MaterialData,TextureNodeList):
    #{
        if(meshObj==None)or(len(MaterialData)<=0)or(len(TextureNodeList)<=0):
            return
        meshPath=meshObj.fullPathName()
        cmds.select(clear = True)
        cmds.select(meshPath)#选择这个物体
        LastVex=0
        for Mindex in range(0,len(MaterialData)):
        #{
            material    =   cmds.shadingNode("lambert",name=meshPath+'_mat_'+str(Mindex),asShader=True)
            matName     =   MaterialData[Mindex].LocalName
            cmds.addAttr(material,longName='MMDName',niceName='MMD名称',dataType='string')
            cmds.setAttr(material+'.MMDName',matName,type='string')
            TexIndex    =   MaterialData[Mindex].TextureIndex
            # 设置文件纹理节点的图片路径
            texNode = TextureNodeList[TexIndex]
            # 将文件纹理节点链接到材质的颜色属性上
            if texNode!=None:
                cmds.connectAttr(texNode + ".outColor", material + ".color")
            #.f[始:终]
            cmds.select(meshPath + ".f[%i:%i]" %((LastVex+3)/3-1 , (LastVex+MaterialData[Mindex].Influence)/3), r = True)
            cmds.hyperShade(assign = material)
            #由于材质赋予的面并非对应整个uv壳，那么移动的时候可能会导致uv散乱
            # 将选定的顶点转换为UV ,
            #uvs = cmds.polyListComponentConversion(toUV=True)
            #cmds.select(clear = True)
            #cmds.select(uvs,add=True)
            #UVoffset = materialTable[relTexPath][1]
            ## 移动选定的UV坐标
            #cmds.polyEditUV(relative=True,uValue=UVoffset, vValue=0)

            #获取当前材质的最大影响数量，去位偏移下个材质的影响置，每个材质的索引范围是【0，影响数量】
            LastVex+=MaterialData[Mindex].Influence
        #}
        cmds.select(clear = True)
    #}
    def ShaderFxMaterial(self,shaderPath,meshObj,MaterialData,TextureNodeList):
        if(meshObj==None)or(len(MaterialData)<=0)or(len(TextureNodeList)<=0):
            return
        meshPath=meshObj.fullPathName()
        cmds.select(clear = True)
        cmds.select(meshPath)
        LastVex=0
        bToonTex={}
        for Mindex in range(0,len(MaterialData)):
            shader=cmds.shadingNode("ShaderfxShader",name='_mat_'+str(Mindex),asShader=True)
            cmds.shaderfx(sfxnode=shader,loadGraph = shaderPath)
            dif = MaterialData[Mindex].Diffuse
            amb = MaterialData[Mindex].Ambient
            cmds.setAttr(shader+'.Diffuse',dif[0],dif[1],dif[2],type='float3')
            cmds.setAttr(shader+'.Ambient',amb[0],amb[1],amb[2],type='float3')
            cmds.setAttr(shader+'.Alpha',dif[3])
            texid = cmds.shaderfx(sfxnode=shader,getNodeIDByName = 'AlbedoTex')
            texAttr = 'AlbedoTex'+str(texid)#对于Group,它的dagNode上的属性名需要加上NodeID
            TexIndex    =   MaterialData[Mindex].TextureIndex
            texNode = TextureNodeList[TexIndex]
            if texNode!=None:
                hasAlpha=cmds.getAttr(texNode+'.fileHasAlpha')
                ShadingStateID=cmds.shaderfx(sfxnode=shader,getNodeIDByName = 'AlphaBlending')
                cmds.shaderfx(sfxnode=shader,edit_bool = [ShadingStateID,'value',hasAlpha])#根据图像文件是否有alpha来选择绘制模式
                cmds.connectAttr(texNode + ".fileTextureName", shader+'.%s'%texAttr)
                cmds.setAttr(shader+'.userAlbedoTex',True)

            if MaterialData[Mindex].SpaceMaping!=-1:
                mapIndex = MaterialData[Mindex].SpaceMaping
                mapingTex=TextureNodeList[mapIndex]
                if (mapingTex!=None):
                    
                    mapGroupId = cmds.shaderfx(sfxnode=shader,getNodeIDByName = 'SpaceMaping')
                    mapAttr = 'SpaceMaping'+str(mapGroupId)#对于Group,它的dagNode上的属性名需要加上NodeID
                    cmds.connectAttr(mapingTex + ".fileTextureName", shader+'.%s'%mapAttr)
                    cmds.setAttr(shader+'.userSpaceTex',True)
                    blendStateID = cmds.shaderfx(sfxnode=shader,getNodeIDByName = 'SpaceMapingType')
                    blendMode=int(MaterialData[Mindex].BlendMode)
                    if  (blendMode==0) or(blendMode==3):
                        cmds.shaderfx(sfxnode=shader,edit_stringlist = [blendStateID,'options',0])
                    else:
                        cmds.shaderfx(sfxnode=shader,edit_stringlist = [blendStateID,'options',blendMode])

            if MaterialData[Mindex].ToonType==0:
                toonIndex = MaterialData[Mindex].ToonValue
                if(toonIndex!=-1):
                    toonTex = TextureNodeList[toonIndex]
                    if(toonTex!=None):
                        toonGroupId = cmds.shaderfx(sfxnode=shader,getNodeIDByName = 'ToonMaping')
                        toonAttr = 'ToonMaping'+str(toonGroupId)#对于Group,它在dagNode上的属性名需要加上NodeID
                        cmds.connectAttr(toonTex + ".fileTextureName", shader+'.%s'%toonAttr)
                        cmds.setAttr(shader+'.userToonTex',True)
            if MaterialData[Mindex].ToonType==1:
                #-1:toon0,0:toon01,1:toon02,...
                toonIndex = MaterialData[Mindex].ToonValue
                texFileName = self.ToonMaping[toonIndex+1]
                fileNode=None
                if texFileName not in bToonTex:
                    path =Util.getResourcePath(texFileName)
                    fileNode   =   cmds.shadingNode("file", asTexture=True)
                    cmds.setAttr(fileNode + ".fileTextureName",path , type="string")
                    bToonTex[texFileName]=fileNode
                else:
                    fileNode=bToonTex[texFileName]
                toonGroupId = cmds.shaderfx(sfxnode=shader,getNodeIDByName = 'ToonMaping')
                toonAttr = 'ToonMaping'+str(toonGroupId)#对于Group,它在dagNode上的属性名需要加上NodeID
                cmds.connectAttr(fileNode + ".fileTextureName", shader+'.%s'%toonAttr)
                cmds.setAttr(shader+'.userToonTex',True)
            cmds.select(meshPath + ".f[%i:%i]" %((LastVex+3)/3-1 , (LastVex+MaterialData[Mindex].Influence)/3), r = True)
            cmds.hyperShade(assign = shader)
            LastVex+=MaterialData[Mindex].Influence
            
    def BuildSkeleton(self,BoneData):
    #{
        if(len(BoneData)<=0):
            return
        #创建一个组，骨骼为这个
        index_bone=OpenMaya.MIntArray()
        BonePathArray=[]#创建string类型的路径列表，用于cmds选择物体
        MD2NodePathArray = []
        for j in range(len(BoneData)):
        #{
            bonePath=OpenMayaAnim.MFnIkJoint()
            #获取骨骼位置
            bonePos=OpenMaya.MVector(BoneData[j].Position[0],BoneData[j].Position[1],-BoneData[j].Position[2])
            #所有骨骼生成在世界位置下（组位置为世界位置的0，0，0）
            joint=bonePath.create(self.Root)
            rotate=OpenMaya.MEulerRotation(0,0,0)
            #{  骨骼朝向
            if(BoneData[j].LocalAxis):
                xDir = OpenMaya.MVector(BoneData[j].localX[0],BoneData[j].localX[1],-BoneData[j].localX[2])
                xDir.normalize()
                zDir = OpenMaya.MVector(BoneData[j].localZ[0],BoneData[j].localZ[1],-BoneData[j].localZ[2])
                zDir.normalize()
                #MVector的叉乘好像只有插件能用
                crssDir=Util.Cross(xDir,zDir)
                yDir = OpenMaya.MVector(crssDir[0],crssDir[1],crssDir[2])
                yDir.normalize()
                src_matrix = [
                        [xDir[0],xDir[1],xDir[2],0.0],
                        [yDir[0],yDir[1],yDir[2],0.0],
                        [zDir[0],zDir[1],zDir[2],0.0],
                        [0.0  ,0.0  ,0.0  ,1.0]
                        ]
                Rm=OpenMaya.MMatrix()
                # 将矩阵设置为单位矩阵
                Rm.setToIdentity()
                
                for r in range(4):
                    for f in range(4):
                        #https://groups.google.com/g/python_inside_maya/c/Gou02IHsYKA
                        OpenMaya.MScriptUtil.setDoubleArray(Rm[r], f, src_matrix[r][f])
                mtm=OpenMaya.MTransformationMatrix(Rm)
                #获取这个矩阵的欧拉角旋转，并且调用欧拉角的函数转成向量
                rotate=(mtm.eulerRotation())

            #setOrientation在使用命令行绑定子父级的时候会自动计算
            bonePath.setOrientation(rotate)
            bonePath.setTranslation(bonePos,OpenMaya.MSpace.kTransform)
            #用于读写附着属性的node
            jointObjPath = OpenMaya.MFnDependencyNode(joint)

            #MFnDependencyNode获取节点的string属性,并且写入值 
            radiusPlug=jointObjPath.findPlug('radius',False)
            
            overEnabled=jointObjPath.findPlug('overrideEnabled',False)
            overEnabled.setBool(True)

            colorPlug=jointObjPath.findPlug('overrideColor',False)
            #名字
            boneName_jp= str(BoneData[j].Name)
            if boneName_jp in self.NameTable:
                boneName_english=self.NameTable[boneName_jp]
                radiusPlug.setFloat(0.1)
                #颜色
                colorPlug.setInt(21)

            else:
                boneName_english='joint_Null'+str(j)
                radiusPlug.setFloat(0.3)
                colorPlug.setInt(0)
            jointObjPath.setName(boneName_english)
            #有部分骨骼链并不完整，需要手动调整
            if j>0 and BoneData[j].ParentIndex>=0:
                cmds.parent(bonePath.fullPathName(),BonePathArray[BoneData[j].ParentIndex])
                #应该在绑定子父级之后写入变换

            #把轴方向锁了，避免互动控制柄的时候自动计算
            cmds.setAttr(bonePath.fullPathName()+'.jointOrient',lock=True)
            mdNode = cmds.createNode( 'MD2MayaNode', name=('MD_'+bonePath.name()+"_#") )
            cmds.connectAttr( bonePath.fullPathName() + ".message", mdNode + ".MDnLinkNode",force=True)
            cmds.setAttr(mdNode+'.MDnBoneName',BoneData[j].Name,type="string")
            index_bone.append(j)#写入权重时候用到的骨骼数组下标列表
            #将DagPath的字符串写入数组，以备执行cmds
            MD2NodePathArray.append(mdNode)
            BonePathArray.append(bonePath.fullPathName())
        #}
        SkeletonData =[BonePathArray,MD2NodePathArray,index_bone]
        return SkeletonData
    #}
    #处理骨骼链接关系
    def RelationalData(self,BonesData,SkeletonPath):
    #{
        if len(BonesData)<1 or SkeletonPath==None:
            return
        for bp in range(len(SkeletonPath[0])):
        #{   
            if BonesData[bp].InheritBone[0] or BonesData[bp].InheritBone[1]:
            #{  变换继承
                #这里需要使用joint节点上的值驱动，因为ik计算完是直接输出到目标节点上的
                #
                ParentPath=SkeletonPath[0][BonesData[bp].InheritIndex]
                CurrentPath = SkeletonPath[1][bp]
                weight=BonesData[bp].InheritInfluence#权重
                cmds.setAttr(CurrentPath+'.MDnInheritedWeight',weight)
                if BonesData[bp].InheritBone[0]:
                #{ 
                    cmds.connectAttr( ParentPath + ".rotate", CurrentPath + ".MDnInheredRotate",force=True)
                #}
                if BonesData[bp].InheritBone[1]:
                #{  
                    cmds.connectAttr( ParentPath + ".translate", CurrentPath + ".MDnInheredTranslate",force=True)
                #}
            #}end if(变换继承)
            if BonesData[bp].ikEnable:
            #{  IK骨
                target  =   SkeletonPath[1][BonesData[bp].targetIndex]
                ikbone  =   SkeletonPath[1][bp]
                cmds.connectAttr( target  + ".MDnOutRotate", ikbone + ".TargetRotate",force=True)
                cmds.connectAttr( target  + ".MDnOutTranslate", ikbone + ".TargetTranslate",force=True)
                for i in range(len(BonesData[bp].ikTable)):
                #{    
                    #避免target在ik列表中
                    if BonesData[bp].ikTable[i]==BonesData[bp].targetIndex:
                        continue
                    tabMD2=SkeletonPath[1][BonesData[bp].ikTable[i]]
                    tabBone=SkeletonPath[0][BonesData[bp].ikTable[i]]

                    cmds.connectAttr( tabMD2  + ".MDnOutRotate", ikbone+ ".MDnIKTable[%i].MDnTabRotate"%i,force=True)
                    cmds.connectAttr( tabMD2 + ".MDnOutTranslate",ikbone + ".MDnIKTable[%i].MDnTabTranslate"%i,force=True)
                    cmds.connectAttr( tabMD2  + ".MDnOutJointOrient",ikbone + ".MDnIKTable[%i].MDnTabJointOrient"%i,force=True)
                    
                    cmds.connectAttr( ikbone + ".MDnOutIK[%i].MDnOutIKTranslate"%i, tabBone  + ".translate",force=True)
                    cmds.connectAttr( ikbone + ".MDnOutIK[%i].MDnOutIKRotate"%i,tabBone + ".rotate",force=True)
                    if BonesData[bp].ikLimit[i]:
                    #{
                        xMin=(BonesData[bp].MinLimit[i][0])*(180/3.1415926)
                        xMax=(BonesData[bp].MaxLimit[i][0])*(180/3.1415926)
                        yMin=(BonesData[bp].MinLimit[i][1])*(180/3.1415926)
                        yMax=(BonesData[bp].MaxLimit[i][1])*(180/3.1415926)
                        zMin=(BonesData[bp].MinLimit[i][2])*(180/3.1415926)
                        zMax=(BonesData[bp].MaxLimit[i][2])*(180/3.1415926)
                        cmds.setAttr( ikbone + ".MDnIKTable[%i].MDnEnableAxisLimit"%i,BonesData[bp].ikLimit[i])
                        cmds.setAttr( ikbone + ".MDnIKTable[%i].MDnAxisLimitMin"%i,-xMax,-yMax,zMin,type='double3')
                        cmds.setAttr( ikbone + ".MDnIKTable[%i].MDnAxisLimitMax"%i,-xMin,-yMin,zMax,type='double3')
                    #}
                #}
                #列表中最后一个骨骼在全局骨骼中的索引
                lastIndex = BonesData[bp].ikTable[len(BonesData[bp].ikTable)-1]#连接到列表中的最后一个元素的父级矩阵用以回调
                cmds.connectAttr(SkeletonPath[0][lastIndex] + ".parentMatrix[0]", ikbone + ".MDnIKTable[%i].MDnTabParentMatrix"%(len(BonesData[bp].ikTable)-1),force=True)

                cmds.setAttr(SkeletonPath[0][bp]+'.radius',1)
                cmds.setAttr(SkeletonPath[1][bp]+'.MDnIKState',1)
                cmds.setAttr(SkeletonPath[1][bp]+'.MDnIKLoop',BonesData[bp].loopCount)
                cmds.setAttr(SkeletonPath[1][bp]+'.MDnIKAngle',BonesData[bp].LimitRadian*(180/3.1415926))
            #}if end(IK骨)
            if not BonesData[bp].LockTransform[0]:
            #{  旋转锁定
                cmds.setAttr(SkeletonPath[0][bp]+'.MnRotateX',lock=True)
                cmds.setAttr(SkeletonPath[0][bp]+'.MnRotateY',lock=True)
                cmds.setAttr(SkeletonPath[0][bp]+'.MnRotateZ',lock=True)
            #}
            if not BonesData[bp].LockTransform[1]:
            #{  平移锁定
                cmds.setAttr(SkeletonPath[0][bp]+'.MnTranslateX',lock=True)
                cmds.setAttr(SkeletonPath[0][bp]+'.MnTranslateY',lock=True)
                cmds.setAttr(SkeletonPath[0][bp]+'.MnTranslateZ',lock=True)
            #}
            if not BonesData[bp].Visibility:
            #{ 隐藏骨
                #cmds.setAttr(SkeletonPath[0][bp]+'.visibility',0)
                cmds.setAttr(SkeletonPath[0][bp]+'.drawStyle',2)
                #cmds.setAttr(SkeletonPath[0][bp]+'.useOutlinerColor',True)#outlinerColor
                #cmds.setAttr(SkeletonPath[0][bp]+'.outlinerColor',0.9,0.4,0.4,type='float3')#
            #}
        #}
    #}
    def BuildSkinCluster(self,meshDag,WeightData,SkeletonData,vertexCount,jointCount):
    #{
        if (meshDag == None )or(len(WeightData)<1):
            return
        cmds.select(clear = True)
        cmds.select(SkeletonData[0],add=True)
        #加选mesh节点
        cmds.select(meshDag.fullPathName(),add=True)
        #这个函数返回一个skinCluster节点名：{skinCluster}
        #生成蒙皮绑定cluster[0]=skinCluster
        cluster = cmds.skinCluster(toSelectedBones = True,
                                    skinMethod=2,
                                    maximumInfluences=4,
                                    obeyMaxInfluences=True)
        
        selList = OpenMaya.MSelectionList()
        selList.add(cluster[0])
        clusterNode = OpenMaya.MObject()
        selList.getDependNode(0, clusterNode)
        skin = OpenMayaAnim.MFnSkinCluster(clusterNode)

        vertexCom=OpenMaya.MItMeshVertex(meshDag)
        v_component=OpenMaya.MFnSingleIndexedComponent()
        mObj = v_component.create(OpenMaya.MFn.kMeshVertComponent)
        Index_vertex=OpenMaya.MIntArray()
        
        weight=OpenMaya.MDoubleArray(vertexCount*jointCount,0.0)
        blendWeight=OpenMaya.MDoubleArray(vertexCount,0.0)
        
        while not vertexCom.isDone():
            vexID=vertexCom.index()
            valueTest=0.0
            if WeightData[vexID].WeightType==0:
                    #骨骼索引
                    index_a=WeightData[vexID].Index[0]
                    #顶点计数*骨骼数=当前顶点的权重区间【0-骨骼数】
                    index_b=vexID*(jointCount)+index_a
                    weight[index_b]=WeightData[vexID].WeightValue[index_a]
            if WeightData[vexID].WeightType==1:
                for x in range(0,2):
                    index_a=WeightData[vexID].Index[x]

                    index_b=vexID*(jointCount)+index_a
                    weight[index_b]=WeightData[vexID].WeightValue[index_a]
            if WeightData[vexID].WeightType==2:
                for y in range(0,4):
                    index_a=WeightData[vexID].Index[y]
                    index_b=vexID*(jointCount)+index_a
                    weight[index_b]=WeightData[vexID].WeightValue[index_a]
            if WeightData[vexID].WeightType==3:
                for z in range(0,2):
                    index_a=WeightData[vexID].Index[z]
                    index_b=vexID*(jointCount)+index_a
                    weight[index_b]=WeightData[vexID].WeightValue[index_a]
            if WeightData[vexID].WeightType==4:
                blendWeight[vexID]=1.0
                for w in range(0,4):
                    index_a=WeightData[vexID].Index[w]
                    index_b=vexID*(jointCount)+index_a
                    weight[index_b]=WeightData[vexID].WeightValue[index_a]
            vertexCom.next()
        skin.setWeights(meshDag,mObj,SkeletonData[2],weight,True)
        skin.setBlendWeights(meshDag,mObj,blendWeight)
    #}
    def buildRigidBody(self,RigidBodyData):
    #{
        """
        这里需要把旋转轴的x和Y反转一下
        """
        if len(RigidBodyData)<1:
            return
        cmds.select(clear = True)
        RigidBodyGroup=cmds.group(empty=True,name='RigidBodyGroup#')
        cmds.setAttr(RigidBodyGroup+'.visibility',0)
        for RB in range(len(RigidBodyData)):
            if RigidBodyData[RB].ShapeType==0:
                Shape=cmds.polySphere(r=RigidBodyData[RB].ShapeSize[0],constructionHistory=False)[0]
            if RigidBodyData[RB].ShapeType==1:
                Shape=cmds.polyCube(w=RigidBodyData[RB].ShapeSize[0]*2,h=RigidBodyData[RB].ShapeSize[1]*2,d=RigidBodyData[RB].ShapeSize[2]*2,constructionHistory=False)[0]
            if RigidBodyData[RB].ShapeType==2:
                Shape=cmds.polyCylinder(r=RigidBodyData[RB].ShapeSize[0],h=RigidBodyData[RB].ShapeSize[1],rcp=True,sz=5,constructionHistory=False)[0]
            cmds.setAttr(Shape+'.translateX',RigidBodyData[RB].Position[0])
            cmds.setAttr(Shape+'.translateY',RigidBodyData[RB].Position[1])
            cmds.setAttr(Shape+'.translateZ',-RigidBodyData[RB].Position[2])
            ZxyOrient= OpenMaya.MEulerRotation(-RigidBodyData[RB].Rotation[0], -RigidBodyData[RB].Rotation[1], RigidBodyData[RB].Rotation[2],2)
            XyzOrient= ZxyOrient.reorder(0)#重定向到zxy
            cmds.setAttr(Shape+'.rotateX',XyzOrient[0]*(180/3.1415926))
            cmds.setAttr(Shape+'.rotateY',XyzOrient[1]*(180/3.1415926))
            cmds.setAttr(Shape+'.rotateZ',XyzOrient[2]*(180/3.1415926))
            #看起来ZXY的旋转顺序是正确的
            #cmds.setAttr(Shape+'.rotateOrder',2)
            cmds.parent(Shape,RigidBodyGroup)
        cmds.select(clear = True)
    #}
    #ref:[https://github.com/GRGSIBERIA/mmd-transporter/blob/master/mmd-transporter/importer/rigidgen.py]
    def bulletPhysics(self,RigidBodyData,SkeletonPath):
    #{
        """
                        Constraint|⇲
                meshShape->Rigdibody ->PairBlend->Transform
                Transform.Rotate->RelatedBone.MnRotate
            *在刚体类型为[追踪骨骼]的时候，修改RigdibodyType为1(运动动力学)即可
            *在刚体类型为[物理演算]的时候，修改RigidbodyType为2(物理动力学)
            *在刚体类型为[物理+骨骼位置对齐]的时候，RigidbodyType需要2，并且PairBlend的transform的平移部分需要修改为[仅限输入1]
                **这个模式看起来像是只计算物理的动态的旋转部分，所以transform的平移需要使用骨骼约束来的值
        """
        if len(RigidBodyData)<1 or SkeletonPath==None:
            return
        cmds.select(clear = True)
        bulletRigidList=[]
        RigidBodyGroup=cmds.group(empty=True,name='RigidBodyGroup#')
        cmds.setAttr(RigidBodyGroup+'.visibility',0)
        colliderShapeType=1
        for RB in range(len(RigidBodyData)):
            Shape=cmds.createNode('transform',parent=RigidBodyGroup)
            cmds.setAttr(Shape+'.translateX',RigidBodyData[RB].Position[0])
            cmds.setAttr(Shape+'.translateY',RigidBodyData[RB].Position[1])
            cmds.setAttr(Shape+'.translateZ',-RigidBodyData[RB].Position[2])
            ZxyOrient= OpenMaya.MEulerRotation(-RigidBodyData[RB].Rotation[0], -RigidBodyData[RB].Rotation[1], RigidBodyData[RB].Rotation[2],2)
            XyzOrient= ZxyOrient.reorder(0)#重定向到zxy
            cmds.setAttr(Shape+'.rotateX',XyzOrient[0]*(180/3.1415926))
            cmds.setAttr(Shape+'.rotateY',XyzOrient[1]*(180/3.1415926))
            cmds.setAttr(Shape+'.rotateZ',XyzOrient[2]*(180/3.1415926))
            #{获取连接骨骼SkeletonPath[0]=mayaJointPathArray
            BoneIndex=RigidBodyData[RB].RelatedBoneIndex
            RelatedBone=SkeletonPath[0][BoneIndex]
            cmds.select(Shape,replace=True)#替换现有选择
            #RigidBodyShape = bullet.RigidBody.CreateRigidBody().executeCommandCB()[1]#return:[transform,RigidBodyShape]
            #ref:[https://github.com/alicevision/mayaAPI/blob/master/2016.sp1/linux/lib/python2.7/site-packages/maya/app/mayabullet/RigidBody.py]
            RigidBodyShape = bullet.RigidBody.CreateRigidBody().doCommand()[1]#这个函数只会处理链接关系，不会链接shape
            PairBlendPath=cmds.listConnections( Shape+'.translateX', source=True , destination=False)[0]

            cmds.setAttr(RigidBodyShape+'.visibility',0)
            cmds.setAttr(RigidBodyShape+'.lodVisibility',0)
            cmds.setAttr(RigidBodyShape+'.autoFit',0)#关闭shape适配
            if RigidBodyData[RB].ShapeType==0:
                cmds.setAttr(RigidBodyShape+'.colliderShapeType',2)#球体
                cmds.setAttr(RigidBodyShape+'.radius',RigidBodyData[RB].ShapeSize[0])
            if RigidBodyData[RB].ShapeType==1:
                cmds.setAttr(RigidBodyShape+'.colliderShapeType',1)#方块extentsX
                cmds.setAttr(RigidBodyShape+'.extents',RigidBodyData[RB].ShapeSize[0]*2,RigidBodyData[RB].ShapeSize[1]*2,RigidBodyData[RB].ShapeSize[2]*2,type='float3')#方块extentsX
                cmds.DeleteHistory()#清除历史
            if RigidBodyData[RB].ShapeType==2:
                colliderShapeType=3
                cmds.setAttr(RigidBodyShape+'.colliderShapeType',3)#胶囊体
                cmds.setAttr(RigidBodyShape+'.radius',RigidBodyData[RB].ShapeSize[0])
                cmds.setAttr(RigidBodyShape+'.length',RigidBodyData[RB].ShapeSize[1]+RigidBodyData[RB].ShapeSize[0]*2)


            if RigidBodyData[RB].PhysicsMode==0:#[追踪骨骼]
                ConstraintPath=cmds.parentConstraint(RelatedBone,Shape,maintainOffset=True,weight=1.0)[0]
                cmds.setAttr(RigidBodyShape+'.bodyType',1)
            if RigidBodyData[RB].PhysicsMode==1:#[物理演算]
                cmds.setAttr(RigidBodyShape+'.bodyType',2)
                Util.orientConstraint(Shape,RelatedBone,'MnRotate')
            if RigidBodyData[RB].PhysicsMode==2:#[物理+骨骼位置对齐]
                ConstraintPath=cmds.pointConstraint(RelatedBone,Shape,maintainOffset=True,weight=1.0)[0]
                Util.orientConstraint(Shape,RelatedBone,'MnRotate')#为
                cmds.setAttr(RigidBodyShape+'.bodyType',2)
                cmds.setAttr(PairBlendPath+'.translateXMode',1)
                cmds.setAttr(PairBlendPath+'.translateYMode',1)
                cmds.setAttr(PairBlendPath+'.translateZMode',1)
            #{Group ref:[https://github.com/GRGSIBERIA/mmd-transporter/blob/master/mmd-transporter/importer/rigidgen.py]
            #这里的输入值大于1会导致写入失败
            cmds.setAttr(RigidBodyShape+'.mass',RigidBodyData[RB].Mass)
            cmds.setAttr(RigidBodyShape+'.linearDamping',max(0.0,min(1.0,RigidBodyData[RB].MoveAttenuation)))
            cmds.setAttr(RigidBodyShape+'.angularDamping',max(0.0,min(1.0,RigidBodyData[RB].RotationDamping)))
            cmds.setAttr(RigidBodyShape+'.restitution',max(0.0,min(1.0,RigidBodyData[RB].Repulsion)))
            cmds.setAttr(RigidBodyShape+'.friction',max(0.0,min(1.0,RigidBodyData[RB].FrictionForce)))
            collisionGroup = 2**RigidBodyData[RB].GroupID
            noCollisionGroup = (-RigidBodyData[RB].GroupMask - 1) ^ 0xFFFF
            cmds.setAttr("%s.collisionFilterGroup" % RigidBodyShape, collisionGroup)
            cmds.setAttr("%s.collisionFilterMask" % RigidBodyShape, noCollisionGroup)
            
            #}

            bulletRigidList.append([Shape,RigidBodyShape])
        cmds.select(clear = True)
        return bulletRigidList
    #}

    def createRigidCoupling(self,JointData,bulletRigidList):
    #{
        if len(JointData)<1 or bulletRigidList==None:
            return
        ConstraintGroup=cmds.group(empty=True,name='RigidBodyConstraintGroup#')
        cmds.setAttr(ConstraintGroup+'.visibility',0)
        for c in range(len(JointData)):
        #{
            RigidA = bulletRigidList[JointData[c].RelatedRigidbodyA][1]
            RigidB = bulletRigidList[JointData[c].RelatedRigidbodyB][1]
            
            ConstraintTrans=cmds.polyCube(width=0.15,height=0.15,depth=0.15,constructionHistory=False)[0]
            ConstraintShape=Util.RigidBodyConstraint(RigidA,RigidB,ConstraintTrans)
            
            cmds.setAttr(ConstraintTrans+'.translate',JointData[c].Position[0],JointData[c].Position[1],-JointData[c].Position[2],type='double3')
            ZxyOrient= OpenMaya.MEulerRotation(-JointData[c].Rotate[0], -JointData[c].Rotate[1], JointData[c].Rotate[2],2)
            XyzOrient= ZxyOrient.reorder(0)#重定向到zxy
            cmds.setAttr(ConstraintTrans+'.rotate',XyzOrient[0]*(180/3.1415926),XyzOrient[1]*(180/3.1415926),XyzOrient[2]*(180/3.1415926),type='double3')
            cmds.setAttr(ConstraintShape+'.constraintType',5)
            cmds.setAttr(ConstraintShape+'.useReferenceFrame',0)
            cmds.setAttr(ConstraintShape+'.linearConstraintX',2)#受限
            cmds.setAttr(ConstraintShape+'.linearConstraintY',2)#受限
            cmds.setAttr(ConstraintShape+'.linearConstraintZ',2)#受限
            PosLimitMin=JointData[c].PositionLimitMin
            PosLimitMax=JointData[c].PositionLimitMax
            cmds.setAttr(ConstraintShape+'.linearConstraintMin',PosLimitMin[0],PosLimitMin[1],PosLimitMin[2],type='float3')
            cmds.setAttr(ConstraintShape+'.linearConstraintMax',PosLimitMax[0],PosLimitMax[1],PosLimitMax[2],type='float3')
            #cmds.setAttr(ConstraintShape+'.linearConstraintMin',2)#受限
            cmds.setAttr(ConstraintShape+'.angularConstraintX',2)#受限
            cmds.setAttr(ConstraintShape+'.angularConstraintY',2)#受限
            cmds.setAttr(ConstraintShape+'.angularConstraintZ',2)#受限
            angLimitMin = JointData[c].RotateLimitMin
            angLimitMax = JointData[c].RotateLimitMax
            cmds.setAttr(ConstraintShape+'.angularConstraintMin',angLimitMin[0],angLimitMin[1],angLimitMin[2],type='float3')
            cmds.setAttr(ConstraintShape+'.angularConstraintMax',angLimitMax[0],angLimitMax[1],angLimitMax[2],type='float3')
            cmds.setAttr(ConstraintShape+'.linearSpringEnabledX',1)
            cmds.setAttr(ConstraintShape+'.linearSpringEnabledY',1)
            cmds.setAttr(ConstraintShape+'.linearSpringEnabledZ',1)
            cmds.setAttr(ConstraintShape+'.linearSpringStiffness',JointData[c].PositionSpring[0],JointData[c].PositionSpring[1],JointData[c].PositionSpring[2],type='float3')
            cmds.setAttr(ConstraintShape+'.angularSpringEnabledX',1)
            cmds.setAttr(ConstraintShape+'.angularSpringEnabledY',1)
            cmds.setAttr(ConstraintShape+'.angularSpringEnabledZ',1)
            cmds.setAttr(ConstraintShape+'.angularSpringStiffness',JointData[c].RotateSpring[0],JointData[c].RotateSpring[1],JointData[c].RotateSpring[2],type='float3')
            cmds.parent(ConstraintTrans, ConstraintGroup)
        #}
    #}

    def Execution(self,PmxFile):
    #{
        meshDagPath = self.BulidMesh(PmxFile.VertexArray,PmxFile.VertexIndex)
        self.BuildBlendShape(meshDagPath,PmxFile.MorphData)
        texFileList=self.createTextureNode(self.TexturePath)
        if (self.shadingType==0):
            self.ShaderFxMaterial(self.shaderPath,meshDagPath,PmxFile.MaterialData,texFileList)
        if (self.shadingType==1):
            self.LambertMaterial(meshDagPath,PmxFile.MaterialData,texFileList)
        SkeletonData = self.BuildSkeleton(PmxFile.BoneData)
        self.BuildSkinCluster(meshDagPath,PmxFile.WeightArray,SkeletonData,len(PmxFile.VertexArray),len(PmxFile.BoneData))
        self.RelationalData(PmxFile.BoneData,SkeletonData)
        if (self.PhysicsType==1):
            bulletRigidList=self.bulletPhysics(PmxFile.RigidBodyData,SkeletonData)
            self.createRigidCoupling(PmxFile.JointData,bulletRigidList)
        else:
            self.buildRigidBody(PmxFile.RigidBodyData)
    #}