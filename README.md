# Cykaflex

## Introducción
Cykaflex es un sistema de software simplificado para la composición de documentos, diseñado como una alternativa a LaTeX en español. Su objetivo es facilitar la elaboración de documentos para usuarios que no dominan el inglés.

### Propuesta
Crear una versión en español de LaTeX y su respectivo compilador, haciendo la interfaz con este sistema de marcas más interactiva y menos dramática para los usuarios hispanohablantes.

## Especificación Léxica

### Comentarios
- `%`: Este símbolo será usado para denotar comentarios en Cykaflex.

### Keywords
- `cm`: Se refiere a una medida en centímetros.
- `pt`: Representa una medida en puntos, utilizada en tipografía.
- `inicio`: Marca el comienzo de un bloque o sección de código.
- `fin`: Marca el final de un bloque o sección de código.
- `documento`: Indica la estructura principal del documento.

### Expresiones Regulares
- `{`: `t_RIGHT_KEY = r'{'`
- `}`: `t_LEFT_KEY = r'}'`
- `]`: `t_RIGHT_BRACKET = r']'`
- `[`: `t_LEFT_BRACKET = r'['`
- `"texto"`: `t_CONTENT = r'".+"'`
- `texto`: `t_TEXTO = r'texto'`
- `cm`: `t_CENTIMETER = r'cm'`
- `pt`: `t_POINT = r'pt'`
- Numeración: `t_NUMBER = r'[0-9]+'`

## Gramática
- `documento -> clasedocumento iniciodocumento contenidodocumento findocumento`

- `clasedocumento -> DOCUMENTCLASS LEFT_BRACKET NUMBER metrics RIGHT_BRACKET LEFT_KEY document_type RIGHT_KEY`
- `metrics -> POINT`
- `metrics -> CENTIMETER`
- `iniciodocumento -> INICIO LEFT_KEY DOCUMENT RIGHT_KEY`
- `findocumento -> FIN LEFT_KEY DOCUMENT RIGHT_KEY`

- `contenidodocumento -> elemento contenidodocumento`
- `contenidodocumento -> ''`

- `elemento -> comentario`
- `elemento -> titulo`
- `elemento -> seccion`
- `elemento -> subseccion`
- `elemento -> subsubseccion`
- `elemento -> lista`
- `elemento -> NEWPAGE`
- `elemento -> texto`
- `elemento -> chapter`

- `contenidodocumentoseccion -> elementos contenidodocumentoseccion`
- `contenidodocumentoseccion -> ''`

- `elementos -> comentario`
- `elementos -> titulo`
- `elementos -> subseccion`
- `elementos -> lista`
- `elementos -> NEWPAGE`
- `elementos -> texto`
- `elementos -> chapter`

- `contenidodocumentosubseccion -> elementoss contenidodocumentosubseccion`
- `contenidodocumentosubseccion -> ''`

- `elementoss -> comentario`
- `elementoss -> titulo`
- `elementoss -> subsubseccion`
- `elementoss -> lista`
- `elementoss -> NEWPAGE`
- `elementoss -> texto`
- `elementoss -> chapter`

- `contenidodocumentosubsubseccion -> elementosss contenidodocumentosubsubseccion`
- `contenidodocumentosubsubseccion -> ''`

- `elementosss -> comentario`
- `elementosss -> titulo`
- `elementosss -> lista`
- `elementosss -> NEWPAGE`
- `elementosss -> texto`
- `elementosss -> chapter`

- `comentario -> COMMENT LEFT_KEY CONTENT RIGHT_KEY`
- `titulo -> TITULOPAGINA LEFT_BRACKET styles RIGHT_BRACKET LEFT_KEY CONTENT RIGHT_KEY`
- `styles -> NEGRITA`
- `styles -> CURSIVA`
- `texto -> TEXTO LEFT_KEY CONTENT RIGHT_KEY`

- `seccion -> SECCION LEFT_BRACKET CONTENT RIGHT_BRACKET LEFT_KEY contenidodocumentoseccion RIGHT_KEY`
- `subseccion -> SUBSECCION LEFT_BRACKET CONTENT RIGHT_BRACKET LEFT_KEY contenidodocumentosubseccion RIGHT_KEY`
- `subsubseccion -> SUBSUBSECCION LEFT_BRACKET CONTENT RIGHT_BRACKET LEFT_KEY contenidodocumentosubsubseccion RIGHT_KEY`

- `lista -> enumerar`
- `lista -> itemizar`
- `enumerar -> INICIOE LEFT_BRACKET ENUMERAR RIGHT_BRACKET LEFT_KEY items RIGHT_KEY`
- `itemizar -> INICIOI LEFT_BRACKET ITEMIZAR RIGHT_BRACKET LEFT_KEY items RIGHT_KEY`
- `items -> item items`
- `items -> ''`
- `item -> ITEM LEFT_KEY CONTENT RIGHT_KEY`

