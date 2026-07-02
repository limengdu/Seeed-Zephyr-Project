import * as fs from "fs";
import * as path from "path";
import * as yaml from "js-yaml";
import {
  Board,
  Catalog,
  Example,
  ExpansionBoard,
  ExpansionPort,
  GroveBoardStatus,
  GroveExample,
  GroveMatrixStatus,
  GroveModule,
  GrovePinRole,
  ValidationStatus,
} from "../model/types";

// Reads one YAML file into a plain object.
// 把一个 YAML 文件读成普通对象。
function readYaml(file: string): Record<string, unknown> {
  const data = yaml.load(fs.readFileSync(file, "utf-8"));
  return data && typeof data === "object" ? (data as Record<string, unknown>) : {};
}

function listYamlFiles(dir: string): string[] {
  if (!fs.existsSync(dir)) {
    return [];
  }
  return fs
    .readdirSync(dir)
    .filter((name) => name.endsWith(".yaml"))
    .map((name) => path.join(dir, name))
    .sort();
}

function asString(value: unknown, fallback = ""): string {
  return value === null || value === undefined ? fallback : String(value);
}

function asStringList(value: unknown): string[] {
  return Array.isArray(value) ? value.map((item) => String(item)) : [];
}

function asRecordList(value: unknown): Array<Record<string, unknown>> {
  return Array.isArray(value)
    ? value.filter((item): item is Record<string, unknown> => {
        return item !== null && typeof item === "object" && !Array.isArray(item);
      })
    : [];
}

// Reads the full offline catalog from a repository checkout.
// 从仓库签出读取完整的离线目录。
export function readCatalog(repoRoot: string): Catalog {
  return {
    boards: readBoards(repoRoot),
    modules: readGroveModules(repoRoot),
    expansions: readExpansionBoards(repoRoot),
  };
}

function readBoards(repoRoot: string): Board[] {
  const boardDir = path.join(repoRoot, "metadata", "boards");
  const boards: Board[] = [];
  for (const file of listYamlFiles(boardDir)) {
    const raw = readYaml(file);
    const id = asString(raw.id, path.basename(file, ".yaml"));
    const examples = readBoardExamples(repoRoot, id);
    boards.push({
      id,
      displayName: asString(raw.display_name, id),
      zephyrTarget: asString(raw.zephyr_target),
      vendor: asString(raw.vendor),
      soc: asString(raw.soc),
      formFactor: asString(raw.form_factor, "xiao"),
      alsoKnownAs: asStringList(raw.also_known_as),
      versionPolicy: asString(raw.version_policy, "latest_stable"),
      examples,
      status: deriveBoardStatus(examples),
    });
  }
  return boards;
}

function readBoardExamples(repoRoot: string, boardId: string): Example[] {
  const dir = path.join(repoRoot, "examples", "boards", boardId);
  if (!fs.existsSync(dir)) {
    return [];
  }
  const examples: Example[] = [];
  for (const entry of fs.readdirSync(dir).sort()) {
    const exampleDir = path.join(dir, entry);
    const exampleFile = path.join(exampleDir, "example.yaml");
    if (!fs.existsSync(exampleFile)) {
      continue;
    }
    const raw = readYaml(exampleFile);
    examples.push({
      id: asString(raw.id, `${boardId}_${entry}`),
      boardId: asString(raw.board_id, boardId),
      demo: asString(raw.demo, entry),
      zephyrTarget: asString(raw.zephyr_target),
      validationStatus: asString(raw.validation_status, "unknown") as ValidationStatus,
      expectedBehavior: asString(raw.expected_behavior),
      unsupportedReason: raw.unsupported_reason
        ? asString(raw.unsupported_reason)
        : undefined,
      dirPath: exampleDir,
      files: fs
        .readdirSync(exampleDir)
        .filter((name) => fs.statSync(path.join(exampleDir, name)).isFile()),
    });
  }
  return examples;
}

// Board status mirrors the CLI: the first supported example, else the first example.
// 板子状态与 CLI 一致:取第一个被支持的示例,否则取第一个示例。
function deriveBoardStatus(examples: Example[]): ValidationStatus {
  if (examples.length === 0) {
    return "unknown";
  }
  const supported = examples.find((ex) => ex.validationStatus !== "unsupported");
  return (supported ?? examples[0]).validationStatus;
}

