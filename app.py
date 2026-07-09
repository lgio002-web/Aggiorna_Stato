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

# Dati di mockup iniziali (usati solo al primo avvio con DB vuoto).
# Dati reali forniti: date convertite da GG/MM/AAAA a AAAA-MM-GG.
DATI_MOCKUP = [
    {
        "sistema": "Corriere Espresso",
        "iniziativa": "143248, 141780, 143247",
        "data_inizio_certificazione": "2026-06-22",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "Kit non consegnato",
        "stato_sts": "In Esecuzione",
        "note": "",
    },
    {
        "sistema": "GPL Routing",
        "iniziativa": "141696",
        "data_inizio_certificazione": "2026-06-22",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "Kit non consegnato",
        "stato_sts": "In Esecuzione",
        "note": "",
    },
    {
        "sistema": "Mediation",
        "iniziativa": "141780",
        "data_inizio_certificazione": "2026-06-22",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "2026-07-09",
        "stato_sts": "In Esecuzione",
        "note": "",
    },
    {
        "sistema": "MLP - Servizi di backend MLP MLC",
        "iniziativa": "141708, 141696",
        "data_inizio_certificazione": "2026-06-22",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "No Certificazione BE",
        "stato_sts": "In Esecuzione",
        "note": "141696 In Esecuzione; No Certificazione BE",
    },
    {
        "sistema": "Seguimi 2",
        "iniziativa": "143999",
        "data_inizio_certificazione": "2026-06-22",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "Kit non consegnato",
        "stato_sts": "",
        "note": "Ripianificato",
    },
    {
        "sistema": "ROAD",
        "iniziativa": "141646",
        "data_inizio_certificazione": "2026-07-06",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "Kit non consegnato",
        "stato_sts": "ND",
        "note": "Iniziativa Semplice",
    },
    {
        "sistema": "TTREPO",
        "iniziativa": "143248",
        "data_inizio_certificazione": "2026-06-22",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "2026-06-29",
        "stato_sts": "In Esecuzione",
        "note": "",
    },
    {
        "sistema": "GME SFI",
        "iniziativa": "144286",
        "data_inizio_certificazione": "2026-06-22",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "2026-06-22",
        "stato_sts": "",
        "note": "",
    },
    {
        "sistema": "GME MEP",
        "iniziativa": "142430, 144286",
        "data_inizio_certificazione": "2026-06-22",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "2026-06-23",
        "stato_sts": "",
        "note": "",
    },
    {
        "sistema": "MLP APP MLC",
        "iniziativa": "142230, 141708, 144011, 141696, 143248",
        "data_inizio_certificazione": "2026-06-22",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "2026-06-30",
        "stato_sts": "",
        "note": "",
    },
    {
        "sistema": "MLP - Servizi di backend MLP SDA",
        "iniziativa": "141780",
        "data_inizio_certificazione": "2026-06-22",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "2026-06-30",
        "stato_sts": "",
        "note": "",
    },
    {
        "sistema": "T&T SDA",
        "iniziativa": "141780, 143248",
        "data_inizio_certificazione": "2026-06-22",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "2026-07-02",
        "stato_sts": "",
        "note": "",
    },
    {
        "sistema": "Click&Collect",
        "iniziativa": "141696",
        "data_inizio_certificazione": "2026-06-22",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "2026-07-06",
        "stato_sts": "",
        "note": "",
    },
    {
        "sistema": "SAP HANA",
        "iniziativa": "142230",
        "data_inizio_certificazione": "2026-06-22",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "2026-07-06",
        "stato_sts": "",
        "note": "",
    },
    {
        "sistema": "BEP",
        "iniziativa": "141780",
        "data_inizio_certificazione": "2026-06-22",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "2026-07-07",
        "stato_sts": "",
        "note": "",
    },
    {
        "sistema": "MLP - APP SDA",
        "iniziativa": "141780, 143248",
        "data_inizio_certificazione": "2026-06-22",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "2026-07-07",
        "stato_sts": "",
        "note": "",
    },
    {
        "sistema": "NPSO",
        "iniziativa": "138512",
        "data_inizio_certificazione": "2026-06-22",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "2026-07-07",
        "stato_sts": "",
        "note": "",
    },
    {
        "sistema": "T&T 2.0",
        "iniziativa": "138512, 141696, 144248, 141780, 142230, 143248",
        "data_inizio_certificazione": "2026-06-22",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "2026-07-09",
        "stato_sts": "",
        "note": "",
    },
    {
        "sistema": "T&T OLD",
        "iniziativa": "138512, 141780, 142230, 143248",
        "data_inizio_certificazione": "2026-06-22",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "2026-07-09",
        "stato_sts": "",
        "note": "",
    },
    {
        "sistema": "GEOPLUS",
        "iniziativa": "141646",
        "data_inizio_certificazione": "2026-07-06",
        "data_fine_certificazione": "2026-07-10",
        "data_consegna_kit": "2026-07-09",
        "stato_sts": "",
        "note": "",
    },
]


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
            note                        TEXT
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
                     data_fine_certificazione, data_consegna_kit, stato_sts, note)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    riga["sistema"],
                    riga["iniziativa"],
                    riga["data_inizio_certificazione"],
                    riga["data_fine_certificazione"],
                    riga["data_consegna_kit"],
                    riga["stato_sts"],
                    riga["note"],
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
                 data_fine_certificazione, data_consegna_kit, stato_sts, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                riga["sistema"],
                riga["iniziativa"],
                riga["data_inizio_certificazione"],
                riga["data_fine_certificazione"],
                riga["data_consegna_kit"],
                riga["stato_sts"],
                riga["note"],
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
             data_fine_certificazione, data_consegna_kit, stato_sts, note)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            dati["sistema"],
            dati["iniziativa"],
            dati["data_inizio_certificazione"],
            dati["data_fine_certificazione"],
            dati["data_consegna_kit"],
            dati["stato_sts"],
            dati["note"],
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
            note = ?
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


