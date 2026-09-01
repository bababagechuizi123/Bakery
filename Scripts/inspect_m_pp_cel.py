import unreal


ASSET_PATH = "/Game/PostProcess/M_PP_Cel"
material = unreal.load_asset(ASSET_PATH)
if not material:
    raise RuntimeError(f"Could not load {ASSET_PATH}")

print("CODEX_MATERIAL", material.get_path_name())
for prop in (
    "material_domain",
    "blend_mode",
    "shading_model",
    "blendable_location",
    "blendable_priority",
    "blendable_output_alpha",
    "enable_stencil_test",
    "stencil_compare",
    "stencil_ref_value",
):
    try:
        print("CODEX_PROPERTY", prop, repr(material.get_editor_property(prop)))
    except Exception:
        pass

try:
    expressions = material.get_editor_property("editor_only_data").get_editor_property("expression_collection").get_editor_property("expressions")
except Exception:
    print("CODEX_MEL_METHODS", [name for name in dir(unreal.MaterialEditingLibrary) if "expression" in name.lower() or "input" in name.lower()])
    try:
        expressions = material.get_editor_property("expressions")
    except Exception as exc:
        print("CODEX_EXPRESSIONS_ERROR", repr(exc))
        expressions = []

print("CODEX_EXPRESSION_COUNT", len(expressions))
interesting = (
    "parameter_name", "default_value", "constant", "r", "g", "b", "a",
    "scene_texture_id", "function", "material_function", "desc",
    "const_a", "const_b", "clamp_mode", "min_default", "max_default",
)

for index, expression in enumerate(expressions):
    cls = expression.get_class().get_name()
    print("CODEX_NODE", index, cls, expression.get_name())
    for prop in interesting:
        try:
            value = expression.get_editor_property(prop)
            if value not in (None, "", 0, 0.0, False):
                print("  CODEX_NODE_PROPERTY", prop, repr(value))
        except Exception:
            pass

    # MaterialExpression inputs are exposed as properties in Python. Printing their
    # connected expression names reconstructs the graph without changing it.
    for name in dir(expression):
        if name.startswith("_") or name in interesting:
            continue
        try:
            value = expression.get_editor_property(name)
        except Exception:
            continue
        if isinstance(value, unreal.ExpressionInput):
            source = value.get_editor_property("expression")
            if source:
                print("  CODEX_INPUT", name, "<-", source.get_name(), "output", value.get_editor_property("output_index"))

for prop in (
    unreal.MaterialProperty.MP_EMISSIVE_COLOR,
    unreal.MaterialProperty.MP_OPACITY,
):
    try:
        node = unreal.MaterialEditingLibrary.get_material_property_input_node(material, prop)
        print("CODEX_OUTPUT", str(prop), node.get_name() if node else None)
    except Exception as exc:
        print("CODEX_OUTPUT_ERROR", str(prop), repr(exc))


visited = set()
def walk(node, depth=0):
    if not node or node.get_path_name() in visited:
        return
    visited.add(node.get_path_name())
    cls = node.get_class().get_name()
    print("CODEX_WALK", depth, cls, node.get_name())
    for prop in interesting:
        try:
            value = node.get_editor_property(prop)
            if value not in (None, "", 0, 0.0, False):
                print("  CODEX_WALK_PROPERTY", prop, repr(value))
        except Exception:
            pass
    try:
        names = unreal.MaterialEditingLibrary.get_material_expression_input_names(node)
        inputs = unreal.MaterialEditingLibrary.get_inputs_for_material_expression(material, node)
        for i, source in enumerate(inputs):
            label = names[i] if i < len(names) else f"Input{i}"
            print("  CODEX_WALK_INPUT", label, "<-", source.get_name() if source else None)
            walk(source, depth + 1)
    except Exception as exc:
        print("  CODEX_WALK_ERROR", repr(exc))

root = unreal.MaterialEditingLibrary.get_material_property_input_node(material, unreal.MaterialProperty.MP_EMISSIVE_COLOR)
walk(root)
