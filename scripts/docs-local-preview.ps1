param(
    [string]$WikiDir = "tmp/wiki-preview",
    [int]$Port = 6065,
    [string]$Repo = "isilionisilme/veterinary-medical-records",
    [string]$Ref = "HEAD",
    [switch]$NoServe,
    [switch]$OpenBrowser
)

$ErrorActionPreference = "Stop"

function Get-ListeningPids {
  param([int]$TargetPort)

  $pids = @()

  try {
    $conns = Get-NetTCPConnection -LocalPort $TargetPort -State Listen -ErrorAction SilentlyContinue
    if ($null -ne $conns) {
      $pids += ($conns | Select-Object -ExpandProperty OwningProcess -Unique)
    }
  } catch {
  }

  try {
    $pattern = ":$TargetPort"
    $lines = netstat -ano -p tcp | Select-String $pattern
    foreach ($line in $lines) {
      $parts = ($line.ToString() -replace "\s+", " ").Trim().Split(" ")
      if ($parts.Length -ge 5 -and $parts[3] -eq "LISTENING") {
        $pidCandidate = 0
        if ([int]::TryParse($parts[4], [ref]$pidCandidate)) {
          $pids += $pidCandidate
        }
      }
    }
  } catch {
  }

  return ($pids | Where-Object { $_ -gt 0 } | Select-Object -Unique)
}

function Stop-PortListeners {
  param([int]$TargetPort)

  $pids = Get-ListeningPids -TargetPort $TargetPort
  if ($pids.Count -eq 0) {
    return
  }

  foreach ($targetPid in $pids) {
    try {
      $proc = Get-Process -Id $targetPid -ErrorAction Stop
      Write-Host "[3/3] Stopping existing process on port ${TargetPort}: $($proc.ProcessName) (PID $targetPid)"
      Stop-Process -Id $targetPid -Force -ErrorAction Stop
    } catch {
      Write-Warning "Could not stop process with PID $targetPid on port ${TargetPort}: $($_.Exception.Message)"
      try {
        taskkill /PID $targetPid /F | Out-Null
      } catch {
      }
    }
  }

  $maxWaitMs = 5000
  $intervalMs = 200
  $elapsed = 0
  while ($elapsed -lt $maxWaitMs) {
    $remaining = Get-ListeningPids -TargetPort $TargetPort
    if ($remaining.Count -eq 0) {
      return
    }
    Start-Sleep -Milliseconds $intervalMs
    $elapsed += $intervalMs
  }

  throw "Port $TargetPort is still in LISTEN state after kill attempts."
}

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$wikiPath = Join-Path $repoRoot $WikiDir
New-Item -ItemType Directory -Force -Path $wikiPath | Out-Null

Write-Host "[1/3] Generating wiki snapshot from local docs..."
python scripts/sync_docs_to_wiki.py --wiki-dir $wikiPath --repo $Repo --ref $Ref

$pages = Get-ChildItem -Path $wikiPath -Filter *.md |
  Where-Object { $_.Name -notlike '_*.md' } |
  Sort-Object Name |
  ForEach-Object { [System.IO.Path]::GetFileNameWithoutExtension($_.Name) }

$pagesJson = ($pages | ConvertTo-Json)
Set-Content -Path (Join-Path $wikiPath "pages.json") -Value $pagesJson -Encoding UTF8

