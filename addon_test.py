bl_info = {
    "name": "Add Cube at 3D Cursor with Update Feature",
    "blender": (2, 80, 0),
    "version": (1, 0, 0),  # Update this when you release a new version
    "category": "Object",
    "description": "Addon to add a cube at the 3D cursor with update feature",
}

import bpy
import requests
import ast

# Use the provided raw link for the .py file
ADDON_FILE_URL = "https://raw.githubusercontent.com/BS-Creative/blender-addon-update/refs/heads/main/addon_test.py?token=GHSAT0AAAAAACYDQAAQZZZTNF6JKEDM7ZXUZXWG5OA"

class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    check_interval: bpy.props.EnumProperty(
        name="Check for Updates",
        description="How often to check for updates",
        items=[
            ('DAILY', "Daily", ""),
            ('WEEKLY', "Weekly", ""),
            ('MONTHLY', "Monthly", ""),
        ],
        default='WEEKLY'
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Update Preferences")
        layout.prop(self, "check_interval")
        layout.operator("preferences.check_for_update", text="Check for Updates")

class OBJECT_OT_add_cube_at_cursor(bpy.types.Operator):
    bl_idname = "mesh.add_cube_at_cursor"
    bl_label = "Add Cube at 3D Cursor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cursor_location = context.scene.cursor.location
        bpy.ops.mesh.primitive_cube_add(location=cursor_location)
        return {'FINISHED'}

class PREF_OT_check_for_update(bpy.types.Operator):
    bl_idname = "preferences.check_for_update"
    bl_label = "Check for Addon Update"

    def execute(self, context):
        try:
            # Fetch the online addon_test.py content
            response = requests.get(ADDON_FILE_URL)
            online_code = response.text

            # Parse the online code and extract bl_info
            online_bl_info = ast.literal_eval(
                online_code.split("bl_info =")[1].split("\n\n")[0].strip()
            )

            online_version = tuple(online_bl_info["version"])
            current_version = bl_info["version"]

            # Compare versions
            if online_version > current_version:
                self.report({'INFO'}, f"New version available: {online_version}. Please update manually.")
            else:
                self.report({'INFO'}, "Addon is up to date.")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to check for update: {e}")

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(OBJECT_OT_add_cube_at_cursor.bl_idname)

# Function to check updates periodically based on user preference
def check_for_updates_periodically():
    prefs = bpy.context.preferences.addons[__name__].preferences
    check_interval = prefs.check_interval

    # Convert the interval to seconds (daily, weekly, or monthly)
    interval_seconds = {
        'DAILY': 86400,
        'WEEKLY': 604800,
        'MONTHLY': 2592000
    }[check_interval]

    # Check for updates
    bpy.ops.preferences.check_for_update()

    # Schedule next check
    return interval_seconds

def register():
    bpy.utils.register_class(OBJECT_OT_add_cube_at_cursor)
    bpy.utils.register_class(PREF_OT_check_for_update)
    bpy.utils.register_class(AddonPreferences)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

    # Register timer for periodic update checking
    bpy.app.timers.register(check_for_updates_periodically, first_interval=1)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_cube_at_cursor)
    bpy.utils.unregister_class(PREF_OT_check_for_update)
    bpy.utils.unregister_class(AddonPreferences)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)

    # Unregister timer
    bpy.app.timers.unregister(check_for_updates_periodically)

if __name__ == "__main__":
    register()
