import unreal


folder = "/Game/tinytreat"
material_path = f"{folder}/TinyTreat_texture"
excluded_names = {"wall_sign_large", "wall_sign_small"}

material = unreal.load_asset(material_path)
if not isinstance(material, unreal.MaterialInterface):
    raise RuntimeError(f"Material not found: {material_path}")

changed_assets = []
changed_slots = 0

for asset_path in unreal.EditorAssetLibrary.list_assets(folder, recursive=True):
    asset = unreal.load_asset(asset_path)
    if not isinstance(asset, unreal.StaticMesh):
        continue
    if asset.get_name() in excluded_names:
        unreal.log_warning(f"CODEX_TINYTREAT_SKIPPED {asset.get_path_name()}")
        continue

    slot_count = len(asset.get_editor_property("static_materials"))
    asset_changed = False
    for slot_index in range(slot_count):
        if asset.get_material(slot_index) != material:
            asset.set_material(slot_index, material)
            asset_changed = True
            changed_slots += 1

    if asset_changed:
        asset.modify()
        if not unreal.EditorAssetLibrary.save_asset(asset_path, only_if_is_dirty=False):
            raise RuntimeError(f"Failed to save: {asset_path}")
        changed_assets.append(asset.get_path_name())

unreal.log_warning(
    "CODEX_TINYTREAT_DONE "
    f"assets={len(changed_assets)} slots={changed_slots} "
    f"excluded={sorted(excluded_names)}"
)
