import * as assert from "node:assert/strict";
import { test } from "node:test";
import {
  blobCacheName,
  findRelease,
  isNewestRelease,
  modulesWithBlobs,
  parseBlobList,
  parseManifestPath,
  parseReleases,
  parseZephyrVersion,
  repoTag,
} from "../src/versions/releases";

const VERSIONS_YAML = `
releases:
  - version: 0.4.0
    zephyr: v4.4.0
    sdk: 1.0.1
  - version: 0.5.0
    zephyr: v4.5.0
    sdk: 1.0.1
`;

test("parses releases newest first and maps them to repository tags", () => {
  const releases = parseReleases(VERSIONS_YAML);
  assert.deepEqual(releases.map((release) => release.version), ["0.5.0", "0.4.0"]);
  assert.equal(findRelease(releases, "0.4.0")?.zephyr, "v4.4.0");
  assert.equal(isNewestRelease(releases, releases[0]), true);
  assert.equal(isNewestRelease(releases, releases[1]), false);
  assert.equal(repoTag(releases[1]), "v0.4.0");
});

test("rejects a release list with a malformed Zephyr tag", () => {
  assert.throws(() => parseReleases("releases:\n  - version: 0.5.0\n    zephyr: 4.5\n    sdk: 1.0.1\n"));
  assert.throws(() => parseReleases("releases: []\n"));
});

test("reads the Zephyr version and manifest path from workspace files", () => {
  const version = "VERSION_MAJOR = 4\nVERSION_MINOR = 5\nPATCHLEVEL = 0\nVERSION_TWEAK = 0\nEXTRAVERSION =\n";
  assert.equal(parseZephyrVersion(version), "v4.5.0");
  assert.equal(parseZephyrVersion(version.replace("EXTRAVERSION =", "EXTRAVERSION = rc1")), "v4.5.0-rc1");
  assert.equal(parseZephyrVersion("VERSION_MAJOR = 4\n"), undefined);
  assert.equal(parseManifestPath("[manifest]\npath = zephyr\nfile = west.yml\n\n[zephyr]\nbase = zephyr\n"), "zephyr");
  assert.equal(parseManifestPath("[zephyr]\npath = other\n[manifest]\npath = rtos\n"), "rtos");
  assert.equal(parseManifestPath(""), "zephyr");
});

test("lists modules with blobs on disk and names cache files by sha256", () => {
  const sha = "a".repeat(64);
  const entries = parseBlobList(
    [
      `A hal_espressif ${sha} /ws/modules/hal/espressif/zephyr/blobs/lib/esp32c5/libble_app.a`,
      `M hal_silabs ${"b".repeat(64)} /ws path/modules/hal/silabs/zephyr/blobs/libbgcommon.a`,
      `D hal_nordic ${"c".repeat(64)} /ws/modules/hal/nordic/zephyr/blobs/lib.a`,
      "not a blob line",
    ].join("\n"),
  );
  assert.equal(entries.length, 3);
  assert.equal(entries[1].abspath, "/ws path/modules/hal/silabs/zephyr/blobs/libbgcommon.a");
  assert.deepEqual(modulesWithBlobs(entries), ["hal_espressif", "hal_silabs"]);
  assert.equal(blobCacheName(entries[0]), `libble_app.a.${sha}`);
});
