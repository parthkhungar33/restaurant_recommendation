import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..", "..");
const designSrc = path.join(repoRoot, "design");
const designDest = path.resolve(__dirname, "..", "public", "design");

function main() {
  if (!fs.existsSync(designSrc)) {
    console.warn(`[sync-design] Skipped: no folder at ${designSrc}`);
    return;
  }
  fs.mkdirSync(designDest, { recursive: true });
  let n = 0;
  for (const name of fs.readdirSync(designSrc)) {
    if (!name.toLowerCase().endsWith(".png")) {
      continue;
    }
    fs.copyFileSync(path.join(designSrc, name), path.join(designDest, name));
    n += 1;
  }
  if (n) {
    console.log(`[sync-design] Copied ${n} mockup(s) to public/design`);
  }
}

main();
