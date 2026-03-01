import MonacoEditor from '@monaco-editor/react';
import './CykaflexEditor.css';

/* ── Cykaflex language definition ─────────────────────────────── */

const KEYWORDS = [
  'clasedocumento', 'inicio', 'fin', 'documento',
  'titulopagina', 'capitulo', 'seccion', 'subseccion',
  'subsubseccion', 'texto', 'inicioe', 'inicioi',
  'ennumerar', 'itemizar', 'item', 'nuevapagina',
  'negrita', 'cursiva', 'articulo', 'libro', 'pt', 'cm',
];

function setupMonaco(monaco) {
  /* Idempotent — only register once per page load */
  if (monaco.languages.getLanguages().some(l => l.id === 'cykaflex')) return;

  monaco.languages.register({ id: 'cykaflex' });

  monaco.languages.setMonarchTokensProvider('cykaflex', {
    keywords: KEYWORDS,
    tokenizer: {
      root: [
        [/%[^\n]*/,          'comment'],               /* % comment */
        [/"[^"\n]*"/,        'string'],                /* "quoted content" */
        [/[0-9]+/,           'number'],                /* 12, 10, … */
        [/[a-zA-Z][a-zA-Z0-9]*/, {
          cases: { '@keywords': 'keyword', '@default': 'identifier' },
        }],
        [/[\[\]]/,           'delimiter.square'],      /* [ ] */
        [/[{}]/,             'delimiter.curly'],       /* { } */
      ],
    },
  });

  monaco.editor.defineTheme('cykaflex-retro', {
    base:    'vs',
    inherit: true,
    rules: [
      { token: 'keyword',          foreground: '000080', fontStyle: 'bold'   },
      { token: 'string',           foreground: '800000'                       },
      { token: 'comment',          foreground: '008000', fontStyle: 'italic'  },
      { token: 'number',           foreground: '000080'                       },
      { token: 'delimiter.square', foreground: '800080', fontStyle: 'bold'   },
      { token: 'delimiter.curly',  foreground: 'A05000', fontStyle: 'bold'   },
      { token: 'identifier',       foreground: 'AA0000'                       },
    ],
    colors: {
      'editor.background':                '#FFFFFF',
      'editor.foreground':                '#000000',
      'editor.lineHighlightBackground':   '#EEF0FF',
      'editor.lineHighlightBorder':       '#C8C8FF',
      'editorLineNumber.foreground':      '#A0A0A0',
      'editorLineNumber.activeForeground':'#000080',
      'editorCursor.foreground':          '#000000',
      'editor.selectionBackground':       '#000080',
      'editor.inactiveSelectionBackground':'#C0C0C0',
      'editorGutter.background':          '#F0F0F0',
    },
  });
}

/* ── Editor options (stable reference — defined outside component) */

const EDITOR_OPTIONS = {
  fontFamily:          '"Courier New", "Lucida Console", monospace',
  fontSize:            13,
  lineHeight:          19,
  lineNumbers:         'on',
  minimap:             { enabled: false },
  scrollBeyondLastLine: false,
  wordWrap:            'on',
  tabSize:             2,
  insertSpaces:        true,
  automaticLayout:     true,   /* reacts to container resize */
  renderWhitespace:    'none',
  smoothScrolling:     true,
  cursorStyle:         'block',
  cursorBlinking:      'phase',
  renderLineHighlight: 'all',
  overviewRulerLanes:  0,
  hideCursorInOverviewRuler: true,
  scrollbar: {
    verticalScrollbarSize:   14,
    horizontalScrollbarSize: 14,
  },
};

/* ── Component ─────────────────────────────────────────────────── */

export default function CykaflexEditor({ value, onChange }) {
  return (
    <div className="editor-shell deep-sunken">
      <MonacoEditor
        height="100%"
        language="cykaflex"
        value={value}
        theme="cykaflex-retro"
        beforeMount={setupMonaco}
        onChange={onChange}
        options={EDITOR_OPTIONS}
      />
    </div>
  );
}
