# 情報 > 「ファイル」メニュー > 「外部データ」メニュー

import bpy
import os, shutil

################
# オペレーター #
################

class ResaveAllImage(bpy.types.Operator):
	bl_idname = "image.resave_all_image"
	bl_label = "全ての画像をtexturesフォルダに保存し直す"
	bl_description = "外部ファイルを参照している画像データを全てtexturesフォルダに保存し直します"
	bl_options = {'REGISTER'}
	
	@classmethod
	def poll(cls, context):
		if (context.blend_data.filepath == ""):
			return False
		for img in bpy.data.images:
			if (img.filepath != ""):
				return True
		return False
	def execute(self, context):
		for img in context.blend_data.images:
			if (img.filepath != ""):
				try:
					img.pack()
					img.unpack()
				except RuntimeError:
					pass
		self.report(type={"INFO"}, message="texturesフォルダに保存し直しました")
		return {'FINISHED'}

class IsolationTexturesUnusedFiles(bpy.types.Operator):
	bl_idname = "image.isolation_textures_unused_files"
	bl_label = "texturesフォルダ内の未使用ファイルを隔離"
	bl_description = "このBlendファイルのあるフォルダのtextures内で、使用していないファイルをbackupフォルダに隔離します"
	bl_options = {'REGISTER'}
	
	@classmethod
	def poll(cls, context):
		path = context.blend_data.filepath
		if (context.blend_data.filepath == ""):
			return False
		dir = os.path.dirname(path)
		if (not os.path.isdir( os.path.join(dir, "textures") )):
			return False
		for img in bpy.data.images:
			if (img.filepath != ""):
				return True
		return False
	def execute(self, context):
		names = []
		for img in context.blend_data.images:
			if (img.filepath != ""):
				names.append(bpy.path.basename(img.filepath))
		tex_dir = os.path.join( os.path.dirname(context.blend_data.filepath), "textures")
		backup_dir = os.path.join(tex_dir, "backup")
		if (not os.path.isdir(backup_dir)):
			os.mkdir(backup_dir)
		for name in os.listdir(tex_dir):
			path = os.path.join(tex_dir, name)
			if (not os.path.isdir(path)):
				if (name not in names):
					src = path
					dst = os.path.join(path, backup_dir, name)
					shutil.move(src, dst)
					self.report(type={'INFO'}, message=name+"を隔離")
		return {'FINISHED'}

class OpenRecentFiles(bpy.types.Operator):
	bl_idname = "wm.open_recent_files"
	bl_label = "「最近使ったファイル」をテキストで開く"
	bl_description = "「最近使ったファイル」をBlenderのテキストエディタで開きます"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		path = os.path.join(bpy.utils.user_resource('CONFIG'), "recent-files.txt")
		pre_texts = context.blend_data.texts[:]
		bpy.ops.text.open(filepath=path)
		for text in context.blend_data.texts[:]:
			for pre in pre_texts:
				if (text.name == pre.name):
					break
			else:
				new_text = text
				break
		max_area = 0
		target_area = None
		for area in context.screen.areas:
			if (area.type == 'TEXT_EDITOR'):
				target_area = area
				break
			if (max_area < area.height * area.width):
				max_area = area.height * area.width
				target_area = area
		target_area.type = 'TEXT_EDITOR'
		for space in target_area.spaces:
			if (space.type == 'TEXT_EDITOR'):
				space.text = new_text
		return {'FINISHED'}

class OpenBookmarkText(bpy.types.Operator):
	bl_idname = "wm.open_bookmark_text"
	bl_label = "「ブックマーク」をテキストで開く"
	bl_description = "ファイルブラウザのブックマークをBlenderのテキストエディタで開きます"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		path = os.path.join(bpy.utils.user_resource('CONFIG'), "bookmarks.txt")
		pre_texts = context.blend_data.texts[:]
		bpy.ops.text.open(filepath=path)
		for text in context.blend_data.texts[:]:
			for pre in pre_texts:
				if (text.name == pre.name):
					break
			else:
				new_text = text
				break
		max_area = 0
		target_area = None
		for area in context.screen.areas:
			if (area.type == 'TEXT_EDITOR'):
				target_area = area
				break
			if (max_area < area.height * area.width):
				max_area = area.height * area.width
				target_area = area
		target_area.type = 'TEXT_EDITOR'
		for space in target_area.spaces:
			if (space.type == 'TEXT_EDITOR'):
				space.text = new_text
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
		self.layout.operator('image.reload_all_image', icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(ResaveAllImage.bl_idname, icon="PLUGIN")
		self.layout.operator(IsolationTexturesUnusedFiles.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(OpenRecentFiles.bl_idname, icon="PLUGIN")
		self.layout.operator(OpenBookmarkText.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