- `chapter -> CHAPTER LEFT_BRACKET CONTENT RIGHT_BRACKET LEFT_KEY contenidodocumento RIGHT_KEY`
- `document_type -> ARTICLE`
- `document_type -> BOOK`

## Ejemplos de Código
### Primer Ejemplo
```cykaflex
% Comentario inicial describiendo el documento
clasedocumento[12pt]{libro}
inicio{documento}
% Título del libro:
titulopagina[negrita]{"La Ciencia de Cykaflex"}
% Primer capítulo:
capitulo["Introducción"] {
    texto{"Este capítulo introduce los conceptos básicos y la importancia de Cykaflex en la documentación moderna."}
    seccion["Historia"]{
        texto{"Cykaflex fue desarrollado en el año 2024, con el objetivo de simplificar la creación de documentos estructurados."}
        subseccion["Evolución"]{
            texto{"Inicialmente, Cykaflex comenzó como un proyecto pequeño y se ha convertido en una herramienta esencial para muchos profesionales."}
        }
    }
}
% Segundo capítulo:
capitulo["Aplicaciones Prácticas"] {
    texto{"Este capítulo describe las diversas aplicaciones de Cykaflex en diferentes campos."}
    seccion["Educación"]{
        texto{"En el ámbito educativo, Cykaflex facilita la organización de apuntes y material didáctico."}
        subseccion["Casos de Uso"]{
            texto{"Profesores y estudiantes utilizan Cykaflex para estructurar sus cursos y trabajos de investigación."}
        }
    }
    seccion["Industria"]{
        texto{"En la industria, Cykaflex se aplica en la documentación técnica y manuales de operación."}
        subseccion["Beneficios"]{
            texto{"La claridad y estructura de Cykaflex ayudan a mejorar la comunicación técnica y reducir errores en la interpretación de manuales."}
        }
    }
}
fin{documento}
```
### Segundo Ejemplo
```cykaflex
% Comentario inicial
clasedocumento[10pt]{articulo}

inicio{documento}

% Título del artículo:
titulopagina[cursiva]{"Innovación en Cykaflex: Un estudio de caso"}

% Resumen del artículo:
seccion["Resumen"]{
    texto{"Este artículo presenta un estudio de caso sobre la innovación y adaptabilidad de Cykaflex en la redacción científica."}
}

% Introducción del artículo:
seccion["Introducción"]{
    texto{"Cykaflex ha revolucionado la manera en que se redactan documentos científicos, ofreciendo herramientas que mejoran la eficiencia y la claridad."}
}

% Metodología empleada en el estudio:
seccion["Metodología"]{
    texto{"Se analizó el uso de Cykaflex en un grupo de 100 científicos durante un año para determinar su impacto en la productividad y calidad de los documentos producidos."}
}

% Resultados obtenidos:
seccion["Resultados"]{
    texto{"Los resultados indican una mejora significativa en la eficiencia de redacción y en la satisfacción de los usuarios con documentos más estructurados y claros."}

    subseccion["Datos Estadísticos"]{
        texto{"El 90% de los usuarios reportó una reducción en el tiempo de redacción, mientras que el 85% destacó una mejora en la calidad de sus publicaciones."}
    }
}

% Conclusiones del estudio:
seccion["Conclusiones"]{
    texto{"Cykaflex ha demostrado ser una herramienta valiosa en la redacción científica, mejorando significativamente tanto la eficiencia como la calidad de los documentos."}
}

fin{documento}
```
### Tercer Ejemplo
```cykaflex
% Comentario sobre el documento
clasedocumento[11pt]{libro}

inicio{documento}

% Título del libro:
titulopagina[negrita]{"Breve Introducción a Cykaflex"}

% Capítulo único:
capitulo["Capítulo Único"] {
    % Introducción al capítulo:
    texto{"Este es un ejemplo muy simple de cómo se puede estructurar un libro con Cykaflex."}

    % Sección dentro del capítulo:
    seccion["Propósito de Cykaflex"]{
        % Descripción del propósito:
        texto{"Cykaflex es una herramienta diseñada para simplificar la creación de documentos estructurados, proporcionando claridad y consistencia en la presentación."}
    }

    % Subsección para detalles adicionales:
    subseccion["Facilidad de Uso"]{
        % Explicación de la facilidad de uso:
        texto{"La facilidad de uso es uno de los principales beneficios de Cykaflex, permitiendo a los usuarios concentrarse en el contenido más que en la forma."}
    }
}

fin{documento}
```

## Bibliografía
1. [LaTeX Commands by NaSA](https://www.giss.nasa.gov/tools/latex/ltx-2.html)
2. [Manual de LaTeX](https://manualdelatex.com/simbolos#chapter10)
3. [Engineering a Compiler - 3rd Edition, Keith D. Cooper, Linda Torczon](https://shop.elsevier.com/books/engineering-a-compiler/cooper/978-0-12-815412-0)
4. [TeX - LaTeX Stack Exchange](https://tex.stackexchange.com/)
5. [Comprehensive TeX Archive Network](https://ctan.org/)

