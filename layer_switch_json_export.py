import c4d
import json

def get_visibility_keys_for_rendering(obj):
    vis_keys = []
    doc = obj.GetDocument()
    orig_time = doc.GetTime()  # Original time to revert back later

    track = obj.FindCTrack(c4d.DescID(c4d.ID_BASEOBJECT_VISIBILITY_RENDER))
        
    if track:
        curve = track.GetCurve()
        for i in range(curve.GetKeyCount()):
            key = curve.GetKey(i)
            frame = key.GetTime().GetFrame(doc.GetFps())

            # Set the document's time to this keyframe
            doc.SetTime(c4d.BaseTime(frame, doc.GetFps()))
            c4d.EventAdd(c4d.EVENT_ANIMATE)  # Update animation
            doc.ExecutePasses(None, True, True, True, c4d.BUILDFLAGS_NONE)

            # Check object's visibility state at this frame
            is_visible = obj.GetRenderMode() != c4d.OBJECT_OFF

            vis_keys.append({"frame": frame, "visibility": is_visible})

    # Revert the document's time to the original
    doc.SetTime(orig_time)
    c4d.EventAdd(c4d.EVENT_ANIMATE)
    doc.ExecutePasses(None, True, True, True, c4d.BUILDFLAGS_NONE)

    return vis_keys

if __name__ == "__main__":
    doc = c4d.documents.GetActiveDocument()
    if not doc:
        print("No active document found.")
    else:
        output_data = {}
        selected_objects = doc.GetActiveObjects(0)
        
        for obj in selected_objects:
            keys = get_visibility_keys_for_rendering(obj)
            if keys:
                output_data[obj.GetName()] = keys

        # Get the save path from the user with default filename "layer_switch.json"
        save_path = c4d.storage.SaveDialog(title="Save as JSON", def_path="layer_switch.json", force_suffix="json")
        if save_path:
            with open(save_path, 'w') as file:
                json.dump(output_data, file, indent=4)