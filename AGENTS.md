## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, invoke the `skill` tool with `skill: "graphify"` before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## Documentation

The project documentation is under docs/. It is organized in progressive layers:
- User guide: for end users of djdevx / ddx
- Developer guide: for contributors and maintainers extending the project

Rules:
- Read the relevant documentation before making changes to behavior, interfaces, CLI commands, or developer workflows.
- After modifying code, update the documentation as needed in both the user guide and developer guide.
- If you introduce or change a utility, command, API, config option, interface, or workflow, update the relevant docs and ensure the changes are reflected in the appropriate documentation pages.
- If a code change affects developer-facing conventions, architecture, or contribution practices, update docs/developer-guide/ as needed.
- If you add a new utility or interface, also review and update docs/developer-guide/code-standards.md to reflect the new standard or requirement.
- Do not leave implementation and documentation out of sync. If the code behavior changes, the docs must be updated before finalizing the work.

## Code standards

Rules:
- Always follow the standards defined in docs/developer-guide/code-standards.md.
- Do not invent new code standards or conventions without explicit user approval.
- When in doubt, follow the project's existing established patterns and documentation.
- Keep changes consistent with the repository's architecture, naming conventions, and testing practices.
- If a change introduces a new pattern or requirement, document it in the developer guide and update the code standards file when appropriate.
- This is important to keep in mind for all changes: simplicity, more maintainablity, separation of concerns, single responsibility per component, and plugin capability.
