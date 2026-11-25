---
description: Cierra la sesión - reescribe HANDOFF.md, actualiza registros, commit y push
---

Cierra esta sesión de Claude Code. Nota extra del usuario (puede estar vacía): $ARGUMENTS

1. Comprueba con comandos que no quede nada corriendo (subagentes, procesos en background). Si algo sigue, espera
   a que termine o dilo y detente.
2. **Reescribe** `HANDOFF.md` en la raíz (se reemplaza, no se agrega; máximo ~60 líneas), en español:
   - **Objetivo** del tema en curso, en una línea.
   - **Hecho** en esta sesión, con rutas de archivos y commits.
   - **Pendiente**, en orden, con el próximo paso concreto primero.
   - **Decisiones abiertas** y preguntas para el usuario.
   - **Trampas / lecciones** que la próxima sesión debe saber.
   Lo que salga del handoff anterior y siga siendo útil va a `docs/claude/historial.md` (al final, con fecha).
3. Si aprendiste algo reutilizable y el repo tiene `.claude/skills/`, enriquece la skill correspondiente.
4. `git add` solo de los archivos tocados, commit (`docs(handoff): <resumen>` en inglés) y `git push`.
   Este push está autorizado: es el gate acordado para el handoff. Si estás en un branch `claude/...`, pushea
   ese branch.
5. Termina con este bloque:

> ## 🔴 NUEVA SESIÓN — esta va por ~<N>k tokens (objetivo 200–300k)
> Estado guardado y pusheado en `HANDOFF.md`. Abre una sesión nueva y escribe: `/riprendi`
