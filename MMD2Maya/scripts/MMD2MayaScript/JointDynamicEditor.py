



import maya.cmds as cmds
from functools import partial
from MMD2MayaScript.JointDynamicEditorScript import nDynamics as dynamic

class DynamicEditor():
	def __init__(self):
		self.SceneNucleus=[]
		self.createWindow()
		self.updateNucleusTable()
	def createWindow(self):
		if cmds.window('DynamicEditor', exists=True):
		    cmds.deleteUI('DynamicEditor')
		window = cmds.window('DynamicEditor' ,title="动力学骨骼", width=100,height=80)
		form = cmds.formLayout()
		layout1=cmds.columnLayout( adjustableColumn=True )
		cmds.separator(height=10 )
		cmds.rowLayout( numberOfColumns=2,columnAttach=[(1, 'left', 60), (2, 'left', 105)] )
		cmds.text( label=' 动力场:' )
		cmds.text( label='hairSystem:' )
		cmds.setParent('..')
		cmds.rowLayout( numberOfColumns=4,columnAttach=[(1, 'left', 65)])
		cmds.textScrollList('nucleusTable',numberOfRows=8,append=['新建'],allowMultiSelection=False,width=120,selectCommand=partial(self.selectChange))
		cmds.text( label=' -> ' )
		cmds.textScrollList('HairSyetemTable',numberOfRows=8, append=['新建'],allowMultiSelection=False,width=120)
		cmds.setParent('..')	
		cmds.separator(height=10 )
		cmds.rowLayout( numberOfColumns=2,columnAttach=[(1, 'left', 20)])
		cmds.checkBox( label='写入到父级',value=True )
		cmds.setParent('..')	
		cmds.separator(height=10 )
		cmds.rowLayout( numberOfColumns=2)
		cmds.button( label='⚫->⚪->🔘',width=200 ,height=40,command=partial(self.createDynamicByRoot))
		cmds.button( label='⚫->⚪->⚫' ,width=200 ,height=40,command=partial(self.createDynamicTailToRoot))

		cmds.showWindow( window )
	def updateNucleusTable(self):
		self.SceneNucleus=self.searchSceneNucleus()
		cmds.textScrollList('nucleusTable',edit=True,removeAll =True )
		if len(self.SceneNucleus)>1:
			cmds.textScrollList('nucleusTable',edit=True,append =self.SceneNucleus,selectIndexedItem=len(self.SceneNucleus)-1)
			self.selectChange()
		else:
			cmds.textScrollList('nucleusTable',edit=True,append =self.SceneNucleus,selectIndexedItem=1)
			self.selectChange()
	def searchSceneNucleus(self):
		nucleusTab=[]
		nucleusNode = cmds.ls(type='nucleus')
		if nucleusNode!=None:
			for nn in nucleusNode:
				nucleusTab.append(nn)
		nucleusTab.append('新建')
		return nucleusTab
		#return nodeTab
	def selectChange(self):
		index=cmds.textScrollList('nucleusTable',query=True,selectIndexedItem=True)[0]
		actvNucleus=self.SceneNucleus[index-1]
		hairTab = self.searchHairSystem(actvNucleus)
		cmds.textScrollList('HairSyetemTable',edit=True,removeAll =True )
		cmds.textScrollList('HairSyetemTable',edit=True,append =hairTab )
		if len(hairTab)>1:
			cmds.textScrollList('HairSyetemTable',edit=True,selectIndexedItem=len(hairTab)-1)
		else:
			cmds.textScrollList('HairSyetemTable',edit=True,selectIndexedItem=1)
	def searchHairSystem(self,nucleus):
		shapes=[]
		if cmds.objExists(nucleus):
			outputCount = cmds.getAttr(nucleus + '.outputObjects', size=True)
			for index in range(outputCount):
				hairNode = cmds.listConnections( nucleus + '.outputObjects[%i]'%index,d=True, s=False)[0]
				shapes.append(hairNode)
		shapes.append('新建')
		
		return shapes

	def searchJointsByRoot(self,root):
		joints = [root]
		childJoints = cmds.listRelatives(root, allDescendents=True, type='joint')
		childJoints.reverse()
		for child in childJoints:
			joints.append(child)
		return joints

	def SearchJointsTailToRoot(self,root,tail):
		joints = [tail]
		currentJoint = tail
		while (currentJoint != root):
			parentJoint = cmds.listRelatives(currentJoint, parent=True, type='joint')
			if parentJoint:
				joints.append(parentJoint[0])
				currentJoint = parentJoint[0]
			else:
				return
		joints.reverse()
		return joints

	def createDynamicByRoot(self,value):
		selectList = cmds.ls(selection=True, type='joint')
		nucleus = cmds.textScrollList('nucleusTable',query=True,selectItem=True)[0]
		hairSys = cmds.textScrollList('HairSyetemTable',query=True,selectItem=True)[0]
		if not cmds.objExists(nucleus):
			ns=dynamic.createNucleus()
			nucleus=ns[0]
			hairSys=ns[1]
			#更新nucleusTable和HairSyetemTable
			self.updateNucleusTable()
		elif not cmds.objExists(hairSys):
			hairSys=dynamic.createHairSyetem(nucleus)
			#更新HairSyetemTable
			self.selectChange()
		if selectList:
			for joint in selectList:
				jointList=self.searchJointsByRoot(joint)
				dynamic.createDynamic(jointList,nucleus,hairSys)
	def createDynamicTailToRoot(self,value):
		selectList = cmds.ls(selection=True, type='joint')
		if not selectList:
			return
		if len(selectList)==2:
			nucleus = cmds.textScrollList('nucleusTable',query=True,selectItem=True)[0]
			hairSys = cmds.textScrollList('HairSyetemTable',query=True,selectItem=True)[0]
			if not cmds.objExists(nucleus):
				ns=dynamic.createNucleus()
				nucleus=ns[0]
				hairSys=ns[1]
				#更新nucleusTable和HairSyetemTable
				self.updateNucleusTable()
			elif not cmds.objExists(hairSys):
				hairSys=dynamic.createHairSyetem(nucleus)
				#更新HairSyetemTable
				self.selectChange()
			root = selectList[0]
			tail = selectList[1]
			jointList=self.SearchJointsTailToRoot(root,tail)
			dynamic.createDynamic(jointList,nucleus,hairSys)