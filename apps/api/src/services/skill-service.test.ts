import { describe, expect, it } from "vitest";
import { buildSkillSetupFiles } from "./skill-service.js";

describe("buildSkillSetupFiles", () => {
  it("mirrors each custom skill into Claude and Codex setup paths", () => {
    const files = buildSkillSetupFiles([
      {
        id: "skill-1",
        name: "Spec Issue Draft",
        description: "Generate a GitHub issue draft from a spec doc",
        prompt: "Read the linked spec and draft the issue body.",
        scope: "global",
        repoUrl: null,
        workspaceId: null,
        enabled: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      },
    ]);

    expect(files).toHaveLength(2);
    expect(files[0]).toEqual({
      path: ".claude/commands/Spec Issue Draft.md",
      content: "Read the linked spec and draft the issue body.",
    });
    expect(files[1].path).toBe(".codex/skills/spec-issue-draft/SKILL.md");
    expect(files[1].content).toContain('name: "Spec Issue Draft"');
    expect(files[1].content).toContain("# Spec Issue Draft");
  });
});
