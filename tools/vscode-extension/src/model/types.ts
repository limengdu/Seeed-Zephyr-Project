// Data models for the XIAO + Zephyr catalog, aligned to the repository metadata schema.
// XIAO + Zephyr 目录的数据模型,与仓库元数据 schema 对齐。

export type ValidationStatus =
  | "build-only"
  | "hardware-tested"
  | "experimental"
  | "blocked"
  | "unsupported"
  | "unknown";

export interface Example {
  id: string;
  boardId: string;
  demo: string;
  zephyrTarget: string;
  validationStatus: ValidationStatus;
  expectedBehavior: string;
  unsupportedReason?: string;
  dirPath: string;
  files: string[];
}

export interface Board {
  id: string;
  displayName: string;
  zephyrTarget: string;
  vendor: string;
  soc: string;
  formFactor: string;
  alsoKnownAs: string[];
  versionPolicy: string;
  examples: Example[];
  status: ValidationStatus;
}

export interface GroveModule {
  id: string;
  sku: string;
  displayName: string;
  category: string;
  interface: string;
  defaultAddress: string | null;
  defaultBaud: number | null;
  powerRail: string;
  zephyrSupport: string;
  zephyrCompatible: string | null;
  zephyrDriver: string | null;
  requiredConfigs: string[];
  supportedTemplates: string[];
  examples: GroveExample[];
}

export type GroveMatrixStatus =
  | "build-verified"
  | "build-failed"
  | "hardware-tested"
  | "pending"
  | "excluded"
  | "unknown";

export interface GroveBoardStatus {
  boardId: string;
  status: GroveMatrixStatus;
  target?: string;
  reason?: string;
  evidence?: string;
}

export interface GrovePinRole {
  role: string;
  default: string;
  allowed: string[];
}

export interface GroveExample {
  id: string;
  moduleId: string;
  demo: string;
  interface: string;
  connector: string;
  pinPolicy: string;
  excludedBoards: string[];
  expectedBehavior: string;
  dirPath: string;
  files: string[];
  pins: GrovePinRole[];
  boardStatus: GroveBoardStatus[];
}

export interface ExpansionPort {
  id: string;
  type: string;
  label: string;
}

export interface ExpansionBoard {
  id: string;
  sku: string;
  displayName: string;
  compatibleFormFactor: string;
  zephyrShield: string | null;
  ports: ExpansionPort[];
  onboard: string[];
}

export interface Catalog {
  boards: Board[];
  modules: GroveModule[];
  expansions: ExpansionBoard[];
}
