import './ErrorConsole.css';

const TYPE_LABELS = {
  lex_error:    'ERROR LÉXICO',
  parse_error:  'ERROR SINTÁCTICO',
  server_error: 'ERROR DEL SERVIDOR',
  network_error:'ERROR DE RED',
};

export default function ErrorConsole({ error, open, onToggle }) {
  /* Render nothing when there is no active error */
  if (!error) return null;

  const label      = TYPE_LABELS[error.error_type] ?? 'ERROR';
  const hasLocation = error.line > 0;

  return (
    <div className="ec-root">
      {/* ── Title bar — always visible when there's an error ── */}
      <button className="ec-bar raised" onClick={onToggle} aria-expanded={open}>
        <span className="ec-led" aria-hidden="true" />
        <span className="ec-bar-title">
          CONSOLA — {label}
          {hasLocation && ` — Línea ${error.line}`}
          {hasLocation && error.col ? `, Col ${error.col}` : ''}
        </span>
        <span className="ec-toggle" aria-hidden="true">{open ? '▼' : '▲'}</span>
      </button>

      {/* ── Terminal body — slides in when open ── */}
      <div className={`ec-body ${open ? 'ec-body--open' : ''}`} aria-hidden={!open}>
        <div className="term-line">
          <span className="term-prompt">cykaflex:~$</span>
          <span className="term-cmd"> compile --source documento.cyk</span>
        </div>

        <div className="term-line term-err">
          <span className="term-badge">[{label}]</span>
          {hasLocation && (
            <span className="term-loc">
              {` línea ${error.line}${error.col ? `, pos ${error.col}` : ''}: `}
            </span>
          )}
          <span className="term-msg">{error.detail}</span>
        </div>

        <div className="term-line">
          <span className="term-prompt">cykaflex:~$</span>
          <span className="term-cursor" aria-hidden="true">█</span>
        </div>
      </div>
    </div>
  );
}
