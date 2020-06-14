# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from . import server
import pprint
import numpy as np
import mathutils as mu
from . import qt

ppp = pprint.PrettyPrinter(indent=4)


bl_info = {
    "name": "VR Hands",
    "author": "ambi",
    "description": "Need a hand?",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "3D View > Sidebar > VR",
    "warning": "",
    "category": "3D View",
}


class PG_VRHands(bpy.types.PropertyGroup):
    active: bpy.props.BoolProperty(name="Running", default=False)
    armature: bpy.props.PointerProperty(name="Armature", type=bpy.types.Object)


def dm(m, d):
    return d[m] if m in d else ""


def ncoords(a):
    return mu.Vector([-a[0], -a[2], -a[1]]) / 1000.0


def server_debug():
    ppp.pprint(server.data)
    return 0.5


# ARM_NAME = "Root"
finger_names = ["thumb", "index", "middle", "ring", "pinky"]


def lookat(dr, fw):
    dr = dr.normalized()
    rotAxis = fw.cross(dr).normalized()
    if rotAxis.length == 0.0:
        rotAxis = mu.Vector([0.0, 1.0, 0.0])
    return mu.Quaternion(rotAxis, fw.angle(dr))


def data_transfer():
    # obj = bpy.data.objects[bpy.context.scene.vr_hands.armature]
    obj = bpy.context.scene.vr_hands.armature
    bones = obj.pose.bones
    data = server.data

    if "right" in data:
        dr = data["right"]
        bones["wrist_r"].location = ncoords(dr["palm_position"])

        d_pyr = dr["direction_pyr"]
        n_pyr = dr["palm_normal_pyr"]
        qroll = mu.Quaternion(mu.Vector([0.0, -1.0, 0.0]), n_pyr[2])
        qpitch = mu.Quaternion(mu.Vector([-1.0, 0.0, 0.0]), d_pyr[0])
        qyaw = mu.Quaternion(mu.Vector([0.0, 0.0, 1.0]), d_pyr[1])
        bones["wrist_r"].rotation_quaternion = qroll @ qpitch @ qyaw

        # for f in range(5):
        #     for j in range(1, 4):
        #         jt = "finger_{}_{}".format(f, j)
        #         jtp = jt + "_prev_joint"
        #         jtn = jt + "_next_joint"
        #         bb = bones["finger_{}_{}_r".format(finger_names[f], j - 1)]
        #         vdif = ncoords(dr[jtn]) - ncoords(dr[jtp])
        #         bb.location = vdif
        #         bb.rotation_quaternion = lookat(vdif, mu.Vector([0.0, 1.0, 0.0]))
        # bb.rotation_quaternion = mu.Quaternion((1.0, 0.0, 0.0, 0.0))
        # rqt = bb.rotation_quaternion.inverted()

    # 100 fps
    return 0.01


class OBJECT_OT_StartVRHServer(bpy.types.Operator):
    bl_idname = "object.vr_hands_start"
    bl_label = "Start VRH server"

    def execute(self, context):
        print("Starting VR hands...")
        bpy.context.scene.vr_hands.active = True
        server.start()
        # bpy.app.timers.register(server_debug)
        bpy.app.timers.register(data_transfer)
        return {"FINISHED"}


class OBJECT_OT_StopVRHServer(bpy.types.Operator):
    bl_idname = "object.vr_hands_stop"
    bl_label = "Start VRH server"

    def execute(self, context):
        print("Stopping VR hands...")
        context.scene.vr_hands.active = False
        server.stop()
        # bpy.app.timers.unregister(server_debug)
        bpy.app.timers.unregister(data_transfer)
        return {"FINISHED"}


class OBJECT_PT_VRH_main(bpy.types.Panel):
    bl_label = "VR Hands"
    bl_idname = "OBJECT_PT_VRH_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "VR"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        row = col.row()
        row.label(text="Armature Root:")
        row.prop(context.scene.vr_hands, "armature", text="")
        row = col.row()
        b = row.box()
        if not bpy.context.scene.vr_hands.active:
            row = b.row()
            row.operator(OBJECT_OT_StartVRHServer.bl_idname, text="Start Server")
        else:
            b.alert = True
            row = b.row()
            row.operator(OBJECT_OT_StopVRHServer.bl_idname, text="Stop Server")


cls = (OBJECT_PT_VRH_main, PG_VRHands, OBJECT_OT_StartVRHServer, OBJECT_OT_StopVRHServer)


def register():
    for c in cls:
        bpy.utils.register_class(c)
    bpy.types.Scene.vr_hands = bpy.props.PointerProperty(type=PG_VRHands)


def unregister():
    del bpy.types.Scene.vr_hands
    for c in cls:
        bpy.utils.unregister_class(c)