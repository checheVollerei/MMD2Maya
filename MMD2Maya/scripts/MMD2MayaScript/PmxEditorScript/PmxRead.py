import struct
class VertexStrust:
    def __init__(self,vertex=[],normal=[],texcoord=[]):
        self.Vertex     =   vertex
        self.Normal     =   normal
        self.Texcoord   =   texcoord

class WeightStrust:
    def __init__(self,WeightType,Index=[],WeightValue={}):
        self.WeightType     =   WeightType
        self.Index          =   Index
        self.WeightValue    =   WeightValue
        

class SurfaceStrust:
    def __init__(self,index):
        self.Index      =   index

class TextureStrust:
    def __init__(self,path):
        self.TexturePath    =   path
#对于材质，它最少需要有的是：名字，基础色，高光色，高光强度，贴图的索引（用于根据贴图的路径数组去寻找贴图）
#目前就想到这些。 c
class MaterialStrust:
    def __init__(self):
        self.LocalName      =   ''
        self.UniversalName  =   ''
        self.Diffuse        =   [0,0,0,0]
        self.Specular       =   [0,0,0]
        self.Strength       =   5.0
        self.Ambient        =   [0,0,0]
        self.SpaceMaping    =   -1  #TexIndex
        self.BlendMode      =   0   #0:无效，1：乘，2:加，3：附加uv映射
        self.EdgeColor      =   [0,0,0,0]
        self.EdgeScale      =   0.0
        self.TextureIndex   =   0
        self.ToonType       =   -1 # -1:没有toonMaping 0:ToonValue=TexIndex,1:ToonValue=[0...10]
        self.ToonValue      =   0 #index
        self.Influence      =   0

class BoneStrust:
    def __init__(self):
        self.Name           =   None
        self.Position       =   [0,0,0]#世界（模型下的）位置
        self.ParentIndex    =   0       #父级索引
        #{ TailType==0 ==>位置， TailType==1 ==> 骨骼索引
        self.TailType       =   0   #是否尾部  次级索引或者vec3的位置
        self.TailPosition   =    [0,0,0]#尾部位置（骨骼为尾端的情况下）,TailPosition-Position
        self.TailIndex      =   0 #尾部指向骨骼索引 TailIndex.Position-Position

        #}

        #{
        self.Visibility     =    True#是否显示
        self.LockTransform  =     [False,False] #变换锁定 [0]:Translete [1]:Rotate
        #}

        #{ 继承数据
        self.InheritBone        =   [False,False]#是否继承
        self.InheritIndex       =   0#继承索引
        self.InheritInfluence   =   0#继承权重
        #}
        self.LocalAxis      =   False
        self.localX         =   [1,0,0]
        self.localZ         =   [0,0,1]   
        #{ IK数据
        self.targetIndex =   0
        self.ikEnable   =   False
        self.loopCount  =   1
        self.LimitRadian=  0
        self.ikTable    =   []
        self.ikLimit    =   []
        self.MinLimit   =   []
        self.MaxLimit   =   []
        #}
class MorphStrust:
    def __init__(self):
        self.MorphName      =   ''
        self.PanelType      =   0
        self.MorphType      =   0
        self.DataSize       =   0
        #{ 组合数据
        self.MorphIndex     =   []
        self.MorphInfluence =   []
        #}
        #{ 顶点数据
        self.VertexIndex    =   []
        self.VertexOffset   =   []
        #}

class RigidBodyStrust:

    def __init__(self):

        self.Name           =   ''
        self.RelatedBoneIndex  =   0
        self.GroupID        =   0
        self.GroupMask      =   0

        self.ShapeType      =   0
        self.ShapeSize      =   [0,0,0]#[0]:radius,[1]length,cube:[x,y,z]
        self.Position       =   [0,0,0]
        self.Rotation       =   [0,0,0]

        self.Mass           =   1   #质量
        self.MoveAttenuation=   0   #移动衰减->线性阻尼
        self.RotationDamping=   0   #旋转阻尼->角度阻尼
        self.Repulsion      =   0   #反応力->恢复力(?大概)
        self.FrictionForce  =   1   #摩擦力


        self.PhysicsMode    =   0


