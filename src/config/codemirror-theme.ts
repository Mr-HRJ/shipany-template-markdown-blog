import { EditorView } from '@codemirror/view';
import { Extension } from '@codemirror/state';
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language';
import { tags as t } from '@lezer/highlight';

// mdnice 风格的颜色配置
const colors = {
  background: '#f5f5f5',
  foreground: '#202020',
  selection: '#b3d7ff',
  activeLine: '#dddcdc',
  cursor: '#505050',
  comment: '#ac002b',
  string: '#e46918',
  keyword: '#023a52',
  variable: '#90a959',
  link: '#b26a00',
  heading: '#202020',
};

// 编辑器主题
const mdMirrorTheme = EditorView.theme({
  '&': {
    fontSize: '14px',
    backgroundColor: colors.background,
  },
  '.cm-content': {
    caretColor: colors.cursor,
    padding: '20px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif',
  },
  '.cm-cursor, .cm-dropCursor': {
    borderLeftColor: colors.cursor,
  },
  '&.cm-focused .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection': {
    backgroundColor: colors.selection,
  },
  '.cm-activeLine': {
    backgroundColor: colors.activeLine,
  },
  '.cm-gutters': {
    backgroundColor: colors.background,
    color: '#b0b0b0',
    border: 'none',
  },
  '.cm-activeLineGutter': {
    backgroundColor: colors.activeLine,
  },
  '.cm-line': {
    wordBreak: 'break-all',
  },
});

// 语法高亮
const mdMirrorHighlight = HighlightStyle.define([
  { tag: t.heading, color: colors.heading, fontWeight: '700' },
  { tag: t.heading1, fontSize: '1.5em' },
  { tag: t.heading2, fontSize: '1.3em' },
  { tag: t.heading3, fontSize: '1.1em' },
  { tag: t.strong, fontWeight: '700', color: colors.heading },
  { tag: t.emphasis, fontStyle: 'italic' },
  { tag: t.link, color: colors.link, textDecoration: 'underline' },
  { tag: t.url, color: colors.link },
  { tag: t.monospace, color: colors.string, backgroundColor: 'rgba(0,0,0,0.05)', padding: '2px 4px', borderRadius: '3px' },
  { tag: t.quote, color: colors.comment, fontStyle: 'italic' },
  { tag: t.comment, color: colors.comment },
  { tag: t.string, color: colors.string },
  { tag: t.keyword, color: colors.keyword, fontWeight: '600' },
  { tag: t.variableName, color: colors.variable },
  { tag: t.propertyName, color: colors.variable },
  { tag: t.atom, color: '#aa759f' },
  { tag: t.number, color: '#aa759f' },
]);

export const mdMirrorExtension: Extension = [
  mdMirrorTheme,
  syntaxHighlighting(mdMirrorHighlight),
];
