# Spec Template

Esta carpeta es la plantilla para crear nuevas specs siguiendo SDD.

## Estructura

Toda spec contiene 4 archivos, creados en orden por las 4 fases de SDD:

| Archivo | Fase SDD | Cuándo se crea | Quién aprueba |
|---|---|---|---|
| `requirements.md` | Specify | Inicio | Humano |
| `design.md` | Plan | Tras aprobar requirements | Humano |
| `tasks.md` | Plan | Junto con design | Humano |
| `impl-log.md` | Implement + Validate | Continuo durante implementación | Agente actualiza, humano audita |

## Comando para crear una nueva spec

```bash
# Desde el agente
/spec-init <nombre-de-feature>

# O manualmente:
cp -r specs/_template specs/<nombre-de-feature>
```

## Reglas

1. **No saltar fases.** No empezar `design.md` antes de aprobar `requirements.md`.
2. **No empezar `tasks.md` antes de aprobar `design.md`.**
3. **No implementar antes de aprobar `tasks.md`.**
4. **Mantener `impl-log.md` actualizado** en cada sesión de trabajo.

## Sobre el formato EARS en requirements

EARS (Easy Approach to Requirements Syntax) ofrece 5 patrones:

| Patrón | Plantilla | Cuándo usar |
|---|---|---|
| Ubiquitous | `THE SYSTEM SHALL <response>` | Requisito siempre activo |
| Event-driven | `WHEN <trigger> THE SYSTEM SHALL <response>` | Reacción a un evento |
| State-driven | `WHILE <state> THE SYSTEM SHALL <response>` | Durante un estado |
| Optional | `WHERE <feature> THE SYSTEM SHALL <response>` | Si una opción está activa |
| Unwanted | `IF <unwanted condition>, THEN THE SYSTEM SHALL <response>` | Manejo de error o caso no deseado |

Más info: https://alistairmavin.com/ears/