class JointStrust:
    def __init__(self):

        self.Name               =   ''
        self.Type               =   0       #0:spring6DOF,1:6DOF,2:P2P,3:ConeTwist,4:Slider,5:Hinge;其中2.0版本仅支持Spring6DOF,其余皆是2.1版本才支持
        self.RelatedRigidbodyA  =   0
        self.RelatedRigidbodyB  =   0
        self.Position           =   [0,0,0]#
        self.Rotate             =   [0,0,0]
        self.PositionLimitMin   =   [0,0,0]
        self.PositionLimitMax   =   [0,0,0]
        self.RotateLimitMin     =   [0,0,0]
        self.RotateLimitMax     =   [0,0,0]
        self.PositionSpring     =   [0,0,0]
        self.RotateSpring       =   [0,0,0]

    #def __str__(self):
    #    return self.TexturePath
class DecodePMX:
    #这里定义几个类型，直接跳过indexType 
    # 1 2 4分别对应byte/ubyte/short/ushort/int
    # 这里没定义实际大小，直接用字面意义的大小了，因为是直接跳过（*v*）
    # 解码还是要引入骨骼索引类型进行解码：注意是 Bone index 
    def LoadVertexData(self,file,Data_Count,Additional,indexType,indexCount):

        self.VertexArray=[None]*Data_Count
        self.WeightArray=[None]*Data_Count

        for i in range(Data_Count):
            #vector3
            Vx=struct.unpack('f', file.read(4))[0]
            Vy=struct.unpack('f', file.read(4))[0]
            Vz=struct.unpack('f', file.read(4))[0]
            #vector3
            Nx=struct.unpack('f', file.read(4))[0]
            Ny=struct.unpack('f', file.read(4))[0]
            Nz=struct.unpack('f', file.read(4))[0]
            #vector2
            u=struct.unpack('f',file.read(4))[0]
            v=struct.unpack('f',file.read(4))[0]
            #additional vector4s,看下文档
            #发现这个附加vec4指的是多UV或者顶点色
            #但是它好像没有关键字来确定具体是哪个东西

            for _ in range(Additional):
                file.seek(4*4,1)
            WeightDeformType=file.read(1)[0]
            #print('形变类型'+str(WeightDeformType))

            weightType=WeightDeformType
            boneIndex=[0,0,0,0]
            boneValue=[0,0,0,0]
            weightValue={}
            if WeightDeformType<0:
                print('没有骨骼绑定'+str(WeightDeformType))
            if WeightDeformType==0:
                #self.BDEF_1(file,indexType)
                #file.seek(indexCount,1)
                boneIndex[0]=struct.unpack(indexType, file.read(indexCount))[0]
                if boneIndex[0] not in weightValue:
                    weightValue[boneIndex[0]]=1.0
                #if boneIndex[0]<0:
                #    print('无骨骼绑定')
                weightValue[0]=1.0
            elif WeightDeformType==1:
                #self.BDEF_2(file,indexType)
                boneIndex[0]=struct.unpack(indexType, file.read(indexCount))[0]
                boneIndex[1]=struct.unpack(indexType, file.read(indexCount))[0]

                #这是个float值，定义了bone_1的权重值,bone_2=1-bone_1
                #file.seek(4,1)
                weightValue_temp=struct.unpack('f', file.read(4))[0]
                boneValue[0]=weightValue_temp
                boneValue[1]=1.0-weightValue_temp
                for x in range(2):
                    if boneIndex[x] not in weightValue:
                        weightValue[boneIndex[x]]=boneValue[x]
                    else:
                        weightValue[boneIndex[x]]+=boneValue[x]
                #print('\n顶点编号：'+str(i))
                #print('骨骼1：'+str(boneIndex[0])+'\t值'+str(weightValue[0]))
                #print('骨骼2：'+str(boneIndex[1])+'\t值'+str(weightValue[1]))
            elif WeightDeformType==2:
                #self.BDEF_4(file,indexType)
                #print('变形测试')
                boneIndex[0]=struct.unpack(indexType, file.read(indexCount))[0]
                boneIndex[1]=struct.unpack(indexType, file.read(indexCount))[0]
                boneIndex[2]=struct.unpack(indexType, file.read(indexCount))[0]
                boneIndex[3]=struct.unpack(indexType, file.read(indexCount))[0]

                boneValue[0]=struct.unpack('f', file.read(4))[0]
                boneValue[1]=struct.unpack('f', file.read(4))[0]
                boneValue[2]=struct.unpack('f', file.read(4))[0]
                boneValue[3]=struct.unpack('f', file.read(4))[0]
                for x in range(4):
                    if boneIndex[x] not in weightValue:
                        weightValue[boneIndex[x]]=boneValue[x]
                    else:
                        weightValue[boneIndex[x]]+=boneValue[x]
            #球面变形 #草，我还以为这个不会用到
            elif WeightDeformType==3:
                #print('变形测试')                
                #self.SDEF(file,indexType)
                #file.seek(indexCount,1)
                #file.seek(indexCount,1)
                #file.seek(4,1)
                boneIndex[0]=struct.unpack(indexType, file.read(indexCount))[0]
                boneIndex[1]=struct.unpack(indexType, file.read(indexCount))[0]
                weightValue_temp=struct.unpack('f', file.read(4))[0]
                boneValue[0]=weightValue_temp
                boneValue[1]=1.0-weightValue_temp
                for x in range(2):
                    if boneIndex[x] not in weightValue:
                        weightValue[boneIndex[x]]=boneValue[x]
                    else:
                        weightValue[boneIndex[x]]+=boneValue[x]
                file.seek(4*3,1)#C?什么C？怪哦
                file.seek(4*3,1)#R0?
                file.seek(4*3,1)#R1?
            elif WeightDeformType==4:
                boneIndex[0]=struct.unpack(indexType, file.read(indexCount))[0]
                boneIndex[1]=struct.unpack(indexType, file.read(indexCount))[0]
                boneIndex[2]=struct.unpack(indexType, file.read(indexCount))[0]
                boneIndex[3]=struct.unpack(indexType, file.read(indexCount))[0]

                boneValue[0]=struct.unpack('f', file.read(4))[0]
                boneValue[1]=struct.unpack('f', file.read(4))[0]
                boneValue[2]=struct.unpack('f', file.read(4))[0]
                boneValue[3]=struct.unpack('f', file.read(4))[0]
                for x in range(4):
                    if boneIndex[x] not in weightValue:
                        weightValue[boneIndex[x]]=boneValue[x]
                    else:
                        weightValue[boneIndex[x]]+=boneValue[x]
            EdgeScale=struct.unpack('f',file.read(4))
            self.VertexArray[i]=VertexStrust([Vx,Vy,Vz],[Nx,Ny,Nz],[u,v])
            self.WeightArray[i]=WeightStrust(weightType,boneIndex,weightValue)
    def LoadSurfaceData(self,file,Data_Count,indexType):
        self.VertexIndex=[None]*Data_Count
        
        #定义一个Types列表，用无效位置直接随便填一个占位
        index_Types=['*','B','H','*','i']
        types=index_Types[indexType]
        for x in range(Data_Count):
            #这里的Index是顶点的：vertexIndex
            SurfaceData =struct.unpack(types,file.read(indexType))[0]
            self.VertexIndex[x]=SurfaceStrust(SurfaceData)

    def LoadTextureData(self,file,Data_Count,CodingModel):
        self.TexturePaths=[None]*Data_Count
        #根据贴图数量进行循环读取
        for i in range(Data_Count):
            TextSize=struct.unpack('i',file.read(4))[0]
            TexturePath=file.read(TextSize).decode(CodingModel)
            self.TexturePaths[i]=TextureStrust( TexturePath)

    def LoadMaterialData(self,file,Data_Count,CodingModel,indexType,indexSize):
        #self.MaterialData=[None]*Data_Count
        self.MaterialData=[]
        flagsName=['剔除：','地面投影：','绘制投影：','接受投影：','法线外扩：','顶点色：','点绘制：','线绘制：']
        for x in range(Data_Count):
            mat = MaterialStrust()
            size=struct.unpack('i',file.read(4))[0]
            Name_jp = file.read(size).decode(CodingModel)
            size=struct.unpack('i',file.read(4))[0]
            #其实是英文板块的描述吧
            Name_en=file.read(size).decode(CodingModel)
            diffuseColor=struct.unpack('ffff',file.read(16))
            specularColor=struct.unpack('fff',file.read(12))
            specularStrength=struct.unpack('f',file.read(4))
            ambientColor =struct.unpack('fff',file.read(12))
            mat.LocalName      = Name_jp
            mat.UniversalName  = Name_en
            mat.Diffuse        = diffuseColor
            mat.Specular       = specularColor
            mat.Strength       = specularStrength
            mat.Ambient        = ambientColor
            #print('环境色:'+str(ambientColor))
            #FlagsType是一个一字节的byte，它的每一位二进制决定了一个bool值
            DrawingFlags=(file.read(1)[0])
            # 遍历每一位
            flagsValue=[]
            for i in range(8):
                # 获取当前位的值
                bit = (DrawingFlags >> (7 - i)) & 1
                flagsValue.append(bit)
                # 打印当前位的值
            edgeColor=struct.unpack('ffff',file.read(16))
            edgeScale=struct.unpack('f',file.read(4))[0]
            textureIndex=struct.unpack(indexType,file.read(indexSize))[0]
            environmentIndex=struct.unpack(indexType,file.read(indexSize))[0]
            #0 = 禁用、1 = 乘法、2 = 加法、3 = 附加 vec4*
            environmentBlendMode=struct.unpack('b',file.read(1))[0]
            toonType=struct.unpack('b',file.read(1))[0]
            toonValue=None
            if toonType==0:
                toonValue=struct.unpack(indexType,file.read(indexSize))[0]
            if toonType==1:
                toonValue=struct.unpack('b',file.read(1))[0]
                #for x in range(10):
            size=struct.unpack('i',file.read(4))[0]
            metaData=file.read(size).decode(CodingModel)
            #当前材质的影响面数，应该是个偏移量，从上一个材质的索引<<--->>上个索引+这个材质索引的区间
            surfaceCount=struct.unpack('i',file.read(4))[0]
            mat.SpaceMaping    =   environmentIndex
            mat.BlendMode      =   environmentBlendMode
            mat.EdgeColor      =   edgeColor
            mat.EdgeScale      =   edgeScale
            mat.TextureIndex   =   textureIndex
            mat.ToonType       =   toonType
            mat.ToonValue      =   toonValue
            mat.Influence      =   surfaceCount
            self.MaterialData.append(mat)
    def LoadBoneData(self,file,DataCount,CodingModel,BoneIndexType,BoneIndexSize):
            self.BoneData=[]
            for i_0 in range(DataCount):
                self.BoneData.append(BoneStrust())
                size= struct.unpack('i', file.read(4))[0]#text数量
                BoneNameLocal=file.read(size).decode(CodingModel)
                size= struct.unpack('i', file.read(4))[0]#text数量
                BoneNameUniversal=file.read(size).decode(CodingModel)
                #骨骼位置
                BonePosition =struct.unpack('fff',file.read(4*3))
                BoneParentIndex =struct.unpack(BoneIndexType,file.read(BoneIndexSize))[0]
                self.BoneData[i_0].Name=BoneNameLocal
                self.BoneData[i_0].Position=BonePosition
                self.BoneData[i_0].ParentIndex=BoneParentIndex
                BoneLayer=struct.unpack('i',file.read(4))[0]
                BoneFlags=file.read(1)[0]
                BoneFlagsName=['尾部索引位置','旋转','平移','可见','启用','IK','*','*','旋转继承','平移继承','轴锁定','本地坐标','变形后物理','外部父变形']
                flagsValue=[]
                for i_1 in range(6):
                    bit = (BoneFlags >> i_1) & 1
                    flagsValue.append(bit)
                #填充无效位置，匹配文档
                flagsValue.append(0)
                flagsValue.append(0)
                BoneFlags_2=file.read(1)[0]
                for i_1 in range(6):
                    bit = (BoneFlags_2 >> i_1) & 1
                    flagsValue.append(bit)
                TailBonePosition=None
                if flagsValue[0]==0:
                    TailBonePosition=struct.unpack('fff',file.read(4*3))
                TailBoneIndex=None
                if flagsValue[0]==1:
                    TailBoneIndex=struct.unpack(BoneIndexType,file.read(BoneIndexSize))[0]
                self.BoneData[i_0].TailType     =   bool(flagsValue[0])
                self.BoneData[i_0].TailPosition =   TailBonePosition
                self.BoneData[i_0].TailIndex    =   TailBoneIndex
                self.BoneData[i_0].Visibility   =   bool(flagsValue[3])
                self.BoneData[i_0].LockTransform=   [bool(flagsValue[1]),bool(flagsValue[2])]
                #如果有继承变换，读取继承变换的值
                InheritBone=[False]*2
                InheritIndex=0
                InheritInfluence=0.0
                if flagsValue[8]==1 or flagsValue[9]==1:
                    ParentIndex=struct.unpack(BoneIndexType,file.read(BoneIndexSize))[0]
                    ParentInfluence=struct.unpack('f',file.read(4))[0]
                    InheritIndex=ParentIndex
                    InheritInfluence=ParentInfluence
                    if flagsValue[8]==1:
                        InheritBone[0]=True
                    if flagsValue[9]==1:
                        InheritBone[1]=True
                self.BoneData[i_0].InheritBone      =   InheritBone
                self.BoneData[i_0].InheritIndex     =   InheritIndex
                self.BoneData[i_0].InheritInfluence =   InheritInfluence
                #Fixed axis如果有锁定轴，读取锁定轴信息
                if flagsValue[10]==1:
                    AxisDirection=struct.unpack('fff',file.read(4*3))
                #Local co-ordinate,局部坐标轴
                if flagsValue[11]==1:
                    self.BoneData[i_0].localX   =   struct.unpack('fff',file.read(4*3))
                    self.BoneData[i_0].localZ   =   struct.unpack('fff',file.read(4*3))
                self.BoneData[i_0].LocalAxis=bool(flagsValue[11])
                #External parent父级索引
                if flagsValue[13]==1:
                    BoneParentIndex=struct.unpack('i',file.read(4))
                ikEnable=False
                ikTabel=[]#[0]:target==>终  [Tabelend]:len(LinkCount)-1==>始
                ikLimit=[]
                MinLimit=[]
                MaxLimit=[]
                targetIndex=-1
                if flagsValue[5]==1:
                    ikEnable=True
                    TargetIndex=struct.unpack(BoneIndexType,file.read(BoneIndexSize))[0]
                    LoopCount=struct.unpack('i',file.read(4))[0]
                    LimitRadian=struct.unpack('f',file.read(4))[0]
                    self.BoneData[i_0].loopCount   =  LoopCount
                    self.BoneData[i_0].LimitRadian =  LimitRadian
                    LinkCount   =   struct.unpack('i',file.read(4))[0]
                    targetIndex =   TargetIndex
                    #IK Links
                    for x in range(LinkCount):
                        BoneIndex=struct.unpack(BoneIndexType,file.read(BoneIndexSize))[0]
                        HasLimits=bool(struct.unpack('b',file.read(1))[0])
                        ikTabel.append(BoneIndex)
                        if HasLimits:
                            LimitMin=struct.unpack('fff',file.read(4*3))
                            LimitMax=struct.unpack('fff',file.read(4*3))
                            ikLimit.append(True)
                            MinLimit.append(LimitMin)
                            MaxLimit.append(LimitMax)
                        else:
                            LimitMin=[0.0,0.0,0.0]
                            LimitMax=[0.0,0.0,0.0]
                            ikLimit.append(False)
                            MinLimit.append(LimitMin)
                            MaxLimit.append(LimitMax)

                self.BoneData[i_0].targetIndex =   targetIndex
                self.BoneData[i_0].ikEnable   =   ikEnable
                self.BoneData[i_0].ikTable    =   ikTabel
                self.BoneData[i_0].ikLimit    =   ikLimit
                self.BoneData[i_0].MinLimit   =   MinLimit
                self.BoneData[i_0].MaxLimit   =   MaxLimit

    def LoadMorphData(self,file,DataCount,CodingModel,indexData):
        self.MorphData=[]
        for dc in range(DataCount):
        #{
            self.MorphData.append(MorphStrust())
            size=struct.unpack('i',file.read(4))[0]
            MorphName_jp=file.read(size).decode(CodingModel)
            size=struct.unpack('i',file.read(4))[0]
            MorphName_en=file.read(size).decode(CodingModel)
            GroupType=struct.unpack('b',file.read(1))[0]
            MorphType=struct.unpack('b',file.read(1))[0]
            OffsetSize=struct.unpack('i',file.read(4))[0]
            #{初始化数据
            MorphIndexArray=[0]*OffsetSize
            InfluenceArray=[0.0]*OffsetSize
            VertexIndexArray=[0]*OffsetSize
            TranslationArray=[0.0,0.0,0.0]*OffsetSize
            #}
            self.MorphData[dc].MorphName = MorphName_jp
            self.MorphData[dc].PanelType = GroupType
            self.MorphData[dc].MorphType = MorphType
            self.MorphData[dc].DataSize = OffsetSize
            for x in range(OffsetSize):
                #Group	
                if MorphType==0:
                    
                    MorphIndex=struct.unpack(self.IndexTable[indexData[6]],file.read(indexData[6]))[0]
                    Influence=struct.unpack('f',file.read(4))[0]
                    MorphIndexArray[x]  =   MorphIndex
                    InfluenceArray[x]   =   Influence
                #vertex
                if MorphType==1:

                    VertexIndex= struct.unpack(self.VertexIndexTable[indexData[2]],file.read(indexData[2]))[0]
                    Translation=struct.unpack('fff',file.read(4*3))
                    VertexIndexArray[x]=VertexIndex
                    TranslationArray[x]=Translation

                    if VertexIndex not in self.faceIndexTable:
                       self.faceIndexTable[VertexIndex]=0.0
                #Bone
                if MorphType==2:
                    BoneIndex=struct.unpack(self.IndexTable[indexData[5]],file.read(indexData[5]))[0]
                    Translation=struct.unpack('fff',file.read(4*3))
                    Rotation=struct.unpack('ffff',file.read(4*4))

                #UV
                if MorphType==3 or MorphType==4 or MorphType==5 or MorphType==6 or MorphType==7:
                    VertexIndex= struct.unpack(self.IndexTable[indexData[2]],file.read(indexData[2]))[0]
                    Floats=struct.unpack('ffff',file.read(4*4))
                    
                #material
                if MorphType==8:
                    MaterialIndex=struct.unpack(self.IndexTable[indexData[4]],file.read(indexData[4]))[0]
                    Unknown=struct.unpack('b',file.read(1))
                    Diffuse=struct.unpack('ffff',file.read(4*4))
                    Specular=struct.unpack('fff',file.read(4*3))
                    Specularity=struct.unpack('f',file.read(4))
                    Ambient=struct.unpack('fff',file.read(4*3))
                    EdgeColour=struct.unpack('ffff',file.read(4*4))
                    EdgeSize=struct.unpack('f',file.read(4))
                    TextureTint=struct.unpack('ffff',file.read(4*4))
                    EnvironmentTint=struct.unpack('ffff',file.read(4*4))
                    ToonTint=struct.unpack('ffff',file.read(4*4))
                    
                #Flip
                if MorphType==9:
                    MorphIndex=struct.unpack(self.IndexTable[indexData[6]],file.read(indexData[6]))[0]
                    Influence=struct.unpack('f',file.read(4))
                    
                #Impulse
                if MorphType==10:
                    RigidBodyIndex=struct.unpack(self.IndexTable[indexData[7]],file.read(indexData[7]))[0]
                    LocalFlag=struct.unpack('b',file.read(1))
                    MovementSpeed=struct.unpack('fff',file.read(4*3))
                    RotationTorque=struct.unpack('fff',file.read(4*3))
            self.MorphData[dc].MorphIndex = MorphIndexArray
            self.MorphData[dc].MorphInfluence = InfluenceArray
            self.MorphData[dc].VertexIndex = VertexIndexArray
            self.MorphData[dc].VertexOffset = TranslationArray
        #}for End(dc)            
    #这个数据没用-直接跳过
    def LoadDisplayData(self,file,DataCount,CodingModel,indexData):

        for dc in range(DataCount):
            
            textSize=struct.unpack('i',file.read(4))[0]
            DisplayName_jp=file.read(textSize).decode(CodingModel)
            textSize=struct.unpack('i',file.read(4))[0]
            DisplayName_en=file.read(textSize).decode(CodingModel)
            SpecialFlag=struct.unpack('b',file.read(1))[0]
            FrameCount=struct.unpack('i',file.read(4))[0]

            for fc in range(FrameCount):
                FrameType=struct.unpack('b',file.read(1))[0]

                if FrameType==0:

                    BoneIndex=struct.unpack(self.IndexTable[indexData[5]],file.read(indexData[5]))[0]
                if FrameType==1:
                    MorphIndex=struct.unpack(self.IndexTable[indexData[6]],file.read(indexData[6]))[0]

    def LoadRigidBodyData(self,file,DataCount,CodingModel,index):

        self.RigidBodyData=[]
        for dc in range(DataCount):
            
            textSize=struct.unpack('i',file.read(4))[0]
            RigidBodyName_jp=file.read(textSize).decode(CodingModel)
            textSize=struct.unpack('i',file.read(4))[0]
            RigidBodyName_en=file.read(textSize).decode(CodingModel)

            LinkBoneIndex=struct.unpack(self.IndexTable[index],file.read(index))[0]

            GroupId=struct.unpack('b',file.read(1))[0]

            NonCollisionGroup=struct.unpack('h',file.read(2))[0]
            #0=sphere, 1=cube, 2=Capsule
            Shape=struct.unpack('b',file.read(1))[0]
            #球体有效值在[0]半径，Cube 三个值xyz缩放 ，capsule有效值在[0][1]半径和高度
            #看了下索引和在pmx里的值，是有冗余值的
            ShapeSize=struct.unpack('fff',file.read(4*3))
            ShapePosition=struct.unpack('fff',file.read(4*3))
            ShapeRotation=struct.unpack('fff',file.read(4*3))
            Mass=struct.unpack('f',file.read(4))[0]
            MoveAttenuation=struct.unpack('f',file.read(4))[0]
            RotationDamping=struct.unpack('f',file.read(4))[0]
            Repulsion=struct.unpack('f',file.read(4))[0]
            FrictionForce=struct.unpack('f',file.read(4))[0]
            #0=[追踪骨骼]，1=[物理演算] 2= [物理+骨骼位置对齐],绑定信息ref:BuildModel->bulletPhysics
            PhysicsMode=struct.unpack('b',file.read(1))[0]
            rigid = RigidBodyStrust()
            rigid.Name              = RigidBodyName_jp
            rigid.RelatedBoneIndex  = LinkBoneIndex
            rigid.GroupID           = GroupId
            rigid.GroupMask         = NonCollisionGroup
            rigid.ShapeType         = Shape
            rigid.ShapeSize         = ShapeSize
            rigid.Position          = ShapePosition
            rigid.Rotation          = ShapeRotation
            rigid.Mass              = Mass
            rigid.MoveAttenuation   = MoveAttenuation
            rigid.RotationDamping   = RotationDamping
            rigid.Repulsion         = Repulsion
            rigid.FrictionForce     = FrictionForce
            rigid.PhysicsMode       = PhysicsMode
            self.RigidBodyData.append(rigid)

    def LoadJointData(self,file,DataCount,CodingModel,index):
    #{
        self.JointData=[]
        for x in range(DataCount):
            
            size=struct.unpack('i',file.read(4))[0]
            MorphName_jp=file.read(size).decode(CodingModel)
            size=struct.unpack('i',file.read(4))[0]
            MorphName_en=file.read(size).decode(CodingModel)
            jointType=struct.unpack('b',file.read(1))[0]
            rigA = struct.unpack(self.IndexTable[index],file.read(index))[0]
            rigB = struct.unpack(self.IndexTable[index],file.read(index))[0]
            position = struct.unpack('fff',file.read(4*3))
            rotate = struct.unpack('fff',file.read(4*3))
            PosLimitMin = struct.unpack('fff',file.read(4*3))
            PosLimitMax = struct.unpack('fff',file.read(4*3))
            RotLimitMin=struct.unpack('fff',file.read(4*3))
            RotLimitMax=struct.unpack('fff',file.read(4*3))
            PosSpring=struct.unpack('fff',file.read(4*3))
            RotSpring = struct.unpack('fff',file.read(4*3))
            joint=JointStrust()
            joint.Name              = MorphName_jp
            joint.Type              = jointType
            joint.RelatedRigidbodyA = rigA
            joint.RelatedRigidbodyB = rigB
            joint.Position          = position
            joint.Rotate            = rotate
            joint.PositionLimitMin  = PosLimitMin
            joint.PositionLimitMax  = PosLimitMax
            joint.RotateLimitMin    = RotLimitMin
            joint.RotateLimitMax    = RotLimitMax
            joint.PositionSpring    = PosSpring
            joint.RotateSpring      = RotSpring

            self.JointData.append(joint)
    #}
    def __init__(self,pmx_path=None):
        self.VertexIndexTable   = ['*','B','H','*','i']
        self.IndexTable         = ['*','b','h','*','i']
        self.ModelName=[None,None]
        self.Briefing=[None,None]#简介
        self.VertexArray    =   []#以法线数量构建的顶点数组
        self.WeightArray    =   []#权重数据结构，包含了顶点的权重类型，骨骼索引，权重数值
        self.VertexIndex    =   []#顶点索引
        self.TexturePaths   =   []#贴图信息
        self.MaterialData   =   []#材质信息
        self.BoneData       =   [] #骨骼信息
        self.faceIndexTable =   {}#
        self.MorphData      =   []#表情变形数据
        self.RigidBodyData  =   []#bullet刚体数据
        self.JointData      =   []#bullet刚体约束器
        if pmx_path:
            self.PmxRead(pmx_path)
    
    def PmxRead(self,PmxFile):
        codingSet=['utf-16','utf-8']
        #定义一个indexType的索引列表，
        #（除VertexIndex之外的调用，他是额外的长度）
        index_Types=['*','b','h','*','i']
        with open(PmxFile, 'rb') as f:
            #通过使用utf-8的编码模式将4byte编码成string
            chunkName = bytes(struct.unpack('4b', f.read(4))).decode('utf-8')
            version=struct.unpack('f',f.read(4))
            Globals_count=struct.unpack('b',f.read(1))
            #索引的数据类型 1，2，4
            #1 是byte类型，其范围是0-255
            #2 是short类型，其范围是0-32767
            #4 是int类型，其范围是0-2147483647
            #顶点的索引是以上(1,2)的uType版本其范围大概是两倍int类型相同
            globalData=[]
            for i in range(Globals_count[0]):
                tempdata=struct.unpack('b',f.read(1))
                globalData.append(tempdata[0])
            #顺序是根据pmx二进制文件结构编写的
            #根据解码出来的解码id确定解码方式
            codingModel=codingSet[int(globalData[0])]
            size= int(struct.unpack('i', f.read(4))[0])#
            modelNamelocal=f.read(size).decode(codingModel)
            size= int(struct.unpack('i', f.read(4))[0])
            ModelNameUniversal=f.read(size).decode(codingModel)
            size= int(struct.unpack('i', f.read(4))[0])#
            CommentsLocal=f.read(size).decode(codingModel)
            size= int(struct.unpack('i', f.read(4))[0])#
            CommentsUniversal=f.read(size).decode(codingModel)
            globalName=['文字编码:','附加项:','顶点:','纹理:','材质:','骨骼:','形态:','刚体:']
            
            self.ModelName[0]=modelNamelocal
            self.ModelName[1]=ModelNameUniversal
            self.Briefing[0]=CommentsLocal
            self.Briefing[1]=CommentsUniversal
            vertexCount=struct.unpack('i', f.read(4))[0]
            self.LoadVertexData(f,vertexCount,globalData[1],index_Types[globalData[5]],globalData[5])
            #解析面模块的数据，这个数量是顶点索引数，面数要/3
            triangleCount=struct.unpack('i',f.read(4))[0]
            self.LoadSurfaceData(f,triangleCount,globalData[2])
            textureCount = struct.unpack('i',f.read(4))[0]
            self.LoadTextureData(f,textureCount,codingModel)
            MaterialCount = struct.unpack('i',f.read(4))[0]
            self.LoadMaterialData(f,MaterialCount,codingModel,index_Types[globalData[3]],globalData[3])
            BoneCount = struct.unpack('i',f.read(4))[0]
            self.LoadBoneData(f,BoneCount,codingModel,index_Types[globalData[5]],globalData[5])
            MorphCount=struct.unpack('i',f.read(4))[0]
            self.LoadMorphData(f,MorphCount,codingModel,globalData)
            DisplayCount=struct.unpack('i',f.read(4))[0]
            self.LoadDisplayData(f,DisplayCount,codingModel,globalData)
            RigidBodyCount=struct.unpack('i',f.read(4))[0]
            self.LoadRigidBodyData(f,RigidBodyCount,codingModel,globalData[5])

            jointCount=struct.unpack('i',f.read(4))[0]
            self.LoadJointData(f,jointCount,codingModel,globalData[7])
            rest_of_file = f.read()