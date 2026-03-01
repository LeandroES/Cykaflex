import './StatusBar.css';

export default function StatusBar({ status, error, result }) {
  const stateMap = {
    idle:      { icon: '○', label: 'Listo',                 cls: ''            },
    compiling: { icon: '◌', label: 'Compilando...',         cls: 'sb--compiling' },
    ok:        { icon: '●', label: 'Compilado correctamente', cls: 'sb--ok'    },
    error:     { icon: '✕', label: 'Error de compilación',  cls: 'sb--error'   },
  };

  const { icon, label, cls } = stateMap[status] ?? stateMap.idle;

  const fmtLabel = result?.mediaType?.includes('pdf')
    ? 'PDF'
    : result?.mediaType
      ? 'PS'
      : '—';

  return (
    <footer className={`statusbar sunken ${cls}`}>
      {/* Compilation state */}
      <div className="sb-seg">
        <span>{icon}</span>
        <span>{label}</span>
      </div>

      {/* Error location */}
      {error?.line > 0 && (
        <div className="sb-seg sb-seg--error">
          Línea {error.line}{error.col ? `, Col ${error.col}` : ''}
        </div>
      )}

      <div className="sb-spacer" />

      {/* Output format */}
      <div className="sb-seg sb-seg--format">
        {fmtLabel}
      </div>

      {/* App label */}
      <div className="sb-seg">
        Cykaflex Editor 0.2.0
      </div>
    </footer>
  );
}
