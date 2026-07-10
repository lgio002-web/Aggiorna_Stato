"""
============================================================================
 Dashboard Certificazioni Sistemi - Poste Italiane
============================================================================
 Applicazione web Full CRUD realizzata con Streamlit per la gestione dello
 stato di certificazione dei sistemi software.

 - Database: SQLite locale (certificazioni.db), inizializzato automaticamente
 - UI/UX: stile moderno ispirato a Figma con branding Poste Italiane
 - Funzionalita': Create, Read, Update, Delete (CRUD completo)
 - Pronta per il deploy su Streamlit Community Cloud

 Avvio locale:  streamlit run app.py
============================================================================
"""

import os
import sqlite3
from datetime import date, datetime

import pandas as pd
import streamlit as st

# ============================================================================
# 1. COSTANTI E CONFIGURAZIONE GLOBALE
# ============================================================================

# Percorso del database: sempre nella stessa cartella di questo file.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certificazioni.db")

# Colori istituzionali Poste Italiane
POSTE_GIALLO = "#FFCC00"
POSTE_BLU = "#003399"

# Valori predefiniti per i menu a tendina (selectbox)
STATI_STS = [
    "In Esecuzione",
    "ND",
    "Completato",
    "In Attesa",
    "Sospeso",
    "Pianificato",
    "Ripianificato",
    "",
]
STATI_KIT = [
    "Consegnato",
    "Kit non consegnato",
    "No Certificazione BE",
    "In lavorazione",
    "ND",
]

# Dati di mockup iniziali: vuoti. Il database NON viene piu' precaricato con
# dati di esempio; conserva solo i record realmente inseriti dall'utente.
DATI_MOCKUP = []


# ============================================================================
# 2. LIVELLO DATI (SQLite) - Funzioni di accesso al database
# ============================================================================

