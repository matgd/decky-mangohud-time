import {
  ButtonItem,
  PanelSection,
  PanelSectionRow,
  Navigation,
  staticClasses,
  SliderField,
  Dropdown,
  TextField,
  DropdownItem,
} from "@decky/ui";
import {
  addEventListener,
  removeEventListener,
  callable,
  definePlugin,
  toaster,
  // routerHook
} from "@decky/api"
import { useEffect, useState } from "react";
import { FaClock } from "react-icons/fa";

// TODO: Don't keep defaults in multiple places
const DEFAULT_ALPHA = 1.0;
const DEFAULT_BACKGROUND_ALPHA = 0.0;
const OFFSET_X_BASE = 233;
const OFFSET_Y_BASE = -6;
const DEFAULT_TIME_FORMAT = "%H:%M";
const DEFAULT_POSITION = "top-right";

const OFFSET_X_SLIDER_FIELD_RANGE = 100;
const OFFSET_Y_SLIDER_FIELD_RANGE = OFFSET_X_SLIDER_FIELD_RANGE;

const pyMangohudUpsertTimePreset = callable<[
  preset_number: number,
  alpha: number,
  background_alpha: number,
  offset_y: number,
  offset_x: number,
  time_format: string,
  position: string,
], void>("mangohud_upsert_time_preset");
const pyMangohudGetCurrentPresetData = callable<[preset_number: number], any>("mangohud_get_current_preset_data");
const pyMangohudPresetIsEmpty = callable<[preset_number: number], boolean>("mangohud_preset_is_empty");
const pyMangohudPresetNonPluginKeysInside = callable<[preset_number: number], boolean>("mangohud_preset_non_plugin_keys_inside");
const pyDeletePreset = callable<[preset_number: number], void>("mangohud_delete_preset");

