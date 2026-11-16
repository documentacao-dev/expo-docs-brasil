import { isTranslated } from './translation-status.js';

describe(isTranslated, () => {
  test('aceita o marcador na última linha', () => {
    expect(isTranslated('---\ntitle: Oi\n---\n\nTexto.\n\n{/* ia-translate: true */}\n')).toBe(
      true
    );
  });

  test('ignora o marcador fora da última linha', () => {
    expect(isTranslated('{/* ia-translate: true */}\n\nTexto.\n')).toBe(false);
  });

  test('página sem marcador está em inglês', () => {
    expect(isTranslated('Text.\n')).toBe(false);
  });
});
