# Tabla maestra de decisiones y casos de prueba

> Documento de apoyo para el Bloque 1 del DEL PINO Knowledge Agent. Las políticas son ficticias y fueron preparadas con fines educativos.

## 1. Tabla maestra de decisiones y políticas compartidas

| Tema | Decisión única del MVP | Documentos donde debe coincidir |
|---|---|---|
| Alcance | Agente interno para colaboradores; responde solo con documentación recuperada. | 01, 02, 03 |
| Información ficticia | Todas las políticas adicionales se presentan como material educativo, no como política legal vigente. | 01, 02, 03 |
| Envío | Envío nacional mediante Correo Argentino. | 01, 02, 03 |
| Costo de envío | Se calcula por peso y tamaño del paquete; puede requerir código postal y modalidad. No hay montos fijos. | 01, 02, 03 |
| Referencia de despacho | Hasta 10 días hábiles desde confirmación, pago y disponibilidad; no es fecha de entrega. | 01, 02 |
| Fecha concreta | Requiere confirmación humana. El agente no promete fechas exactas. | 01, 02, 03 |
| Medios de pago | Efectivo coordinado, transferencia, Mercado Pago y cuotas cuando estén habilitadas. | 01, 03 |
| Tienda online | Pago completo antes de preparar el pedido. | 01 |
| Personalizados | Pago completo o seña del 50% y saldo del 50% antes del despacho. | 01, 03 |
| Inicio de producción | Especificaciones aprobadas y pago completo o seña verificada. | 03 |
| Datos mínimos de cortina | Barral o riel; medida del barral o riel; distancia hasta el piso. | 01, 03 |
| Medida de ventana | No es suficiente por sí sola. | 01, 03 |
| Precio y presupuesto | Siempre requieren confirmación humana. | 01, 03 |
| Stock y color | Información en tiempo real no incluida en el corpus. | 01, 03 |
| Arrepentimiento estándar | Solicitud dentro de 15 días corridos; sin uso, limpio y completo. | 03 |
| Incidencia visible | Daños, faltantes y diferencias visibles de medidas, color, variante o especificaciones deben reportarse dentro de 72 horas. | 02, 03 |
| Garantía educativa | 90 días corridos para defectos de fabricación o materiales que aparezcan durante el uso normal; no reemplaza el reporte de 72 horas para diferencias visibles. | 03 |
| Personalizado por arrepentimiento | No admite devolución una vez confeccionado según especificaciones aprobadas. | 03 |
| Error atribuible a DEL PINO | La empresa asume el costo logístico aprobado. | 02, 03 |
| Error de dirección del cliente | Puede generar un nuevo costo de envío. | 02 |
| Reembolso | Se inicia dentro de 5 días hábiles luego de la aprobación y validación necesaria; acreditación depende del medio. | 03 |
| Seguimiento real | El agente no está integrado con pedidos ni Correo Argentino. | 01, 02 |
| Fallback | "No encontré esa información en los documentos disponibles. El caso debe ser confirmado por la persona responsable." | 01 y comportamiento del agente |

## 2. Preguntas respondibles

