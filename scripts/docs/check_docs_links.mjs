import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import markdownLinkCheck from 'markdown-link-check';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, '../..');

const roots = [
  path.join(repoRoot, 'docs', 'README.md'),
  path.join(repoRoot, 'docs', 'project'),
  path.join(repoRoot, 'docs', 'shared'),
];

async function collectMarkdownFiles(targetPath) {
  const stats = await fs.stat(targetPath);
  if (stats.isFile()) {
    return targetPath.endsWith('.md') ? [targetPath] : [];
  }

  const entries = await fs.readdir(targetPath, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const fullPath = path.join(targetPath, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await collectMarkdownFiles(fullPath)));
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      files.push(fullPath);
    }
  }

  return files;
}

function runLinkCheck(filePath, markdownContent) {
  return new Promise((resolve) => {
    markdownLinkCheck(
      markdownContent,
      {
        baseUrl: pathToFileURL(path.dirname(filePath)).toString(),
        configFile: path.join(repoRoot, '.markdown-link-check.json'),
      },
      (error, results = []) => {
        if (error) {
          resolve({ filePath, error, broken: [] });
          return;
        }

        const broken = results.filter((result) => result.status === 'dead');
        resolve({ filePath, error: null, broken });
      },
    );
  });
}

async function main() {
  const filesNested = await Promise.all(roots.map((targetPath) => collectMarkdownFiles(targetPath)));
  const files = filesNested.flat().sort((left, right) => left.localeCompare(right));

  if (files.length === 0) {
    console.log('No markdown files found under canonical docs scope.');
    return;
  }

  let hasErrors = false;
  for (const filePath of files) {
    const markdownContent = await fs.readFile(filePath, 'utf8');
    const result = await runLinkCheck(filePath, markdownContent);
    const relativePath = path.relative(repoRoot, filePath).replaceAll('\\', '/');

    if (result.error) {
      hasErrors = true;
      console.error(`ERROR ${relativePath}: ${result.error.message}`);
      continue;
    }

    if (result.broken.length === 0) {
      console.log(`OK ${relativePath}`);
      continue;
    }

    hasErrors = true;
    console.error(`BROKEN ${relativePath}`);
    for (const brokenLink of result.broken) {
      console.error(`  - ${brokenLink.link} (${brokenLink.statusCode ?? 'no-status'})`);
    }
  }

  if (hasErrors) {
    process.exitCode = 1;
  }
}

await main();
