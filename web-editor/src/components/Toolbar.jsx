import { useRef } from 'react';
import './Toolbar.css';

export default function Toolbar({ status, result, format, onFormatChange, onDownload, onSaveSource, hasSource, filename, setFilename, handleFileUpload }) {
  const fileInputRef = useRef(null);
  const canDownload = !!(result?.url || result?.psText);

  const statusConfig = {
    idle:      { icon: '○', label: 'Listo',            cls: ''                    },
    compiling: { icon: '◌', label: 'Compilando...',    cls: 'toolbar-st--compiling' },
    ok:        { icon: '●', label: 'OK',               cls: 'toolbar-st--ok'      },
    error:     { icon: '✕', label: 'Error',            cls: 'toolbar-st--error'   },
  }[status] ?? { icon: '○', label: 'Listo', cls: '' };

  return (
    <header className="toolbar raised">
      {/* ── Logo & title ── */}
      <div className="toolbar-brand">
        <span className="toolbar-logo" aria-hidden="true">◆</span>
        <span className="toolbar-name">CYKAFLEX</span>
        <span className="toolbar-sub">Editor v0.3</span>
      </div>

      <div className="toolbar-divider" />

      {/* ── Controls ── */}
      <div className="toolbar-controls">
        {/* Format selector */}
        <label className="toolbar-field">
          <span>Formato:</span>
          <select
            className="toolbar-select sunken"
            value={format}
            onChange={e => onFormatChange(e.target.value)}
          >
            <option value="auto">Auto</option>
            <option value="pdf">PDF</option>
            <option value="ps">PostScript</option>
          </select>
        </label>

        {/* Hidden file input — triggered by the open button */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".cyk"
          style={{ display: 'none' }}
          onChange={handleFileUpload}
        />

        {/* Open .cyk file */}
        <button
          className="btn"
          onClick={() => fileInputRef.current?.click()}
          title="Abrir un archivo .cyk desde el disco"
        >
          📂 Abrir .cyk
        </button>

        {/* Filename */}
        <label className="toolbar-field">
          <span>Nombre:</span>
          <input
            type="text"
            className="toolbar-input sunken"
            maxLength={50}
            placeholder="documento"
            value={filename}
            onChange={e => setFilename(e.target.value)}
            title="Nombre base para guardar / descargar archivos"
          />
        </label>

        {/* Save source */}
        <button
          className="btn"
          onClick={onSaveSource}
          disabled={!hasSource}
          title={hasSource ? 'Guardar código fuente como .cyk' : 'El editor está vacío'}
        >
          💾 Guardar .cyk
        </button>

        {/* Download compiled output */}
        <button
          className="btn"
          onClick={onDownload}
          disabled={!canDownload}
          title={canDownload ? 'Descargar documento compilado' : 'Sin documento compilado'}
        >
          ▼ Descargar Salida
        </button>
      </div>

      <div className="toolbar-divider" />

      {/* ── Status chip ── */}
      <div className={`toolbar-status ${statusConfig.cls}`}>
        <span className="toolbar-status-icon">{statusConfig.icon}</span>
        <span>{statusConfig.label}</span>
      </div>
    </header>
  );
}
