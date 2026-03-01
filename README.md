# ◆ Cykaflex

> **Un lenguaje de marcas tipográfico en español, con compilador nativo a PostScript.**

Cykaflex es un sistema de composición de documentos diseñado como alternativa hispanohablante a LaTeX. Su filosofía central es la **separación estricta entre contenido y presentación**: el autor escribe _qué_ dice el documento en sintaxis Cykaflex (archivos `.cyk`), y el compilador decide _cómo_ se ve, generando PostScript puro sin depender de `pdflatex` ni de ninguna distribución TeX.

---
<img width="1073" height="1161" alt="1" src="https://github.com/user-attachments/assets/ffc1e0f4-29ef-4da2-9543-bf0e51d4ef64" />

## Arquitectura del Proyecto — Cloud-Native

Cykaflex es una aplicación **multi-servicio contenedorizada con Docker**. Cada componente vive en su propio contenedor y se comunica a través de una red interna de Docker Compose.

```
Cykaflex/
├── docker-compose.yml          ← Orquestador: levanta ambos servicios
│
├── compiler-api/               ← Backend  (Python · FastAPI)  puerto 8000
│   ├── Dockerfile
│   ├── requirements.txt        ← fastapi, uvicorn, ply, pandas
│   └── app/
│       ├── main.py             ← Endpoints REST (/health /compile /tokenise /ast)
│       └── compiler/
│           ├── lexer.py        ← Analizador léxico (ply.lex)
│           ├── parser_ll1.py   ← Parser LL(1) predictivo recursivo
│           ├── ast_nodes.py    ← AST — Patrón Composite
│           ├── codegen_postscript.py ← Generador PS — Patrón Visitor
│           └── __init__.py     ← Exporta compile_to_ps()
│
└── web-editor/                 ← Frontend (React 18 · Vite 6)  puerto 3000
    ├── Dockerfile
    └── src/
        ├── App.jsx             ← Raíz: layout dividido + estado global
        ├── hooks/useCompile.js ← Debounce 1 s + AbortController
        └── components/
            ├── Toolbar.jsx     ← Barra de herramientas con gestión de archivos
            ├── CykaflexEditor.jsx ← Monaco Editor con resaltado personalizado
            ├── PreviewPanel.jsx   ← Visor PDF (iframe) o PS (pre)
            ├── ErrorConsole.jsx   ← Consola de errores estilo terminal
            └── StatusBar.jsx      ← Barra de estado inferior
```

### Backend — `compiler-api`

El núcleo del sistema es un **compilador de cuatro fases** escrito en Python puro:

| Fase | Módulo | Tecnología | Rol |
|---|---|---|---|
| **Análisis Léxico** | `lexer.py` | `ply.lex` | Convierte el texto fuente en un flujo de tokens (7 símbolos + 23 keywords) |
| **Análisis Sintáctico** | `parser_ll1.py` | LL(1) recursivo descendente | Valida la gramática y construye el AST |
| **AST** | `ast_nodes.py` | Patrón Composite | 10 tipos de nodos tipados con `@dataclass` |
| **Generación de Código** | `codegen_postscript.py` | Patrón Visitor | Emite PostScript-Adobe 3.0 válido, sin `pdflatex` |

La API REST está expuesta con **FastAPI + Uvicorn** y ofrece:

- `GET /health` — verificación de liveness
- `POST /compile` — código fuente → PostScript (+ conversión a PDF vía Ghostscript)
- `POST /tokenise` — depuración: devuelve lista de tokens
- `POST /ast` — depuración: devuelve el AST en JSON

### Frontend — `web-editor`

Interfaz de usuario retro-moderna inspirada en la estética **NeXTSTEP / Windows 95**, con fuentes del sistema, fondos `#C0C0C0` y bordes biselados. Tecnologías clave:

- **Monaco Editor** con gramática Monarch personalizada para resaltado de sintaxis Cykaflex
- **Renderizado en tiempo real**: el hook `useCompile` tiene un debounce de 1 000 ms y cancelación con `AbortController`
- **Panel dividido** con resize por arrastre (20 %–80 %)
- **Gestión de archivos `.cyk`**: abrir desde disco, editar el nombre y guardar el código fuente o la salida compilada

---

## Características Tipográficas Avanzadas

### Justificación perfecta mediante macros PostScript nativas

El motor **no simula** la justificación: inyecta una macro `JustifyShow` en el prólogo del PostScript generado. Esta macro usa `stringwidth` del intérprete para medir el ancho _real_ de cada cadena y distribuir el espacio restante exactamente entre las palabras con `widthshow`. La última línea de cada párrafo se renderiza alineada a la izquierda para evitar el estiramiento antinatural.

### Numeración automática de secciones y subsecciones

