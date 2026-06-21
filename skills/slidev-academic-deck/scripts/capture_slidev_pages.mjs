#!/usr/bin/env node

import fs from 'node:fs/promises'
import path from 'node:path'
import { createRequire } from 'node:module'

const requireFromCwd = createRequire(path.join(process.cwd(), 'package.json'))
const requireFromScript = createRequire(import.meta.url)

function parseArgs(argv) {
  const args = {
    url: 'http://localhost:3030',
    pages: [],
    out: '/tmp/slidev-check',
    width: 1600,
    height: 900,
    wait: 900,
  }

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    const next = argv[i + 1]
    if (arg === '--url') {
      args.url = next
      i += 1
    } else if (arg === '--pages') {
      args.pages = next.split(',').map((value) => Number.parseInt(value.trim(), 10)).filter(Number.isFinite)
      i += 1
    } else if (arg === '--out') {
      args.out = next
      i += 1
    } else if (arg === '--width') {
      args.width = Number.parseInt(next, 10)
      i += 1
    } else if (arg === '--height') {
      args.height = Number.parseInt(next, 10)
      i += 1
    } else if (arg === '--wait') {
      args.wait = Number.parseInt(next, 10)
      i += 1
    } else if (arg === '--help' || arg === '-h') {
      args.help = true
    }
  }

  return args
}

function usage() {
  console.log(`Usage:
  capture_slidev_pages.mjs --url http://localhost:3030 --pages 3,4,7,10 --out /tmp/slidev-check

Options:
  --url      Slidev dev server URL. Default: http://localhost:3030
  --pages    Comma-separated 1-based slide numbers. Required.
  --out      Output directory. Default: /tmp/slidev-check
  --width    Viewport width. Default: 1600
  --height   Viewport height. Default: 900
  --wait     Milliseconds to wait after navigation. Default: 900`)
}

async function loadChromium() {
  for (const load of [requireFromCwd, requireFromScript]) {
    try {
      return load('playwright-chromium').chromium
    } catch {
      try {
        return load('playwright').chromium
      } catch {
        // Try the next resolver.
      }
    }
  }

  throw new Error('Could not load playwright-chromium or playwright. Run this from a Slidev project with Playwright installed.')
}

function slideUrl(baseUrl, page) {
  const clean = baseUrl.replace(/\/+$/, '')
  return `${clean}/${page}`
}

const args = parseArgs(process.argv.slice(2))

if (args.help || args.pages.length === 0) {
  usage()
  process.exit(args.help ? 0 : 1)
}

await fs.mkdir(args.out, { recursive: true })

const chromium = await loadChromium()
const browser = await chromium.launch({ headless: true })
const page = await browser.newPage({ viewport: { width: args.width, height: args.height } })

try {
  for (const slide of args.pages) {
    const target = slideUrl(args.url, slide)
    await page.goto(target, { waitUntil: 'networkidle' })
    await page.waitForTimeout(args.wait)
    const file = path.join(args.out, `slide-${String(slide).padStart(2, '0')}.png`)
    await page.screenshot({ path: file, fullPage: false })
    console.log(file)
  }
} finally {
  await browser.close()
}
