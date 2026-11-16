import fs from 'node:fs';
import path from 'node:path';

/**
 * Convenção da tradução: a ÚLTIMA linha do .mdx é o marcador `ia-translate: true` (comentário MDX).
 * Este módulo lista as páginas de docs/pages (fora de ja/ e versions/) que ainda não
 * têm o marcador, para o site mostrar o aviso "ainda em inglês".
 */
export const TRANSLATION_MARKER = '{/* ia-translate: true */}';
const EXCLUDED_DIRECTORIES = new Set(['ja', 'versions']);

function* walk(directory, pagesDirectory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const fullPath = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      if (directory === pagesDirectory && EXCLUDED_DIRECTORIES.has(entry.name)) {
        continue;
      }
      yield* walk(fullPath, pagesDirectory);
    } else if (entry.name.endsWith('.mdx')) {
      yield fullPath;
    }
  }
}

export function isTranslated(content) {
  const lines = content.split('\n').filter(line => line.trim() !== '');
  return lines.length > 0 && lines.at(-1).trim() === TRANSLATION_MARKER;
}

function toRoute(relativeFile) {
  const route = '/' + relativeFile.replace(/\.mdx$/, '').replace(/(^|\/)index$/, '');
  return route === '/' ? '/' : route.replace(/\/$/, '');
}

/** @returns {{ pages: Record<string, string> }} rota do Next -> arquivo relativo a docs/pages */
export function getTranslationStatus(
  pagesDirectory = path.join(import.meta.dirname, '..', 'pages')
) {
  const pages = {};
  for (const file of [...walk(pagesDirectory, pagesDirectory)].sort()) {
    if (!isTranslated(fs.readFileSync(file, 'utf8'))) {
      const relativeFile = path.relative(pagesDirectory, file).split(path.sep).join('/');
      pages[toRoute(relativeFile)] = relativeFile;
    }
  }
  return { pages };
}
