import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";

/**
 * OpenCode V2 plugin for Justify development workflow.
 * Provides non-destructive lifecycle awareness for change records during session events.
 */
export default {
  id: "justify.workflow",
  async setup(ctx) {
    if (ctx?.session?.hook) {
      try {
        ctx.session.hook("beforeCompaction", async (event) => {
          const changesDir = join(process.cwd(), "docs", "changes");
          if (existsSync(changesDir)) {
            const files = readdirSync(changesDir).filter(
              (f) => f.endsWith(".md") && f !== "README.md"
            );
            if (event && typeof event === "object") {
              event.activeChangeRecords = files;
            }
          }
        });
      } catch (_) {
        // Non-destructive fallback
      }
    }
  },
};