| ID | Pregunta | Documento esperado | Sección / página esperada | Contenido mínimo de la respuesta |
|---|---|---|---|---|
| R01 | ¿Qué medios de pago acepta DEL PINO? | 01 | 4. Medios de pago / p. 4 | Efectivo coordinado, transferencia, Mercado Pago y cuotas según disponibilidad. |
| R02 | ¿La compra de la tienda online se paga completa? | 01 | 3 y 4 / p. 4 | Sí, pago completo antes de preparar el pedido. |
| R03 | ¿Cómo se paga una cortina a medida? | 01 o 03 | 4 / p. 4 | Pago completo o seña 50% y saldo 50% antes del despacho. |
| R04 | ¿Qué datos tengo que pedir para una cortina a medida? | 01 o 03 | 01: 7 / p. 6; 03: 2 / p. 3 | Barral o riel, medida del barral o riel y distancia hasta el piso. |
| R05 | ¿Alcanza con medir la ventana? | 01 o 03 | 01: 7 / p. 6; 03: 2 / p. 3 | No; no define ancho de cobertura ni altura desde el sistema de instalación. |
| R06 | ¿DEL PINO hace envíos a todo el país? | 01 o 02 | 01: 7 / p. 6; 02: 2 / p. 3 | Sí, envíos nacionales mediante Correo Argentino. |
| R07 | ¿Cómo se calcula el costo del envío? | 02 | 3 / p. 4 | Por peso y tamaño; puede requerir código postal y modalidad; no monto fijo. |
| R08 | ¿El plazo de 10 días incluye la entrega? | 02 | 4 y 5 / pp. 4-5 | No, es referencia de despacho, no de recepción final. |
| R09 | ¿Qué datos se piden para consultar un envío? | 01 o 02 | 01: 8 / p. 7; 02: 6 / p. 5 | Número de pedido, contacto de compra y código de seguimiento si fue despachado. |
| R10 | ¿Qué hay que pedir si el paquete llegó dañado? | 02 o 03 | 9 / p. 7; 10 / p. 8 | Reporte dentro de 72 horas y fotos de paquete, producto y etiqueta. |
| R11 | ¿Cuánto tiempo hay para devolver un producto estándar por arrepentimiento? | 03 | 6 / p. 5 | 15 días corridos, sin uso, limpio y completo. |
| R12 | ¿Se puede devolver una cortina a medida porque el cliente cambió de opinión? | 03 | 7 / p. 6 | No, si fue confeccionada según especificaciones aprobadas. |
| R13 | ¿Cuánto dura la garantía educativa? | 03 | 9 / p. 7 | 90 días corridos desde la entrega por defectos de fabricación. |
| R14 | ¿Quién paga el reenvío si la dirección estaba mal? | 02 | 8 / p. 6 | Puede pagarlo el cliente si el dato incorrecto fue suyo; DEL PINO si fue error propio. |
| R15 | ¿Cuándo empieza a fabricarse un pedido personalizado? | 03 | 4 / p. 4 | Tras aprobar especificaciones y verificar pago completo o seña. |
| R16 | ¿Qué pasa si el cliente quiere cambiar el color después de iniciada la producción? | 03 | 5 / p. 5 | No está garantizado; puede ser inviable o requerir nuevo presupuesto. |
| R17 | ¿Qué soluciones puede aprobar DEL PINO ante una falla? | 03 | 11 / p. 8 | Ajuste, reemplazo, pieza faltante, reembolso parcial o total según evaluación. |
| R18 | ¿En cuánto tiempo inicia DEL PINO un reembolso aprobado? | 03 | 11 / p. 8 | Dentro de 5 días hábiles tras validación; acreditación depende del medio. |

## 3. Preguntas que deben activar fallback o derivación

| ID | Pregunta | Motivo | Comportamiento esperado |
|---|---|---|---|
| F01 | ¿Cuánto cuesta hoy una cortina de tres metros? | Precio y presupuesto no documentados. | Fallback y derivación a presupuesto humano. |
| F02 | ¿Hay stock de cortina beige? | Stock en tiempo real. | Indicar que debe verificarse manualmente. |
| F03 | ¿Qué descuento me pueden hacer? | Descuento no autorizado ni documentado. | No inventar porcentaje; derivar. |
| F04 | ¿Cuánto cuesta el envío a mi casa? | Falta cotización real, peso y tamaño final. | Explicar variables y derivar cálculo. |
| F05 | ¿Puede llegar el viernes 24? | Fecha exacta. | No prometer; solicitar confirmación humana. |
| F06 | ¿Dónde está ahora el pedido DP-1234? | Estado real de pedido. | Explicar que no hay integración y derivar seguimiento. |
| F07 | ¿Quedan tres unidades del combo azul? | Inventario real. | Fallback o verificación manual. |
| F08 | ¿Cuál es el número de cuotas sin interés disponible hoy? | Condición vigente de Mercado Pago. | Indicar que depende de lo mostrado al pagar. |
| F09 | ¿Qué sucursal de Correo Argentino está abierta ahora? | Información externa en tiempo real. | No responder desde el corpus. |
| F10 | ¿Puedo autorizar un reembolso de $80.000? | Monto y decisión operativa real. | No decidir ni inventar; escalar. |

