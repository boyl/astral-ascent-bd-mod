# Astral Ascent Build Selector

**1.0.0-beta.1 · Steam Windows PC · verified game build 2.6.4**

## Download

**[Download the complete Mod ZIP (62.4 MB)](https://github.com/boyl/astral-ascent-bd-mod/releases/download/v1.0.0-beta.1/AstralAscent-BD-Mod-v1.0.0-beta.1.zip)**

[Release notes and checksums](https://github.com/boyl/astral-ascent-bd-mod/releases/tag/v1.0.0-beta.1). This is a prerelease. Use the Mod ZIP above; GitHub's `Source code` archives are not installable packages.

An unofficial gameplay mod with immediate build equipment, custom aura selection and saved aura plans. Chinese and English are included in one package.

## Install

1. Install [PowerShell 7](https://learn.microsoft.com/powershell/scripting/install/installing-powershell-on-windows) if `pwsh` is not available.
2. Close Astral Ascent. Extract the complete ZIP, open `astral-bd`, then run `INSTALL.cmd`.
3. Start the game normally from Steam, a shortcut or the game EXE. The mod loads automatically.
4. Press **F8**, or **Back + Start** on an XInput controller.
5. Select **English** from **Language / 语言**. The setting is remembered. On Builds or Aura Plans, controller **Y** switches languages.

Python and Frida are bundled. No separate Python installation is required. The installer checks the exact game executable and stops if an unrelated `version.dll` already exists.

## Use

- **Builds / Complete:** immediately replace Player 1's 5 auras, 4 spells and recipe gambits. Most recipes use the first gambit slot; 3D Hunter includes all four slots per spell.
- **Builds / Growth:** equip spells immediately. Subsequent room progress unlocks four retained rewards: the first gambit, two auras, three auras, and remaining primary gambits. Aura rewards require empty slots.
- **Custom Auras:** filter 355 original auras by rarity and element; view English effects, select a slot and equip immediately. Duplicate auras and clearing individual slots are supported.
- **Aura Plans:** enter an optional name and save all five current aura slots. Select a saved plan and apply it immediately. Empty slots are preserved; spells and gambits stay unchanged. Blank names are generated automatically.
- The selected build becomes the default for future new runs. Custom auras and aura plans do not change that default. Continuing a saved run does not reapply the build.

| Controller | Action |
|---|---|
| Back + Start | Open / close |
| LB / RB | Previous / next tab |
| Up / Down or left stick | Select |
| LT / RT | Jump 8 entries |
| Left / Right | Build mode / target aura slot |
| A | Equip build / equip aura / apply plan |
| B | Close |
| X | Claim reward / aura element / save plan |
| Y | Switch language on Builds and Plans; clear slot on Custom Auras |
| Right stick click | Aura rarity |
| Left stick click | Reset aura filters |

## Builds

12 recipes: Missiles + Ice Swords, Snowflakes + Ice Shards, Thundercloud Summons, Low-cost Spell Cycle, **3D Hunter (Marked Ice Swords)**, Ice Shards + Ice Idols, Spark Loop, Slimes + Sparks, Burning Idols + Homing Shields, Ice Idols + Poison Chain, Full-life First Strike Missiles, Ice Strike + Brittle Ice.

Recipes reflect community build ideas and verified component IDs. This release does **not** claim measured T0 performance for every recipe. Source links are stored in `recipes.en.json`.

## Saves, updates and removal

Equipment uses the game's original checkpoint. Hub/start-platform changes are saved at the next room checkpoint. Use the game's normal **save and quit** option to continue a run.

User data is separate under `%LOCALAPPDATA%\AstralAscentBD`:

- `profile.json`: default build and growth progress.
- `aura-plans.json`: saved aura plans.
- `ui-settings.json`: chosen language.
- `autoload-error.log` / `runtime.jsonl`: local diagnostics; not included in public releases.

To update, close the game and run the new package's `INSTALL.cmd`. To remove, close the game and run `UNINSTALL.cmd`. Original saves and user plans remain. **Disable Mod** stops future automatic build grants; already equipped original components remain.

## Supported scope and limitations

- Exact verified Steam Windows x64 game executable SHA-256: `CA376D2B741F65C75C416317517D24C316DD8A32A4EAE6559030797B3B9AA88B`.
- Modifies Player 1. Full co-op, every character/unlock combination, other platforms, Proton and other game builds are not certified.
- Uses native runtime hooks and D3D11; it is not an A2M2 sprite replacement. **Workshop subscription alone cannot install the native loader. Manual installation is required.**
- English uses original English aura names/effect templates. Chinese display requires a Chinese-capable Windows font; English falls back to Segoe UI when Microsoft YaHei is unavailable.
- Bundled ImGui, Python and Frida retain their license files. Game assets, names and effect text belong to their respective owners. No game executable or save file is distributed.

## Verification

Previous equipment/save tests covered the existing gameplay path. This release adds Chinese/English catalog identity checks and isolated D3D/controller checks for both languages. These UI checks are separate from actual game performance tests.
