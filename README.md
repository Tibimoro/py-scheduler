# Proyecto planificador: Memoria explicativa

**Grupo:**

* Sourour Rihane
* Pamela Cristina Arias Bravo

## 1. Node Selection Logic

Nuestra lógica de selección de nodos está basada en la política del menor número de pods asignados. Primero filtramos los nodos según etiquetas y tolerancias de taints, luego elegimos el nodo con menos carga:

* En la versión básica (polling), se revisa la lista de pods y se cuenta cuántos hay por nodo.
* En la versión extendida, se usa `node_tolerates_taints()` para asegurar que el pod puede tolerar los taints del nodo.

## 2. Observations of Scheduling Behavior

* La programación funciona correctamente: los pods con `schedulerName: my-scheduler` se asignan según nuestra lógica.
* Cuando no hay nodos disponibles (por ejemplo, por taints sin tolerations), el scheduler registra errores pero no falla.
* Las extensiones de política como etiquetas (`env=prod`) o tolerations permiten un control fino del destino del pod.

## 3. Polling vs Event-Driven Scheduler

**Polling:**

* Ventaja: Simple de implementar.
* Desventaja: Menos eficiente. Consulta constante a la API Server.

**Watch (event-driven):**

* Ventaja: Responde a eventos en tiempo real, usa menos recursos.
* Desventaja: Más complejo de manejar (conexiones, errores de streaming).

## 4. Reflexión

**¿Por qué usamos Binding en vez de modificar directamente el Pod?**

* Porque es la forma recomendada y atómica de indicar al API Server la decisión de asignación. Evita conflictos.

**¿Ventajas e inconvenientes de polling vs watch?**

* Polling es simple pero ineficiente. Watch es más reactivo y eficiente, pero puede fallar si no se gestiona bien.

**¿Cómo afectan los taints y tolerations?**

* Permiten reservar nodos para ciertos pods. Nuestro scheduler ignora nodos con taints si el pod no los tolera.

**¿Qué políticas reales se podrían implementar?**

* Afinidad por etiquetas (por zona, entorno, etc.)
* Balanceo de carga (spread)
* Uso de recursos (CPU, RAM)
* Tolerancia a fallos (anti-affinity)

## 5. Estructura de Entrega

```
py-scheduler/
├── Dockerfile
├── rbac-deploy.yaml
├── requirements.txt
├── scheduler.py
├── scheduler_watch.py
├── test-pod.yaml
├── watch-deploy.yaml
├── screenshots/
│   ├── 01-cluster-created.png
│   ├── 02-default-scheduler-test.png
│   ├── 03-my-scheduler-running.png
│   ├── 04-pod-scheduled-by-my-scheduler.png
│   ├── 07-policy-extension-labels.png
│   └── 08-taint-aware-scheduler-result.png
└── README.md
```

##

---