## 4. Preguntas ambiguas o fronterizas

| ID | Pregunta | Riesgo | Respuesta esperada sin excederse |
|---|---|---|---|
| A01 | La cortina a medida llegó más corta de lo esperado. ¿La cambiamos? | No se sabe si hubo error de confección o de medición del cliente. | Si la diferencia era visible, registrar dentro de 72 horas; pedir especificaciones y evidencia; comparar antes de decidir. |
| A02 | La caja llegó golpeada, pero la cortina parece estar bien. ¿Corresponde devolución? | Daño de embalaje no implica daño de producto. | Registrar evidencia dentro de 72 horas y evaluar; no aprobar automáticamente. |
| A03 | El cliente pagó la seña y ahora quiere cambiar el color. ¿Se puede? | Depende de si la producción comenzó. | Verificar estado de producción; no confirmar el cambio sin revisión. |
| A04 | El color se ve distinto al de la foto. ¿Es una falla? | Puede depender de referencia aprobada e iluminación. | Comparar variante confirmada y evidencia; derivar si no es concluyente. |
| A05 | El tracking no cambia hace varios días. ¿Está perdido? | Falta confirmación del operador. | Revisar tracking y consultar a Correo Argentino; no declarar extravío. |
| A06 | La costura se abrió luego del lavado. ¿Cubre garantía? | Depende de instrucciones de cuidado y evidencia. | Solicitar evidencia y modo de lavado; no aprobar ni rechazar automáticamente. |

## 5. Revisión final de contradicciones

- **Pagos:** los documentos 01 y 03 utilizan la misma regla: pago completo en tienda online; personalizados completos o 50% de seña y 50% antes del despacho.
- **Producción:** el documento 03 exige especificaciones aprobadas y pago completo o seña verificada antes de comenzar. El documento 02 exige saldo cancelado antes del despacho. No existe conflicto.
- **Envíos:** los tres documentos identifican a Correo Argentino y separan el presupuesto del producto del costo logístico.
- **Plazos:** 10 días hábiles es referencia de despacho; 15 días es plazo de arrepentimiento para productos estándar; 72 horas es plazo para daños o diferencias visibles detectables al recibir; 90 días es garantía educativa para defectos que aparezcan durante el uso normal. Cada plazo tiene una finalidad distinta.
- **Fechas exactas:** los tres documentos requieren confirmación humana y prohíben convertir plazos generales en compromisos.
- **Personalizados:** no se aceptan devoluciones por arrepentimiento una vez producidos según datos aprobados, pero sí se revisan errores de confección, defectos, daños o faltantes.
- **Costos logísticos:** DEL PINO asume errores propios o daños aprobados; el cliente puede asumir retorno por arrepentimiento o reenvío causado por dirección incorrecta.
- **Reembolsos:** solo se inician después de la aprobación y validación necesaria; el documento no promete la fecha final de acreditación.
- **Información en tiempo real:** precios, stock, descuentos, cotizaciones de envío, fechas y estados reales quedan fuera del corpus.
- **Privacidad:** los documentos no incluyen datos personales reales y los casos de prueba utilizan identificadores ficticios.

**Resultado:** la prioridad entre el reporte de 72 horas y la garantía de 90 días quedó explicitada. No se detectan contradicciones internas pendientes entre los tres documentos.
