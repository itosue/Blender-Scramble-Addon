import bpy

################
# オペレーター #
################

class ViewSelectedEX(bpy.types.Operator):
	bl_idname = "view3d.view_selected_ex"
	bl_label = "選択部分を視点の中心に"
	bl_description = "選択中の物に3D視点の中心を合わせます(ズームはしません)"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		co = bpy.context.space_data.cursor_location[:]
		bpy.ops.view3d.snap_cursor_to_selected()
		bpy.ops.view3d.view_center_cursor()
		bpy.context.space_data.cursor_location = co
		return {'FINISHED'}

class ResetCursor(bpy.types.Operator):
	bl_idname = "view3d.reset_cursor"
	bl_label = "カーソルの位置をリセット"
	bl_description = "カーソルのXYZを0.0にします(他の位置も可)"
	bl_options = {'REGISTER', 'UNDO'}
	
	co = bpy.props.FloatVectorProperty(name="カーソル位置", default=(0.0, 0.0, 0.0), step=10, precision=3)
	isLookCenter = bpy.props.BoolProperty(name="視点を3Dカーソルに", default=False)
	
	def execute(self, context):
		context.space_data.cursor_location = self.co
		if (self.isLookCenter):
			bpy.ops.view3d.view_center_cursor()
		return {'FINISHED'}

class ResetView(bpy.types.Operator):
	bl_idname = "view3d.reset_view"
	bl_label = "視点を中心に"
	bl_description = "3Dビューの視点を座標の中心に移動します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		co = context.space_data.cursor_location[:]
		bpy.ops.view3d.view_center_cursor()
		context.space_data.cursor_location = co
		return {'FINISHED'}

################
# メニュー追加 #
################

# メニューを登録する関数
def menu(self, context):
	self.layout.separator()
	self.layout.operator(ResetView.bl_idname, icon="PLUGIN")
	self.layout.operator(ResetCursor.bl_idname, icon="PLUGIN")
	self.layout.operator(ViewSelectedEX.bl_idname, icon="PLUGIN")