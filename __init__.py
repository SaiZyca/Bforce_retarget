bl_info = {
    "name": "Bforce_retarget",
    "author": "BingAI", # Add my name as the author
    "description": "A simple addon for retargeting bones",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Object > Bforce_retarget",
    "category": "Object",
}

import bpy

class Bforce_retarget(bpy.types.Operator):
    """Bforce_retarget"""
    bl_idname = "object.bforce_retarget"
    bl_label = "Bforce_retarget"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        target_armature, source_armature = self.get_source_and_target_armture(context)
        if context.mode == 'OBJECT':
        # collect bones name
            for source_bone in source_armature.pose.bones:
                for target_bone in target_armature.pose.bones:
                    if target_bone.name.lower() == source_bone.name.lower():
                        self.retarget_bone_by_name(context, source_armature, source_bone.name, target_armature, target_bone.name)

        elif context.mode == 'POSE':
            selected_pose_bones = context.selected_pose_bones
            if len(selected_pose_bones) == 2:
                for pose_bone in selected_pose_bones:
                    if pose_bone == context.active_pose_bone:
                        target_bone_name = pose_bone.name
                    else:
                        source_bone_name = pose_bone.name
                                            
                self.retarget_bone_by_name(context, source_armature, source_bone_name, target_armature, target_bone_name)
                    
                return {'FINISHED'}
            else:
                # Return cancelled
                return {'CANCELLED'}
                
        return {'FINISHED'}

    def get_source_and_target_armture(self, context):
        selected_objects = context.selected_objects
        if len(selected_objects) == 2 and all(obj.type == 'ARMATURE' for obj in selected_objects):
            for obj in selected_objects:
                if obj == context.object:
                    target_armature = bpy.data.objects[obj.name]
                    target_armature.data.display_type = 'STICK'
                    target_armature.show_in_front = True

                else:
                    source_armature = bpy.data.objects[obj.name]
                    source_armature.data.display_type = 'OCTAHEDRAL'
                    source_armature.show_in_front = False
                    
        return target_armature, source_armature

    def retarget_bone_by_name(self, context, source_armature, source_bone_name, target_armature, target_bone_name):
        # init
        bpy.ops.object.mode_set(mode="EDIT")
        self.clean_bone_select(context)
        # clean active bone
        source_armature.data.edit_bones.active = None
        target_armature.data.bones.active = None
        # get armature bone 
        source_bone = source_armature.data.edit_bones[source_bone_name]
        source_bone.select = True
        
        target_bone = target_armature.data.edit_bones[target_bone_name]
        target_bone.select = True
        target_armature.data.edit_bones.active = target_armature.data.edit_bones[target_bone_name]

        bpy.ops.armature.calculate_roll(type='ACTIVE')
        # define pose_bone and 
        bpy.ops.object.mode_set(mode="POSE")
        source_bone = source_armature.pose.bones[source_bone_name]
        target_bone = target_armature.pose.bones[target_bone_name]
        target_armature.data.bones.active = target_armature.data.bones[target_bone_name]
        
        constrant = source_bone.constraints.new('COPY_TRANSFORMS')
        constrant.target = target_armature
        constrant.subtarget = target_bone_name
        
        return {'FINISHED'}
        
    def clean_bone_select(self, context):
        if context.selected_bones:
            for bone in context.selected_bones:
                bone.select = False
        if context.selected_pose_bones:
            for pose_bone in context.selected_pose_bones:
                pose_bone.bone.select = False
            
        return {'FINISHED'}
        

    def draw(self, context):
        layout = self.layout
        layout.operator("object.bforce_retarget", text="Retarget Bones")

    # Modify the poll method to check only the object type
    @classmethod
    def poll(cls, context):
        # Check if the object is an armature
        return context.object and context.object.type == 'ARMATURE'

class Bforce_remove(bpy.types.Operator):
    """Bforce_remove"""
    bl_idname = "object.bforce_remove"
    bl_label = "Bforce_remove"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_bones = context.selected_pose_bones
        for bone in selected_bones:
            for constrant in bone.constraints:
                if constrant.type == 'COPY_TRANSFORMS':
                    bone.constraints.remove(constrant)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        # Set the emboss parameter to False and the icon parameter to CANCEL
        layout.operator("object.bforce_remove", text="Remove Constraints", emboss=False, icon='CANCEL')

    # Add a poll method to check the object type
    @classmethod
    def poll(cls, context):
        # Check if the object is an armature and is in pose mode
        return context.object and context.object.type == 'ARMATURE' and context.mode == 'POSE'

class Bforce_panel(bpy.types.Panel):
    """Bforce_panel"""
    bl_label = "Bforce Panel"
    bl_idname = "OBJECT_PT_bforce"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bforce"

    def draw(self, context):
        layout = self.layout
        # Use the draw method of the operators to draw the buttons
        Bforce_retarget.draw(self, context)
        Bforce_remove.draw(self, context)

def register():
    bpy.utils.register_class(Bforce_retarget)
    bpy.utils.register_class(Bforce_remove)
    bpy.utils.register_class(Bforce_panel)

def unregister():
    bpy.utils.unregister_class(Bforce_retarget)
    bpy.utils.unregister_class(Bforce_remove)
    bpy.utils.unregister_class(Bforce_panel)

if __name__ == "__main__":
    register()
