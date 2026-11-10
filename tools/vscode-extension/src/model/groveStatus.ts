import type { GroveBoardStatus, GroveMatrixStatus } from "./types";

// Counts Grove boards by their recorded validation status.
// 按记录的验证状态分别统计 Grove 开发板数量。
export function summarizeGroveStatus(rows: readonly GroveBoardStatus[]): string {
  const statuses: GroveMatrixStatus[] = [
    "hardware-tested",
    "build-verified",
    "build-failed",
    "pending",
    "excluded",
    "unknown",
  ];
  const counts = new Map<GroveMatrixStatus, number>();
  for (const row of rows) {
    counts.set(row.status, (counts.get(row.status) ?? 0) + 1);
  }
  return statuses
    .filter((status) => counts.has(status))
    .map((status) => `${counts.get(status)} ${status}`)
    .join(" - ") || "unknown";
}
