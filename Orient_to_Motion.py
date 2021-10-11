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

bl_info = {
    "name": "Orient to Motion",
    "author": "Michael Soluyanov (Multlabs.com), stib (https://github.com/stibinator) ",
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
        lockkeys = []
        last=False
        print("OTM")
        
        
        if keys=="keys":
            for fc in ob.animation_data.action.fcurves:
                for kf in fc.keyframe_points:
                    if fc.data_path == 'location':
                    #   add rotation KFs on the left and right handles as well as the control points
                    #   this makes for better interpolation around tight corners
                        lockkeys.append(kf.handle_left[0])
                        lockkeys.append(kf.co[0])
                        lockkeys.append(kf.handle_right[0])
        else:
            fc = ob.animation_data.action.fcurves
            kmin = int(fc.find("location", index = 0).keyframe_points[0].co[0])
            kmax = int(fc.find("location", index = 0).keyframe_points[-1].co[0])
            for i in range(1, 3):
                for kf in fc.keyframe_points: 
                    kmin = min(kmin, int(fc.find("location", index = i).keyframe_points[kf].co[0]))
                    kmax = max(kmax, int(fc.find("location", index = i).keyframe_points[kf].co[0]))

            for frame in range(int(kmin), int(kmax)):
                lockkeys.append(frame)

        for i in range(0, len(lockkeys)):
            locations = [ob.animation_data.action.fcurves.find("location", index= 0), ob.animation_data.action.fcurves.find("location", index= 1), ob.animation_data.action.fcurves.find("location", index= 2)]
            
            prevTime = lockkeys[i] - 0.5
            nextTime = lockkeys[i] + 0.5
            prevPos = [locations[0].evaluate(prevTime), locations[1].evaluate(prevTime), locations[2].evaluate(prevTime)]
            nextPos = [locations[0].evaluate(nextTime), locations[1].evaluate(nextTime), locations[2].evaluate(nextTime)]
            rotvector= (nextPos[0] - prevPos[0], nextPos[1] - prevPos[1], nextPos[2] - prevPos[2])
            DirectionVector = mathutils.Vector(rotvector)
             
            #apply rotation
            
            if ob.rotation_mode == 'QUATERNION':
                if rotvector==(0,0,0) and last:
                    bpy.context.object.rotation_quaternion = last
                else:
                    bpy.context.object.rotation_quaternion = DirectionVector.to_track_quat(forward,up)
                bpy.context.object.keyframe_insert(data_path='rotation_quaternion', frame=lockkeys[i] )
                last=bpy.context.object.rotation_quaternion
            else:
                if rotvector==(0,0,0) and last:
                    bpy.context.object.rotation_euler = last
                else:
                    if last:
                        bpy.context.object.rotation_euler = DirectionVector.to_track_quat(forward,up).to_euler(ob.rotation_mode, last)
                    else:
                        print("false")
                        bpy.context.object.rotation_euler = DirectionVector.to_track_quat(forward,up).to_euler(ob.rotation_mode)
                    
                last=bpy.context.object.rotation_euler
                bpy.context.object.keyframe_insert(data_path='rotation_euler', frame=lockkeys[i] )
                     


class OrientToMotion(bpy.types.Operator):
    """Orient object to its motion path"""
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
