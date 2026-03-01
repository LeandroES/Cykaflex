/**
 * useCompile — Debounced Cykaflex compilation hook.
 *
 * Watches `source` and `format` for changes; after 1 000 ms of quiet the
 * hook fires a POST /api/compile and updates the derived state below.
 *
 * Returns
 * -------
 * result       — { url: string|null, psText: string|null, mediaType: string }
 *                 `url`    is a Blob URL valid for the current render cycle (PDF)
 *                 `psText` is the raw PostScript string (when GS is absent)
 * compileError — { ok, error_type, line, col, detail } | null
 * status       — 'idle' | 'compiling' | 'ok' | 'error'
 */

import { useState, useEffect, useRef } from 'react';

const DEBOUNCE_MS = 1000;

export function useCompile(source, format = 'auto') {
  const [result,       setResult]       = useState(null);
  const [compileError, setCompileError] = useState(null);
  const [status,       setStatus]       = useState('idle');

  const timerRef   = useRef(null);
  const prevUrlRef = useRef(null);

  useEffect(() => {
    if (!source?.trim()) {
      setResult(null);
      setCompileError(null);
      setStatus('idle');
      return;
    }

    clearTimeout(timerRef.current);
    setStatus('compiling');

    const abortCtrl = new AbortController();

    timerRef.current = setTimeout(async () => {
      try {
        const resp = await fetch('/api/compile', {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify({ source, output_format: format }),
          signal:  abortCtrl.signal,
        });

        /* Revoke previous Blob URL to avoid memory leaks */
        if (prevUrlRef.current) {
          URL.revokeObjectURL(prevUrlRef.current);
          prevUrlRef.current = null;
        }

        if (resp.ok) {
          const blob      = await resp.blob();
          const mediaType = resp.headers.get('Content-Type') || '';

          let url    = null;
          let psText = null;

          if (mediaType.includes('pdf')) {
            url = URL.createObjectURL(blob);
            prevUrlRef.current = url;
          } else {
            /* PostScript — read as text; no blob URL needed */
            psText = await blob.text();
          }

          setResult({ url, psText, mediaType });
          setCompileError(null);
          setStatus('ok');

        } else if (resp.status === 400) {
          const data = await resp.json();
          setCompileError(data);
          setResult(null);
          setStatus('error');

        } else {
          setCompileError({
            ok:         false,
            error_type: 'server_error',
            line:       0,
            col:        0,
            detail:     `Error del servidor: HTTP ${resp.status}`,
          });
          setResult(null);
          setStatus('error');
        }

      } catch (err) {
        if (err.name === 'AbortError') return; /* cleanup — ignore */
        setCompileError({
          ok:         false,
          error_type: 'network_error',
          line:       0,
          col:        0,
          detail:     `Error de red: ${err.message}`,
        });
        setResult(null);
        setStatus('error');
      }
    }, DEBOUNCE_MS);

    return () => {
      clearTimeout(timerRef.current);
      abortCtrl.abort();
    };
  }, [source, format]);

  return { result, compileError, status };
}
