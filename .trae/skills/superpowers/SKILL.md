---
name: "superpowers"
description: "A complete software development workflow skill. Invoke when the user wants to start a new feature, plan development, or use the superpowers workflow (brainstorming, planning, TDD)."
---

# Superpowers

Superpowers is a complete software development workflow for your coding agents, built on top of a set of composable "skills" and some initial instructions that make sure your agent uses them.

## Core Workflow

The Superpowers workflow consists of several stages that should be followed in order:

1.  **Brainstorming**: Activates before writing code. Refines rough ideas through questions, explores alternatives, presents design in sections for validation.
2.  **Writing Plans**: Activates with approved design. Breaks work into bite-sized tasks (2-5 minutes each). Every task has exact file paths, complete code, verification steps.
3.  **Subagent Driven Development**: Activates with plan. Dispatches fresh subagent per task with two-stage review (spec compliance, then code quality), or executes in batches with human checkpoints.
4.  **Test Driven Development**: Activates during implementation. Enforces RED-GREEN-REFACTOR: write failing test, watch it fail, write minimal code, watch it pass, commit. Deletes code written before tests.
5.  **Requesting Code Review**: Activates between tasks. Reviews against plan, reports issues by severity. Critical issues block progress.
6.  **Finishing a Development Branch**: Activates when tasks complete. Verifies tests, presents options (merge/PR/keep/discard), cleans up worktree.

## Usage Instructions

### 1. Brainstorming (Design Phase)

When the user asks to build something new or modify a feature, start with brainstorming.

-   **Goal**: Tease out a clear specification from the user.
-   **Action**: Ask clarifying questions. Don't jump to coding.
-   **Output**: Present the design in chunks for the user to read and digest.
-   **Validation**: Wait for user sign-off on the design.

### 2. Writing Plans (Planning Phase)

After the design is approved, create an implementation plan.

-   **Goal**: Create a step-by-step guide for implementation.
-   **Content**:
    -   Bite-sized tasks (2-5 minutes execution time).
    -   Exact file paths.
    -   Verification steps for each task.
-   **Principles**: Emphasize TDD, YAGNI, and DRY.

### 3. Execution (Implementation Phase)

Once the plan is approved (user says "go"), start executing the tasks.

-   **Workflow**:
    -   **TDD**: Write a failing test first. Verify it fails. Write code to make it pass. Verify it passes. Refactor.
    -   **Review**: Inspect and review work after each task.
    -   **Loop**: Continue to the next task until the plan is complete.

### 4. Git Worktrees (Optional but Recommended)

For larger features, consider using git worktrees to isolate the workspace.

## Philosophy

-   **Test-Driven Development**: Write tests first, always.
-   **Systematic over ad-hoc**: Process over guessing.
-   **Complexity reduction**: Simplicity as primary goal.
-   **Evidence over claims**: Verify before declaring success.
