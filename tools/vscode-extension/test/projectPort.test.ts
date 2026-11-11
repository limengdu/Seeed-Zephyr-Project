import * as assert from "node:assert/strict";
import { test } from "node:test";
import { decideProjectPort } from "../src/commands/projectSettings";

const portA = { device: "/dev/cu.usbmodemA", description: "Board A" };
const portB = { device: "/dev/cu.usbmodemB", description: "Board B" };

test("keeps a saved port when another device is the only one detected", () => {
  assert.deepEqual(decideProjectPort(portA.device, [portB], false), {
    kind: "keep",
    port: portA.device,
  });
});

test("keeps a saved port when no device is detected", () => {
  assert.deepEqual(decideProjectPort(portA.device, [], false), {
    kind: "keep",
    port: portA.device,
  });
});

test("assigns the only detected port when the project has no saved port", () => {
  assert.deepEqual(decideProjectPort(undefined, [portB], false), {
    kind: "assign",
    port: portB,
  });
});

test("opens the picker when Select Port is requested", () => {
  assert.deepEqual(decideProjectPort(portA.device, [portB], true), {
    kind: "choose",
  });
});

test("reports no port when nothing is saved and nothing is detected", () => {
  assert.deepEqual(decideProjectPort(undefined, [], false), {
    kind: "missing",
  });
});

test("opens the picker when several ports are detected and none is saved", () => {
  assert.deepEqual(decideProjectPort(undefined, [portA, portB], false), {
    kind: "choose",
  });
});
