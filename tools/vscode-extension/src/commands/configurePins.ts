import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";
import * as yaml from "js-yaml";
import { runCapture } from "../cli/cliBridge";
import { locateCli } from "../cli/cliLocator";
import { getEffectiveBoard } from "./projectSettings";
import type { ProjectInfo } from "../statusBar";
import {
  PinAssignments,
  PinDiagramData,
} from "../panels/pinConfiguratorHtml";
import { PinConfiguratorPanel } from "../panels/pinConfiguratorPanel";

interface Snapshot {
  board?: unknown;
  source_asset?: unknown;
  pins?: unknown;
}

interface GroveExampleYaml {
  kind?: unknown;
  module_id?: unknown;
  demo?: unknown;
}

export async function configurePins(
  repoRoot: string | undefined,
  context: vscode.ExtensionContext,
  project: ProjectInfo,
  onSaved?: () => void,
): Promise<void> {
  // Opens the visual pin configurator for a generated Grove project and saves via CLI.
  // 为生成后的 Grove 项目打开可视化引脚配置器，并通过 CLI 保存。
  const board = getEffectiveBoard(context, project);
  if (!board) {
    void vscode.window.showErrorMessage("Select a board before configuring pins.");
    return;
  }
  const exampleRef = resolveGroveRef(project.appDir);
  if (!exampleRef) {
    void vscode.window.showErrorMessage("This project is not a generated Grove project.");
    return;
  }

  const cli = locateCli(repoRoot);
  const pinsResult = await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: "Loading pinout..." },
    () => runCapture(cli, ["show", "pins", board, exampleRef, "--json"]),
  );
  if (!pinsResult.ok) {
    void vscode.window.showErrorMessage(`Pinout load failed: ${pinsResult.message}`);
    return;
  }

  let data: PinDiagramData;
  try {
    data = JSON.parse(pinsResult.stdout) as PinDiagramData;
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    void vscode.window.showErrorMessage(`Pinout output is not valid JSON: ${detail}`);
    return;
  }

  const snapshot = readSnapshot(project.appDir);
  const initialPins = readSnapshotPins(snapshot);
  await PinConfiguratorPanel.show({
    title: "Configure Grove Pins",
    mode: "edit",
    data,
    extensionUri: context.extensionUri,
    initialAssignments: initialPins,
    onSave:
      data.example.pin_policy === "selectable"
        ? async (assignments) => {
            const args = [
              "set-pins",
              board,
              "--app",
              project.appDir,
              ...pinArgs(assignments),
              "--json",
            ];
            const result = await runCapture(cli, args);
            if (!result.ok) {
              throw new Error(result.message);
            }
            onSaved?.();
          }
        : undefined,
  });
}

function resolveGroveRef(appDir: string): string | undefined {
  // Resolves the original grove/<module>/<demo> reference from snapshot or example.yaml.
  // 从 snapshot 或 example.yaml 解析原始 grove/<module>/<demo> 引用。
  const snapshot = readSnapshot(appDir);
  const fromSnapshot = normalizeSourceAsset(snapshot.source_asset);
  if (fromSnapshot) {
    return fromSnapshot;
  }

  const exampleFile = path.join(appDir, "example.yaml");
  if (!fs.existsSync(exampleFile)) {
    return undefined;
  }
  const raw = yaml.load(fs.readFileSync(exampleFile, "utf-8")) as GroveExampleYaml | undefined;
  if (!raw || raw.kind !== "grove" || typeof raw.module_id !== "string" || typeof raw.demo !== "string") {
    return undefined;
  }
  return `grove/${raw.module_id}/${raw.demo}`;
}

function normalizeSourceAsset(value: unknown): string | undefined {
  if (typeof value !== "string") {
    return undefined;
  }
  const parts = value.split("/").filter(Boolean);
  if (parts[0] === "examples") {
    parts.shift();
  }
  if (parts[0] !== "grove" || parts.length !== 3) {
    return undefined;
  }
  return parts.join("/");
}

function readSnapshot(appDir: string): Snapshot {
  const file = path.join(appDir, "snapshot.json");
  if (!fs.existsSync(file)) {
    return {};
  }
  try {
    const data = JSON.parse(fs.readFileSync(file, "utf-8")) as Snapshot;
    return data && typeof data === "object" ? data : {};
  } catch {
    return {};
  }
}

function readSnapshotPins(snapshot: Snapshot): PinAssignments {
  // Reads the last saved role-to-pin mapping from snapshot.json.
  // 从 snapshot.json 读取上次保存的角色到引脚映射。
  const pins = snapshot.pins;
  if (!pins || typeof pins !== "object" || Array.isArray(pins)) {
    return {};
  }
  const result: PinAssignments = {};
  for (const [role, pin] of Object.entries(pins)) {
    if (typeof pin === "string") {
      result[role] = pin;
    }
  }
  return result;
}

function pinArgs(assignments: PinAssignments): string[] {
  const args: string[] = [];
  for (const [role, pin] of Object.entries(assignments)) {
    args.push("--pin", `${role}=${pin}`);
  }
  return args;
}
