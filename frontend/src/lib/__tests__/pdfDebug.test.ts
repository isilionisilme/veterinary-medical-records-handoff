import { describe, expect, it } from "vitest";
import { analyzeTransform } from "../pdfDebug";

describe("analyzeTransform", () => {
  it("returns neutral analysis for none", () => {
    expect(analyzeTransform("none")).toEqual({
      determinant: null,
      negativeDeterminant: false,
      hasMirrorScale: false,
    });
  });

  it("detects negative determinant on matrix transforms", () => {
    expect(analyzeTransform("matrix(-1, 0, 0, 1, 0, 0)")).toEqual({
      determinant: -1,
      negativeDeterminant: true,
      hasMirrorScale: true,
    });
  });

  it("calculates determinant for matrix3d transforms", () => {
    expect(analyzeTransform("matrix3d(2, 0, 0, 0, 0, 3, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)")).toEqual({
      determinant: 6,
      negativeDeterminant: false,
      hasMirrorScale: false,
    });
  });
});
