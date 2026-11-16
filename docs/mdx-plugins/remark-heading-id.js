import { visit } from 'unist-util-visit';

/**
 * @typedef {import('@types/mdast').Root} Root
 * @typedef {import('@types/mdast').Heading} Heading
 */

/**
 * Tradução: o título traduzido carrega o id do original no fim, para os links `#ancora`
 * continuarem valendo sem reescrita. No arquivo .mdx fica `## Criar um projeto \{#create-a-project}`
 * (a barra é necessária porque `{...}` solto é uma expressão no MDX).
 *
 * Este plugin remove o sufixo ` {#id}` do texto visível e fixa o id do heading
 * (`data.hProperties.id`, que o rehype-slug respeita; `data.id`, que o remark-export-headings
 * exporta). Precisa rodar ANTES do remark-export-headings.
 */
const SUFFIX = /\s*\{#([A-Za-z0-9_.:-]+)\}\s*$/;

export default function remarkHeadingId() {
  /** @param {Root} tree */
  return tree => {
    visit(tree, 'heading', (/** @type {Heading} */ node) => {
      const last = node.children.at(-1);
      if (last?.type !== 'text') {
        return;
      }
      const match = SUFFIX.exec(last.value);
      if (!match) {
        return;
      }
      last.value = last.value.slice(0, match.index);
      if (last.value === '') {
        node.children.pop();
      }
      node.data = {
        ...node.data,
        id: match[1],
        hProperties: { ...node.data?.hProperties, id: match[1] },
      };
    });
  };
}