function Content() {
  const [showPresetKeys, setShowPresetKeys] = useState<boolean>(false);
  const [presetEmpty, setPresetEmpty] = useState<boolean>(true);
  const [presetNonPluginKeysInside, setPresetNonPluginKeysInside] = useState<boolean>(false);

  const [errorMsg, setErrorMsg] = useState<string>("");
  const [presetMsg, setPresetMsg] = useState<string>("");


  const [preset, setPreset] = useState<number>(3);
  const [alpha, setAlpha] = useState<number>(1.0);
  const [backgroundAlpha, setBackgroundAlpha] = useState<number>(0.0);
  const [offsetX, setOffsetX] = useState<number>(0);
  const [offsetY, setOffsetY] = useState<number>(0);
  const [timeFormat, setTimeFormat] = useState<string>("%H:%M");
  const [position, setPosition] = useState<string>("top-right");

  const timeFormatOptions = [
    { label: "23:45", data: "%H:%M" },
    { label: "11:45 PM", data: "%I:%M %p" },
    { label: "23", data: "%H" },
    { label: "23:", data: "%H:" },
    { label: ":45", data: ":%M" },
    { label: "23:45:30", data: "%H:%M:%S" },
    { label: "11:45:30 PM", data: "%I:%M:%S %p" },
    { label: "2025-12-31 23:45", data: "%Y-%m-%d %H:%M" },
    { label: "2025-12-31 11:45 PM", data: "%Y-%m-%d %I:%M %p" },
  ];

  const positionOptions = [
    { label: "top-left", data: "top-left" },
    { label: "top-right", data: "top-right" },
    { label: "bottom-left", data: "bottom-left" },
    { label: "bottom-right", data: "bottom-right" },
  ];

  const presetLoad = async () => {
    try {
      const curr = await pyMangohudGetCurrentPresetData(3);
      const isEmpty = await pyMangohudPresetIsEmpty(preset);
      const nonPluginDataDetected = await pyMangohudPresetNonPluginKeysInside(preset);

      setPresetEmpty(isEmpty);
      setPresetNonPluginKeysInside(nonPluginDataDetected);

      if (isEmpty) {
        setPresetMsg(`Preset ${preset} is empty.`);
        setShowPresetKeys(false);
        return
      } else if (nonPluginDataDetected) {
        // TODO: Test this
        setPresetMsg(`Preset ${preset} contains non-plugin keys. Changes may overwrite existing settings.`);
        setShowPresetKeys(false);
        return
      }

      if (curr.alpha) setAlpha(parseFloat(curr.alpha));
      if (curr.background_alpha) setBackgroundAlpha(parseFloat(curr.background_alpha));
      if (curr.offset_x) setOffsetX(parseInt(curr.offset_x));
      if (curr.offset_y) setOffsetY(parseInt(curr.offset_y));
      if (curr.time_format) setTimeFormat(curr.time_format);
      if (curr.position) setPosition(curr.position);
      setShowPresetKeys(true);
    } catch (e) {
      setErrorMsg(`Failed to load current preset data: ${e}`);
    }
  }

  const deleteCurrentPreset = async () => {
    try {
      await pyDeletePreset(preset);
      setPresetEmpty(true);
      setShowPresetKeys(false);
    } catch (e) {
      setErrorMsg(`Failed to delete preset: ${e}`);
    }
  }

  useEffect(() => {
    setShowPresetKeys(false);
    presetLoad().catch(e => {
      setErrorMsg(`Error during preset load: ${e}`);
    });
  }, [preset])

  const applyChanges = async () => {
    try {
      await pyMangohudUpsertTimePreset(
        preset,
        alpha,
        backgroundAlpha,
        offsetY,
        offsetX,
        timeFormat,
        position
      );
    } catch (e) {
      setErrorMsg(`Failed to apply changes: ${e}`);
    }
  }

  const defaultSettings = async () => {
    setAlpha(DEFAULT_ALPHA);
    setBackgroundAlpha(DEFAULT_BACKGROUND_ALPHA);
    setOffsetX(OFFSET_X_BASE);
    setOffsetY(OFFSET_Y_BASE);
    setTimeFormat(DEFAULT_TIME_FORMAT);
    setPosition(DEFAULT_POSITION);
    await applyChanges();
  }

  const createPreset = async () => {
    await defaultSettings();
    await presetLoad();
  }


  // useEffect(() => {
  //   onFieldChange();
  // }, [alpha, backgroundAlpha, offsetX, offsetY, timeFormat, position]);

  if (errorMsg !== "") {
    return (
      <PanelSection title="MangoHud config">
        <div>Error: {errorMsg}</div>
      </PanelSection>
    )
  }

  // TODO:
  //  - Fix 0s in offset fields when loading preset
  //  - Apply automatically on field change
  return (
    <PanelSection title="MangoHud config">
      <PanelSectionRow>
        <SliderField label="Affected preset" min={1} max={6} step={1} value={preset} onChange={(v) => setPreset(v)} showValue={true} description="Change preset to overwrite" />
      </PanelSectionRow>

      {(presetEmpty || presetNonPluginKeysInside) && (
        <>
          <PanelSectionRow>
            <div>{presetMsg}</div>
          </PanelSectionRow>
          <PanelSectionRow>
            <ButtonItem layout="below" onClick={() => createPreset()}>Create preset</ButtonItem>
          </PanelSectionRow>
        </>
      )}

      {showPresetKeys && (
        <>
          <PanelSectionRow>
            <ButtonItem layout="below" onClick={() => applyChanges()}>Apply changes</ButtonItem>
          </PanelSectionRow>
          <PanelSectionRow>
            <SliderField label="Text alpha" min={0} max={1} step={0.1} value={alpha} onChange={(v) => setAlpha(v)} showValue={true} description="Change text opacity" />
          </PanelSectionRow>
          <PanelSectionRow>
            <SliderField label="Background alpha" min={0} max={1} step={0.1} value={backgroundAlpha} onChange={(v) => setBackgroundAlpha(v)} showValue={true} description="Change background opacity" />
          </PanelSectionRow>
          <PanelSectionRow>
            <SliderField label="Offset X" min={OFFSET_X_BASE - OFFSET_X_SLIDER_FIELD_RANGE} max={OFFSET_X_BASE + OFFSET_X_SLIDER_FIELD_RANGE} showValue={true} step={1} value={offsetX} onChange={(v) => setOffsetX(v)} description="Adjust the placement on X axis" />
          </PanelSectionRow>
          <PanelSectionRow>
            <SliderField label="Offset Y" min={OFFSET_Y_BASE - OFFSET_Y_SLIDER_FIELD_RANGE} max={OFFSET_Y_BASE + OFFSET_Y_SLIDER_FIELD_RANGE} showValue={true} step={1} value={offsetY} onChange={(v) => setOffsetY(v)} description="Adjust the placement on Y axis" />
          </PanelSectionRow>
          <PanelSectionRow>
            <DropdownItem label="Time format" rgOptions={timeFormatOptions} selectedOption={timeFormat} onChange={(v) => setTimeFormat(v.data)} description="Select time format" />
          </PanelSectionRow>
          <PanelSectionRow>
            <DropdownItem label="Clock position" rgOptions={positionOptions} selectedOption={position} onChange={(v) => setPosition(v.data)} description="Select clock position" />
          </PanelSectionRow>
          <PanelSectionRow>
            <ButtonItem layout="below" onClick={() => defaultSettings()}>Reset to defaults</ButtonItem>
          </PanelSectionRow>
          <PanelSectionRow>
            <ButtonItem layout="below" onClick={() => deleteCurrentPreset()}>Delete preset</ButtonItem>
          </PanelSectionRow>
        </>
      )}
    </PanelSection>
  )
};

export default definePlugin(() => {
  console.log("Template plugin initializing, this is called once on frontend startup")

  // serverApi.routerHook.addRoute("/decky-plugin-test", DeckyPluginRouterTest, {
  //   exact: true,
  // });

  // Add an event listener to the "timer_event" event from the backend
  // const listener = addEventListener<[
  //   test1: string,
  //   test2: boolean,
  //   test3: number
  // ]>("timer_event", (test1, test2, test3) => {
  //   console.log("Template got timer_event with:", test1, test2, test3)
  //   toaster.toast({
  //     title: "template got timer_event",
  //     body: `${test1}, ${test2}, ${test3}`
  //   });
  // });

  return {
    // The name shown in various decky menus
    name: "MangoHud Preset Clock",
    // The element displayed at the top of your plugin's menu
    titleView: <div className={staticClasses.Title}>MangoHud Preset Clock</div>,
    // The content of your plugin's menu
    content: <Content />,
    // The icon displayed in the plugin list
    icon: <FaClock />,
    // Fixes DropdownItem not updating
    alwaysRender: true,
    // The function triggered when your plugin unloads
    onDismount() {
      console.log("Unloading")
      // removeEventListener("timer_event", listener);
      // serverApi.routerHook.removeRoute("/decky-plugin-test");
    },
  };
});
