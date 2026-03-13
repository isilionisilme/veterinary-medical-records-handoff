#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, "../..");
const frontendRoot = path.join(repoRoot, "frontend");
const srcRoot = path.join(frontendRoot, "src");

const HEX_RE = /#(?:[0-9a-fA-F]{3,8})\b/g;
const INLINE_STYLE_RE = /style\s*=\s*\{\{/g;
const ICON_BUTTON_NO_LABEL_RE = /<IconButton(?![^>]*\blabel\s*=)[^>]*>/g;
const RAW_HTML_BUTTON_RE = /<button\b([\s\S]*?)>([\s\S]*?)<\/button>/g;
const RAW_DS_BUTTON_RE = /<Button\b([\s\S]*?)>([\s\S]*?)<\/Button>/g;
const TOOLTIP_PRIMITIVE_BYPASS_RE = /@radix-ui\/react-tooltip|TooltipPrimitive\./g;

const HEX_ALLOWLIST = new Set([
  path.join("frontend", "src", "index.css"),
  path.join("frontend", "tailwind.config.cjs"),
]);

const INLINE_STYLE_ALLOWLIST = new Map([
  [path.join("frontend", "src", "App.tsx"), ["style={reviewSplitLayoutStyle}", "style={{ top:"]],
]);

const ICON_ONLY_ALLOWLIST = new Map([
  [path.join("frontend", "src", "App.tsx"), ["data-testid=\"review-split-handle\""]],
  [path.join("frontend", "src", "components", "app", "IconButton.tsx"), ["<Button"]],
]);

const TOOLTIP_BYPASS_ALLOWLIST = new Set([
  path.join("frontend", "src", "components", "ui", "tooltip.tsx"),
]);

function readCssToken(cssContent, tokenName) {
  const tokenRegex = new RegExp(`${tokenName}\\s*:\\s*([^;]+);`);
  const match = cssContent.match(tokenRegex);
  return match ? match[1].trim() : "";
}

function walkFiles(dirPath) {
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry.name);
    if (entry.isDirectory()) {
      files.push(...walkFiles(fullPath));
      continue;
    }
    if (/\.(ts|tsx|js|jsx|css)$/.test(entry.name)) {
      files.push(fullPath);
    }
  }
  return files;
}

function relativeToRepo(filePath) {
  return path.relative(repoRoot, filePath);
}

function lineNumberAt(content, index) {
  return content.slice(0, index).split("\n").length;
}

function isAllowlisted(relativePath, snippet) {
  const allowTokens = ICON_ONLY_ALLOWLIST.get(relativePath) ?? [];
  return allowTokens.some((token) => snippet.includes(token));
}

function stripTagsAndExpressions(value) {
  return value
    .replace(/<[^>]+>/g, " ")
    .replace(/\{[^}]*\}/g, " ")
    .replace(/&[a-zA-Z]+;/g, " ")
    .replace(/[×✕ⓘ]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function looksIconOnly(innerContent) {
  const textContent = stripTagsAndExpressions(innerContent);
  const hasVisibleText = /[\p{L}\p{N}]/u.test(textContent);
  const hasIconLikeMarkup =
    /<svg\b/i.test(innerContent) ||
    /<[A-Z][A-Za-z0-9]*\b/.test(innerContent) ||
    /[×✕ⓘ]/u.test(innerContent);
  return hasIconLikeMarkup && !hasVisibleText;
}

function collectRawIconOnlyButtonViolations(relativePath, content, findings) {
  for (const match of content.matchAll(RAW_HTML_BUTTON_RE)) {
    const snippet = match[0];
    const innerContent = match[2] ?? "";
    if (!looksIconOnly(innerContent) || isAllowlisted(relativePath, snippet)) {
      continue;
    }
    findings.push(
      `${relativePath}:${lineNumberAt(content, match.index)} raw <button> appears icon-only; use <IconButton label=...> or document an allowlisted exception`
    );
  }

  for (const match of content.matchAll(RAW_DS_BUTTON_RE)) {
    const snippet = match[0];
    const attrs = match[1] ?? "";
    const innerContent = match[2] ?? "";
    if (/\basChild\b/.test(attrs) || !looksIconOnly(innerContent) || isAllowlisted(relativePath, snippet)) {
      continue;
    }
    findings.push(
      `${relativePath}:${lineNumberAt(content, match.index)} raw <Button> appears icon-only; use <IconButton label=...> or document an allowlisted exception`
    );
  }
}

const files = [
  ...walkFiles(srcRoot),
  path.join(frontendRoot, "tailwind.config.cjs"),
];

const findings = [];

const indexCssPath = path.join(frontendRoot, "src", "index.css");
const indexCssRelativePath = relativeToRepo(indexCssPath);
const indexCssContent = fs.readFileSync(indexCssPath, "utf8");
const surfaceTokenValue = readCssToken(indexCssContent, "--surface");
const surfaceMutedTokenValue = readCssToken(indexCssContent, "--surface-muted");

if (!surfaceTokenValue) {
  findings.push(`${indexCssRelativePath}: missing --surface token definition`);
}

if (!surfaceMutedTokenValue) {
  findings.push(`${indexCssRelativePath}: missing --surface-muted token definition`);
}

if (surfaceTokenValue && surfaceMutedTokenValue && surfaceTokenValue === surfaceMutedTokenValue) {
  findings.push(
    `${indexCssRelativePath}: --surface-muted must differ from --surface to preserve A0 container contrast`
  );
}

for (const filePath of files) {
  const relativePath = relativeToRepo(filePath);
  const content = fs.readFileSync(filePath, "utf8");

  if (!HEX_ALLOWLIST.has(relativePath)) {
    const hexMatches = [...content.matchAll(HEX_RE)];
    for (const match of hexMatches) {
      findings.push(
        `${relativePath}:${lineNumberAt(content, match.index)} hard-coded hex color ${match[0]} outside token allowlist`
      );
    }
  }

  const styleMatches = [...content.matchAll(INLINE_STYLE_RE)];
  if (styleMatches.length > 0) {
    const allowTokens = INLINE_STYLE_ALLOWLIST.get(relativePath) ?? [];
    for (const match of styleMatches) {
      const start = Math.max(0, match.index - 40);
      const end = Math.min(content.length, match.index + 80);
      const snippet = content.slice(start, end);
      const allowed = allowTokens.some((token) => snippet.includes(token));
      if (!allowed) {
        findings.push(
          `${relativePath}:${lineNumberAt(content, match.index)} inline style={{...}} is not allow-listed`
        );
      }
    }
  }

  const iconButtonMatches = [...content.matchAll(ICON_BUTTON_NO_LABEL_RE)];
  for (const match of iconButtonMatches) {
    findings.push(
      `${relativePath}:${lineNumberAt(content, match.index)} IconButton missing required label`
    );
  }

  collectRawIconOnlyButtonViolations(relativePath, content, findings);

  if (!TOOLTIP_BYPASS_ALLOWLIST.has(relativePath)) {
    for (const match of content.matchAll(TOOLTIP_PRIMITIVE_BYPASS_RE)) {
      findings.push(
        `${relativePath}:${lineNumberAt(content, match.index)} tooltip implementation bypasses shared Tooltip wrapper`
      );
    }
  }
}

if (findings.length > 0) {
  console.error("Design system check failed:");
  for (const finding of findings) {
    console.error(`- ${finding}`);
  }
  process.exit(1);
}

console.log("Design system check passed.");
