import { describe, expect, it } from "vitest";
import { extractSpecRefFromIssueBody } from "./issues.js";

describe("extractSpecRefFromIssueBody", () => {
  it("extracts a primary spec line from generated issue drafts", () => {
    const body = [
      "## Related Context",
      "",
      "- Primary spec: `docs/specs/operator-bootstrap-and-cluster-access.md`",
    ].join("\n");

    expect(extractSpecRefFromIssueBody(body)).toBe(
      "docs/specs/operator-bootstrap-and-cluster-access.md",
    );
  });

  it("extracts a generic Spec line", () => {
    const body = [
      "## Artifact Chain",
      "",
      "- Issue: `#123`",
      "- Spec: `docs/specs/runtime-change.md`",
    ].join("\n");

    expect(extractSpecRefFromIssueBody(body)).toBe("docs/specs/runtime-change.md");
  });

  it("returns undefined when the issue body does not link a spec", () => {
    expect(extractSpecRefFromIssueBody("## Summary\n\nNo spec here.")).toBeUndefined();
  });
});
