# Kit de inicio de Mintlify

Usa el kit de inicio para implementar tu documentación y dejarla lista para personalizarla.

Haz clic en el botón verde **Use this template** en la parte superior de este repositorio para copiar el kit de inicio de Mintlify. El kit de inicio contiene ejemplos de

- Páginas de guía
- Navegación
- Personalizaciones
- Páginas de referencia de API
- Uso de componentes populares

**[Sigue la guía completa de inicio rápido](https://starter.mintlify.com/quickstart)**

## Redacción asistida por IA

Configura tu herramienta de programación con IA para trabajar con Mintlify:

```bash
npx skills add https://mintlify.com/docs
```

Este comando instala la habilidad de documentación de Mintlify para tus herramientas de IA configuradas, como Claude Code, Cursor, Windsurf y otras. La habilidad incluye una referencia de componentes, estándares de redacción y orientación sobre el flujo de trabajo.

Consulta las [guías de herramientas de IA](/ai-tools) para obtener instrucciones de configuración específicas de cada herramienta.

## Desarrollo

Instala la [CLI de Mintlify](https://www.npmjs.com/package/mint) para previsualizar localmente los cambios en tu documentación. Para instalarla, usa el siguiente comando:

```
npm i -g mint
```

Ejecuta el siguiente comando en la raíz de tu documentación, donde se encuentra tu `docs.json`:

```
mint dev
```

Consulta tu vista previa local en `http://localhost:3000`.

## Publicar cambios

Instala nuestra aplicación de GitHub desde tu [panel](https://dashboard.mintlify.com/settings/organization/github-app) para propagar los cambios de tu repositorio a tu implementación. Los cambios se implementan automáticamente en producción después de hacer push a la rama predeterminada.

## ¿Necesitas ayuda?

### Solución de problemas

- Si tu entorno de desarrollo no se está ejecutando: ejecuta `mint update` para asegurarte de tener la versión más reciente de la CLI.
- Si una página se carga como 404: asegúrate de estar trabajando en una carpeta con un `docs.json` válido.

### Recursos
- [Documentación de Mintlify](https://mintlify.com/docs)
