export const DEFAULT_PROMPT_TEMPLATE = `You are an autonomous coding agent. Your job is to WRITE CODE and open a pull request.

## Your Task

Read your task file at: {{TASK_FILE}}

This is a fresh implementation task. Your branch starts clean from main — there is
no existing PR and no prior work. You must write the code, not review it.

## Workflow

1. Read and understand the task file completely.
2. Follow every required repository instruction and linked artifact referenced in the task file before editing code.
3. Explore the codebase to understand the relevant code.
4. Implement the changes described in the task.
5. Write tests if the repository has a test suite.
6. Verify your changes compile and tests pass.
7. If the task file links a spec doc, update that spec so its \`## Plan\` checklist and \`Status\` reflect what this PR actually completes.
8. Update the PR body file at {{PR_BODY_FILE}} so it accurately describes the implementation, validation, and artifact chain.
9. Commit your work to the current branch ({{BRANCH_NAME}}).
10. Push and open a pull request using the \`gh\` CLI:
   \`\`\`
{{#if ISSUE_NUMBER}}   gh pr create --title "{{TASK_TITLE}}" --body "Closes #{{ISSUE_NUMBER}}"{{else}}   gh pr create --title "{{TASK_TITLE}}" --body "Implements task {{TASK_ID}}"{{/if}}
   \`\`\`
11. After opening the PR, you are done. Do NOT wait for CI checks or monitor them.
   The orchestration system handles CI monitoring and code review automatically.
{{#if AUTO_MERGE}}
   If CI passes and review is approved, the PR will be merged automatically.
{{/if}}

## Important

- You are a CODING agent, not a reviewer. Your job is to write and commit code.
- Your branch will be empty (identical to main) when you start. That is expected.
- Do NOT exit without making changes. If the task is unclear, make your best attempt.
- Do NOT look for existing PRs for this task — there are none. Create one.
- Do NOT skip repository instruction files or linked specs referenced in the task file.

## Environment Note
If this is the first task on this repo, you may need to install project dependencies
and build tools. Check if they're available before installing. Once installed, tools
persist for future tasks on this repo.

## Scope

You are task {{TASK_ID}} working on branch {{BRANCH_NAME}}. Other tasks may be running
concurrently on this same repository — each on its own branch. You MUST stay in scope:

- Do NOT look at, review, or interact with other PRs or branches.
- Do NOT run \`gh pr list\` to browse PRs. You only need to create YOUR PR.
- If you see references to other branches named \`optio/task-*\`, ignore them — those belong to other agents.
- Your working directory is your worktree. Do not navigate outside it.

## Guidelines

- Work only on what the task file describes. Do not refactor unrelated code.
- Follow the existing code style and conventions in this repository.
- If you get stuck or need information you don't have, stop and explain what you need.
- Do not modify CI/CD configuration unless the task specifically requires it.
`;

export const TASK_FILE_PATH = ".optio/task.md";
export const PR_BODY_FILE_PATH = ".optio/pr-body.md";

export const DEFAULT_REVIEW_PROMPT_TEMPLATE = `You are a code reviewer. You have been assigned to review exactly ONE pull request: PR #{{PR_NUMBER}}.

## IMPORTANT
- You are reviewing ONLY PR #{{PR_NUMBER}}. Do not look at, review, or comment on any other PRs.
- Do not fetch lists of open PRs. Your scope is strictly PR #{{PR_NUMBER}}.

## Steps

1. Read the diff for PR #{{PR_NUMBER}}:
   \`\`\`
   gh pr diff {{PR_NUMBER}}
   \`\`\`

2. Read the original task description to understand what this PR is supposed to accomplish:
   \`\`\`
   cat {{TASK_FILE}}
   \`\`\`

{{#if TEST_COMMAND}}
3. Run the test suite to verify the changes work:
   \`\`\`
   {{TEST_COMMAND}}
   \`\`\`
{{/if}}

4. Review the code changes in PR #{{PR_NUMBER}} for:
   - Correctness: Does it do what the task asked?
   - Tests: Are there tests for the new behavior?
   - Bugs: Any logic errors, edge cases, or regressions?
   - Security: Any vulnerabilities introduced?
   - Style: Does it follow the repo's conventions?

5. Submit your review for PR #{{PR_NUMBER}} using the GitHub CLI:
   - If the code is good: \`gh pr review {{PR_NUMBER}} --approve --body "Your review summary"\`
   - If changes are needed: \`gh pr review {{PR_NUMBER}} --request-changes --body "What needs fixing"\`

6. After submitting your review, you are done. Do not review any other PRs.

## Guidelines

- Review ONLY PR #{{PR_NUMBER}}. Nothing else.
- Do NOT modify any code, create commits, push changes, or check out branches.
- Do NOT run builds, install dependencies, or execute test suites.
- Your job is to READ the diff and submit a review. That's it.
- Only request changes for real issues, not style nitpicks.
- Be specific about what needs fixing and why.
- If the code correctly implements the task, approve it.
`;

