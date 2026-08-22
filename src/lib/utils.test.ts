import { describe, expect, it } from "vitest";

import { cn, formatClock, formatDuration, formatMs } from "./utils";

describe("cn", () => {
  it("merges conflicting tailwind classes, last wins", () => {
    expect(cn("px-2", "px-4")).toBe("px-4");
  });

  it("drops falsy values", () => {
    expect(cn("a", false, undefined, "b")).toBe("a b");
  });
});

describe("formatClock", () => {
  it.each([
    [0, "0:00"],
    [9, "0:09"],
    [60, "1:00"],
    [1490, "24:50"],
    [3600, "60:00"],
  ])("renders %i seconds as %s", (seconds, expected) => {
    expect(formatClock(seconds)).toBe(expected);
  });

  it("clamps negatives to zero rather than printing -1:-5", () => {
    expect(formatClock(-30)).toBe("0:00");
  });
});

describe("formatDuration", () => {
  it("keeps hundredths for a share string", () => {
    expect(formatDuration(84_210)).toBe("1:24.21");
  });

  it("pads the seconds", () => {
    expect(formatDuration(61_000)).toBe("1:01.00");
  });
});

describe("formatMs", () => {
  it("keeps one decimal under 10 ms, where test timings actually live", () => {
    expect(formatMs(0.42)).toBe("0.4 ms");
  });

  it("rounds above 10 ms", () => {
    expect(formatMs(212.6)).toBe("213 ms");
  });
});
