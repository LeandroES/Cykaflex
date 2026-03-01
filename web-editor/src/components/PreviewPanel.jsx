import './PreviewPanel.css';

/* ── Empty / loading placeholders ─────────────────────────────── */

function Placeholder({ icon, title, hint }) {
  return (
    <div className="preview-placeholder">
      {icon && <div className="ph-icon" aria-hidden="true">{icon}</div>}
      <div className="ph-title">{title}</div>
      {hint && <div className="ph-hint">{hint}</div>}
    </div>
  );
}

/* ── PostScript raw viewer ─────────────────────────────────────── */

function PSViewer({ text }) {
  return (
    <div className="ps-viewer">
      <div className="ps-viewer-bar raised">
        <span>PostScript — Vista cruda</span>
        <span className="ps-badge">PS</span>
      </div>
      <pre className="ps-content">{text}</pre>
    </div>
  );
}

/* ── Main component ───────────────────────────────────────────── */

export default function PreviewPanel({ result, status }) {
  /* 1 — idle: no source typed yet */
  if (status === 'idle') {
    return (
      <div className="preview-shell deep-sunken preview-empty">
        <Placeholder
          icon="☐"
          title="Sin previsualización"
          hint="Escribe código Cykaflex para compilar automáticamente"
        />
      </div>
    );
  }

  /* 2 — first compile in progress, nothing to show yet */
  if (status === 'compiling' && !result) {
    return (
      <div className="preview-shell deep-sunken preview-empty">
        <Placeholder
          title={<>Compilando<span className="blink">_</span></>}
        />
      </div>
    );
  }

  /* 3 — error and no previous successful result */
  if (!result) {
    return (
      <div className="preview-shell deep-sunken preview-empty">
        <Placeholder
          icon="✕"
          title={<span style={{ color: '#800000' }}>Error de compilación</span>}
          hint="Consulta la consola inferior para más detalles"
        />
      </div>
    );
  }

  /* 4 — PDF result */
  if (result.url && result.mediaType.includes('pdf')) {
    return (
      <div className="preview-shell deep-sunken">
        <iframe
          src={result.url}
          className="preview-iframe"
          title="Vista previa del documento PDF"
        />
      </div>
    );
  }

  /* 5 — PostScript text result */
  if (result.psText) {
    return (
      <div className="preview-shell deep-sunken">
        <PSViewer text={result.psText} />
      </div>
    );
  }

  /* Fallback */
  return (
    <div className="preview-shell deep-sunken preview-empty">
      <Placeholder icon="?" title="Estado desconocido" />
    </div>
  );
}