El `PostScriptVisitor` mantiene contadores de estado internos. Las secciones se numeran automáticamente con dígitos arábigos (`1.`, `2.`, …) y las subsecciones con letras mayúsculas (`A.`, `B.`, …), reiniciándose en cada nueva sección. El autor _nunca_ escribe el número manualmente.

### Polimorfismo de estilos en el bloque `texto`

El comando `texto` acepta cualquier combinación de modificadores opcionales entre corchetes, en cualquier orden:

```
texto[14pt][negrita][cursiva]{"Texto con estilo combinado."}
```

El parser resuelve los modificadores en tiempo de análisis y el generador selecciona la variante tipográfica correcta:

| Combinación | Fuente PostScript |
|---|---|
| _(ninguno)_ | `Helvetica` |
| `[negrita]` | `Helvetica-Bold` |
| `[cursiva]` | `Helvetica-Oblique` |
| `[negrita][cursiva]` | `Helvetica-BoldOblique` |

### Soporte nativo para el español

El prólogo de cada documento generado incluye una macro `ReEncodeFont` que re-registra las cuatro variantes de Helvetica bajo `ISOLatin1Encoding`, garantizando la correcta representación de caracteres como `á`, `é`, `í`, `ó`, `ú`, `ñ` y `¿`/`¡` en cualquier intérprete PostScript estándar.

---

## Instalación y Uso

### Requisitos previos

- [Docker](https://www.docker.com/) y [Docker Compose](https://docs.docker.com/compose/) instalados.

### Levantar el proyecto

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd Cykaflex

# Construir las imágenes y arrancar los servicios
docker compose up --build
```

Abrir el navegador en **http://localhost:3000**.

Para arrancar en segundo plano:

```bash
docker compose up -d --build
```

Ver logs de un servicio específico:

```bash
docker compose logs -f compiler-api
docker compose logs -f web-editor
```

### Flujo de trabajo típico

1. Escribe o abre un archivo `.cyk` en el editor Monaco.
2. El documento se compila automáticamente cada segundo (debounce).
3. El PDF renderizado aparece en el panel derecho en tiempo real.
4. Usa ** Guardar .cyk** para guardar el código fuente.
5. Usa ** Descargar Salida** para descargar el PDF o PostScript compilado.

---

## Especificación Léxica y Gramática

### Keywords principales

| Token | Valor | Descripción |
|---|---|---|
| `cm` | `cm` | Medida en centímetros |
| `pt` | `pt` | Medida en puntos tipográficos |
| `inicio` | `inicio` | Abre el bloque principal del documento |
| `fin` | `fin` | Cierra el bloque principal |
| `documento` | `documento` | Identificador del bloque raíz |
| `clasedocumento` | `clasedocumento` | Declaración de clase de documento |
| `titulopagina` | `titulopagina` | Título del documento |
| `capitulo` | `capitulo` | Capítulo (sólo en tipo `libro`) |
| `seccion` | `seccion` | Sección |
| `subseccion` | `subseccion` | Subsección |
| `subsubseccion` | `subsubseccion` | Subsubsección |
| `texto` | `texto` | Párrafo de texto |
| `nuevapagina` | `nuevapagina` | Salto de página explícito |
| `inicioe` | `inicioe` | Lista enumerada |
| `inicioi` | `inicioi` | Lista con viñetas |
| `item` | `item` | Elemento de lista |
| `negrita` | `negrita` | Estilo negrita |
| `cursiva` | `cursiva` | Estilo cursiva |

### Expresiones regulares de símbolos

| Patrón | Token |
|---|---|
| `{` | `LEFT_KEY` |
| `}` | `RIGHT_KEY` |
| `[` | `LEFT_BRACKET` |
| `]` | `RIGHT_BRACKET` |
| `"[^"]+"` | `CONTENT` |
| `[0-9]+` | `NUMBER` |
| `%[^\n]*` | `COMMENT` (descartado) |

### Gramática condensada (LL(1))

```
programa         → clasedocumento bloque_documento

clasedocumento   → CLASEDOCUMENTO [ NUMBER metrics ] { doc_type }
metrics          → pt | cm
doc_type         → articulo | libro

bloque_documento → inicio{documento} cuerpo fin{documento}

cuerpo           → elemento cuerpo | ε
elemento         → titulopagina | capitulo | seccion | subseccion
                 | subsubseccion | texto | lista | nuevapagina | COMMENT

texto            → TEXTO modifier* { CONTENT }
modifier         → [ NUMBER pt ] | [ negrita ] | [ cursiva ]

seccion          → SECCION [ CONTENT ] { cuerpo }
subseccion       → SUBSECCION [ CONTENT ] { cuerpo }
lista            → enumerar | itemizar
enumerar         → INICIOE [ ennumerar ] { items }
items            → ITEM { CONTENT } items | ε
```

