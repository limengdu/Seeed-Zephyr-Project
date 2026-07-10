import * as assert from "node:assert/strict";
import * as path from "node:path";
import { test } from "node:test";
import {
  discoverProjects,
  ProjectFileReader,
  resolveActiveProject,
} from "../src/projectDiscovery";

class MemoryFiles implements ProjectFileReader {
  constructor(private readonly files: ReadonlyMap<string, string>) {}

  exists(file: string): boolean {
    return this.files.has(file);
  }

  readText(file: string): string {
    const content = this.files.get(file);
    if (content === undefined) {
      throw new Error(`Missing test file: ${file}`);
    }
    return content;
  }
}

test("discovers every Zephyr project in a multi-root workspace", () => {
  const generatedProject = path.join("workspace", "generated");
  const plainProject = path.join("workspace", "plain");
  const unrelatedFolder = path.join("workspace", "notes");
  const files = new MemoryFiles(new Map([
    [path.join(generatedProject, "snapshot.json"), JSON.stringify({ board: "xiao_esp32s3" })],
    [path.join(plainProject, "CMakeLists.txt"), "project(app)"],
    [path.join(plainProject, "prj.conf"), "CONFIG_GPIO=y"],
  ]));

  assert.deepEqual(
    discoverProjects([generatedProject, plainProject, unrelatedFolder], files),
    [
      { appDir: generatedProject, board: "xiao_esp32s3" },
      { appDir: plainProject, board: undefined },
    ],
  );
});

test("keeps a generated project visible when its receipt is unreadable", () => {
  const project = path.join("workspace", "broken-receipt");
  const files = new MemoryFiles(new Map([
    [path.join(project, "snapshot.json"), "{"],
  ]));

  assert.deepEqual(discoverProjects([project], files), [
    { appDir: project, board: undefined },
  ]);
});

test("selects the requested project from a multi-project workspace", () => {
  const firstProject = { appDir: path.join("workspace", "first"), board: "first" };
  const secondProject = { appDir: path.join("workspace", "second"), board: "second" };

  assert.equal(
    resolveActiveProject(
      [firstProject, secondProject],
      [secondProject.appDir, firstProject.appDir],
    ),
    secondProject,
  );
});
