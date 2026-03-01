import { useState, useEffect, useRef, useCallback } from 'react';

import Toolbar        from './components/Toolbar';
import CykaflexEditor from './components/CykaflexEditor';
import PreviewPanel   from './components/PreviewPanel';
import ErrorConsole   from './components/ErrorConsole';
import StatusBar      from './components/StatusBar';
import { useCompile } from './hooks/useCompile';

import './App.css';

/* ── Starter document shown on first load ─────────────────────── */
const INITIAL_SOURCE = `clasedocumento[12pt]{articulo}
inicio{documento}
titulopagina[negrita]{"Mi Documento Cykaflex"}
texto{"Bienvenido al editor Cykaflex."}
texto{"Este documento se compila automaticamente."}
fin{documento}
`;

/* ── Root component ───────────────────────────────────────────── */

export default function App() {
  const [source,      setSource]      = useState(INITIAL_SOURCE);
  const [format,      setFormat]      = useState('auto');
  const [splitPos,    setSplitPos]    = useState(50);   /* % */
  const [consoleOpen, setConsoleOpen] = useState(false);

  const containerRef = useRef(null);
  const draggingRef  = useRef(false);

  const { result, compileError, status } = useCompile(source, format);

  /* Auto-open error console whenever a new compile error arrives */
  useEffect(() => {
    if (compileError) setConsoleOpen(true);
  }, [compileError]);

  /* ── Split-pane drag ────────────────────────────────────────── */

  const handleDividerMouseDown = useCallback((e) => {
    e.preventDefault();
    draggingRef.current = true;
    document.body.style.cursor     = 'col-resize';
    document.body.style.userSelect = 'none';

    const onMouseMove = (ev) => {
      if (!draggingRef.current || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const pct  = ((ev.clientX - rect.left) / rect.width) * 100;
      setSplitPos(Math.max(20, Math.min(80, pct)));
    };

    const onMouseUp = () => {
      draggingRef.current = false;
      document.body.style.cursor     = '';
      document.body.style.userSelect = '';
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup',   onMouseUp);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup',   onMouseUp);
  }, []);

  /* ── Save source ────────────────────────────────────────────── */

  const handleSaveSource = useCallback(() => {
    const blob = new Blob([source], { type: 'text/plain;charset=utf-8' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = 'documento.cyk';
    a.click();
    URL.revokeObjectURL(url);
  }, [source]);

  /* ── Download ───────────────────────────────────────────────── */

  const handleDownload = useCallback(() => {
    if (!result) return;

    const a = document.createElement('a');

    if (result.url) {
      /* PDF — already a Blob URL */
      a.href     = result.url;
      a.download = 'documento.pdf';
    } else if (result.psText) {
      /* PostScript — create Blob on the fly */
      const blob = new Blob([result.psText], { type: 'application/postscript' });
      a.href     = URL.createObjectURL(blob);
      a.download = 'documento.ps';
    } else {
      return;
    }

    a.click();
  }, [result]);

  /* ── Render ─────────────────────────────────────────────────── */

  return (
    <div className="app">

      {/* ── Toolbar ─────────────────────────────────────────── */}
      <Toolbar
        status={status}
        result={result}
        format={format}
        onFormatChange={setFormat}
        onDownload={handleDownload}
        onSaveSource={handleSaveSource}
        hasSource={source.trim().length > 0}
      />

      {/* ── Split pane ──────────────────────────────────────── */}
      <div className="content" ref={containerRef}>

        {/* Left pane — editor */}
        <div className="pane" style={{ width: `${splitPos}%` }}>
          <div className="pane-titlebar">
            <span className="pane-titlebar-dot" />
            EDITOR CYKAFLEX
          </div>
          <div className="pane-body">
            <CykaflexEditor value={source} onChange={setSource} />
          </div>
        </div>

        {/* Drag handle */}
        <div className="divider" onMouseDown={handleDividerMouseDown} />

        {/* Right pane — preview */}
        <div className="pane" style={{ width: `${100 - splitPos}%` }}>
          <div className="pane-titlebar">
            <span className="pane-titlebar-dot" />
            PREVISUALIZACION
          </div>
          <div className="pane-body">
            <PreviewPanel result={result} status={status} />
          </div>
        </div>

      </div>

      {/* ── Error console ───────────────────────────────────── */}
      <ErrorConsole
        error={compileError}
        open={consoleOpen}
        onToggle={() => setConsoleOpen(o => !o)}
      />

      {/* ── Status bar ──────────────────────────────────────── */}
      <StatusBar status={status} error={compileError} result={result} />

    </div>
  );
}