# ============================================================================
# 3. FUNZIONI DI SUPPORTO (parsing date, formattazione)
# ============================================================================

def parse_data(valore: str):
    """Prova a convertire una stringa in oggetto date (formato YYYY-MM-DD).

    Restituisce un oggetto date se possibile, altrimenti None (utile per
    gestire valori testuali come 'Kit non consegnato')."""
    if not valore:
        return None
    try:
        return datetime.strptime(str(valore).strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
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
    """READ + EDIT: tabella globale editabile con filtri e salvataggio su DB.

    Tutti i campi sono modificabili direttamente nella tabella (tranne l'ID,
    che identifica il record). Le modifiche vengono salvate nel database
    premendo il pulsante 'Salva modifiche'."""
    st.markdown('<div class="section-title">Elenco Certificazioni</div>', unsafe_allow_html=True)

    # Filtri rapidi in cima.
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        ricerca = st.text_input(
            "🔎 Cerca per Sistema o Iniziativa",
            placeholder="Es: Corriere, GPL, 143248...",
        )
    with col_f2:
        stati_disponibili = ["Tutti"] + sorted(df["stato_sts"].dropna().unique().tolist())
        filtro_stato = st.selectbox("Filtra per Stato STS", stati_disponibili)

    # Applicazione dei filtri.
    df_filtrato = df.copy()
    if ricerca:
        maschera = (
            df_filtrato["sistema"].str.contains(ricerca, case=False, na=False)
            | df_filtrato["iniziativa"].str.contains(ricerca, case=False, na=False)
        )
        df_filtrato = df_filtrato[maschera]
    if filtro_stato != "Tutti":
        df_filtrato = df_filtrato[df_filtrato["stato_sts"] == filtro_stato]

    if df_filtrato.empty:
        st.info("Nessun record corrisponde ai criteri di ricerca selezionati.")
        return

    st.caption(
        "✏️ Modifica le celle **oppure aggiungi nuove righe** con il pulsante **+** "
        "in fondo alla tabella, poi premi **Salva modifiche** per aggiornare il database."
    )

    # Tabella completamente editabile (tutti i campi tranne l'ID, che resta
    # nascosto ma serve internamente per identificare i record).
    df_edit = df_filtrato.reset_index(drop=True).copy()

    # Colonna "Stato" visiva: pallino rosso per record critici, verde per gli altri.
    df_edit.insert(
        0,
        "stato_visivo",
        df_edit.apply(
            lambda r: "🔴"
            if (is_valore_critico(r["data_consegna_kit"]) or is_valore_critico(r["stato_sts"]))
            else "🟢",
            axis=1,
        ),
    )

    tabella_modificata = st.data_editor(
        df_edit,
        use_container_width=True,
        hide_index=True,
        height=430,
        num_rows="dynamic",
        key="editor_certificazioni",
        # column_order esclude 'id' dalla visualizzazione (resta nel DataFrame).
        column_order=[
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
            "stato_visivo": st.column_config.TextColumn(
                "Stato", disabled=True, width="small",
                help="🔴 = da attenzionare · 🟢 = regolare",
            ),
            "sistema": st.column_config.TextColumn("Sistema", required=True),
            "iniziativa": st.column_config.TextColumn("Iniziativa"),
            "data_inizio_certificazione": st.column_config.TextColumn(
                "Inizio Cert.", help="Formato AAAA-MM-GG o testo"
            ),
            "data_fine_certificazione": st.column_config.TextColumn(
                "Fine Cert.", help="Formato AAAA-MM-GG o testo"
            ),
            "data_consegna_kit": st.column_config.TextColumn(
                "Consegna Kit", help="Data (AAAA-MM-GG) o testo (es. 'Kit non consegnato')"
            ),
            "stato_sts": st.column_config.SelectboxColumn(
                "Stato STS", options=STATI_STS
            ),
            "note": st.column_config.TextColumn("Note"),
        },
    )

    col_save, col_info = st.columns([1, 3])
    with col_save:
        if st.button("💾 Salva modifiche", type="primary"):
            n_agg, n_new = salva_modifiche_tabella(df_edit, tabella_modificata)
            if n_agg or n_new:
                messaggi = []
                if n_new:
                    messaggi.append(f"{n_new} nuovi sistemi aggiunti")
                if n_agg:
                    messaggi.append(f"{n_agg} record aggiornati")
                st.success(" · ".join(messaggi) + ".")
                st.rerun()
            else:
                st.info("Nessuna modifica da salvare.")
    with col_info:
        st.caption(f"Visualizzati {len(df_filtrato)} di {len(df)} sistemi totali.")


def salva_modifiche_tabella(df_originale: pd.DataFrame, df_modificato: pd.DataFrame):
    """Salva le modifiche della tabella nel database.

    - Le righe esistenti (con ID) vengono aggiornate se cambiate.
    - Le righe nuove (senza ID, aggiunte dall'utente) vengono inserite.
    Restituisce una tupla (n_aggiornati, n_nuovi)."""
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

    n_aggiornati = 0
    n_nuovi = 0
    for _, riga in df_modificato.iterrows():
        rid = riga.get("id")
        dati = {c: ("" if pd.isna(riga.get(c)) else str(riga.get(c))) for c in campi}

        if pd.isna(rid) or str(rid).strip() == "":
            # Riga nuova: inserisci solo se e' stato indicato almeno il Sistema.
            if dati["sistema"].strip():
                inserisci_sistema(dati)
                n_nuovi += 1
        else:
            # Riga esistente: aggiorna solo se qualche campo e' cambiato.
            riga_old = orig_by_id.get(int(rid))
            if riga_old is not None and any(
                str(riga.get(c)) != str(riga_old[c]) for c in campi
            ):
                aggiorna_sistema(int(rid), dati)
                n_aggiornati += 1
    return n_aggiornati, n_nuovi


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
                data_consegna_kit = data_kit_valore.isoformat()
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
            "data_inizio_certificazione": data_inizio.isoformat(),
            "data_fine_certificazione": data_fine.isoformat(),
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
                data_consegna_kit = data_kit_input.isoformat()
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
            "data_inizio_certificazione": data_inizio.isoformat(),
            "data_fine_certificazione": data_fine.isoformat(),
            "data_consegna_kit": data_consegna_kit,
            "stato_sts": stato_sts,
            "note": note.strip(),
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


# ============================================================================
# 6. FUNZIONE PRINCIPALE
# ============================================================================

def main():
    # Configurazione pagina in modalita' wide.
    st.set_page_config(
        page_title="Dashboard Certificazioni - Poste Italiane",
        page_icon="📮",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inizializzazione DB e stile.
    init_db()
    inietta_css()
    render_header()

    # Caricamento dati.
    df = leggi_sistemi()

    # KPI di sintesi.
    render_kpi(df)
    st.write("")  # spaziatura

    # --- Sidebar: creazione rapida ---
    with st.sidebar:
        st.markdown(
            f'<div class="section-title">Menu Rapido</div>', unsafe_allow_html=True
        )
        st.markdown(
            "Utilizza i tab principali per gestire i sistemi:\n\n"
            "- **Elenco**: visualizza e filtra\n"
            "- **Aggiungi**: inserisci nuovi sistemi\n"
            "- **Modifica**: aggiorna i dati\n"
            "- **Elimina**: rimuovi record"
        )
        st.divider()
        st.metric("Record nel Database", len(df))
        st.caption(f"Database: `{os.path.basename(DB_PATH)}`")

        st.divider()
        st.markdown("**Ripristino dati**")
        st.caption(
            "Riporta il database all'elenco iniziale completo "
            f"({len(DATI_MOCKUP)} sistemi), scartando le modifiche."
        )
        conferma_reset = st.checkbox("Confermo il ripristino completo")
        if st.button("🔄 Ripristina elenco iniziale", disabled=not conferma_reset):
            ripristina_dati_iniziali()
            st.success(f"Database ripristinato con {len(DATI_MOCKUP)} sistemi.")
            st.rerun()

    # --- Tabs principali per il CRUD ---
    tab_read, tab_create, tab_update, tab_delete = st.tabs(
        ["📋 Elenco", "➕ Aggiungi Sistema", "✏️ Modifica", "🗑️ Elimina"]
    )

    with tab_read:
        sezione_read(df)
    with tab_create:
        sezione_create()
    with tab_update:
        sezione_update(df)
    with tab_delete:
        sezione_delete(df)

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
