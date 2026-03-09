import fs from 'node:fs/promises';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import markdownLinkCheck from 'markdown-link-check';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, '../..');

const roots = [
  path.join(repoRoot, 'docs', 'README.md'),
  path.join(repoRoot, 'docs', 'projects'),
  path.join(repoRoot, 'docs', 'shared'),
];

function parseArgs(argv) {
  const args = { baseRef: null };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--base-ref') {
      args.baseRef = argv[i + 1] ?? null;
      i += 1;
    }
  }
  return args;
}

function changedMarkdownFiles(baseRef) {
  const run = (gitArgs) => {
    const out = execFileSync('git', gitArgs, {
      cwd: repoRoot,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    return out
      .split(/\r?\n/)
      .map((line) => line.trim().replaceAll('\\', '/'))
      .filter(Boolean);
  };

  const changed = new Set([
    ...run(['diff', '--name-only', '--diff-filter=ACMR', `${baseRef}...HEAD`]),
    ...run(['diff', '--name-only', '--diff-filter=ACMR']),
    ...run(['diff', '--cached', '--name-only', '--diff-filter=ACMR']),
  ]);

  return [...changed]
    .filter((relPath) => relPath.endsWith('.md'))
    .filter((relPath) => relPath === 'docs/README.md' || relPath.startsWith('docs/projects/') || relPath.startsWith('docs/shared/'))
    .map((relPath) => path.join(repoRoot, relPath));
}

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
  const { baseRef } = parseArgs(process.argv.slice(2));
  let files = [];

  if (baseRef) {
    files = changedMarkdownFiles(baseRef).sort((left, right) => left.localeCompare(right));
  } else {
    const filesNested = await Promise.all(roots.map((targetPath) => collectMarkdownFiles(targetPath)));
    files = filesNested.flat().sort((left, right) => left.localeCompare(right));
  }

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
