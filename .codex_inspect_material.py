import unreal

print("MEL_METHODS", [name for name in dir(unreal.MaterialEditingLibrary) if "expression" in name.lower() or "input" in name.lower()])
asset = unreal.EditorAssetLibrary.load_asset('/Game/PostProcess/PPM_CrossLine_d_b')
print("ASSET", asset)
print("ASSET_CLASS", asset.get_class().get_name() if asset else None)
if asset:
    for prop in ('expressions', 'editor_only_data'):
        try:
            value = asset.get_editor_property(prop)
            print("PROP", prop, value)
        except Exception as exc:
            print("PROP_ERR", prop, repr(exc))
unreal.SystemLibrary.quit_editor()
