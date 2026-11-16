import { u } from 'unist-builder';

import remarkHeadingId from './remark-heading-id.js';

function run(heading) {
  const tree = u('root', [heading]);
  remarkHeadingId()(tree);
  return tree.children[0];
}

describe('remark-heading-id', () => {
  it('remove o sufixo e fixa o id', () => {
    const node = run(
      u('heading', { depth: 2 }, [u('text', 'Criar um projeto {#create-a-project}')])
    );
    expect(node.children[0].value).toBe('Criar um projeto');
    expect(node.data.id).toBe('create-a-project');
    expect(node.data.hProperties.id).toBe('create-a-project');
  });

  it('mantém o texto antes do sufixo quando há código inline', () => {
    const node = run(
      u('heading', { depth: 2 }, [u('inlineCode', 'foo'), u('text', ' é legal {#the-foo-is-cool}')])
    );
    expect(node.children).toHaveLength(2);
    expect(node.children[1].value).toBe(' é legal');
    expect(node.data.id).toBe('the-foo-is-cool');
  });

  it('não mexe em título sem sufixo', () => {
    const node = run(u('heading', { depth: 2 }, [u('text', 'Plain title')]));
    expect(node.data).toBeUndefined();
    expect(node.children[0].value).toBe('Plain title');
  });
});
