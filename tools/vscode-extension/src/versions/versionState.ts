import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import { parseManifestPath, parseReleases, parseZephyrVersion, Release } from "./releases";

// Version facts read from disk: repository examples, Zephyr workspace, and release mapping.
// 从磁盘读取的版本信息：仓库示例、Zephyr 工作区和版本映射表。
export interface VersionState {
  repoVersion: string | undefined;
  workspace: string;
  zephyrInstalled: string | undefined;
  releases: Release[] | undefined;
}

// Zephyr workspace used by the CLI: $ZEPHYR_WORKSPACE or ~/zephyrproject.
// CLI 使用的 Zephyr 工作区：$ZEPHYR_WORKSPACE 或 ~/zephyrproject。
export function zephyrWorkspacePath(): string {
  return process.env.ZEPHYR_WORKSPACE || path.join(os.homedir(), "zephyrproject");
}

export function westCommandPath(workspace: string): string {
  return process.platform === "win32"
    ? path.join(workspace, ".venv", "Scripts", "west.exe")
    : path.join(workspace, ".venv", "bin", "west");
}

export function manifestDir(workspace: string): string {
  return path.join(workspace, parseManifestPath(readText(path.join(workspace, ".west", "config")) ?? ""));
}

export function readZephyrInstalled(workspace: string): string | undefined {
  const versionFile = readText(path.join(manifestDir(workspace), "VERSION"));
  return versionFile ? parseZephyrVersion(versionFile) : undefined;
}

export function readRepoVersion(repoRoot: string | undefined): string | undefined {
  if (!repoRoot) {
    return undefined;
  }
  const content = readText(
    path.join(repoRoot, "packages", "seeed-zephyr", "src", "seeed_zephyr", "__init__.py"),
  );
  return content?.match(/__version__\s*=\s*"([^"]+)"/)?.[1];
}

export function readRepoReleases(repoRoot: string | undefined): Release[] | undefined {
  if (!repoRoot) {
    return undefined;
  }
  const content = readText(path.join(repoRoot, "metadata", "versions.yaml"));
  if (!content) {
    return undefined;
  }
  try {
    return parseReleases(content);
  } catch {
    return undefined;
  }
}

// Combines repository releases with the last downloaded list, preferring the longer one.
// 合并仓库内的版本列表与上次下载的列表，取更完整的那份。
export function readVersionState(
  repoRoot: string | undefined,
  cachedReleases: Release[] | undefined,
): VersionState {
  const workspace = zephyrWorkspacePath();
  const repoReleases = readRepoReleases(repoRoot);
  const releases =
    (repoReleases?.length ?? 0) >= (cachedReleases?.length ?? 0) ? repoReleases : cachedReleases;
  return {
    repoVersion: readRepoVersion(repoRoot),
    workspace,
    zephyrInstalled: readZephyrInstalled(workspace),
    releases,
  };
}

function readText(file: string): string | undefined {
  try {
    return fs.readFileSync(file, "utf-8");
  } catch {
    return undefined;
  }
}