export const REVIEW_TASK_FILE_PATH = ".optio/review-context.md";

/**
 * Render a prompt template by replacing {{VARIABLE}} placeholders.
 */
export function renderPromptTemplate(template: string, vars: Record<string, string>): string {
  let result = template;

  // Handle {{#if VAR}}...{{else}}...{{/if}} blocks
  result = result.replace(
    /\{\{#if\s+(\w+)\}\}([\s\S]*?)(?:\{\{else\}\}([\s\S]*?))?\{\{\/if\}\}/g,
    (_match, varName: string, ifBlock: string, elseBlock: string | undefined) => {
      const value = vars[varName];
      const truthy = value && value !== "false" && value !== "0";
      return truthy ? ifBlock : (elseBlock ?? "");
    },
  );

  // Handle simple {{VAR}} replacements
  result = result.replace(/\{\{(\w+)\}\}/g, (_match, varName: string) => {
    return vars[varName] ?? "";
  });

  return result.trim();
}

/**
 * Generate the task file content that gets written into the worktree.
 */
export function renderTaskFile(vars: {
  taskTitle: string;
  taskBody: string;
  taskId: string;
  ticketSource?: string;
  ticketUrl?: string;
  specRef?: string;
}): string {
  const parts = [
    `# ${vars.taskTitle}`,
    "",
    vars.taskBody,
    "",
    "## Required Repository Instructions",
    "",
    "- Read and follow `AGENTS.md`.",
    "- Read `CLAUDE.md` for product and runtime context.",
    "- Read `docs/process/feature-driven-development.md` for the issue/spec/task/PR workflow.",
  ];
  if (vars.specRef) {
    parts.push(`- Read and follow the primary spec: \`${vars.specRef}\`.`);
    parts.push(
      "- If this task implements part of that spec, update the spec's `## Plan` checklist and `Status` before opening the PR.",
    );
  }
  parts.push(
    "",
    "## Artifact Chain",
    "",
    `- Source issue: ${formatTicketSource(vars.ticketSource, vars.ticketUrl)}`,
    `- Primary spec: ${vars.specRef ? `\`${vars.specRef}\`` : "`N/A (no linked spec)`"}`,
    "",
    "---",
    `*Optio Task ID: ${vars.taskId}*`,
  );
  return parts.join("\n");
}

export function renderPrBodyFile(vars: {
  taskId: string;
  ticketSource?: string;
  ticketExternalId?: string;
  ticketUrl?: string;
  specRef?: string;
}): string {
  const issueRef = formatIssueReference(vars.ticketSource, vars.ticketExternalId);
  const closesLine =
    vars.ticketSource === "github" && vars.ticketExternalId
      ? `Closes #${vars.ticketExternalId}`
      : "<!-- Add a closing reference if this PR resolves a GitHub issue -->";
  const specRef = vars.specRef ? `\`${vars.specRef}\`` : "`N/A (no linked spec)`";
  const specClosure =
    vars.specRef != null
      ? `- [ ] Spec checklist/status updated in \`${vars.specRef}\``
      : "- [ ] Spec: `N/A (no linked spec)`";

  const parts = [
    "## Summary",
    "",
    "<!-- Replace this with the implementation summary before opening the PR. -->",
    "",
    "## Artifact Chain",
    "",
    `- Issue: ${issueRef}`,
    `- Spec: ${specRef}`,
    "",
    "## Changes",
    "",
    "<!-- Summarize the actual code and docs changes here. -->",
    "",
    "## Validation",
    "",
    "- [ ] Governance checks pass (`make governance-check`)",
    "- [ ] Full local gate passes (`make check`)",
    "- Commands run:",
    "- Additional evidence:",
    "",
    "## Closure",
    "",
    specClosure,
    "- [ ] Deferred or carry-over follow-ups moved to GitHub issues / project items",
    "- Follow-up issue(s):",
    "",
    "## Related",
    "",
    `- Optio task: \`${vars.taskId}\``,
  ];

  if (vars.ticketUrl) {
    parts.push(`- Source ticket URL: ${vars.ticketUrl}`);
  }
  parts.push(closesLine);
  return parts.join("\n") + "\n";
}

function formatIssueReference(ticketSource?: string, ticketExternalId?: string): string {
  if (ticketSource === "github" && ticketExternalId) {
    return `\`#${ticketExternalId}\``;
  }
  if (ticketSource && ticketExternalId) {
    return `\`N/A (${ticketSource} ticket ${ticketExternalId})\``;
  }
  return "`N/A (no linked GitHub issue)`";
}

function formatTicketSource(ticketSource?: string, ticketUrl?: string): string {
  if (ticketSource && ticketUrl) {
    return `[${ticketSource}](${ticketUrl})`;
  }
  if (ticketSource) {
    return `\`${ticketSource}\``;
  }
  return "`N/A (no linked source issue)`";
}
