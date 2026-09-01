import unreal


LEVEL_PATH = "/Game/Maps/TinyTreat_Bakery_Showcase"
ASSET_ROOT = "/Game/tinytreat"

unreal.EditorAssetLibrary.make_directory("/Game/Maps")
if unreal.EditorAssetLibrary.does_asset_exist(LEVEL_PATH):
    if not unreal.EditorLevelLibrary.load_level(LEVEL_PATH):
        raise RuntimeError(f"Could not load level: {LEVEL_PATH}")
else:
    if not unreal.EditorLevelLibrary.new_level(LEVEL_PATH):
        raise RuntimeError(f"Could not create level: {LEVEL_PATH}")

spawned = []


def mesh_asset(name):
    asset = unreal.load_asset(f"{ASSET_ROOT}/{name}")
    if not isinstance(asset, unreal.StaticMesh):
        unreal.log_warning(f"CODEX_BAKERY_MISSING {name}")
        return None
    return asset


def spawn(name, xyz, yaw=0.0, scale=1.0, label=None):
    mesh = mesh_asset(name)
    if mesh is None:
        return None
    actor = unreal.EditorLevelLibrary.spawn_actor_from_object(
        mesh, unreal.Vector(*xyz), unreal.Rotator(0.0, yaw, 0.0)
    )
    if isinstance(scale, tuple):
        actor.set_actor_scale3d(unreal.Vector(*scale))
    else:
        actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    actor.set_actor_label(label or name)
    actor.tags = ["TinyTreatBakery"]
    spawned.append(actor)
    return actor


def light(light_class, xyz, intensity, color, label, rotation=None):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        light_class, unreal.Vector(*xyz), rotation or unreal.Rotator()
    )
    actor.set_actor_label(label)
    component = actor.get_component_by_class(unreal.LightComponent)
    component.set_editor_property("intensity", intensity)
    component.set_editor_property("light_color", unreal.Color(*color, 255))
    spawned.append(actor)
    return actor


# 12 m x 10 m shop floor.
for x in (-400.0, 0.0, 400.0):
    for y in (-300.0, 100.0, 500.0):
        spawn("floor_wood", (x, y, 0.0), label=f"Floor_{int(x)}_{int(y)}")

# Back and side walls; the front remains open so the whole bakery is easy to inspect.
for x in (-400.0, 0.0, 400.0):
    spawn("wall_panelled_bakery_straight", (x, 700.0, 0.0), label="BackWall")
for y in (-300.0, 100.0, 500.0):
    spawn("wall_panelled_bakery_straight", (-600.0, y, 0.0), 90.0, label="LeftWall")
    spawn("wall_panelled_bakery_straight", (600.0, y, 0.0), 90.0, label="RightWall")
spawn("wall_panelled_bakery_corner_inner", (-600.0, 700.0, 0.0), label="BackLeftCorner")
spawn("wall_panelled_bakery_corner_inner", (600.0, 700.0, 0.0), 90.0, label="BackRightCorner")

# Customer-facing display and checkout line.
spawn("display_case_long", (-230.0, 185.0, 0.0), 0.0, label="MainPastryDisplay")
spawn("display_case_short", (165.0, 185.0, 0.0), 0.0, label="CakeDisplay")
spawn("counter_table", (420.0, 205.0, 0.0), 0.0, label="CheckoutCounter")
spawn("cash_register", (420.0, 205.0, 92.0), 180.0, label="CashRegister")
spawn("pricing_card", (-330.0, 185.0, 105.0), label="DisplayPriceCardA")
spawn("pricing_card", (-100.0, 185.0, 105.0), label="DisplayPriceCardB")
spawn("pricing_card", (165.0, 185.0, 105.0), label="DisplayPriceCardC")

# Pastries arranged around and behind the display.
spawn("bread", (-315.0, 185.0, 108.0), label="DisplayBread")
spawn("pretzel", (-110.0, 185.0, 108.0), label="DisplayPretzel")
spawn("cream_puff", (150.0, 185.0, 108.0), label="DisplayCreamPuff")
spawn("pastry_stand_A_decorated", (330.0, 510.0, 0.0), label="DecoratedPastryStand")
spawn("pastry_stand_B_decorated", (485.0, 510.0, 0.0), label="WindowPastryStand")

# Two small café seating groups near the open storefront.
for x in (-300.0, 280.0):
    spawn("table_round_A", (x, -155.0, 0.0), label="CafeTable")
    spawn("chair", (x - 90.0, -155.0, 0.0), 90.0, label="CafeChair")
    spawn("chair", (x + 90.0, -155.0, 0.0), -90.0, label="CafeChair")
    spawn("mug_A_blue" if x < 0 else "mug_A_pink", (x, -155.0, 78.0), label="TableMug")

# Back-of-house preparation area.
spawn("countertop_straight_A_large", (-320.0, 545.0, 0.0), 180.0, label="PrepCounterA")
spawn("countertop_straight_B_long", (30.0, 545.0, 0.0), 180.0, label="PrepCounterB")
spawn("bread_oven", (495.0, 565.0, 0.0), 180.0, label="BreadOven")
spawn("stand_mixer", (-260.0, 535.0, 92.0), 180.0, label="StandMixer")
spawn("mixing_bowl", (-75.0, 535.0, 92.0), label="MixingBowl")
spawn("dough_roller", (70.0, 535.0, 94.0), label="DoughRoller")
spawn("flour_sack_closed", (205.0, 585.0, 0.0), label="FlourSack")
spawn("wall_shelf_bakery_A", (-310.0, 682.0, 175.0), 180.0, label="BackShelfA")
spawn("wall_shelf_bakery_B", (20.0, 682.0, 175.0), 180.0, label="BackShelfB")

# Signage and soft dressing.
spawn("wall_sign_large", (0.0, 690.0, 225.0), 180.0, label="BakeryWallSign")
spawn("rug", (0.0, -360.0, 2.0), label="EntranceRug")
spawn("basket_A", (-500.0, 35.0, 0.0), label="BreadBasket")
spawn("cookie_jar", (285.0, 205.0, 93.0), label="CookieJar")
spawn("coffee_machine", (500.0, 390.0, 0.0), 180.0, label="CoffeeMachine")

# Lighting: warm shop light plus a cool skylight for readable shadows.
sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 350))
sky.set_actor_label("Bakery_SkyLight")
sky_comp = sky.get_component_by_class(unreal.SkyLightComponent)
sky_comp.set_editor_property("intensity", 0.8)
spawned.append(sky)

light(unreal.RectLight, (-260.0, 120.0, 330.0), 3500.0, (255, 197, 140), "WarmDisplayLight")
light(unreal.RectLight, (260.0, 120.0, 330.0), 3500.0, (255, 197, 140), "WarmCheckoutLight")
light(unreal.RectLight, (0.0, 510.0, 330.0), 3000.0, (255, 210, 165), "WarmPrepLight")

player = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.PlayerStart, unreal.Vector(0.0, -470.0, 95.0), unreal.Rotator(0.0, 0.0, 0.0)
)
player.set_actor_label("Bakery_PlayerStart")
spawned.append(player)

if not unreal.EditorLevelLibrary.save_current_level():
    raise RuntimeError(f"Failed to save level: {LEVEL_PATH}")

unreal.log_warning(f"CODEX_BAKERY_LEVEL_DONE path={LEVEL_PATH} actors={len(spawned)}")
