---
name: douyin-script-master
description: Use when another agent needs to generate or batch-produce Douyin talking-head scripts for creators using AI to improve efficiency and follower growth, with review roles, risk control, and rewrite loops.
---

# Douyin Script Master

## Overview

This is the single entry skill for Douyin talking-head script generation in this project.

Do not treat old batch files as the primary rule source. Use the companion files in this folder as the authoritative working set for generation, review, risk control, and rewrite.

## When to Use

- Another agent needs to generate one or more Douyin talking-head scripts
- The target account is a real-person creator using AI for writing or editing assistance
- The goal is not just plays, but stronger follow reasons and follower growth
- The workflow needs multi-role review, platform risk control, and rewrite loops

Do not use this skill for subtitle generation, video rendering, or post-processing. Those belong to `skills/video-editing`.

## Required Companion Files

Read these files in this folder before writing scripts:

1. `rule-pack.md`
2. `review-roles.md`
3. `risk-control.md`
4. `scoring-loop.md`
5. `prompt-template.md`

## Fixed Target

- Core audience: creators who want to build self-media accounts and use AI to improve efficiency and gain followers
- Delivery style: real-person talking-head videos
- AI boundary: AI helps with drafting, structuring, and editing efficiency; humans make the final judgment
- Primary goal order: stop > finish > save/comment > follow

## Standard Workflow

1. Lock one root problem for each script
2. Choose one preferred angle from the rule pack
3. Generate a full 1.5 minute script
4. Run structure review
5. Run Douyin risk review
6. Run 12 audience-role reviews
7. Run scoring review
8. If any critical gate fails, rewrite only the failing parts and review again

## Review Topology

If subagents are available, use this pattern per script:

- 1 generator
- 1 structure reviewer
- 1 risk reviewer
- 12 audience-role reviewers
- 1 scoring reviewer

If subagents are not available, simulate the same review order sequentially in one session.

## Hard Gates

A script is not formally usable unless all of the following are true:

- structure review: pass
- risk review: pass
- audience-role positive count: at least 8 of 12
- final score: at least 82 out of 100

## Rewrite Rule

When a script fails:

- point to the exact broken rule
- adjust only the failing section first
- do not fully rewrite from scratch unless the root problem itself is wrong
- re-run the failed review stages

## Output Expectation

Each delivered script should include:

- main title
- subtitle
- angle
- duration
- opening hook
- full script
- proof anchor
- AI boundary sentence
- closing CTA

## Final Note

This skill is the main reusable entry for other agents in this project.

If an agent asks which local skill to use for script generation, use:

- `C:\custom\project1\ideas\self-media\skills\script-writing\口播生成复用技能\SKILL.md`
