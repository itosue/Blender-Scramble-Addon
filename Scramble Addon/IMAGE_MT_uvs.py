# 「UV/画像エディター」エリア > 「UV」メニュー
# "UV/Image Editor" Area > "UV" Menu

import bpy, bmesh

################
# オペレーター #
################

class ConvertMesh(bpy.types.Operator):
	bl_idname = "uv.convert_mesh"
	bl_label = "Convert UV to mesh"
	bl_description = "Converts new mesh to UV active"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		obj = context.object
		if (not obj):
			self.report(type={'ERROR'}, message="An active object is not found")
			return {'CANCELLED'}
		if (obj.type != 'MESH'):
			self.report(type={'ERROR'}, message="This is not mesh object")
			return {'CANCELLED'}
		me = obj.data
		if (not me.uv_layers.active):
			self.report(type={'ERROR'}, message="UV cannot be found")
			return {'CANCELLED'}
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		
		new_mesh_name = obj.name + ":" + me.uv_layers.active.name
		new_me = bpy.data.meshes.new(new_mesh_name)
		new_obj = bpy.data.objects.new(new_mesh_name, new_me)
		context.scene.objects.link(new_obj)
		
		bm = bmesh.new()
		bm.from_mesh(me)
		uv_lay = bm.loops.layers.uv.active
		
		pydata_verts = []
		already_verts = []
		pydata_uvs = []
		for face in bm.faces:
			for loop in face.loops:
				uv = loop[uv_lay].uv
				vert = loop.vert
				id = (vert.index, uv.x, uv.y)
				if (id not in already_verts):
					x = (uv.x - 0.5) * 2
					y = (uv.y - 0.5) * 2
					pydata_verts.append((x, y, 0.0))
					pydata_uvs.append(uv[:])
					already_verts.append(id)
		
		pydata_edges = []
		pydata_faces = []
		already_edges = []
		already_faces = []
		for face in bm.faces:
			ids = []
			for loop in face.loops:
				id = (loop.vert.index, loop[uv_lay].uv.x, loop[uv_lay].uv.y)
				ids.append(id)
			for loop in face.loops:
				uv = loop[uv_lay].uv
				vert = loop.vert
				edge = loop.edge
				face = loop.face
				"""
				pydata_edge = []
				vert_index = [edge.verts[0].index, edge.verts[1].index]
				for index in vert_index:
					for id in ids:
						if (index == id[0]):
							pydata_edge.append(already_verts.index(id))
							break
				if (set(pydata_edge) not in already_edges):
					pydata_edges.append(pydata_edge)
					already_edges.append(set(pydata_edge))
				"""
				pydata_face = []
				vert_index = []
				for v in face.verts:
					vert_index.append(v.index)
				for index in vert_index:
					for id in ids:
						if (index == id[0]):
							pydata_face.append(already_verts.index(id))
							break
				
				if (set(pydata_face) not in already_faces):
					pydata_faces.append(pydata_face)
					already_faces.append(set(pydata_face))
		new_me.from_pydata(pydata_verts, [], pydata_faces)
		
		new_me.uv_textures.new(me.uv_layers.active.name)
		new_bm = bmesh.new()
		new_bm.from_mesh(new_me)
		uv_lay = new_bm.loops.layers.uv.active
		for face in new_bm.faces:
			for loop in face.loops:
				uv = loop[uv_lay].uv
				vert = loop.vert
				
				loop[uv_lay].uv = pydata_uvs[vert.index]
		new_bm.to_mesh(new_me)
		new_bm.free()
		
		new_obj.select = True
		context.scene.objects.active = new_obj
		return {'FINISHED'}

class scale_uv_parts(bpy.types.Operator):
	bl_idname = "uv.scale_uv_parts"
	bl_label = "Resize UV Islands"
	bl_description = "UV island into central position and resize"
	bl_options = {'REGISTER', 'UNDO'}
	
	scale = bpy.props.FloatProperty(name="Size", default=0.9, min=0, max=10, soft_min=0, soft_max=10, step=3, precision=2)
	items = [
		('MEDIAN', "Median Point", "", 1),
		('CENTER', "Bounding Box Center", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="Center")
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
	def execute(self, context):
		pre_pivot_point = context.space_data.pivot_point
		context.space_data.pivot_point = self.mode
		ob = context.active_object
		me = ob.data
		bpy.ops.uv.select_all(action='DESELECT')
		bm = bmesh.from_edit_mesh(me)
		uv_lay = bm.loops.layers.uv.active
		alreadys = []
		for face in bm.faces:
			for loop in face.loops:
				uv = loop[uv_lay].uv
				vert = loop.vert
				id = (vert.index, uv.x, uv.y)
				if id not in alreadys:
					alreadys.append(id)
					loop[uv_lay].select = True
					bpy.ops.uv.select_linked(extend=False)
					bpy.ops.transform.resize(value=(self.scale, self.scale, self.scale))
					for f in bm.faces:
						for l in f.loops:
							if l[uv_lay].select:
								u = l[uv_lay].uv
								v = l.vert
								i = (v.index, u.x, u.y)
								alreadys.append(i)
					bpy.ops.uv.select_all(action='DESELECT')
		bmesh.update_edit_mesh(me)
		context.space_data.pivot_point = pre_pivot_point
		return {'FINISHED'}

################
# メニュー追加 #
################

# メニューのオン/オフの判定
def IsMenuEnable(self_id):
	for id in bpy.context.user_preferences.addons["Scramble Addon"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		self.layout.separator()
		self.layout.operator(scale_uv_parts.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(ConvertMesh.bl_idname, icon='PLUGIN')
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
