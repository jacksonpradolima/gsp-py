---
mode: agent
---
You are tasked with generating a commit message based on a git diff and following conventional commits specification. The git diff will be provided to you, and your job is to analyze the changes and create an appropriate, concise, and informative commit message.

Don't summarize or cut short content. If you run out of tokens, then please, wait for me to say 'Go' to continue generating content.
To generate an effective commit message, follow these steps:

1. Analyze the diff carefully, noting:
- Which files were modified
- The nature of the changes (additions, deletions, modifications)
- Any significant code or content changes
2. Summarize the main purpose of the changes in a brief (50-72 characters) title line.
3. If necessary, provide more detailed explanations in the body of the commit message, with each point on a new line prefixed by a hyphen (-).
4. Focus on explaining the "why" behind the changes, not just the "what".
5. Use the imperative mood for the title (e.g., "Add feature" instead of "Added feature").
6. If the changes are related to a specific issue or ticket, include the reference (e.g., "Fixes #123").
7. Output the result as a **shell command** like this:
git commit -F - <<'MSG'

<your commit message here>

MSG

Structure your commit message as follows:
```
Title line

- Detailed explanation point 1
- Detailed explanation point 2
- ...
```

<example_diff>
diff --git a/README.md b/README.md
index c1788657b95998a2f177a4f86d68a60f2a80117f..da818fca1c2742de5ef4090cb440d92c11d41ae7 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -6,7 +6,7 @@ Hello world
Unchanged line

-Removed line
+Added line

## Another unchanged line
</example_diff>

<example_commit_message>
docs: Updated README.md

- Changed `Removed line` to `Added line`
</example_commit_message>

Only return the commit message.

<git_diff>
```
%<diff>s
```
</git_diff>
