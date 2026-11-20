import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import process from 'node:process';

const ENTRY_NAME = 'entry.png';
const SOURCE_URL = new URL(`./${ENTRY_NAME}`, import.meta.url);
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const MAX_BYTES = 1048576;

function fail(reason: string): never {
  process.stderr.write(`main.ts: ${reason}\n`);
  process.exit(1);
}

function startsWithPngSignature(bytes: Buffer): boolean {
  if (bytes.length < PNG_SIGNATURE.length) return false;
  return PNG_SIGNATURE.equals(bytes.subarray(0, PNG_SIGNATURE.length));
}

function loadValidatedEntry(): Buffer {
  let source: Buffer;
  try {
    source = readFileSync(SOURCE_URL);
  } catch (error) {
    fail(`cannot read ${ENTRY_NAME}: ${(error as Error).message}`);
  }

  if (!startsWithPngSignature(source)) {
    fail(`${ENTRY_NAME} is not a PNG (bad signature)`);
  }
  if (source.length > MAX_BYTES) {
    fail(`${ENTRY_NAME} is ${source.length} bytes, over the ${MAX_BYTES} byte limit`);
  }
  return source;
}

function main(): void {
  const source = loadValidatedEntry();
  const destination = join(OUTPUT_DIR, ENTRY_NAME);

  try {
    mkdirSync(OUTPUT_DIR, { recursive: true });
    writeFileSync(destination, source);
  } catch (error) {
    fail(`cannot write ${destination}: ${(error as Error).message}`);
  }

  const written = readFileSync(destination);
  if (written.length !== source.length) {
    fail(`size mismatch after copy: wrote ${written.length}, expected ${source.length}`);
  }

  process.exit(0);
}

main();
