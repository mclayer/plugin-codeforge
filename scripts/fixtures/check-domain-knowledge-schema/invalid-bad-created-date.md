---
type: domain-knowledge
area: test-area
topic_slug: invalid-bad-created-date
title: Invalid fixture — created field not ISO date format
status: Active
tags:
  - test
  - fixture
created: 09/May/2026
updated: 2026-05-09
---

# Invalid fixture — bad created date

## Summary

This file has a `created` field that is not in YYYY-MM-DD ISO date format.

## Pattern

Schema violation: created date format wrong.

## Usage

Use this fixture in `test-check-domain-knowledge-schema.sh` T6 (bad created date).
