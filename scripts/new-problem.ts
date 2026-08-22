/**
 * Scaffold a new problem from content/_template.
 *
 *   pnpm new-problem rope-apply
 *
 * Fills in the slug and the next free id, leaves status as "draft" so the
 * half-written problem never reaches the site -- but content CI still runs its
 * tests, so it cannot rot either.
 */
import { cpSync, existsSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const PROBLEMS = join(ROOT, "content", "problems");
const TEMPLATE = join(ROOT, "content", "_template");

const slug = process.argv[2];

if (!slug) {
  console.error("usage: pnpm new-problem <slug>");
  process.exit(1);
}

if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(slug)) {
  console.error(`"${slug}" is not kebab-case. Try something like "rope-apply".`);
  process.exit(1);
}

const dir = join(PROBLEMS, slug);
if (existsSync(dir)) {
  console.error(`content/problems/${slug} already exists`);
  process.exit(1);
}

const nextId =
  readdirSync(PROBLEMS, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && !entry.name.startsWith("_"))
    .map((entry) => {
      const meta = join(PROBLEMS, entry.name, "meta.json");
      if (!existsSync(meta)) return 0;
      return Number(JSON.parse(readFileSync(meta, "utf8")).id) || 0;
    })
    .reduce((max, id) => Math.max(max, id), 0) + 1;

cpSync(TEMPLATE, dir, { recursive: true });

const metaPath = join(dir, "meta.json");
const title = slug
  .split("-")
  .map((word) => word[0].toUpperCase() + word.slice(1))
  .join(" ");

writeFileSync(
  metaPath,
  readFileSync(metaPath, "utf8").replace('"SLUG"', `"${slug}"`).replace('"TITLE"', `"${title}"`).replace('"id": 0', `"id": ${nextId}`),
);

console.log(`created content/problems/${slug} (id ${nextId}, status draft)

next:
  1. write tests.py first -- the tests are the product
  2. write solution.py until they pass, starter.py so they don't
  3. python python/test_problem.py ${slug}
  4. flip status to "published" in meta.json`);
