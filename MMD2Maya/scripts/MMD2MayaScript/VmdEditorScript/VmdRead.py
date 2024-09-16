import struct


class BoneMotionStrust:

    def __init__(self):
        self.FrameTime      =   0
        self.Translation    =   [0.0,0.0,0.0]
        self.Rotation       =   [0.0,0.0,0.0]
        self.TweenedX       =   [0.0,0.0,0.0,0.0]
        self.TweenedY       =   [0.0,0.0,0.0,0.0]
        self.TweenedZ       =   [0.0,0.0,0.0,0.0]
        self.QuatLerp       =   [0.0,0.0,0.0,0.0]

class MorphMotionStrust:
    def __init__(self):
        #self.MorphName  =   ''
        self.FrameTime  = 0
        self.weight     = 0.0 

class CameraMotionStrust:
    def __init__(self):
        self.FrameTime  = 0
        self.Distance   = 0.0
        self.Interest   = [0,0,0]
        self.Rotate     = [0,0,0]
        self.InterestTweenedX   = [0,0,0,0]#单元素取值范围:0-127
        self.InterestTweenedY   = [0,0,0,0]
        self.InterestTweenedZ   = [0,0,0,0]
        self.RotateTweenedX     = [0,0,0,0]
        self.RotateTweenedY     = [0,0,0,0]
        self.RotateTweenedZ     = [0,0,0,0]
        self.ViewAngle          = 0.0
        self.Perspective        = True 

class LightMotionStrust:
    def __init__(self):
        self.FrameTime  = 0
        self.Color      = [1.0,1.0,1.0]
        self.Position   = [0.0,0.0,0.0]
class ShadowMotionStrust:
    def __init__(self):
        self.FrameTime  = 0
        self.ShadowType = 0     # 0:Off 1:mode1 2:mode2 , 【PCF 和PCSS?】
        self.Distance   = 0.0

#同样以骨骼名去索引帧数据
class IKMotionStrust:
    def __init__(self):
        self.FrameTime  = 0
        self.Show       = True 
        self.Eanble     = True
