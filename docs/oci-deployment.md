# Despliegue en OCI Compute

Esta guía registra el despliegue verificado del MVP **DEL PINO Knowledge Agent** en Oracle Cloud Infrastructure. No contiene claves, credenciales, OCID, IP privada ni datos de facturación.

## Infraestructura

| Componente | Configuración |
|---|---|
| Servicio | OCI Compute |
| Sistema operativo | Ubuntu 24.04 LTS |
| Arquitectura | x86_64 |
| Shape | `VM.Standard.E2.1.Micro` |
| Aplicación | Streamlit |
| Puerto | TCP 8501 |
| Persistencia | `systemd` |
| Usuario | `ubuntu` |
| Directorio | `/home/ubuntu/del-pino-knowledge-agent` |

URL verificada durante el despliegue:

```text
http://161.153.216.80:8501
```

La URL debe comprobarse nuevamente antes de la entrega porque una instancia detenida o una IPv4 reasignada puede dejarla inaccesible.

## Red

La instancia utiliza una subred pública con IPv4 pública, Internet Gateway y ruta de salida. Se habilitaron:

- TCP 22 para SSH;
- TCP 8501 para Streamlit.

La imagen no tenía `ufw`. Se inspeccionó el firewall local mediante:

```bash
sudo iptables -S
sudo iptables -L -n -v --line-numbers
sudo iptables-save
```

El ruleset tenía un rechazo general al final de `INPUT`; se añadió la aceptación de TCP 8501 antes de esa regla y se persistió el cambio sin reemplazar las reglas de Oracle.

> Nunca reutilizar una posición numérica de `iptables` sin inspeccionar primero el ruleset actual.

## Preparación

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y git python3 python3-venv python3-pip

python3 --version
git --version
```

## Clonado e instalación

```bash
cd ~
git clone https://github.com/MachidelPino/del-pino-knowledge-agent.git
cd del-pino-knowledge-agent

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pip check
```

## Variables de entorno

Crear `/home/ubuntu/del-pino-knowledge-agent/.env`:

```env
GOOGLE_API_KEY=<CLAVE_REAL>
GEMINI_CHAT_MODEL=gemini-3.1-flash-lite
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
RAG_RELEVANCE_THRESHOLD=
```

Protegerlo y comprobar que Git lo ignore:

```bash
chmod 600 .env
git check-ignore -v .env
```

## Índice FAISS

```bash
python scripts/build_index.py
```

Resultado verificado:

- 3 PDF;
- 24 páginas;
- 45 fragmentos;
- índice en `storage/faiss_index`.

## Prueba manual

```bash
streamlit run app.py \
  --server.address=0.0.0.0 \
  --server.port=8501 \
  --server.headless=true
```

Health check:

```bash
curl http://localhost:8501/_stcore/health
```

Luego se verificó externamente una consulta respondible, una de fallback y una fronteriza.

## Servicio `systemd`

Archivo:

```text
/etc/systemd/system/del-pino-agent.service
```

Contenido:

```ini
[Unit]
Description=DEL PINO Knowledge Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/del-pino-knowledge-agent
EnvironmentFile=/home/ubuntu/del-pino-knowledge-agent/.env
ExecStart=/home/ubuntu/del-pino-knowledge-agent/.venv/bin/streamlit run app.py --server.address=0.0.0.0 --server.port=8501 --server.headless=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Activación:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now del-pino-agent
sudo systemctl status del-pino-agent
sudo journalctl -u del-pino-agent -n 100 --no-pager
```

## Persistencia

Se comprobó que la aplicación continuara activa después de cerrar SSH y de reiniciar la instancia.

Diagnóstico:

```bash
sudo systemctl status del-pino-agent
sudo journalctl -u del-pino-agent -n 50 --no-pager
curl http://localhost:8501/_stcore/health
```

## Actualización

Después de publicar cambios:

```bash
cd /home/ubuntu/del-pino-knowledge-agent
git pull --ff-only
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart del-pino-agent
sudo systemctl status del-pino-agent
```

Solo es necesario reconstruir el índice si cambian los PDF, la fragmentación o el modelo de embeddings.

## Evidencia y seguridad

La captura final debe guardarse en `assets/screenshots/oci-agent-response.png` y mostrar la URL pública, pregunta, respuesta y fuentes.

No publicar:

- API key;
- clave SSH;
- `.env`;
- OCID;
- IP privada;
- datos de cuenta o facturación.