---

## Ejemplo Práctico — El Manifiesto de Cykaflex

```cykaflex
% Manifiesto de Cykaflex — ejemplo de todas las funcionalidades
clasedocumento[12pt]{articulo}

inicio{documento}

titulopagina[negrita]{"El Manifiesto de Cykaflex"}

seccion["El problema con la documentación actual"]{
    texto{"Históricamente, la composición tipográfica de calidad ha sido territorio exclusivo de quienes dominan sistemas como LaTeX, una herramienta poderosa pero cuya curva de aprendizaje resulta empinada, en especial para usuarios hispanohablantes."}
    texto[cursiva]{"Cykaflex nace de una pregunta simple: ¿puede un lenguaje de marcas ser al mismo tiempo expresivo, legible y en español?"}
}

seccion["Nuestros Principios"]{
    subseccion["Separación de contenido y presentación"]{
        texto{"El autor se ocupa del contenido. El compilador, de la forma. Esta separación reduce el ruido cognitivo y permite que los documentos evolucionen sin reescrituras masivas."}
    }
    subseccion["Tipografía de calidad, sin dependencias externas"]{
        texto[14pt][negrita]{"Cykaflex genera PostScript puro."}
        texto{"No invoca pdflatex, no requiere una distribución TeX. El compilador es autónomo y reproducible dentro de un contenedor Docker de menos de 150 MB."}
    }
    subseccion["Sintaxis diseñada para hispanohablantes"]{
        texto{"Todos los keywords son palabras del español cotidiano: inicio, fin, seccion, negrita, cursiva. Leer un archivo .cyk es casi leer un guión."}
    }
}

seccion["El Estado Actual"]{
    texto{"El compilador implementa un analizador léxico basado en ply.lex, un parser LL(1) predictivo recursivo descendente, construcción de AST bajo el Patrón Composite y generación de código PostScript bajo el Patrón Visitor."}
    texto[cursiva]{"La numeración de secciones y subsecciones es automática. La justificación del texto es perfecta gracias a macros nativas inyectadas en el prólogo PostScript."}

    inicioe[ennumerar]{
        item{"Análisis léxico: 7 símbolos + 23 keywords"}
        item{"Análisis sintáctico: LL(1) recursivo descendente"}
        item{"AST: 10 tipos de nodos (Patrón Composite)"}
        item{"Generación de código: PostScript-Adobe 3.0 (Patrón Visitor)"}
    }
}

nuevapagina

seccion["Cykaflex es un punto de partida"]{
    texto[14pt][negrita][cursiva]{"Este documento fue escrito y compilado por Cykaflex."}
    texto{"Cada sección numerada, cada párrafo justificado, cada carácter especial —á, é, ñ, ¿— es evidencia de que un compilador minimalista puede producir documentos tipográficos de calidad sin depender de sistemas externos."}
}

fin{documento}
```

---

## Alcance y Limitaciones Actuales

La madurez de un sistema de software se mide también por la claridad con la que define sus límites. Cykaflex, en su versión actual, **no soporta**:

| Característica             | Nota |
|----------------------------|---|
| **Imágenes embebidas**     | No hay soporte para incluir gráficos o figuras en el documento. |
| **Fórmulas matemáticas**   | No existe un modo matemático. Para ecuaciones complejas se requeriría un motor adicional (e.g., MathJax o un transpilador a PS). |
| **Estilos en línea**       | El estilo (`negrita`, `cursiva`) aplica al bloque `texto` completo. No es posible marcar una palabra individual dentro de un párrafo. |
| **Tablas**                 | No hay comando para definir estructuras de tabla. |
| **Referencias cruzadas**   | No existe un sistema de etiquetas (`\label`/`\ref`) para referenciar secciones o figuras. |
| **Índices automáticos**    | No se genera tabla de contenidos ni índice analítico. |
| **Fuentes personalizadas** | El sistema está acoplado a la familia Helvetica Type-1. Fuentes externas requieren re-encoding manual en el prólogo PS. |

Estos puntos representan la hoja de ruta natural para futuras fases del proyecto.

---

## Bibliografía

1. [LaTeX Commands by NaSA](https://www.giss.nasa.gov/tools/latex/ltx-2.html)
2. [Manual de LaTeX](https://manualdelatex.com/simbolos#chapter10)
3. [Engineering a Compiler — 3rd Edition, Keith D. Cooper & Linda Torczon](https://shop.elsevier.com/books/engineering-a-compiler/cooper/978-0-12-815412-0)
4. [TeX — LaTeX Stack Exchange](https://tex.stackexchange.com/)
5. [Comprehensive TeX Archive Network (CTAN)](https://ctan.org/)

---

<div align="center">

**Cykaflex** · Compilador tipográfico en español · PostScript nativo · Docker-first

</div>