class DecodeVMD:

    def __init__(self,vmdFile=None):
        self.Briefing=''
        self.BoneMotionData     = {}
        self.MorphMotionData    = {}
        self.IKMotionData       = {}

        if vmdFile:
            self.VMDRead(vmdFile)

    def VMDRead(self,vmdfile):
    #{
        with open(vmdfile,'rb')as f:
        #{
            #头文件是30byte的ascii编码
            chunkName   = (f.read(30).rstrip(b'\0')).decode('ascii')
            #print(chunkName)
            if chunkName.startswith("Vocaloid Motion Data file"):
                vision = 1
            elif chunkName.startswith("Vocaloid Motion Data 0002"):
                vision = 2
            else:
                raise Exception("位置版本号")
            #print(vision)
            #这个解码格式官方文档显示为shift-JIS【即日语编码】，但是有可能是GB2312【听说神帝宇大佬的即是这样的】
            #由于固定10&20byte,编码的时候如果名字过长会导致数据丢失，也会导致解码失败
            #encodeTable = ['shift-jis','gb2312','utf-8','utf-16']
            #for encoding in encodeTable:
            #    try:
            #        #这个模型名称的位数与版本相关，旧版本是10，新版本是20
            #        modelName=(f.read(10*vision).rstrip(b'\0'))
            #        print(str(modelName))
            #        #modelName=modelName.decode(encoding, errors='replace')
            #        modelName=modelName.decode(encoding)
            #        break 
            #    except:
            #        if encoding == 'utf-16':
            #            break
            #        f.seek(-10*vision, 1) # 解码失败，回读
            modelName=(f.read(10*vision).rstrip(b'\0')).decode('shift-jis', errors='replace')
            self.Briefing+=modelName+'\n'
            BoneKeyNumber   = struct.unpack('i', f.read(4))[0]
            self.Briefing+='骨骼帧数：'+str(BoneKeyNumber)+'\n'
            self.ReadBoneData(f,BoneKeyNumber)

            MorphKeyNumber  = struct.unpack('i', f.read(4))[0]
            self.Briefing+='表情帧数：'+str(MorphKeyNumber)+'\n'
            self.ReadMorphData(f,MorphKeyNumber)
            CameraKeyNumber =  struct.unpack('i', f.read(4))[0]
            self.Briefing+='相机帧数：'+str(CameraKeyNumber)+'\n'
            self.ReadCameraData(f,CameraKeyNumber)
            LightKeys =  struct.unpack('i', f.read(4))[0]
            self.Briefing+='灯光帧：'+str(LightKeys)+'\n'
            for Ln in range(LightKeys):
                LightFrame   =   struct.unpack('i', f.read(4))[0]#有效帧
                LightColor =   struct.unpack('fff', f.read(3*4))#
                LightPosition =   struct.unpack('fff', f.read(3*4))#不会是个点光源吧
            ShadowKeys = struct.unpack('i', f.read(4))[0]
            self.Briefing+='阴影帧：'+str(ShadowKeys)+'\n'
            for Sn in range(ShadowKeys):
                ShadowFrame =   struct.unpack('i', f.read(4))[0]#有效帧
                ShadowType = struct.unpack('b', f.read(1))[0]# 0:Off 1:mode1 2:mode2 , 【PCF 和PCSS?】
                ShadowDistance = struct.unpack('f', f.read(4))[0]
            #并非所有文件都有ik数据
            Res=f.read()
            if len(Res)<4:
                return
            f.seek(-len(Res),1)
            IKKeyNumber = struct.unpack('i', f.read(4))[0]
            self.Briefing+='IK帧：'+str(IKKeyNumber)+'\n'
            self.ReadIKData(f,IKKeyNumber)
        #}with end
        #print('读取完--')
    #}

    def ReadBoneData(self,file,keyNumber):
    #{
        self.BoneMotionData = {}
        for x in range(keyNumber):
        #{
            #print('=========================================\n'+'帧编号：'+str(x)) 
            #固定位数的字符串读取出来会发生空格填充，对于PMX的指定位读取不能匹配
            #使用.rstrip(b'\0')跳过填充位
            boneName    =   (file.read(15).rstrip(b'\0')).decode('shift-JIS')

            FrameTime   =   struct.unpack('i', file.read(4))[0]#有效帧

            Translation =   struct.unpack('fff', file.read(3*4))#平移（世界位置）

            Rotation    =   struct.unpack('ffff', file.read(4*4))#旋转（四元数）
            #每四位的后三位是杂乱数据，不是补位\0
            #[0,0,0,0],前两位是前一帧outputTargent的二维坐标，后两位是当前帧inputTargent的二维坐标
            XCurver=[0,0,0,0]
            XCurver[0] =   struct.unpack('b', file.read(1))[0]#补间曲线 （平移X）
            file.seek(3,1)
            XCurver[1] =   struct.unpack('b', file.read(1))[0]#补间曲线 （平移X）
            file.seek(3,1)
            XCurver[2] =   struct.unpack('b', file.read(1))[0]#补间曲线 （平移X）
            file.seek(3,1)
            XCurver[3] =   struct.unpack('b', file.read(1))[0]#补间曲线 （平移X）
            file.seek(3,1)
            YCurver=[0,0,0,0]
            YCurver[0]= struct.unpack('b', file.read(1))[0]#补间曲线 （平移Y）
            file.seek(3,1)
            YCurver[1]= struct.unpack('b', file.read(1))[0]#补间曲线 （平移Y）
            file.seek(3,1)
            YCurver[2]= struct.unpack('b', file.read(1))[0]#补间曲线 （平移Y）
            file.seek(3,1)
            YCurver[3]= struct.unpack('b', file.read(1))[0]#补间曲线 （平移Y）
            file.seek(3,1)

            ZCurver=[0,0,0,0]
            ZCurver[0]= struct.unpack('b', file.read(1))[0]#补间曲线 （平移Z）
            file.seek(3,1)
            ZCurver[1]= struct.unpack('b', file.read(1))[0]#补间曲线 （平移Z）
            file.seek(3,1)
            ZCurver[2]= struct.unpack('b', file.read(1))[0]#补间曲线 （平移Z）
            file.seek(3,1)
            ZCurver[3]= struct.unpack('b', file.read(1))[0]#补间曲线 （平移Z）
            file.seek(3,1)

            RCurver=[0,0,0,0]
            RCurver[0]= struct.unpack('b', file.read(1))[0]#补间曲线 （四元数）
            file.seek(3,1)
            RCurver[1]= struct.unpack('b', file.read(1))[0]#补间曲线 （四元数）
            file.seek(3,1)
            RCurver[2]= struct.unpack('b', file.read(1))[0]#补间曲线 （四元数）
            file.seek(3,1)
            RCurver[3]= struct.unpack('b', file.read(1))[0]#补间曲线 （四元数）
            file.seek(3,1)

            if boneName not in self.BoneMotionData:
                self.BoneMotionData[boneName]=[]
                TempData=BoneMotionStrust()
                TempData.FrameTime=FrameTime
                TempData.Translation = Translation
                TempData.Rotation = Rotation 
                TempData.TweenedX = XCurver
                TempData.TweenedY = YCurver
                TempData.TweenedZ = ZCurver
                TempData.QuatLerp = RCurver
                self.BoneMotionData[boneName].append(TempData)
            else:
                TempData=BoneMotionStrust()
                TempData.FrameTime=FrameTime
                TempData.Translation = Translation
                TempData.Rotation = Rotation 
                TempData.TweenedX = XCurver
                TempData.TweenedY = YCurver
                TempData.TweenedZ = ZCurver
                TempData.QuatLerp = RCurver
                self.BoneMotionData[boneName].append(TempData)
        #}
    #}
    def ReadMorphData(self,file,keyNumber):
    #{
        self.MorphMotionData = {}
        for Mn in range(keyNumber):
        #{
            MorphName    =   (file.read(15).rstrip(b'\0')).decode('shift-JIS')
            MorphFrame   =   struct.unpack('i', file.read(4))[0]#有效帧
            MorphWeight  =   struct.unpack('f', file.read(4))[0]

            if MorphName not in self.MorphMotionData:
                self.MorphMotionData[MorphName]=[]
                tempData = MorphMotionStrust()
                tempData.FrameTime = MorphFrame
                tempData.weight = MorphWeight
                self.MorphMotionData[MorphName].append(tempData)
            else:
                tempData = MorphMotionStrust()
                tempData.FrameTime = MorphFrame
                tempData.weight = MorphWeight
                self.MorphMotionData[MorphName].append(tempData)
        #}
    #}
    def ReadCameraData(self,file,keyNumber):
    #{
        for Cn in range(keyNumber):
        #{
            CameraFrame     =   struct.unpack('i', file.read(4))[0]#有效帧
            CameraDistance  =   struct.unpack('f', file.read(4))[0]#distance？指相机标点到相机的距离?(camera_group上的约束间距？)
            CameraInterest  =   struct.unpack('fff', file.read(3*4))#标点位置？（世界位置）
            CameraRotate    =   struct.unpack('fff', file.read(3*4))#旋转（世界位置）
            #f.seek(24,1)#这24个字节...是插值曲线？
            #[lastOutX,lastOutY,currentInputX,currentInputY]  这个没有补位数据了？
            IX1 = struct.unpack('b', file.read(1))[0]#补间曲线 （平移X）
            IX2 = struct.unpack('b', file.read(1))[0]#补间曲线 （平移X）
            IX3 = struct.unpack('b', file.read(1))[0]#补间曲线 （平移X）
            IX4 = struct.unpack('b', file.read(1))[0]#补间曲线 （平移X）
            
            IY1 = struct.unpack('b', file.read(1))[0]#补间曲线 （平移Y）
            IY2 = struct.unpack('b', file.read(1))[0]#补间曲线 （平移Y）
            IY3 = struct.unpack('b', file.read(1))[0]#补间曲线 （平移Y）
            IY4 = struct.unpack('b', file.read(1))[0]#补间曲线 （平移Y）
            
            IY1 = struct.unpack('b', file.read(1))[0]#补间曲线 （平移Y）
            IY2 = struct.unpack('b', file.read(1))[0]#补间曲线 （平移Y）
            IY3 = struct.unpack('b', file.read(1))[0]#补间曲线 （平移Y）
            IY4 = struct.unpack('b', file.read(1))[0]#补间曲线 （平移Y）
            InterestXCurver =   [IX1,IX2,IX3,IX4]
            InterestYCurver =   [IY1,IY2,IY3,IY4]
            InterestZCurver =   [IZ1,IZ2,IZ3,IZ4]
            #print("补间曲线："+'\n\t X:'+str(InterestXCurver)+'\n\t Y:'+str(InterestYCurver)+'\n\t Z:'+str(InterestZCurver))
            RX1 = struct.unpack('b', file.read(1))[0]#补间曲线 （旋转X）
            RX2 = struct.unpack('b', file.read(1))[0]#补间曲线 （旋转X）
            RX3 = struct.unpack('b', file.read(1))[0]#补间曲线 （旋转X）
            RX4 = struct.unpack('b', file.read(1))[0]#补间曲线 （旋转X）
                                                              
            RY1 = struct.unpack('b', file.read(1))[0]#补间曲线 （旋转Y）
            RY2 = struct.unpack('b', file.read(1))[0]#补间曲线 （旋转Y）
            RY3 = struct.unpack('b', file.read(1))[0]#补间曲线 （旋转Y）
            RY4 = struct.unpack('b', file.read(1))[0]#补间曲线 （旋转Y）
                                                              
            RY1 = struct.unpack('b', file.read(1))[0]#补间曲线 （旋转Y）
            RY2 = struct.unpack('b', file.read(1))[0]#补间曲线 （旋转Y）
            RY3 = struct.unpack('b', file.read(1))[0]#补间曲线 （旋转Y）
            RY4 = struct.unpack('b', file.read(1))[0]#补间曲线 （旋转Y）
            RotateXCurver =   [RX1,RX2,RX3,RX4]
            RotateYCurver =   [RY1,RY2,RY3,RY4]
            RotateZCurver =   [RZ1,RZ2,RZ3,RZ4]
            viewAngle   = struct.unpack('i', file.read(4))[0]#有效帧
            Perspective = struct.unpack('b', file.read(1))[0]#正交相机的切换吧？
        #}
    #}

    def ReadIKData(self,file,keyNumber):
    #{
        self.IKMotionData = {}
        for kn in range(keyNumber):
            IKFrame = struct.unpack('i', file.read(4))[0]
            IKShow  = struct.unpack('b', file.read(1))[0]
            numb    = struct.unpack('i', file.read(4))[0]
            for nb in range(numb):
                IKName = (file.read(20).rstrip(b'\0')).decode('shift-JIS')
                IKEnable = struct.unpack('b', file.read(1))[0]
                if IKName not in self.IKMotionData:
                    self.IKMotionData[IKName] =[]
                    TempData = IKMotionStrust()
                    TempData.FrameTime=IKFrame
                    TempData.Show = IKShow
                    TempData.Eanble = bool(IKEnable)
                    self.IKMotionData[IKName].append(TempData)
                else:
                    TempData = IKMotionStrust()
                    TempData.FrameTime=IKFrame
                    TempData.Show = IKShow
                    TempData.Eanble = bool(IKEnable)
                    self.IKMotionData[IKName].append(TempData)
    #}