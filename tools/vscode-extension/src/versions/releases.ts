import * as path from "path";
import * as yaml from "js-yaml";

// One published seeed-zephyr release and the Zephyr/SDK versions it pins.
// 一个已发布的 seeed-zephyr 版本，以及它锁定的 Zephyr/SDK 版本。
export interface Release {
  version: string;
  zephyr: string;
  sdk: string;
}

// One row of `west blobs list -f "{status} {module} {sha256} {abspath}"`.
// `west blobs list -f "{status} {module} {sha256} {abspath}"` 的一行。
export interface BlobEntry {
  status: string;
  module: string;
  sha256: string;
  abspath: string;
}

export const BLOB_LIST_FORMAT = "{status} {module} {sha256} {abspath}";

const RELEASE_VERSION_RE = /^\d+\.\d+\.\d+$/;
const ZEPHYR_TAG_RE = /^v\d+\.\d+\.\d+$/;

// Parses metadata/versions.yaml into releases ordered newest first.
// 把 metadata/versions.yaml 解析为按从新到旧排序的版本列表。
export function parseReleases(text: string): Release[] {
  const document = yaml.load(text) as { releases?: unknown } | undefined;
  const rows = document?.releases;
  if (!Array.isArray(rows) || rows.length === 0) {
    throw new Error("versions.yaml has no releases.");
  }
  const releases = rows.map((row, index) => {
    const entry = row as Partial<Record<keyof Release, unknown>>;
    const release = {
      version: String(entry.version ?? ""),
      zephyr: String(entry.zephyr ?? ""),
      sdk: String(entry.sdk ?? ""),
    };
    if (
      !RELEASE_VERSION_RE.test(release.version) ||
      !ZEPHYR_TAG_RE.test(release.zephyr) ||
      !RELEASE_VERSION_RE.test(release.sdk)
    ) {
      throw new Error(`versions.yaml release ${index + 1} is malformed.`);
    }
    return release;
  });
  return releases.sort((left, right) => compareVersions(right.version, left.version));
}

export function findRelease(releases: Release[], version: string | undefined): Release | undefined {
  return version ? releases.find((release) => release.version === version) : undefined;
}

export function isNewestRelease(releases: Release[], release: Release): boolean {
  return releases[0]?.version === release.version;
}

// Repository tag that holds the examples of a release, e.g. "v0.5.0".
// 保存某个版本示例的仓库 tag，例如 "v0.5.0"。
export function repoTag(release: Release): string {
  return `v${release.version}`;
}

// Reads the manifest repository path from a west workspace config, defaulting to "zephyr".
// 从 west 工作区配置读取 manifest 仓库路径，默认为 "zephyr"。
export function parseManifestPath(westConfig: string): string {
  let inManifest = false;
  for (const rawLine of westConfig.split(/\r?\n/)) {
    const line = rawLine.trim();
    const section = line.match(/^\[(.+)\]$/);
    if (section) {
      inManifest = section[1] === "manifest";
      continue;
    }
    const value = line.match(/^path\s*=\s*(\S+)/);
    if (inManifest && value) {
      return value[1];
    }
  }
  return "zephyr";
}

// Converts Zephyr's VERSION file into a tag such as "v4.5.0".
// 把 Zephyr 的 VERSION 文件转换成类似 "v4.5.0" 的 tag。
export function parseZephyrVersion(versionFile: string): string | undefined {
  const fields = new Map<string, string>();
  for (const line of versionFile.split(/\r?\n/)) {
    const match = line.match(/^(\w+)\s*=\s*(.*?)\s*$/);
    if (match) {
      fields.set(match[1], match[2]);
    }
  }
  const major = fields.get("VERSION_MAJOR");
  const minor = fields.get("VERSION_MINOR");
  const patch = fields.get("PATCHLEVEL");
  if (!major || !minor || !patch) {
    return undefined;
  }
  const extra = fields.get("EXTRAVERSION");
  return extra ? `v${major}.${minor}.${patch}-${extra}` : `v${major}.${minor}.${patch}`;
}

export function parseBlobList(output: string): BlobEntry[] {
  const entries: BlobEntry[] = [];
  for (const line of output.split(/\r?\n/)) {
    const match = line.trim().match(/^(\S+)\s+(\S+)\s+([0-9a-f]{64})\s+(.+)$/i);
    if (match) {
      entries.push({ status: match[1], module: match[2], sha256: match[3], abspath: match[4] });
    }
  }
  return entries;
}

// Modules whose blobs are on disk; only these are refreshed after a switch.
// 磁盘上已有 blobs 的模块；切换后只刷新这些模块。
export function modulesWithBlobs(entries: BlobEntry[]): string[] {
  const modules = entries
    .filter((entry) => entry.status === "A" || entry.status === "M")
    .map((entry) => entry.module);
  return [...new Set(modules)].sort();
}

// File name west looks up in its blob auto-cache: "<name>.<sha256>".
// west 在 blob 自动缓存里查找的文件名："<name>.<sha256>"。
export function blobCacheName(entry: BlobEntry): string {
  return `${path.basename(entry.abspath)}.${entry.sha256}`;
}

export function compareVersions(left: string, right: string): number {
  const a = left.split(".").map((part) => Number.parseInt(part, 10) || 0);
  const b = right.split(".").map((part) => Number.parseInt(part, 10) || 0);
  for (let index = 0; index < Math.max(a.length, b.length); index += 1) {
    const diff = (a[index] ?? 0) - (b[index] ?? 0);
    if (diff !== 0) {
      return diff;
    }
  }
  return 0;
}
