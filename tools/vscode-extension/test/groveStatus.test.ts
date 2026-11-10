import * as assert from "node:assert/strict";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { test } from "node:test";
import { summarizeGroveStatus } from "../src/model/groveStatus";
import { readCatalog } from "../src/repo/dataReader";

test("Grove summary separates hardware runs from builds and pending boards", () => {
  const summary = summarizeGroveStatus([
    { boardId: "xiao_rp2040", status: "hardware-tested" },
    { boardId: "xiao_rp2350", status: "hardware-tested" },
    { boardId: "xiao_esp32c5", status: "build-verified" },
    { boardId: "xiao_nrf54lm20a", status: "pending" },
  ]);
  assert.equal(summary, "2 hardware-tested - 1 build-verified - 1 pending");
});

test("Grove summary preserves failed, excluded and unknown states", () => {
  const summary = summarizeGroveStatus([
    { boardId: "board-a", status: "build-failed" },
    { boardId: "board-b", status: "excluded" },
    { boardId: "board-c", status: "unknown" },
  ]);
  assert.equal(summary, "1 build-failed - 1 excluded - 1 unknown");
  assert.equal(summarizeGroveStatus([]), "unknown");
});

test("catalog reads Grove hardware status from the example's board matrix", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "seeed-grove-status-"));
  const moduleId = "grove_test_sensor";
  const exampleId = "grove_test_basic_read";
  const files: Record<string, string> = {
    [`metadata/grove_modules/${moduleId}.yaml`]: `id: ${moduleId}\ninterface: gpio\n`,
    [`examples/grove/${moduleId}/basic_read/example.yaml`]: [
      `id: ${exampleId}`,
      `module_id: ${moduleId}`,
      "demo: basic_read",
      "kind: grove",
    ].join("\n"),
    [`metadata/status/${exampleId}.yaml`]: [
      "boards:",
      "  - board_id: xiao_rp2350",
      "    status: hardware-tested",
      "    evidence: Expected sensor output on physical hardware",
      "  - board_id: xiao_esp32c5",
      "    status: build-verified",
      "  - board_id: xiao_nrf54lm20a",
      "    status: pending",
    ].join("\n"),
  };
  for (const [relative, text] of Object.entries(files)) {
    const file = path.join(root, relative);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, text);
  }

  const example = readCatalog(root).modules[0].examples[0];
  assert.equal(example.boardStatus[0].status, "hardware-tested");
  assert.equal(example.boardStatus[0].evidence, "Expected sensor output on physical hardware");
  assert.equal(example.boardStatus[1].status, "build-verified");
  assert.equal(
    summarizeGroveStatus(example.boardStatus),
    "1 hardware-tested - 1 build-verified - 1 pending",
  );
});
