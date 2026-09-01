import unreal


ROOT = "/Game/PostProcess"
MASTER_NAME = "M_InteractionOutline"
INSTANCE_NAME = "MI_InteractionOutline"


def scalar(material, name, default, x, y):
    node = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionScalarParameter, x, y
    )
    node.set_editor_property("parameter_name", name)
    node.set_editor_property("default_value", default)
    return node


def vector(material, name, value, x, y):
    node = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionVectorParameter, x, y
    )
    node.set_editor_property("parameter_name", name)
    node.set_editor_property("default_value", value)
    return node


def expression(material, cls, x, y):
    return unreal.MaterialEditingLibrary.create_material_expression(material, cls, x, y)


def connect(source, output_name, target, input_name):
    unreal.MaterialEditingLibrary.connect_material_expressions(
        source, output_name, target, input_name
    )


unreal.EditorAssetLibrary.make_directory(ROOT)

for path in (f"{ROOT}/{INSTANCE_NAME}", f"{ROOT}/{MASTER_NAME}"):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)

factory = unreal.MaterialFactoryNew()
master = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
    MASTER_NAME, ROOT, unreal.Material, factory
)
if not master:
    raise RuntimeError("Failed to create interaction outline master material")

master.set_editor_property("material_domain", unreal.MaterialDomain.MD_POST_PROCESS)

# Parameters exposed by the material instance.
thickness = scalar(master, "OutlineThickness", 3.0, -1800, -650)
outline_color = vector(
    master, "OutlineColor", unreal.LinearColor(1.0, 0.72, 0.0, 1.0), 450, -250
)
intensity = scalar(master, "OutlineIntensity", 4.0, 450, -80)

# Screen UV and pixel size.
uv = expression(master, unreal.MaterialExpressionTextureCoordinate, -1800, -350)
stencil_center = expression(master, unreal.MaterialExpressionSceneTexture, -1250, 420)
stencil_center.set_editor_property("scene_texture_id", unreal.SceneTextureId.PPI_CUSTOM_STENCIL)
connect(uv, "", stencil_center, "UVs")

# Custom stencil is normalized; multiplying by 255 and saturating produces a mask.
center_scale = expression(master, unreal.MaterialExpressionMultiply, -1000, 420)
center_scale.set_editor_property("const_b", 255.0)
connect(stencil_center, "Color", center_scale, "A")
center_mask = expression(master, unreal.MaterialExpressionSaturate, -800, 420)
connect(center_scale, "", center_mask, "")
one_minus_center = expression(master, unreal.MaterialExpressionOneMinus, -600, 420)
connect(center_mask, "", one_minus_center, "Input")

# Build an 8-neighbour dilation of the stencil mask.
directions = [
    (-1.0, 0.0), (1.0, 0.0), (0.0, -1.0), (0.0, 1.0),
    (-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0),
]
neighbour_masks = []
for index, (dx, dy) in enumerate(directions):
    y = -650 + index * 150
    direction = expression(master, unreal.MaterialExpressionConstant2Vector, -1600, y)
    direction.set_editor_property("r", dx)
    direction.set_editor_property("g", dy)

    pixel_offset = expression(master, unreal.MaterialExpressionMultiply, -1400, y)
    connect(direction, "", pixel_offset, "A")
    connect(thickness, "", pixel_offset, "B")

    inv_size_offset = expression(master, unreal.MaterialExpressionMultiply, -1200, y)
    connect(pixel_offset, "", inv_size_offset, "A")
    connect(stencil_center, "InvSize", inv_size_offset, "B")

    offset_uv = expression(master, unreal.MaterialExpressionAdd, -1000, y)
    connect(uv, "", offset_uv, "A")
    connect(inv_size_offset, "", offset_uv, "B")

    sample = expression(master, unreal.MaterialExpressionSceneTexture, -800, y)
    sample.set_editor_property("scene_texture_id", unreal.SceneTextureId.PPI_CUSTOM_STENCIL)
    connect(offset_uv, "", sample, "UVs")

    scaled = expression(master, unreal.MaterialExpressionMultiply, -600, y)
    scaled.set_editor_property("const_b", 255.0)
    connect(sample, "Color", scaled, "A")
    mask = expression(master, unreal.MaterialExpressionSaturate, -420, y)
    connect(scaled, "", mask, "")
    neighbour_masks.append(mask)

dilated = neighbour_masks[0]
for index, mask in enumerate(neighbour_masks[1:]):
    maximum = expression(master, unreal.MaterialExpressionMax, -180 + index * 120, 180)
    connect(dilated, "", maximum, "A")
    connect(mask, "", maximum, "B")
    dilated = maximum

# Outer ring only: dilated stencil multiplied by the inverse of the original stencil.
outer_ring = expression(master, unreal.MaterialExpressionMultiply, 720, 180)
connect(dilated, "", outer_ring, "A")
connect(one_minus_center, "", outer_ring, "B")

bright_color = expression(master, unreal.MaterialExpressionMultiply, 720, -160)
connect(outline_color, "", bright_color, "A")
connect(intensity, "", bright_color, "B")

scene = expression(master, unreal.MaterialExpressionSceneTexture, 450, -520)
scene.set_editor_property("scene_texture_id", unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)

blend = expression(master, unreal.MaterialExpressionLinearInterpolate, 980, -300)
connect(scene, "Color", blend, "A")
connect(bright_color, "", blend, "B")
connect(outer_ring, "", blend, "Alpha")
unreal.MaterialEditingLibrary.connect_material_property(
    blend, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR
)

unreal.MaterialEditingLibrary.layout_material_expressions(master)
unreal.MaterialEditingLibrary.recompile_material(master)
unreal.EditorAssetLibrary.save_loaded_asset(master)

instance_factory = unreal.MaterialInstanceConstantFactoryNew()
instance = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
    INSTANCE_NAME, ROOT, unreal.MaterialInstanceConstant, instance_factory
)
if not instance:
    raise RuntimeError("Failed to create interaction outline material instance")

unreal.MaterialEditingLibrary.set_material_instance_parent(instance, master)

unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
    instance, "OutlineThickness", 3.0
)
unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
    instance, "OutlineIntensity", 4.0
)
unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
    instance, "OutlineColor", unreal.LinearColor(1.0, 0.72, 0.0, 1.0)
)
unreal.EditorAssetLibrary.save_loaded_asset(instance)

unreal.log(f"CODEX_CREATED {ROOT}/{MASTER_NAME}")
unreal.log(f"CODEX_CREATED {ROOT}/{INSTANCE_NAME}")
