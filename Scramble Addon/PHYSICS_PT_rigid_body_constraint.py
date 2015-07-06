# 「プロパティ」エリア > 「物理演算」タブ > 「剛体コンストレイント」パネル

import bpy

################
# オペレーター #
################

class CopyConstraintSetting(bpy.types.Operator):
	bl_idname = "rigidbody.copy_constraint_setting"
	bl_label = "Copy sets rigid constraints"
	bl_description = "Copies selected objects for other rigid constraints on active object"
	bl_options = {'REGISTER', 'UNDO'}
	
	copy_target_objects = bpy.props.BoolProperty(name="Addressing objects to be copied", default=False)
	
	@classmethod
	def poll(cls, context):
		if 2 <= len(context.selected_objects):
			if context.active_object:
				if context.active_object.rigid_body_constraint:
					return True
		return False
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
	def execute(self, context):
		active_ob = context.active_object
		for ob in context.selected_objects:
			if ob.name == active_ob.name:
				continue
			if not ob.rigid_body_constraint:
				context.scene.objects.active = ob
				bpy.ops.rigidbody.constraint_add()
			for val_name in dir(ob.rigid_body_constraint):
				if not self.copy_target_objects:
					if (val_name in ['object1', 'object2']):
						continue
				if val_name[0] != '_' and 'rna' not in val_name:
					value = active_ob.rigid_body_constraint.__getattribute__(val_name)
					try:
						ob.rigid_body_constraint.__setattr__(val_name, value[:])
					except TypeError:
						try:
							ob.rigid_body_constraint.__setattr__(val_name, value)
						except AttributeError:
							pass
					except AttributeError:
						pass
		context.scene.objects.active = active_ob
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
		self.layout.operator(CopyConstraintSetting.bl_idname, icon='LINKED')
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]