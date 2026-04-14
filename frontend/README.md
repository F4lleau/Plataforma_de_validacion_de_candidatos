# Frontend - Junta Electoral

## Tecnologías principales

- **React**: Biblioteca para construir interfaces de usuario.
- **Vite**: Herramienta de desarrollo rápida para proyectos frontend modernos.
- **Tailwind CSS**: Framework de utilidades para estilos rápidos y consistentes.
- **tailwindcss-animate**: Plugin para animaciones con Tailwind.
- **PostCSS** y **Autoprefixer**: Procesadores de CSS para compatibilidad y optimización.

## ¿Por qué estas tecnologías?

- **React** permite crear interfaces interactivas y escalables.
- **Vite** ofrece recarga rápida y configuración sencilla.
- **Tailwind CSS** agiliza el desarrollo de estilos y mantiene la coherencia visual.

## Instalación de dependencias

1. Clona el repositorio y entra a la carpeta frontend:
   ```bash
   git clone <url-del-repo>
   cd junta_electoral/frontend
   ```
2. Instala las dependencias:
   ```bash
   npm install
   ```

## Comandos útiles

- **Iniciar el servidor de desarrollo:**
  ```bash
  npm run dev
  ```
- **Construir para producción:**
  ```bash
  npm run build
  ```
- **Previsualizar build de producción:**
  ```bash
  npm run preview
  ```

## Archivos clave

- `src/`: Código fuente principal de la aplicación.
- `tailwind.config.js`: Configuración de Tailwind CSS.
- `postcss.config.js`: Configuración de PostCSS.
- `index.html`: Archivo HTML principal.
- `.env`: Variables de entorno para el frontend (si se usan).

## Notas

- Asegúrate de tener Node.js instalado (recomendado v18+).
- No subas archivos de entorno `.env` ni la carpeta `node_modules` al repositorio.
- Consulta la documentación oficial de cada tecnología para más detalles.
  },
  },
  ])

````

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
````
