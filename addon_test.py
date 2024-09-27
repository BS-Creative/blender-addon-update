bl_info = {
    "name": "Add Cube and Sphere at 3D Cursor with Update Feature",
    "blender": (2, 80, 0),  # Minimum Blender version supported
    "version": (1, 1, 1),   # Current version is 1.1.0
    "category": "Object",
    "description": "Addon to add a cube or sphere at the 3D cursor with update feature",
}

import bpy
import os
import requests

# Use the correct raw links directly
VERSION_FILE_URL = "https://raw.githubusercontent.com/BS-Creative/blender-addon-update/refs/heads/main/version.txt?token=GHSAT0AAAAAACYDQAAQ2IINVS4HJPY2SDDQZXWHUTQ"
ADDON_FILE_URL = "https://raw.githubusercontent.com/BS-Creative/blender-addon-update/refs/heads/main/addon_test.py?token=GHSAT0AAAAAACYDQAARK6BW5NZE6Z574ARSZXWHUSA"

class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    check_interval: bpy.props.EnumProperty(
        name="Check for Updates",
        description="How often to check for updates",
        items=[
            ('5_SECONDS', "Every 5 Seconds", ""),
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

class OBJECT_OT_add_sphere_at_cursor(bpy.types.Operator):
    bl_idname = "mesh.add_sphere_at_cursor"
    bl_label = "Add Sphere at 3D Cursor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cursor_location = context.scene.cursor.location
        bpy.ops.mesh.primitive_uv_sphere_add(location=cursor_location)
        return {'FINISHED'}

class PREF_OT_check_for_update(bpy.types.Operator):
    bl_idname = "preferences.check_for_update"
    bl_label = "Check for Addon Update"

    def execute(self, context):
        try:
            # Fetch the version from the online version.txt
            response = requests.get(VERSION_FILE_URL)
            online_version = tuple(map(int, response.text.strip().split(".")))
            current_version = bl_info['version']

            if online_version > current_version:
                self.report({'INFO'}, f"New version available: {online_version}. Updating...")
                # Download and replace the addon with the new version
                download_new_version()
            else:
                self.report({'INFO'}, "Addon is up to date.")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to check for update: {e}")

        return {'FINISHED'}

def download_new_version():
    try:
        # Get the path to the current addon file
        addon_file_path = os.path.join(bpy.utils.user_resource('SCRIPTS'), "addons", "addon_test.py")
        
        # Download the updated addon file
        response = requests.get(ADDON_FILE_URL)
        with open(addon_file_path, 'wb') as file:
            file.write(response.content)

        # Reload the addon to apply the update
        bpy.ops.preferences.addon_disable(module="addon_test")
        bpy.ops.preferences.addon_enable(module="addon_test")

        print("Addon updated successfully!")
    except Exception as e:
        print(f"Error updating addon: {e}")

def menu_func(self, context):
    self.layout.operator(OBJECT_OT_add_cube_at_cursor.bl_idname, text="Add Cube at Cursor")
    self.layout.operator(OBJECT_OT_add_sphere_at_cursor.bl_idname, text="Add Sphere at Cursor")

# Function to check updates periodically based on user preference
def check_for_updates_periodically():
    prefs = bpy.context.preferences.addons[__name__].preferences
    check_interval = prefs.check_interval

    # Convert the interval to seconds (5 seconds, daily, weekly, or monthly)
    interval_seconds = {
        '5_SECONDS': 5,
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
    bpy.utils.register_class(OBJECT_OT_add_sphere_at_cursor)
    bpy.utils.register_class(PREF_OT_check_for_update)
    bpy.utils.register_class(AddonPreferences)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

    # Register timer for periodic update checking
    bpy.app.timers.register(check_for_updates_periodically, first_interval=1)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_cube_at_cursor)
    bpy.utils.unregister_class(OBJECT_OT_add_sphere_at_cursor)
    bpy.utils.unregister_class(PREF_OT_check_for_update)
    bpy.utils.unregister_class(AddonPreferences)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)

    # Unregister timer
    bpy.app.timers.unregister(check_for_updates_periodically)

if __name__ == "__main__":
    register()
