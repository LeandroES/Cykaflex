import { useState } from 'react'

export default function App() {
  const [source, setSource] = useState('')
  const [output, setOutput] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleCompile() {
    setLoading(true)
    try {
      const res = await fetch('/api/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source }),
      })
      const data = await res.json()
      setOutput(data)
    } catch (err) {
      setOutput({ error: err.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={{ fontFamily: 'monospace', padding: '2rem', maxWidth: '900px', margin: '0 auto' }}>
      <h1>Cykaflex Editor</h1>
      <p>Lenguaje de marcado tipográfico en español</p>

      <textarea
        value={source}
        onChange={(e) => setSource(e.target.value)}
        placeholder="Escribe tu código Cykaflex aquí..."
        rows={16}
        style={{ width: '100%', fontSize: '14px', padding: '0.5rem', boxSizing: 'border-box' }}
      />

      <button
        onClick={handleCompile}
        disabled={loading || !source.trim()}
        style={{ marginTop: '0.5rem', padding: '0.5rem 1.5rem', cursor: 'pointer' }}
      >
        {loading ? 'Compilando...' : 'Compilar'}
      </button>

      {output && (
        <pre style={{ marginTop: '1rem', background: '#f4f4f4', padding: '1rem', overflowX: 'auto' }}>
          {JSON.stringify(output, null, 2)}
        </pre>
      )}
    </main>
  )
}
