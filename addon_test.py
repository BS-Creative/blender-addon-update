bl_info = {
    "name": "Add Cube, Sphere, and Ico Sphere with Update Feature",
    "blender": (2, 80, 0),  # Minimum Blender version supported
    "version": (1, 4, 0),   # Updated version to 1.2
    "category": "Object",
    "description": "Addon to add a cube, sphere, and ico sphere at the 3D cursor with update feature",
}

import bpy
import os
import requests

# Use the correct raw links directly
VERSION_FILE_URL = "https://raw.githubusercontent.com/BS-Creative/blender-addon-update/refs/heads/main/version.txt?token=GHSAT0AAAAAACYDQAAQ2IINVS4HJPY2SDDQZXWHUTQ"
ADDON_FILE_URL = "https://raw.githubusercontent.com/BS-Creative/blender-addon-update/refs/heads/main/addon_test.py?token=GHSAT0AAAAAACYDQAARK6BW5NZE6Z574ARSZXWHUSA"

# Global variable to track if an update is available
update_available = False

class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    auto_update: bpy.props.BoolProperty(
        name="Auto Update",
        description="Automatically update the addon when a new version is available",
        default=False
    )

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
        global update_available
        layout = self.layout
        layout.label(text="Update Preferences")
        layout.prop(self, "auto_update")
        layout.prop(self, "check_interval")

        # Only show the "Update to Latest Version" button if an update is available
        if not self.auto_update and update_available:
            layout.operator("preferences.update_to_latest_version", text="Update to Latest Version", icon='FILE_REFRESH')
        
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

class OBJECT_OT_add_ico_sphere_at_cursor(bpy.types.Operator):
    bl_idname = "mesh.add_ico_sphere_at_cursor"
    bl_label = "Add Ico Sphere at 3D Cursor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cursor_location = context.scene.cursor.location
        bpy.ops.mesh.primitive_ico_sphere_add(location=cursor_location)
        return {'FINISHED'}

class PREF_OT_check_for_update(bpy.types.Operator):
    bl_idname = "preferences.check_for_update"
    bl_label = "Check for Addon Update"

    def execute(self, context):
        global update_available
        try:
            # Fetch the version from the online version.txt
            response = requests.get(VERSION_FILE_URL)
            online_version = tuple(map(int, response.text.strip().split(".")))
            current_version = bl_info['version']

            if online_version > current_version:
                prefs = context.preferences.addons[__name__].preferences
                update_available = True  # Mark update as available
                if prefs.auto_update:
                    self.report({'INFO'}, f"New version available: {online_version}. Updating...")
                    download_new_version()
                else:
                    self.report({'INFO'}, f"New version available: {online_version}. Please update manually.")
            else:
                update_available = False  # No update needed
                self.report({'INFO'}, "Addon is up to date.")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to check for update: {e}")

        # Force the preferences panel to update
        context.preferences.addons[__name__].preferences.update_tag()

        return {'FINISHED'}

class PREF_OT_update_to_latest_version(bpy.types.Operator):
    bl_idname = "preferences.update_to_latest_version"
    bl_label = "Update to Latest Version"

    def execute(self, context):
        try:
            self.report({'INFO'}, "Updating to the latest version...")
            download_new_version()
        except Exception as e:
            self.report({'ERROR'}, f"Failed to update: {e}")

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
    self.layout.operator(OBJECT_OT_add_ico_sphere_at_cursor.bl_idname, text="Add Ico Sphere at Cursor")

# Function to check updates periodically based on user preference
def check_for_updates_periodically():
    bpy.ops.preferences.check_for_update()

    # Schedule the next check based on user preferences
    prefs = bpy.context.preferences.addons[__name__].preferences
    check_interval = prefs.check_interval

    # Convert the interval to seconds (5 seconds, daily, weekly, or monthly)
    interval_seconds = {
        '5_SECONDS': 5,
        'DAILY': 86400,
        'WEEKLY': 604800,
        'MONTHLY': 2592000
    }[check_interval]

    return interval_seconds

def register():
    bpy.utils.register_class(OBJECT_OT_add_cube_at_cursor)
    bpy.utils.register_class(OBJECT_OT_add_sphere_at_cursor)
    bpy.utils.register_class(OBJECT_OT_add_ico_sphere_at_cursor)
    bpy.utils.register_class(PREF_OT_check_for_update)
    bpy.utils.register_class(PREF_OT_update_to_latest_version)
    bpy.utils.register_class(AddonPreferences)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

    # Register timer for periodic update checking
    bpy.app.timers.register(check_for_updates_periodically, first_interval=1)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_cube_at_cursor)
    bpy.utils.unregister_class(OBJECT_OT_add_sphere_at_cursor)
    bpy.utils.unregister_class(OBJECT_OT_add_ico_sphere_at_cursor)
    bpy.utils.unregister_class(PREF_OT_check_for_update)
    bpy.utils.unregister_class(PREF_OT_update_to_latest_version)
    bpy.utils.unregister_class(AddonPreferences)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)

    # Unregister timer
    bpy.app.timers.unregister(check_for_updates_periodically)

if __name__ == "__main__":
    register()