function readGroveModules(repoRoot: string): GroveModule[] {
  const dir = path.join(repoRoot, "metadata", "grove_modules");
  const modules: GroveModule[] = [];
  for (const file of listYamlFiles(dir)) {
    const raw = readYaml(file);
    const id = asString(raw.id, path.basename(file, ".yaml"));
    modules.push({
      id,
      sku: asString(raw.sku),
      displayName: asString(raw.display_name),
      category: asString(raw.category),
      interface: asString(raw.interface),
      defaultAddress: raw.default_address ? asString(raw.default_address) : null,
      defaultBaud: typeof raw.default_baud === "number" ? raw.default_baud : null,
      powerRail: asString(raw.power_rail),
      zephyrSupport: asString(raw.zephyr_support),
      zephyrCompatible: raw.zephyr_compatible ? asString(raw.zephyr_compatible) : null,
      zephyrDriver: raw.zephyr_driver ? asString(raw.zephyr_driver) : null,
      requiredConfigs: asStringList(raw.required_configs),
      supportedTemplates: asStringList(raw.supported_templates),
      examples: readGroveExamples(repoRoot, id),
    });
  }
  return modules;
}

function readGroveExamples(repoRoot: string, moduleId: string): GroveExample[] {
  const dir = path.join(repoRoot, "examples", "grove", moduleId);
  if (!fs.existsSync(dir)) {
    return [];
  }
  const examples: GroveExample[] = [];
  for (const entry of fs.readdirSync(dir).sort()) {
    const exampleDir = path.join(dir, entry);
    const exampleFile = path.join(exampleDir, "example.yaml");
    if (!fs.existsSync(exampleFile)) {
      continue;
    }
    const raw = readYaml(exampleFile);
    const id = asString(raw.id, `${moduleId}_${entry}`);
    examples.push({
      id,
      moduleId: asString(raw.module_id, moduleId),
      demo: asString(raw.demo, entry),
      interface: asString(raw.interface),
      connector: asString(raw.connector),
      pinPolicy: asString(raw.pin_policy),
      excludedBoards: asStringList(raw.excluded_boards),
      expectedBehavior: asString(raw.expected_behavior),
      dirPath: exampleDir,
      files: fs
        .readdirSync(exampleDir)
        .filter((name) => fs.statSync(path.join(exampleDir, name)).isFile()),
      pins: readGrovePinRoles(raw.pins),
      boardStatus: readGroveStatus(repoRoot, id),
    });
  }
  return examples;
}

function readGrovePinRoles(value: unknown): GrovePinRole[] {
  return asRecordList(value).map((pin) => ({
    role: asString(pin.role),
    default: asString(pin.default),
    allowed: asStringList(pin.allowed),
  }));
}

function readGroveStatus(repoRoot: string, exampleId: string): GroveBoardStatus[] {
  const file = path.join(repoRoot, "metadata", "status", `${exampleId}.yaml`);
  if (!fs.existsSync(file)) {
    return [];
  }
  const raw = readYaml(file);
  return asRecordList(raw.boards).map((row) => ({
    boardId: asString(row.board_id),
    status: asString(row.status, "unknown") as GroveMatrixStatus,
    target: row.target ? asString(row.target) : undefined,
    reason: row.reason ? asString(row.reason) : undefined,
    evidence: row.evidence ? asString(row.evidence) : undefined,
  }));
}

function readExpansionBoards(repoRoot: string): ExpansionBoard[] {
  const dir = path.join(repoRoot, "metadata", "expansion_boards");
  const expansions: ExpansionBoard[] = [];
  for (const file of listYamlFiles(dir)) {
    const raw = readYaml(file);
    const ports: ExpansionPort[] = asRecordList(raw.ports).map((port) => ({
      id: asString(port.id),
      type: asString(port.type),
      label: asString(port.label),
    }));
    expansions.push({
      id: asString(raw.id, path.basename(file, ".yaml")),
      sku: asString(raw.sku),
      displayName: asString(raw.display_name),
      compatibleFormFactor: asString(raw.compatible_form_factor, "xiao"),
      zephyrShield: raw.zephyr_shield ? asString(raw.zephyr_shield) : null,
      ports,
      onboard: asStringList(raw.onboard),
    });
  }
  return expansions;
}