def get_connection():
    """Restituisce una connessione al database SQLite.

    check_same_thread=False permette l'uso della connessione con il modello
    di esecuzione multi-thread di Streamlit.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crea la tabella 'sistemi' se non esiste e inserisce i dati di mockup
    solo al primissimo avvio (quando la tabella e' vuota)."""
    conn = get_connection()
    cur = conn.cursor()

    # Creazione tabella con tutti i campi richiesti.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sistemi (
            id                          INTEGER PRIMARY KEY AUTOINCREMENT,
            sistema                     TEXT NOT NULL,
            iniziativa                  TEXT,
            data_inizio_certificazione  TEXT,
            data_fine_certificazione    TEXT,
            data_consegna_kit           TEXT,
            stato_sts                   TEXT,
            note                        TEXT,
            classificazione             TEXT DEFAULT ''
        )
        """
    )
    conn.commit()

    # Migrazione: aggiunge la colonna 'classificazione' ai DB gia' esistenti.
    cur.execute("PRAGMA table_info(sistemi)")
    colonne = [r["name"] for r in cur.fetchall()]
    if "classificazione" not in colonne:
        cur.execute("ALTER TABLE sistemi ADD COLUMN classificazione TEXT DEFAULT ''")
        conn.commit()

    # Tabella per la tracciatura degli accessi/visite (analytics).
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS accessi (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp    TEXT,
            ip           TEXT,
            user_agent   TEXT,
            piattaforma  TEXT
        )
        """
    )
    conn.commit()

    # Popolamento iniziale con i dati di mockup se la tabella e' vuota.
    cur.execute("SELECT COUNT(*) AS n FROM sistemi")
    if cur.fetchone()["n"] == 0:
        for riga in DATI_MOCKUP:
            cur.execute(
                """
                INSERT INTO sistemi
                    (sistema, iniziativa, data_inizio_certificazione,
                     data_fine_certificazione, data_consegna_kit, stato_sts,
                     note, classificazione)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    riga["sistema"],
                    riga["iniziativa"],
                    riga["data_inizio_certificazione"],
                    riga["data_fine_certificazione"],
                    riga["data_consegna_kit"],
                    riga["stato_sts"],
                    riga["note"],
                    riga.get("classificazione", ""),
                ),
            )
        conn.commit()

    conn.close()


def ripristina_dati_iniziali():
    """Svuota completamente la tabella e ricarica TUTTI i dati di DATI_MOCKUP.

    Utile per riportare il database esattamente all'elenco iniziale (Excel),
    scartando eventuali modifiche apportate tramite l'interfaccia."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sistemi")
    # Azzera anche il contatore degli id per ripartire da 1.
    cur.execute("DELETE FROM sqlite_sequence WHERE name = 'sistemi'")
    for riga in DATI_MOCKUP:
        cur.execute(
            """
            INSERT INTO sistemi
                (sistema, iniziativa, data_inizio_certificazione,
                 data_fine_certificazione, data_consegna_kit, stato_sts,
                 note, classificazione)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                riga["sistema"],
                riga["iniziativa"],
                riga["data_inizio_certificazione"],
                riga["data_fine_certificazione"],
                riga["data_consegna_kit"],
                riga["stato_sts"],
                riga["note"],
                riga.get("classificazione", ""),
            ),
        )
    conn.commit()
    conn.close()


def leggi_sistemi():
    """READ: legge tutti i record dalla tabella e li restituisce come DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM sistemi ORDER BY id ASC", conn)
    conn.close()
    return df


def inserisci_sistema(dati: dict):
    """CREATE: inserisce un nuovo record nel database."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO sistemi
            (sistema, iniziativa, data_inizio_certificazione,
             data_fine_certificazione, data_consegna_kit, stato_sts,
             note, classificazione)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            dati["sistema"],
            dati["iniziativa"],
            dati["data_inizio_certificazione"],
            dati["data_fine_certificazione"],
            dati["data_consegna_kit"],
            dati["stato_sts"],
            dati["note"],
            dati.get("classificazione", ""),
        ),
    )
    conn.commit()
    conn.close()


def aggiorna_sistema(record_id: int, dati: dict):
    """UPDATE: aggiorna un record esistente identificato dal suo id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE sistemi SET
            sistema = ?,
            iniziativa = ?,
            data_inizio_certificazione = ?,
            data_fine_certificazione = ?,
            data_consegna_kit = ?,
            stato_sts = ?,
            note = ?,
            classificazione = ?
        WHERE id = ?
        """,
        (
            dati["sistema"],
            dati["iniziativa"],
            dati["data_inizio_certificazione"],
            dati["data_fine_certificazione"],
            dati["data_consegna_kit"],
            dati["stato_sts"],
            dati["note"],
            dati.get("classificazione", ""),
            record_id,
        ),
    )
    conn.commit()
    conn.close()


def elimina_sistema(record_id: int):
    """DELETE: rimuove un record dal database tramite il suo id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sistemi WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


def svuota_database():
    """Elimina definitivamente TUTTI i record dal database.

    Utile per ripulire dati di esempio residui (es. sull'istanza cloud) e
    ripartire da zero. Il database resta vuoto finche' non si inseriscono
    nuovi record (nessun ricaricamento automatico di dati di esempio)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sistemi")
    cur.execute("DELETE FROM sqlite_sequence WHERE name = 'sistemi'")
    conn.commit()
    conn.close()


# ============================================================================
# 3. FUNZIONI DI SUPPORTO (parsing date, formattazione, tracciatura)
# ============================================================================

def rileva_piattaforma(user_agent: str) -> str:
    """Deduce la piattaforma/sistema operativo dal campo User-Agent."""
    ua = (user_agent or "").lower()
    if "iphone" in ua:
        return "iPhone"
    if "ipad" in ua:
        return "iPad"
    if "android" in ua:
        return "Android"
    if "windows" in ua:
        return "Windows"
    if "macintosh" in ua or "mac os" in ua:
        return "Mac"
    if "cros" in ua:
        return "ChromeOS"
    if "linux" in ua:
        return "Linux"
    return "Altro"


def info_client():
    """Ricava (ip, user_agent, piattaforma) del client dalla richiesta HTTP.

    Usa gli header esposti da Streamlit. Dietro proxy/cloud l'IP reale e' in
    'X-Forwarded-For'. Se non disponibile, restituisce valori di fallback."""
    ip = "sconosciuto"
    ua = ""
    try:
        headers = dict(st.context.headers or {})
        # Gli header sono case-insensitive: normalizziamo le chiavi.
        headers = {k.lower(): v for k, v in headers.items()}
        ua = headers.get("user-agent", "") or ""
        xff = headers.get("x-forwarded-for", "")
        if xff:
            ip = xff.split(",")[0].strip()
        elif headers.get("x-real-ip"):
            ip = headers["x-real-ip"].strip()
    except Exception:
        pass
    return ip, ua, rileva_piattaforma(ua)


def registra_accesso():
    """Registra un accesso una sola volta per sessione utente."""
    if st.session_state.get("_accesso_registrato"):
        return
    ip, ua, piattaforma = info_client()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO accessi (timestamp, ip, user_agent, piattaforma) VALUES (?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ip, ua, piattaforma),
    )
    conn.commit()
    conn.close()
    st.session_state._accesso_registrato = True


def leggi_accessi() -> pd.DataFrame:
    """Restituisce tutti gli accessi registrati come DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM accessi ORDER BY id DESC", conn)
    conn.close()
    return df


def parse_data(valore: str):
    """Prova a convertire una stringa in oggetto date.

    Accetta sia il formato GG-MM-AAAA sia YYYY-MM-DD (per compatibilita').
    Restituisce un oggetto date se possibile, altrimenti None (utile per
    gestire valori testuali come 'Kit non consegnato')."""
    if not valore:
        return None
    for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(valore).strip(), fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def is_valore_critico(valore: str) -> bool:
    """Ritorna True se il valore rappresenta una condizione critica/di attenzione."""
    if valore is None:
        return False
    testo = str(valore).lower()
    parole_critiche = ["non consegnato", "no certificazione", "nd", "sospeso"]
    return any(p in testo for p in parole_critiche)


# ============================================================================
# 4. STILE (CSS personalizzato in stile Figma + branding Poste Italiane)
# ============================================================================

def inietta_css():
    """Inietta il CSS personalizzato per un look moderno e coerente col brand."""
    st.markdown(
        f"""
        <style>
        /* --- Import font moderno --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        /* --- Sfondo generale elegante --- */
        .stApp {{
            background: linear-gradient(180deg, #f4f6fb 0%, #eaeef7 100%);
        }}

        /* --- Larghezza pagina: usa tutto lo spazio disponibile --- */
        .block-container {{
            max-width: 100% !important;
            padding-left: 2.2rem !important;
            padding-right: 2.2rem !important;
            padding-top: 2rem !important;
        }}
        /* Consenti lo scroll orizzontale della tabella quando serve. */
        [data-testid="stDataFrame"], [data-testid="stDataEditor"] {{
            width: 100% !important;
            overflow-x: auto !important;
        }}

        /* --- Header brandizzato Poste Italiane --- */
        .poste-header {{
            background: linear-gradient(135deg, {POSTE_BLU} 0%, #0047b3 100%);
            padding: 26px 34px;
            border-radius: 16px;
            margin-bottom: 26px;
            box-shadow: 0 8px 24px rgba(0, 51, 153, 0.25);
            display: flex;
            align-items: center;
            gap: 22px;
            border-left: 8px solid {POSTE_GIALLO};
        }}
        .poste-logo {{
            width: 62px;
            height: 62px;
            background: {POSTE_GIALLO};
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 26px;
            color: {POSTE_BLU};
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            flex-shrink: 0;
        }}
        .poste-title-block h1 {{
            color: #ffffff;
            margin: 0;
            font-size: 27px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }}
        .poste-title-block p {{
            color: {POSTE_GIALLO};
            margin: 4px 0 0 0;
            font-size: 14px;
            font-weight: 500;
        }}

        /* --- Card metriche (KPI) --- */
        .metric-card {{
            background: #ffffff;
            border-radius: 14px;
            padding: 18px 22px;
            box-shadow: 0 4px 16px rgba(0, 51, 153, 0.08);
            border-top: 4px solid {POSTE_BLU};
            text-align: center;
        }}
        .metric-card .valore {{
            font-size: 30px;
            font-weight: 800;
            color: {POSTE_BLU};
        }}
        .metric-card .etichetta {{
            font-size: 13px;
            color: #5a6473;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* --- Titoli di sezione --- */
        .section-title {{
            color: {POSTE_BLU};
            font-weight: 700;
            font-size: 20px;
            margin: 8px 0 12px 0;
            padding-bottom: 8px;
            border-bottom: 3px solid {POSTE_GIALLO};
            display: inline-block;
        }}

        /* --- Bottoni --- */
        .stButton > button {{
            background: {POSTE_BLU};
            color: #ffffff;
            border: none;
            border-radius: 10px;
            padding: 8px 20px;
            font-weight: 600;
            transition: all 0.2s ease-in-out;
        }}
        .stButton > button:hover {{
            background: {POSTE_GIALLO};
            color: {POSTE_BLU};
            transform: translateY(-1px);
        }}

        /* --- Tab styling --- */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 6px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background: #ffffff;
            border-radius: 10px 10px 0 0;
            padding: 10px 20px;
            font-weight: 600;
            color: {POSTE_BLU};
        }}
        .stTabs [aria-selected="true"] {{
            background: {POSTE_BLU};
            color: #ffffff !important;
        }}

        /* --- Sidebar --- */
        [data-testid="stSidebar"] {{
            background: #ffffff;
            border-right: 3px solid {POSTE_GIALLO};
        }}
        /* Testo della sidebar sempre scuro e leggibile sul fondo bianco. */
        [data-testid="stSidebar"] * {{
            color: #1f2937 !important;
        }}
        [data-testid="stSidebar"] .section-title {{
            color: {POSTE_BLU} !important;
        }}
        [data-testid="stSidebar"] strong,
        [data-testid="stSidebar"] b {{
            color: {POSTE_BLU} !important;
        }}
        /* Valore delle metriche (numero grande) in blu istituzionale. */
        [data-testid="stSidebar"] [data-testid="stMetricValue"] {{
            color: {POSTE_BLU} !important;
        }}

        /* --- Footer --- */
        .poste-footer {{
            text-align: center;
            color: #8a94a6;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 16px;
            border-top: 1px solid #d9dfea;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    """Renderizza l'header brandizzato con logo stilizzato Poste Italiane."""
    st.markdown(
        """
        <div class="poste-header">
            <div class="poste-logo">PT</div>
            <div class="poste-title-block">
                <h1>Dashboard Certificazioni Sistemi</h1>
                <p>Poste Italiane &nbsp;|&nbsp; Monitoraggio stato certificazione software</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
# 5. COMPONENTI UI - Sezioni CRUD
# ============================================================================

def render_kpi(df: pd.DataFrame):
    """Mostra alcune metriche di sintesi (KPI) in card eleganti."""
    totale = len(df)
    completati = int((df["stato_sts"] == "Completato").sum()) if totale else 0
    in_esecuzione = int((df["stato_sts"] == "In Esecuzione").sum()) if totale else 0
    critici = int(df["data_consegna_kit"].apply(is_valore_critico).sum()) if totale else 0

    col1, col2, col3, col4 = st.columns(4)
    for col, valore, etichetta in [
        (col1, totale, "Sistemi Totali"),
        (col2, in_esecuzione, "In Esecuzione"),
        (col3, completati, "Completati"),
        (col4, critici, "Da Attenzionare"),
    ]:
        col.markdown(
            f"""
            <div class="metric-card">
                <div class="valore">{valore}</div>
                <div class="etichetta">{etichetta}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def evidenzia_righe(row: pd.Series):
    """Formattazione condizionale: colora le righe con valori critici.

    - Rosso tenue per condizioni critiche (kit non consegnato, ND...).
    - Verde tenue per i completati.
    """
    stile = [""] * len(row)
    if is_valore_critico(row.get("data_consegna_kit")) or is_valore_critico(row.get("stato_sts")):
        stile = ["background-color: #ffe0e0"] * len(row)  # rosso tenue
    elif str(row.get("stato_sts")).lower() == "completato":
        stile = ["background-color: #e2f7e5"] * len(row)  # verde tenue
    return stile


def sezione_read(df: pd.DataFrame):
    """READ + EDIT: unica tabella editabile con salvataggio automatico su DB.

    Tutti i campi sono modificabili direttamente nella tabella (tranne l'ID,
    che identifica il record). I record "verdi" vengono mostrati per primi,
    ordinati per data di consegna kit dal piu' recente. Le colonne sono
    ordinabili/filtrabili cliccando sull'intestazione."""
    st.markdown('<div class="section-title">Elenco Certificazioni</div>', unsafe_allow_html=True)

    if df.empty:
        st.info("Nessun record presente. Aggiungi una riga con il pulsante **+** in fondo alla tabella.")
        # Mostra comunque un editor vuoto per consentire l'inserimento.
        df = pd.DataFrame(
            columns=[
                "id", "sistema", "iniziativa", "data_inizio_certificazione",
                "data_fine_certificazione", "data_consegna_kit", "stato_sts",
                "note", "classificazione",
            ]
        )

    st.caption(
        "✏️ Modifica le celle **oppure aggiungi nuove righe** con il pulsante **+** "
        "in fondo alla tabella: **ogni modifica viene salvata automaticamente**. "
        "La colonna **Stato** (🔴/🟢) puoi impostarla tu manualmente; se la lasci vuota "
        "viene calcolata in automatico. Clicca sull'intestazione di una colonna per "
        "**ordinare/filtrare** (testo e date). Date nel formato **GG-MM-AAAA**."
    )

    # --- Calcolo del pallino (verde/rosso) per ogni riga ---
    def _pallino(r):
        cls = str(r.get("classificazione") or "").strip()
        if cls in ("🟢", "🔴"):
            return cls
        critico = is_valore_critico(r.get("data_consegna_kit")) or is_valore_critico(r.get("stato_sts"))
        return "🔴" if critico else "🟢"

    df_ord = df.copy().reset_index(drop=True)
    df_ord["stato_visivo"] = df_ord.apply(_pallino, axis=1)
    # Chiave di ordinamento sulla data di consegna kit (le righe senza data
    # valida finiscono in fondo tra i verdi).
    df_ord["_kit_dt"] = df_ord["data_consegna_kit"].apply(
        lambda v: parse_data(v) or date.min
    )
    # I verdi (0) prima dei rossi (1); tra i verdi, data consegna kit decrescente.
    df_ord["_is_rosso"] = (df_ord["stato_visivo"] == "🔴").astype(int)
    df_ord = df_ord.sort_values(
        by=["_is_rosso", "_kit_dt"], ascending=[True, False], kind="stable"
    ).reset_index(drop=True)
    df_ord = df_ord.drop(columns=["_kit_dt", "_is_rosso"])

    # Colonna con la numerazione progressiva delle righe.
    df_ord.insert(0, "n_riga", range(1, len(df_ord) + 1))

    # Le due colonne pienamente "data" vengono convertite a datetime cosi'
    # l'ordinamento avviene cronologicamente (non alfabeticamente).
    for col in ("data_inizio_certificazione", "data_fine_certificazione"):
        df_ord[col] = df_ord[col].apply(
            lambda v: (pd.Timestamp(parse_data(v)) if parse_data(v) else pd.NaT)
        )

    df_edit = df_ord

    # Chiave dinamica dell'editor: si rigenera dopo ogni salvataggio automatico
    # per azzerare lo stato interno del widget ed evitare inserimenti duplicati.
    if "editor_rev" not in st.session_state:
        st.session_state.editor_rev = 0

    tabella_modificata = st.data_editor(
        df_edit,
        use_container_width=True,
        hide_index=True,
        height=760,
        num_rows="dynamic",
        key=f"editor_certificazioni_{st.session_state.editor_rev}",
        # column_order esclude 'id' e mette N. e Stato come prime colonne.
        column_order=[
            "n_riga",
            "stato_visivo",
            "sistema",
            "iniziativa",
            "data_inizio_certificazione",
            "data_fine_certificazione",
            "data_consegna_kit",
            "stato_sts",
            "note",
        ],
        column_config={
            "n_riga": st.column_config.NumberColumn(
                "N.", width="small", disabled=True, help="Numero progressivo di riga"
            ),
            "stato_visivo": st.column_config.SelectboxColumn(
                "Stato", options=["🟢", "🔴"], width="small",
                help="Classifica manualmente: 🔴 da attenzionare · 🟢 regolare",
            ),
            "sistema": st.column_config.TextColumn("Sistema", required=True, width="medium"),
            "iniziativa": st.column_config.TextColumn("Iniziativa", width="medium"),
            "data_inizio_certificazione": st.column_config.DateColumn(
                "Inizio Cert.", format="DD-MM-YYYY", help="Ordinabile per data"
            ),
            "data_fine_certificazione": st.column_config.DateColumn(
                "Fine Cert.", format="DD-MM-YYYY", help="Ordinabile per data"
            ),
            "data_consegna_kit": st.column_config.TextColumn(
                "Consegna Kit", width="medium",
                help="Data (GG-MM-AAAA) o testo (es. 'Kit non consegnato')"
            ),
            "stato_sts": st.column_config.SelectboxColumn(
                "Stato STS", options=STATI_STS
            ),
            "note": st.column_config.TextColumn("Note", width="large"),
        },
    )

    # Salvataggio automatico: appena una cella o una riga viene modificata
    # (o eliminata), la variazione viene subito scritta nel database.
    n_agg, n_new, n_del = salva_modifiche_tabella(df_edit, tabella_modificata)
    if n_agg or n_new or n_del:
        st.session_state.editor_rev += 1
        st.rerun()

    st.caption(
        f"Totale: {len(df_edit)} sistemi · 💾 salvataggio automatico attivo · "
        "🟢 verdi ordinati per data consegna kit (dal piu' recente)."
    )


def salva_modifiche_tabella(df_originale: pd.DataFrame, df_modificato: pd.DataFrame):
    """Salva le modifiche della tabella nel database.

    - Le righe esistenti (con ID) vengono aggiornate se cambiate.
    - Le righe nuove (senza ID, aggiunte dall'utente) vengono inserite.
    - Le righe rimosse dalla tabella vengono eliminate definitivamente dal DB.
    Restituisce una tupla (n_aggiornati, n_nuovi, n_eliminati)."""
    campi = [
        "sistema",
        "iniziativa",
        "data_inizio_certificazione",
        "data_fine_certificazione",
        "data_consegna_kit",
        "stato_sts",
        "note",
    ]
    # Indicizza le righe originali per ID per un confronto rapido.
    orig_by_id = {
        int(r["id"]): r
        for _, r in df_originale.iterrows()
        if not pd.isna(r["id"])
    }

    def _fmt(campo, valore):
        """Normalizza il valore di una cella in stringa per il salvataggio.

        Le colonne data (datetime dall'editor) vengono formattate GG-MM-AAAA."""
        if valore is None or (not isinstance(valore, str) and pd.isna(valore)):
            return ""
        if campo in ("data_inizio_certificazione", "data_fine_certificazione"):
            if isinstance(valore, (pd.Timestamp, datetime, date)):
                return valore.strftime("%d-%m-%Y")
            d = parse_data(valore)
            return d.strftime("%d-%m-%Y") if d else str(valore)
        return str(valore)

    n_aggiornati = 0
    n_nuovi = 0
    id_presenti = set()
    for _, riga in df_modificato.iterrows():
        rid = riga.get("id")
        dati = {c: _fmt(c, riga.get(c)) for c in campi}
        # La colonna 'stato_visivo' (pallino) viene salvata come classificazione manuale.
        dati["classificazione"] = "" if pd.isna(riga.get("stato_visivo")) else str(riga.get("stato_visivo"))

        if pd.isna(rid) or str(rid).strip() == "":
            # Riga nuova: inserisci solo se e' stato indicato almeno il Sistema.
            if dati["sistema"].strip():
                inserisci_sistema(dati)
                n_nuovi += 1
        else:
            id_presenti.add(int(rid))
            # Riga esistente: aggiorna se un campo o la classificazione sono cambiati.
            riga_old = orig_by_id.get(int(rid))
            if riga_old is not None and any(
                str(riga.get(c)) != str(riga_old[c]) for c in campi + ["stato_visivo"]
            ):
                aggiorna_sistema(int(rid), dati)
                n_aggiornati += 1

    # Cancellazione definitiva: gli ID presenti in origine ma non piu' nella
    # tabella modificata (righe rimosse dall'utente) vengono eliminati dal DB.
    n_eliminati = 0
    for rid_orig in orig_by_id:
        if rid_orig not in id_presenti:
            elimina_sistema(rid_orig)
            n_eliminati += 1

    return n_aggiornati, n_nuovi, n_eliminati


def sezione_create():
    """CREATE: form per l'inserimento di un nuovo sistema con validazione."""
    st.markdown('<div class="section-title">Aggiungi Nuovo Sistema</div>', unsafe_allow_html=True)

    with st.form("form_nuovo_sistema", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sistema = st.text_input("Sistema *", placeholder="Es: Corriere Espresso")
            iniziativa = st.text_input("Iniziativa", placeholder="Es: 143248, 141780")
            data_inizio = st.date_input("Data Inizio Certificazione", value=date.today())
            data_fine = st.date_input("Data Fine Certificazione", value=date.today())
        with col2:
            stato_sts = st.selectbox("Stato STS *", STATI_STS)
            tipo_kit = st.radio(
                "Consegna Kit",
                ["Data specifica", "Stato testuale"],
                horizontal=True,
            )
            if tipo_kit == "Data specifica":
                data_kit_valore = st.date_input("Data Consegna Kit", value=date.today())
                data_consegna_kit = data_kit_valore.strftime("%d-%m-%Y")
            else:
                data_consegna_kit = st.selectbox("Stato Consegna Kit", STATI_KIT)
            note = st.text_area("Note", placeholder="Annotazioni opzionali...")

        inviato = st.form_submit_button("➕ Aggiungi Sistema")

    if inviato:
        # Validazione dei dati obbligatori.
        if not sistema.strip():
            st.error("Il campo 'Sistema' e' obbligatorio.")
            return
        if data_fine < data_inizio:
            st.error("La data di fine certificazione non puo' precedere quella di inizio.")
            return

        dati = {
            "sistema": sistema.strip(),
            "iniziativa": iniziativa.strip(),
            "data_inizio_certificazione": data_inizio.strftime("%d-%m-%Y"),
            "data_fine_certificazione": data_fine.strftime("%d-%m-%Y"),
            "data_consegna_kit": data_consegna_kit,
            "stato_sts": stato_sts,
            "note": note.strip(),
        }
        inserisci_sistema(dati)
        st.success(f"Sistema '{sistema}' aggiunto con successo!")
        st.rerun()


def sezione_update(df: pd.DataFrame):
    """UPDATE: selezione di un record esistente e modifica dei suoi campi."""
    st.markdown('<div class="section-title">Modifica Sistema Esistente</div>', unsafe_allow_html=True)

    if df.empty:
        st.info("Nessun sistema presente da modificare.")
        return

    # Selezione del record tramite menu a tendina (nome sistema + id).
    opzioni = {f"{r['sistema']} (ID {r['id']})": r["id"] for _, r in df.iterrows()}
    scelta = st.selectbox("Seleziona il Sistema da modificare", list(opzioni.keys()))
    record_id = opzioni[scelta]
    record = df[df["id"] == record_id].iloc[0]

    with st.form("form_modifica_sistema"):
        col1, col2 = st.columns(2)
        with col1:
            sistema = st.text_input("Sistema *", value=record["sistema"])
            iniziativa = st.text_input("Iniziativa", value=record["iniziativa"] or "")

            data_inizio_val = parse_data(record["data_inizio_certificazione"]) or date.today()
            data_inizio = st.date_input("Data Inizio Certificazione", value=data_inizio_val)

            data_fine_val = parse_data(record["data_fine_certificazione"]) or date.today()
            data_fine = st.date_input("Data Fine Certificazione", value=data_fine_val)
        with col2:
            # Stato STS con selectbox preimpostato sul valore corrente.
            stato_corrente = record["stato_sts"] if record["stato_sts"] in STATI_STS else STATI_STS[0]
            stato_sts = st.selectbox(
                "Stato STS *", STATI_STS, index=STATI_STS.index(stato_corrente)
            )

            # Gestione Consegna Kit: data oppure stato testuale.
            kit_corrente = record["data_consegna_kit"]
            kit_e_data = parse_data(kit_corrente) is not None
            tipo_kit = st.radio(
                "Consegna Kit",
                ["Data specifica", "Stato testuale"],
                horizontal=True,
                index=0 if kit_e_data else 1,
            )
            if tipo_kit == "Data specifica":
                data_kit_val = parse_data(kit_corrente) or date.today()
                data_kit_input = st.date_input("Data Consegna Kit", value=data_kit_val)
                data_consegna_kit = data_kit_input.strftime("%d-%m-%Y")
            else:
                idx_kit = STATI_KIT.index(kit_corrente) if kit_corrente in STATI_KIT else 0
                data_consegna_kit = st.selectbox("Stato Consegna Kit", STATI_KIT, index=idx_kit)

            note = st.text_area("Note", value=record["note"] or "")

        salvato = st.form_submit_button("💾 Salva Modifiche")

    if salvato:
        if not sistema.strip():
            st.error("Il campo 'Sistema' e' obbligatorio.")
            return
        if data_fine < data_inizio:
            st.error("La data di fine certificazione non puo' precedere quella di inizio.")
            return

        dati = {
            "sistema": sistema.strip(),
            "iniziativa": iniziativa.strip(),
            "data_inizio_certificazione": data_inizio.strftime("%d-%m-%Y"),
            "data_fine_certificazione": data_fine.strftime("%d-%m-%Y"),
            "data_consegna_kit": data_consegna_kit,
            "stato_sts": stato_sts,
            "note": note.strip(),
            "classificazione": record["classificazione"] if "classificazione" in record else "",
        }
        aggiorna_sistema(int(record_id), dati)
        st.success(f"Sistema '{sistema}' aggiornato con successo!")
        st.rerun()


def sezione_delete(df: pd.DataFrame):
    """DELETE: eliminazione protetta di un record con checkbox di conferma."""
    st.markdown('<div class="section-title">Elimina Sistema</div>', unsafe_allow_html=True)

    if df.empty:
        st.info("Nessun sistema presente da eliminare.")
        return

    opzioni = {f"{r['sistema']} (ID {r['id']})": r["id"] for _, r in df.iterrows()}
    scelta = st.selectbox("Seleziona il Sistema da eliminare", list(opzioni.keys()))
    record_id = opzioni[scelta]
    record = df[df["id"] == record_id].iloc[0]

    # Anteprima del record selezionato.
    st.warning(
        f"Stai per eliminare: **{record['sistema']}** "
        f"(Iniziativa: {record['iniziativa'] or 'N/D'} | Stato: {record['stato_sts']})"
    )

    conferma = st.checkbox("Voglio eliminare questo record in modo permanente")
    if st.button("🗑️ Elimina Definitivamente", disabled=not conferma):
        elimina_sistema(int(record_id))
        st.success(f"Sistema '{record['sistema']}' eliminato con successo.")
        st.rerun()


def render_statistiche_accessi():
    """Menu nascosto in basso: statistiche di visita/accesso.

    Cliccando sull'expander si "esplodono" i dati di tracciatura: numero di
    accessi totali, visitatori univoci (per IP) e dettaglio per piattaforma
    (Windows, Mac, Android, iPhone, ...)."""
    st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
    with st.expander("· · ·  Statistiche accessi (riservato)"):
        df_acc = leggi_accessi()

        if df_acc.empty:
            st.info("Nessun accesso registrato finora.")
            return

        totale = len(df_acc)
        ip_validi = df_acc[df_acc["ip"] != "sconosciuto"]["ip"]
        univoci = ip_validi.nunique()
        # Se nessun IP e' rilevabile (es. esecuzione locale) mostriamo almeno
        # il numero di sessioni distinte come approssimazione.
        if univoci == 0:
            univoci = totale

        c1, c2, c3 = st.columns(3)
        c1.metric("Accessi totali", totale)
        c2.metric("Visitatori univoci (IP)", univoci)
        c3.metric("Piattaforme diverse", df_acc["piattaforma"].nunique())

        st.markdown("**Accessi per piattaforma**")
        per_piatt = (
            df_acc.groupby("piattaforma")
            .agg(
                accessi=("id", "count"),
                ip_univoci=("ip", lambda s: s[s != "sconosciuto"].nunique()),
            )
            .reset_index()
            .sort_values("accessi", ascending=False)
        )
        per_piatt.columns = ["Piattaforma", "Accessi", "IP univoci"]
        st.dataframe(per_piatt, use_container_width=True, hide_index=True)
        st.bar_chart(per_piatt.set_index("Piattaforma")["Accessi"])

        st.markdown("**Ultimi accessi**")
        recenti = df_acc[["timestamp", "piattaforma", "ip"]].head(15).copy()
        recenti.columns = ["Data/Ora", "Piattaforma", "IP"]
        st.dataframe(recenti, use_container_width=True, hide_index=True)


# ============================================================================
# 6. FUNZIONE PRINCIPALE
# ============================================================================

def main():
    # Configurazione pagina in modalita' wide.
    st.set_page_config(
        page_title="Dashboard Certificazioni - Poste Italiane",
        page_icon="📮",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Inizializzazione DB e stile.
    init_db()
    inietta_css()
    # Registra l'accesso (una volta per sessione) per le statistiche di visita.
    registra_accesso()
    render_header()

    # Caricamento dati.
    df = leggi_sistemi()

    # --- Unica vista: elenco editabile (nessun menu rapido, nessuna sidebar) ---
    sezione_read(df)

    # --- Menu nascosto in basso con le statistiche di tracciatura ---
    render_statistiche_accessi()

    # Footer.
    st.markdown(
        f"""
        <div class="poste-footer">
            © {date.today().year} Poste Italiane S.p.A. — Dashboard Certificazioni Sistemi.
            Realizzata con Streamlit.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