$indexHtml = @'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Local Wiki Preview</title>
  <style>
    body { margin:0; font-family: Segoe UI, Roboto, Arial, sans-serif; background:#0f172a; color:#e2e8f0; }
    .wrap { display:grid; grid-template-columns:320px 1fr; height:100vh; }
    aside { border-right:1px solid #334155; overflow:auto; padding:16px; background:#111827; }
    main { overflow:auto; padding:24px; }
    h1,h2,h3 { color:#f8fafc; }
    a { color:#93c5fd; text-decoration:none; }
    a:hover { text-decoration:underline; }
    ul { margin:0; padding-left:20px; }
    .top { display:flex; align-items:center; gap:12px; margin-bottom:12px; }
    .badge { font-size:12px; border:1px solid #334155; border-radius:999px; padding:2px 8px; color:#cbd5e1; }
    .crumbs { font-size:12px; color:#94a3b8; margin-bottom:16px; }
    pre { background:#0b1220; border:1px solid #334155; padding:12px; overflow:auto; border-radius:8px; }
    code { background:#0b1220; border:1px solid #334155; padding:1px 4px; border-radius:4px; }
    table { border-collapse: collapse; width:100%; }
    th, td { border:1px solid #334155; padding:6px 8px; text-align:left; }
    blockquote { border-left:3px solid #334155; margin:12px 0; padding:8px 12px; color:#cbd5e1; background:#0b1220; }
  </style>
</head>
<body>
  <div class="wrap">
    <aside>
      <div class="top">
        <strong>Wiki Preview</strong>
        <span class="badge">local</span>
      </div>
      <div style="margin: 0 0 10px 0;">
        <input id="filter" placeholder="Filter pages..." style="width:100%;padding:8px;border:1px solid #334155;border-radius:6px;background:#0b1220;color:#e2e8f0;" />
      </div>
      <div id="sidebar">Loading sidebar...</div>
      <hr style="border-color:#334155; margin: 16px 0;" />
      <div>
        <strong style="font-size:13px; color:#cbd5e1;">All pages</strong>
        <div id="all-pages" style="margin-top:8px;"></div>
      </div>
    </aside>
    <main>
      <div class="crumbs" id="crumbs">/</div>
      <article id="content">Loading page...</article>
    </main>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script>
    const DEFAULT_PAGE = 'Home';

    function pageFromHash() {
      const h = location.hash.replace(/^#/, '').trim();
      return h || DEFAULT_PAGE;
    }

    function setCrumbs(page) {
      document.getElementById('crumbs').textContent = `/${page}`;
    }

    function convertWikiLinks(md) {
      md = md.replace(/\[\[([^\]|]+)\|([^\]]+)\]\]/g, (_, page, label) => `[${label}](#${encodeURIComponent(page)})`);
      md = md.replace(/\[\[([^\]]+)\]\]/g, (_, page) => `[${page}](#${encodeURIComponent(page)})`);
      md = md.replace(/\(https:\/\/github\.com\/[^)]+\/wiki\/([^\)#]+)(?:#[^)]*)?\)/g, (_, page) => `(#${encodeURIComponent(decodeURIComponent(page))})`);
      return md;
    }

    async function loadPage(page) {
      const file = `${decodeURIComponent(page)}.md`;
      try {
        const res = await fetch(file);
        if (!res.ok) throw new Error('Page not found');
        let md = await res.text();
        md = convertWikiLinks(md);
        const html = marked.parse(md, { mangle: false, headerIds: true });
        document.getElementById('content').innerHTML = html;
        setCrumbs(decodeURIComponent(page));
      } catch (err) {
        document.getElementById('content').innerHTML = `<h2>Page not found</h2><p>${file}</p>`;
      }
    }

    async function loadSidebar() {
      try {
        const res = await fetch('_Sidebar.md');
        const md = await res.text();
        const html = marked.parse(convertWikiLinks(md));
        document.getElementById('sidebar').innerHTML = html;
      } catch {
        document.getElementById('sidebar').textContent = 'Sidebar not found';
      }
    }

    function renderAllPages(pages, query = '') {
      const q = query.trim().toLowerCase();
      const filtered = pages.filter(p => !q || p.toLowerCase().includes(q));
      const html = ['<ul>'];
      for (const p of filtered) {
        html.push(`<li><a href="#${encodeURIComponent(p)}">${p}</a></li>`);
      }
      html.push('</ul>');
      document.getElementById('all-pages').innerHTML = html.join('');
    }

    async function loadAllPages() {
      try {
        const res = await fetch('pages.json');
        const pages = await res.json();
        renderAllPages(pages);
        const filter = document.getElementById('filter');
        filter.addEventListener('input', () => renderAllPages(pages, filter.value));
      } catch {
        document.getElementById('all-pages').textContent = 'Page index not available';
      }
    }

    window.addEventListener('hashchange', () => loadPage(pageFromHash()));

    (async () => {
      await loadSidebar();
      await loadAllPages();
      await loadPage(pageFromHash());
    })();
  </script>
</body>
</html>
'@

Set-Content -Path (Join-Path $wikiPath "index.html") -Value $indexHtml -Encoding UTF8
Write-Host "[2/3] Preview frontend generated at $wikiPath/index.html"

if ($NoServe) {
    Write-Host "[3/3] NoServe enabled. Open file manually: $wikiPath/index.html"
    exit 0
}

Stop-PortListeners -TargetPort $Port

if ($OpenBrowser) {
    Start-Process "http://localhost:$Port"
}

Write-Host "[3/3] Serving wiki preview on http://localhost:$Port"
python -m http.server $Port --directory $wikiPath
