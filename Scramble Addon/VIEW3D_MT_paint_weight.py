import bpy

##############
# その他関数 #
##############

################
# オペレーター #
################

class MargeSelectedVertexGroup(bpy.types.Operator):
	bl_idname = "mesh.marge_selected_vertex_group"
	bl_label = "ウェイトの合成"
	bl_description = "選択中のボーンと同じ頂点グループのウェイトを統合した新規頂点グループを作成します"
	bl_options = {'REGISTER', 'UNDO'}
	
	isReplace = bpy.props.BoolProperty(name="アクティブを置換", default=True)
	ext = bpy.props.StringProperty(name="新頂点グループ名の末尾", default="...等の合成")
	
	def execute(self, context):
		obj = context.active_object
		me = obj.data
		if (self.isReplace):
			newVg = obj.vertex_groups[context.active_pose_bone.name]
		else:
			newVg = obj.vertex_groups.new(name=context.active_pose_bone.name+self.ext)
		boneNames = []
		for bone in context.selected_pose_bones:
			boneNames.append(bone.name)
		for vert in me.vertices:
			for vg in vert.groups:
				if (not self.isReplace or newVg.name != obj.vertex_groups[vg.group].name):
					if (obj.vertex_groups[vg.group].name in boneNames):
						newVg.add([vert.index], vg.weight, 'ADD')
		bpy.ops.object.mode_set(mode="OBJECT")
		bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
		obj.vertex_groups.active_index = newVg.index
		return {'FINISHED'}

class VertexGroupAverageAll(bpy.types.Operator):
	bl_idname = "mesh.vertex_group_average_all"
	bl_label = "全頂点の平均ウェイトで塗り潰す"
	bl_description = "全てのウェイトの平均で、全ての頂点を塗り潰します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		obj = context.active_object
		if (obj.type == "MESH"):
			vgs = []
			for i in range(len(obj.vertex_groups)):
				vgs.append([])
			vertCount = 0
			for vert in obj.data.vertices:
				for vg in vert.groups:
					vgs[vg.group].append(vg.weight)
				vertCount += 1
			vg_average = []
			for vg in vgs:
				vg_average.append(0)
				for w in vg:
					vg_average[-1] += w
				vg_average[-1] /= vertCount
			i = 0
			for vg in obj.vertex_groups:
				vg.add(range(vertCount), vg_average[i], "REPLACE")
				i += 1
		bpy.ops.object.mode_set(mode="OBJECT")
		bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
		return {'FINISHED'}

################
# メニュー追加 #
################

# メニューを登録する関数
def menu(self, context):
	self.layout.separator()
	self.layout.operator(MargeSelectedVertexGroup.bl_idname, icon="PLUGIN")
	self.layout.separator()
	self.layout.operator(VertexGroupAverageAll.bl_idname, icon="PLUGIN")
