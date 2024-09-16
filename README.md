
# MMD2Maya
- ## 运行环境 :
	- 平台支持：
		- win64 
	- Maya版本 :
		- Maya2022
		- Maya2023
		- Maya2024
		- Maya2025
- ## 安装说明：
	-  直接把`MMD2MayaSetup.mel`文件拖拽到Maya窗口		
	-  由于实现了预加载 , 所以会弹出外部插件载入的提示 , 选择`允许`载入

- ## 插件介绍 :
	- 本插件是以外部自定义节点`MD2MayaNode`计算数值然后传回Maya内部节点的方式运行的
	- 其平移和旋转的控制是由`MikuDanceTranslate`和`MikuDanceRotates`属性传到MD2MayaNode，经过计算传回默认的translate和rotate
	- 要编辑旋转和平移属性，请右键MD2MayaTool下的平移和旋转图标然后选择覆盖,会在按下W,R并且选择被连接到MD2MayaNode的时候切换到自定义属性的控制柄
	- ### 当前版本不支持的 :
		- 对于连接到`MD2MayaNode`的节点:
			1. 不支持`RotateAxis`属性
			2. 其缩放`Scale`值必须始终为 1
			3. 对于旋转顺序`rotateOrder` 仅支持默认的`xyz`
			4. 不支持控制柄偏移 , 连接之前需要将控制柄恢复到物体中心