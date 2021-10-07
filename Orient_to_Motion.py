# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# Contributed to Germano Cavalcante (mano-wii), Florian Meyer (testscreenings),
# Brendon Murphy (meta-androcto),
# Maintainer:	Vladimir Spivak (cwolf3d)
# Originally an addon by Bart Crouch

bl_info = {
    "name": "Orient to Motion",
    "author": "Michael Soluyanov (Multlabs.com)",
    "version": (1, 0, 0),
    "blender": (2, 92, 0),
    "location": "View3D > Object > Animation -> Orient to Motion",
    "warning": "",
    "description": "Orient object to its motion, keyframe or every frame",
    "category": "Animation",
}


import bpy
import mathutils

def main(context, forward, up, keys):
    
   
    for ob in context.selected_objects:
        lockkeys = [[],[],[],[]]
        last=False
        
        
        
        if keys=="keys":
            for fc in ob.animation_data.action.fcurves:
                for kf in fc.keyframe_points:
                    if fc.data_path == 'location':
                        lockkeys[fc.array_index].append(kf.co[1])
                        lockkeys[3].append(kf.co[0])
        else:
            min = int(ob.animation_data.action.fcurves[0].keyframe_points[0].co[0])
            max = int(ob.animation_data.action.fcurves[0].keyframe_points[0].co[0])
            for fc in ob.animation_data.action.fcurves:
                for kf in fc.keyframe_points: 
                    if kf.co[0]<min: min = kf.co[0]
                    if kf.co[0]>max: max = kf.co[0]
                    
            for frame in range(int(min), int(max)):
                bpy.context.scene.frame_set(frame)
                lockkeys[0].append(ob.location.x)
                lockkeys[1].append(ob.location.y)
                lockkeys[2].append(ob.location.z)
                lockkeys[3].append(frame)
            
        print(lockkeys)
        for i in range(0, len(lockkeys[0])):
           
               
            #define direction
            if i<=0: k1=0
            else: k1 = i-1
            if i>=len(lockkeys[0])-1: k2=len(lockkeys[0])-1
            else: k2 = i+1
            
            
            
            Vector= (lockkeys[0][k2] - lockkeys[0][k1],lockkeys[1][k2] - lockkeys[1][k1],lockkeys[2][k2]-lockkeys[2][k1])
            DirectionVector = mathutils.Vector(Vector)
             
            #apply rotation
            
            if ob.rotation_mode == 'QUATERNION':
                bpy.context.object.rotation_quaternion = DirectionVector.to_track_quat(forward,up)
                bpy.context.object.keyframe_insert(data_path='rotation_quaternion', frame=lockkeys[3][i] )
            else:
                if last:
                    bpy.context.object.rotation_euler = DirectionVector.to_track_quat(forward,up).to_euler(ob.rotation_mode, last)
                else:
                    bpy.context.object.rotation_euler = DirectionVector.to_track_quat(forward,up).to_euler(ob.rotation_mode)
                    
                last=bpy.context.object.rotation_euler
                bpy.context.object.keyframe_insert(data_path='rotation_euler', frame=lockkeys[3][i] )
        
                


class OrientToMotion(bpy.types.Operator):
    """Orient object to it's motion path"""
    bl_idname = "object.orient_to_motion"
    bl_label = "Orient to Motion"
    bl_options = {'REGISTER', 'UNDO'}
    
    forward: bpy.props.EnumProperty(
            name = "Forward axis",
            default = "Z",
            items = [
                ("X", "+X", "X axis forward"),
                ("Y", "+Y", "Y axis forward"),
                ("Z", "+Z", "Z axis forward"),
                
                ("-X", "-X", "X axis backward"),
                ("-Y", "-Y", "Y axis backward"),
                ("-Z", "-Z", "Z axis backward"),             
            ]
        )
    up: bpy.props.EnumProperty(
            name = "Up axis",
            default = "Y",
            items = [
                ("X", "X", "X axis"),
                ("Y", "Y", "Y axis"),
                ("Z", "Z", "Z axis"),
                 
            ]
        )
    keys: bpy.props.EnumProperty(
            name = "Up axis",
            items = [
                ("keys", "Keyframes only",  "Keyframes"),
                ("all", "All frames",  "All frames"),
                 
            ]
        )        

        
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context, self.forward, self.up, self.keys)
        return {'FINISHED'}
    
def menu_func(self, context):
    self.layout.separator()
    self.layout.operator("object.orient_to_motion")
    

def register():
    bpy.utils.register_class(OrientToMotion)
    bpy.types.VIEW3D_MT_object_animation.append(menu_func)


def unregister():
    bpy.utils.unregister_class(OrientToMotion)
    bpy.types.VIEW3D_MT_object_animation.remove(menu_func)


if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.object.orient_to_motion()
