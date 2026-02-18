# Business Requirements Document (BRD) for Tidy Obsidian Utility

## Summary

- Helps keep your markdown repo clean, free of obvious errors and duplicates.

## Objectives

- Highlight problematic areas that might disrupt plug-ins or tools for editing markdown.
- Help identify duplicate file names and blocks of content to keep markdown repo thin.

## Scope

## Requirements

## Stakeholders

- Subject-matter expert,
- Entrepreneurs and executives,
- Authors, writers, and speakers,

## Constraints

- Command line tools that work in a Kubernetes environment suitable to be ran against a Git repo using a scheduling agent. This is for big projects such as markdown training data for artificial intelligence (AI) large language models (LLM).
- Error logging status suitable for a Unix log reporting agent such as syslog server as collection point. For large repos the checks can be automated, then fixed by an assitant with the back end change control system.
    - Readable by Splunk Light, Nagios Log Server, or some other engine. Make it easy to sift, sort, and prioritize quality errors found in large markdown library.
- Focus on tools that help a typical subject-matter expert who might be using Obsidian, LogSeq, or Zettlr to do research. Start with structure, errors, and syntax.

/EOF/
