import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(
    page_title="Monitoring Penjualan & Insentif MHS",
    page_icon="📊",
    layout="wide"
)

# CSS Kustom untuk Tampilan & Spasi Rapih
st.markdown("""
    <style>
        [data-testid="stMetricValue"] {
            font-size: 1.45rem !important;
            word-break: break-word;
            white-space: normal;
        }
        [data-testid="stMetricDelta"] {
            font-size: 0.82rem !important;
            white-space: normal;
        }
        [data-testid="stMetric"] {
            margin-bottom: 0px !important;
            padding-bottom: 0px !important;
        }
        .metric-subtext {
            font-size: 0.78rem;
            color: #94a3b8;
            margin-top: -8px !important;
            padding-bottom: 4px;
        }
        .outlet-card {
            background-color: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 14px 18px;
            margin-bottom: 15px;
        }
        .warn-card {
            background-color: #fff7ed;
            border: 1px solid #fdba74;
            border-radius: 8px;
            padding: 10px 16px;
            margin-bottom: 12px;
            font-size: 0.85rem;
            color: #9a3412;
        }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# PCODE_ELIGIBLE_CLASS
# Sumber: REF_MHS (hasil pencocokan PCODE x Must-Have-SKU resmi, sheet
# REF_MHS pada "2__MUST_HAVE_SKU___OA_AGT.xlsx"), difilter MHS_ELIGIBLE="Ya".
# Key   = Pcode (angka, exact match - BUKAN substring nama produk)
# Value = daftar KODE CLASS (1-13) toko yang MEWAJIBKAN pcode tsb.
# Kalau sebuah pcode tidak ada di dict ini -> bukan Must Have SKU sama sekali.
# Kalau ada tapi kode class toko tidak ada di list-nya -> bukan wajib UNTUK
# class toko itu (meski wajib di class lain).
# =====================================================================
PCODE_ELIGIBLE_CLASS = {
    315200: [2, 3, 4, 5, 6, 7, 10, 11, 12, 13],  # TORA BUBUK 6.5G
    315352: [2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13],  # TORABIKA CAPPUCINO
    315486: [2, 3, 4, 6, 7],  # TORAMOKA
    315517: [2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13],  # TORABIKA CAPPUCINO
    315580: [3, 6, 7],  # TORABIKA JAHE SUSU
    315581: [3, 6, 7],  # TORABIKA JAHE SUSU
    315589: [2, 3, 4, 6, 7],  # TORAMOKA
    315640: [3, 6, 7],  # TORABIKA 3 IN 1
    315647: [6],  # TORACAFE CARAMEL LATTE
    315784: [6],  # TORACAFE CARAMEL LATTE
    316857: [1, 2, 3, 4, 5, 6, 7, 8],  # BURYAM
    318028: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],  # CHAMPION
    318503: [2, 3, 4, 6, 7],  # TORASUSU
    318504: [2, 3, 4, 6, 7],  # TORASUSU
    370034: [2, 3, 4, 5, 6, 7],  # GENTLE GEN TWINPACK MB
    370036: [2, 3, 4, 6, 7],  # GENTLE GEN TWINPACK PG
    370043: [2, 3, 4, 5, 6, 7],  # GENTLE GEN MB, GENTLE GEN TWINPACK MB
    370045: [2, 3, 4, 6, 7],  # GENTLE GEN PG, GENTLE GEN TWINPACK PG
    370050: [2, 3, 4, 6],  # GENTLE GEN TWINPACK ABK
    370069: [2, 3, 4, 5, 6, 7, 8, 9, 10, 12],  # KILAU NIPIS
    370072: [3, 6, 7, 11],  # KILAU NIPIS
    370076: [3, 6],  # GENTLE GEN MB
    370077: [6],  # GENTLE GEN PG
    370078: [6],  # GENTLE GEN ABK
    370090: [3, 6, 7],  # GENTLE GEN PG
    370092: [2, 3, 4, 5, 6, 7],  # GENTLE GEN TWINPACK MB
    370094: [2, 3, 4, 6, 7],  # GENTLE GEN TWINPACK PG
    370095: [2, 3, 4, 6],  # GENTLE GEN TWINPACK ABK
    370106: [2, 3, 4, 6, 7],  # GENTLE GEN TWINPACK SR
    370118: [2, 3, 4, 6],  # KILAU NIPIS
    370141: [3, 6, 7],  # GENTLE GEN MB
    370142: [3, 6, 7],  # GENTLE GEN SR
    370143: [3, 6, 7],  # GENTLE GEN PG
    370144: [3, 6],  # GENTLE GEN ABK
    370145: [6, 7],  # GENTLE GEN MB
    370146: [6],  # GENTLE GEN SR
    370147: [6],  # GENTLE GEN PG
    370150: [2, 3, 4, 5, 6, 7],  # GENTLE GEN TWINPACK MB
    370152: [2, 3, 4, 6, 7],  # GENTLE GEN TWINPACK PG
    370153: [2, 3, 4, 6],  # GENTLE GEN TWINPACK ABK
    370154: [3, 6],  # GENTLE GEN MB
    370155: [6],  # GENTLE GEN PG
    370156: [6],  # GENTLE GEN ABK
    370157: [2, 3, 4, 5, 6, 7, 8, 9, 10, 12],  # KILAU NIPIS
    370158: [2, 3, 4, 5, 6, 7],  # GENTLE GEN TWINPACK MB
    370159: [2, 3, 4, 6, 7],  # GENTLE GEN TWINPACK SR
    370172: [3, 6, 7, 11],  # KILAU NIPIS
    370173: [6],  # GENTLE GEN SR
    370174: [2, 3, 4, 5, 6, 7],  # GENTLE GEN TWINPACK MB
    370176: [2, 3, 4, 6, 7],  # GENTLE GEN TWINPACK PG
    370177: [2, 3, 4, 6],  # GENTLE GEN TWINPACK ABK
    370182: [2, 3, 4, 5, 6, 7, 8, 9, 10, 12],  # KILAU NIPIS
    370187: [6],  # KILAU NIPIS
    370191: [3, 6, 7, 11],  # KILAU NIPIS
    370193: [2, 3, 4, 6, 7],  # GENTLE GEN TWINPACK SR
    370205: [2, 3, 4, 5, 6, 7],  # GENTLE GEN TWINPACK MB
    370206: [2, 3, 4, 6, 7],  # GENTLE GEN TWINPACK PG
    370207: [2, 3, 4, 6],  # GENTLE GEN TWINPACK ABK
    410106: [1, 3, 6, 7, 8, 9],  # SUPER BUBUR AYAM SINGLE
    410107: [6],  # SUPER BUBUR ABON SINGLE
    410108: [6],  # SUPER BUBUR KUAH KARI
    410109: [6],  # SUPER BUBUR KUAH SOTO
    410153: [1, 2, 3, 4, 6, 7, 8, 9],  # MIGELAS KARI AYAM
    410224: [2, 3, 4, 6, 7],  # TORADUO
    410291: [3, 6],  # ENERGEN JAHE
    410332: [6],  # ENERGEN KURMA
    410514: [1, 2, 3, 4, 5, 6, 7, 8, 9],  # MIGELAS AYAM BAWANG
    410533: [3, 6, 8, 9, 10, 11],  # WOW AGLIO OLIO
    410583: [1, 2, 3, 6, 7, 8],  # ENERGEN VANTOP BALLS
    410585: [2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13],  # TORABIKA CAPPUCINO
    410586: [2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13],  # TORABIKA CAPPUCINO
    410588: [1, 3, 6, 7, 9],  # TORACAFE CHOCOLATTE
    410589: [1, 3, 6, 7, 9],  # TORACAFE MILKY LATTE
    410590: [6],  # TORACAFE CAPPUCINO
    410695: [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13],  # ENERGEN COKELAT
    410696: [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13],  # ENERGEN VANILLA
    410697: [1, 2, 3, 4, 6, 7, 11, 12],  # ENERGEN KACANG HIJAU
    410714: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],  # TEH SUSU JASMINE
    410717: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],  # DRINK BENG-BENG
    410721: [2, 3, 4, 6, 7],  # TORASUSU
    410726: [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13],  # TORABIKA CREAMY LATTE
    410737: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],  # DRINK BENG-BENG
    410740: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],  # CHAMPION
    410743: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],  # CHAMPION
    410764: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],  # CHAMPION
    410768: [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13],  # TORABIKA CREAMY LATTE
    410769: [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13],  # TORABIKA CREAMY LATTE
    410805: [1, 2, 3, 6, 7, 8],  # ENERGEN VANTOP BALLS
    410806: [3, 6],  # ENERGEN VANTOP MALKIST
    410820: [1, 2, 3, 4, 5, 6, 7, 8, 9],  # MIGELAS AYAM BAWANG
    410821: [1, 2, 3, 4, 5, 6, 7, 8, 9],  # MIGELAS SOTO AYAM
    410822: [1, 2, 3, 4, 6, 7, 8, 9],  # MIGELAS KARI AYAM
    410823: [1, 6],  # MIGELAS SOSIS BUNTUT
    410824: [1, 6],  # MIGELAS SOSIS BBQ
    410825: [1, 2, 3, 4, 5, 6, 7, 8, 9],  # MIGELAS BASO SAPI
    410826: [1, 2, 3, 4, 5, 6, 7, 8, 9],  # MIGELAS PEDAS MERCON
    410832: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],  # WOW CARBONARA
    410834: [1, 2, 3, 4, 6, 7, 8, 9, 10, 11],  # WOW BOLOGNESE
    410835: [3, 6, 8, 9, 10, 11],  # WOW AGLIO OLIO
    410837: [1, 6],  # MIGELAS GORENG
    410846: [2, 3, 4, 5, 6, 7, 10, 11, 12, 13],  # TURKISH
    410847: [3, 6],  # ENERGEN VANTOP MALKIST
    410864: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],  # CHAMPION
    410868: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],  # TEH SUSU JASMINE
    410871: [3, 6, 8, 9, 10, 11],  # WOW GORENG
    410880: [2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13],  # TORABIKA CAPPUCINO
    410881: [2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13],  # TORABIKA CAPPUCINO
    410883: [2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13],  # TORABIKA CAPPUCINO
    410901: [2, 3, 4, 6, 7],  # TORADUO
    410902: [2, 3, 4, 6, 7],  # TORASUSU
    410903: [2, 3, 4, 6, 7],  # TORAMOKA
    410905: [3, 6],  # ENERGEN VANTOP MALKIST
    411008: [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13],  # TORABIKA CREAMY LATTE
    411014: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],  # CHAMPION
}

PCODE_NAMES = {int(k): v for k, v in {
    370078: "GENTLE GEN ABK",
    370090: "GENTLE GEN PG",
    370092: "GENTLE GEN TWINPACK MB",
    370094: "GENTLE GEN TWINPACK PG",
    370095: "GENTLE GEN TWINPACK ABK",
    370106: "GENTLE GEN TWINPACK SR",
    370118: "KILAU NIPIS",
    370141: "GENTLE GEN MB",
    370142: "GENTLE GEN SR",
    370143: "GENTLE GEN PG",
    370144: "GENTLE GEN ABK",
    370145: "GENTLE GEN MB",
    370146: "GENTLE GEN SR",
    370147: "GENTLE GEN PG",
    370150: "GENTLE GEN TWINPACK MB",
    370152: "GENTLE GEN TWINPACK PG",
    370153: "GENTLE GEN TWINPACK ABK",
    370154: "GENTLE GEN MB",
    370155: "GENTLE GEN PG",
    370156: "GENTLE GEN ABK",
    370157: "KILAU NIPIS",
    370158: "GENTLE GEN TWINPACK MB",
    370159: "GENTLE GEN TWINPACK SR",
    370172: "KILAU NIPIS",
    370173: "GENTLE GEN SR",
    370174: "GENTLE GEN TWINPACK MB",
    370176: "GENTLE GEN TWINPACK PG",
    370177: "GENTLE GEN TWINPACK ABK",
    370182: "KILAU NIPIS",
    370187: "KILAU NIPIS",
    370191: "KILAU NIPIS",
    370193: "GENTLE GEN TWINPACK SR",
    370205: "GENTLE GEN TWINPACK MB",
    370206: "GENTLE GEN TWINPACK PG",
    370207: "GENTLE GEN TWINPACK ABK",
    315200: "TORA BUBUK 6.5G",
    315352: "TORABIKA CAPPUCINO",
    315589: "TORAMOKA",
    315640: "TORABIKA 3 IN 1",
    315647: "TORACAFE CARAMEL LATTE",
    315784: "TORACAFE CARAMEL LATTE",
    316857: "BURYAM",
    318028: "CHAMPION",
    318503: "TORASUSU",
    318504: "TORASUSU",
    370034: "GENTLE GEN TWINPACK MB",
    370036: "GENTLE GEN TWINPACK PG",
    370043: "GENTLE GEN MB, GENTLE GEN TWINPACK MB",
    370045: "GENTLE GEN PG, GENTLE GEN TWINPACK PG",
    370050: "GENTLE GEN TWINPACK ABK",
    370069: "KILAU NIPIS",
    370072: "KILAU NIPIS",
    370076: "GENTLE GEN MB",
    370077: "GENTLE GEN PG",
    410291: "ENERGEN JAHE",
    410332: "ENERGEN KURMA",
    410514: "MIGELAS AYAM BAWANG",
    410533: "WOW AGLIO OLIO",
    411014: "CHAMPION",
    315486: "TORAMOKA",
    315517: "TORABIKA CAPPUCINO",
    315580: "TORABIKA JAHE SUSU",
    315581: "TORABIKA JAHE SUSU",
    410583: "ENERGEN VANTOP BALLS",
    410585: "TORABIKA CAPPUCINO",
    410586: "TORABIKA CAPPUCINO",
    410588: "TORACAFE CHOCOLATTE",
    410589: "TORACAFE MILKY LATTE",
    410590: "TORACAFE CAPPUCINO",
    410695: "ENERGEN COKELAT",
    410696: "ENERGEN VANILLA",
    410697: "ENERGEN KACANG HIJAU",
    410714: "TEH SUSU JASMINE",
    410717: "DRINK BENG-BENG",
    410721: "TORASUSU",
    410726: "TORABIKA CREAMY LATTE",
    410737: "DRINK BENG-BENG",
    410740: "CHAMPION",
    410743: "CHAMPION",
    410764: "CHAMPION",
    410768: "TORABIKA CREAMY LATTE",
    410769: "TORABIKA CREAMY LATTE",
    410805: "ENERGEN VANTOP BALLS",
    410806: "ENERGEN VANTOP MALKIST",
    410820: "MIGELAS AYAM BAWANG",
    410821: "MIGELAS SOTO AYAM",
    410822: "MIGELAS KARI AYAM",
    410823: "MIGELAS SOSIS BUNTUT",
    410824: "MIGELAS SOSIS BBQ",
    410825: "MIGELAS BASO SAPI",
    410826: "MIGELAS PEDAS MERCON",
    410832: "WOW CARBONARA",
    410834: "WOW BOLOGNESE",
    410835: "WOW AGLIO OLIO",
    410846: "TURKISH",
    410847: "ENERGEN VANTOP MALKIST",
    410864: "CHAMPION",
    410868: "TEH SUSU JASMINE",
    410880: "TORABIKA CAPPUCINO",
    410881: "TORABIKA CAPPUCINO",
    410883: "TORABIKA CAPPUCINO",
    410901: "TORADUO",
    410902: "TORASUSU",
    410903: "TORAMOKA",
    410905: "ENERGEN VANTOP MALKIST",
    411008: "TORABIKA CREAMY LATTE",
    410106: "SUPER BUBUR AYAM SINGLE",
    410107: "SUPER BUBUR ABON SINGLE",
    410108: "SUPER BUBUR KUAH KARI",
    410109: "SUPER BUBUR KUAH SOTO",
    410153: "MIGELAS KARI AYAM",
    410224: "TORADUO",
    410871: "WOW GORENG",
    410837: "MIGELAS GORENG",
}.items()}

# =====================================================================
# PCODE_TO_MHS — identitas MHS resmi dari REF_MHS.
# PENTING: perhitungan MHS harus DISTINCT berdasarkan MHS_KEY, bukan PCode.
# Beberapa PCode/varian dapat mewakili 1 MHS yang sama.
# =====================================================================
PCODE_TO_MHS = {
    315200: 'TORA BUBUK 6.5G',
    315352: 'TORABIKA CAPPUCINO',
    315486: 'TORAMOKA',
    315517: 'TORABIKA CAPPUCINO',
    315580: 'TORABIKA JAHE SUSU',
    315581: 'TORABIKA JAHE SUSU',
    315589: 'TORAMOKA',
    315640: 'TORABIKA 3 IN 1',
    315647: 'TORACAFE CARAMEL LATTE',
    315784: 'TORACAFE CARAMEL LATTE',
    316857: 'BURYAM',
    318028: 'CHAMPION',
    318503: 'TORASUSU',
    318504: 'TORASUSU',
    370034: 'GENTLE GEN TWINPACK MB',
    370036: 'GENTLE GEN TWINPACK PG',
    370043: 'GENTLE GEN MB, GENTLE GEN TWINPACK MB',
    370045: 'GENTLE GEN PG, GENTLE GEN TWINPACK PG',
    370050: 'GENTLE GEN TWINPACK ABK',
    370069: 'KILAU NIPIS',
    370072: 'KILAU NIPIS',
    370076: 'GENTLE GEN MB',
    370077: 'GENTLE GEN PG',
    370078: 'GENTLE GEN ABK',
    370090: 'GENTLE GEN PG',
    370092: 'GENTLE GEN TWINPACK MB',
    370094: 'GENTLE GEN TWINPACK PG',
    370095: 'GENTLE GEN TWINPACK ABK',
    370106: 'GENTLE GEN TWINPACK SR',
    370118: 'KILAU NIPIS',
    370141: 'GENTLE GEN MB',
    370142: 'GENTLE GEN SR',
    370143: 'GENTLE GEN PG',
    370144: 'GENTLE GEN ABK',
    370145: 'GENTLE GEN MB',
    370146: 'GENTLE GEN SR',
    370147: 'GENTLE GEN PG',
    370150: 'GENTLE GEN TWINPACK MB',
    370152: 'GENTLE GEN TWINPACK PG',
    370153: 'GENTLE GEN TWINPACK ABK',
    370154: 'GENTLE GEN MB',
    370155: 'GENTLE GEN PG',
    370156: 'GENTLE GEN ABK',
    370157: 'KILAU NIPIS',
    370158: 'GENTLE GEN TWINPACK MB',
    370159: 'GENTLE GEN TWINPACK SR',
    370172: 'KILAU NIPIS',
    370173: 'GENTLE GEN SR',
    370174: 'GENTLE GEN TWINPACK MB',
    370176: 'GENTLE GEN TWINPACK PG',
    370177: 'GENTLE GEN TWINPACK ABK',
    370182: 'KILAU NIPIS',
    370187: 'KILAU NIPIS',
    370191: 'KILAU NIPIS',
    370193: 'GENTLE GEN TWINPACK SR',
    370205: 'GENTLE GEN TWINPACK MB',
    370206: 'GENTLE GEN TWINPACK PG',
    370207: 'GENTLE GEN TWINPACK ABK',
    410106: 'SUPER BUBUR AYAM SINGLE',
    410107: 'SUPER BUBUR ABON SINGLE',
    410108: 'SUPER BUBUR KUAH KARI',
    410109: 'SUPER BUBUR KUAH SOTO',
    410153: 'MIGELAS KARI AYAM',
    410224: 'TORADUO',
    410291: 'ENERGEN JAHE',
    410332: 'ENERGEN KURMA',
    410514: 'MIGELAS AYAM BAWANG',
    410533: 'WOW AGLIO OLIO',
    410583: 'ENERGEN VANTOP BALLS',
    410585: 'TORABIKA CAPPUCINO',
    410586: 'TORABIKA CAPPUCINO',
    410588: 'TORACAFE CHOCOLATTE',
    410589: 'TORACAFE MILKY LATTE',
    410590: 'TORACAFE CAPPUCINO',
    410695: 'ENERGEN COKELAT',
    410696: 'ENERGEN VANILLA',
    410697: 'ENERGEN KACANG HIJAU',
    410714: 'TEH SUSU JASMINE',
    410717: 'DRINK BENG-BENG',
    410721: 'TORASUSU',
    410726: 'TORABIKA CREAMY LATTE',
    410737: 'DRINK BENG-BENG',
    410740: 'CHAMPION',
    410743: 'CHAMPION',
    410764: 'CHAMPION',
    410768: 'TORABIKA CREAMY LATTE',
    410769: 'TORABIKA CREAMY LATTE',
    410805: 'ENERGEN VANTOP BALLS',
    410806: 'ENERGEN VANTOP MALKIST',
    410820: 'MIGELAS AYAM BAWANG',
    410821: 'MIGELAS SOTO AYAM',
    410822: 'MIGELAS KARI AYAM',
    410823: 'MIGELAS SOSIS BUNTUT',
    410824: 'MIGELAS SOSIS BBQ',
    410825: 'MIGELAS BASO SAPI',
    410826: 'MIGELAS PEDAS MERCON',
    410832: 'WOW CARBONARA',
    410834: 'WOW BOLOGNESE',
    410835: 'WOW AGLIO OLIO',
    410837: 'MIGELAS GORENG',
    410846: 'TURKISH',
    410847: 'ENERGEN VANTOP MALKIST',
    410864: 'CHAMPION',
    410868: 'TEH SUSU JASMINE',
    410871: 'WOW GORENG',
    410880: 'TORABIKA CAPPUCINO',
    410881: 'TORABIKA CAPPUCINO',
    410883: 'TORABIKA CAPPUCINO',
    410901: 'TORADUO',
    410902: 'TORASUSU',
    410903: 'TORAMOKA',
    410905: 'ENERGEN VANTOP MALKIST',
    411008: 'TORABIKA CREAMY LATTE',
    411014: 'CHAMPION',
}

# =====================================================================
# CLASS_INFO — target SKU per KODE CLASS (1-13), sesuai memo resmi
# "Scheme Incentive Sales" M245 (Agustus-September 2026) dan Sheet2 /
# REF_TARGET pada "2__MUST_HAVE_SKU___OA_AGT.xlsx".
# code -> (nama kelompok, target jumlah SKU harus terjual / bulan)
# =====================================================================
CLASS_INFO = {
    1:  ("Grosir Snack",             10),
    2:  ("Grosir Kelontong",         15),
    3:  ("Grosir Modern",            15),
    4:  ("Retail Large",             10),
    5:  ("Kios / Retail Small",       7),
    6:  ("Supermarket",              25),
    7:  ("Minimarket",               20),
    8:  ("Kantin - SD",               5),
    9:  ("Kantin - SMP SMA",          5),
    10: ("Kantin - Univ / Institusi", 5),
    11: ("Warduh Modern",             5),
    12: ("Warduh Tradisional",        5),
    13: ("Warduh Mobile",             5),
}


# =====================================================================
# Fallback pemetaan dari kode channel LAMA (kolom teks "Channel" di LBP,
# format "111-RT - RETAIL SMALL" dsb) ke KODE CLASS baru (1-13).
# HANYA dipakai kalau kolom "CLASS" tidak ada di file LBP yang diupload.
# Sengaja TIDAK diisi untuk kode yang ambigu (satu kode channel lama bisa
# mencakup beberapa class baru, mis. '110' bisa Grosir Modern/Minimarket/
# Supermarket sekaligus) — lebih baik toko tsb ditandai "tidak bisa
# diklasifikasikan" daripada dihitung dengan target yang salah.
# =====================================================================
FALLBACK_CHANNEL_PREFIX_TO_CLASS = {
    '111': 5,   # Kios -> 1:1
    '113': 4,   # Retail Large -> 1:1
    # 118 = Kantin (class 8/9/10) -> ambigu
    # 154 = Warduh (class 11/12/13) -> ambigu
    # 105/109/110 = Modern Trade (class 6/7) -> ambigu
    # 114/115/116 = Grosir (class 1/2/3) -> ambigu
    # Jangan menebak class jika channel lama mencakup >1 class.
}


def get_outlet_class_code(row):
    """Tentukan kode class (1-13) sebuah baris transaksi.
    Prioritas: kolom 'CLASS' asli dari LBP (paling akurat, sesuai
    'KODE CLASS PER 08.09.26' di Daftar Master Pelanggan). Kalau kolom
    itu tidak ada / kosong, coba dekati dari 3 digit awal kolom 'Channel'
    (hanya untuk kode yang tidak ambigu)."""
    if 'CLASS' in row and pd.notna(row['CLASS']):
        try:
            return int(row['CLASS'])
        except (ValueError, TypeError):
            pass
    ch_prefix = str(row.get('Channel', ''))[:3]
    return FALLBACK_CHANNEL_PREFIX_TO_CLASS.get(ch_prefix, None)


def cek_sku_valid(pcode, class_code):
    """Cek APAKAH pcode ini wajib ada (Must Have SKU) untuk class_code
    outlet tsb. Persis (exact match Pcode + Kode Class), BUKAN
    tebak-tebakan dari nama produk."""
    if class_code is None:
        return False
    try:
        pcode_int = int(float(pcode))
    except (ValueError, TypeError):
        return False
    eligible_classes = PCODE_ELIGIBLE_CLASS.get(pcode_int)
    if not eligible_classes:
        return False
    return class_code in eligible_classes


def get_target_sku(class_code):
    if class_code is None or class_code not in CLASS_INFO:
        return None
    return CLASS_INFO[class_code][1]


def get_class_name(class_code):
    if class_code is None:
        return "Tidak Terklasifikasi"
    return CLASS_INFO.get(class_code, ("Tidak Dikenal", None))[0]


# Fungsi Penomoran Mulai dari 1
def beri_nomor_urut(df_target):
    df_res = df_target.copy().reset_index(drop=True)
    df_res.insert(0, 'No', range(1, len(df_res) + 1))
    return df_res

# Fungsi Konversi DataFrame ke Bytes Excel (XLSX)
def convert_df_to_excel(df_dict):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df_data in df_dict.items():
            df_data.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

# Parser LBP
def parse_raw_lbp(uploaded_file):
    """Baca LBP langsung atau workbook Mayora. Untuk XLSX, otomatis pilih sheet LBP bila ada."""
    name = uploaded_file.name.lower()
    if name.endswith(('.txt', '.csv')):
        raw_bytes = uploaded_file.read()
        lines = raw_bytes.decode('utf-8', errors='ignore').splitlines()
        cleaned_lines = []
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            if line_str.endswith('|'):
                line_str = line_str[:-1]
            cleaned_lines.append(line_str)
        first_line = cleaned_lines[0] if cleaned_lines else ""
        sep = '|' if '|' in first_line else ('\t' if '\t' in first_line else (';' if ';' in first_line else ','))
        df = pd.read_csv(io.StringIO('\n'.join(cleaned_lines)), sep=sep, low_memory=False)
    else:
        # Excel workbook: gunakan sheet LBP jika tersedia; kalau tidak, gunakan sheet pertama.
        xls = pd.ExcelFile(uploaded_file)
        sheet = next((s for s in xls.sheet_names if str(s).strip().upper() == 'LBP'), xls.sheet_names[0])
        df = pd.read_excel(xls, sheet_name=sheet)
    df.columns = [str(c).strip() for c in df.columns]
    return df

# --- SIDEBAR OPERASIONAL ---
st.sidebar.title("⚙️ Pengaturan Operasional")
st.sidebar.markdown("**Akses:** SS / HOA MV42")

cb_standpro = st.sidebar.number_input(
    "Target Standpro (CB Area):",
    min_value=1,
    value=1090,
    step=25,
    help="Target Base Customer (CB) Standpro area untuk menghitung % pencapaian dan tier insentif."
)

uploaded_lbp = st.sidebar.file_uploader("📂 Upload File LBP / Workbook (.txt / .csv / .xlsx)", type=['txt', 'csv', 'xlsx'])
st.sidebar.caption("💡 Upload LBP .xlsx/.csv/.txt. Jika upload workbook Excel Mayora yang berisi sheet LBP, app otomatis membaca sheet **LBP**. Kolom CLASS 1-13 dipakai sebagai klasifikasi resmi.")

# --- PEMROSESAN DATA & DASHBOARD ---
if uploaded_lbp is not None:
    try:
        with st.spinner("Memproses data LBP & memetakan SKU sesuai Must Have SKU resmi..."):
            df_raw = parse_raw_lbp(uploaded_lbp)

            st.caption('ℹ️ Mesin menghitung MHS secara DISTINCT berdasarkan MHS_KEY setelah Net Qty per PCode menjadi positif. PCode yang tidak eligible untuk CLASS outlet tidak dihitung.')

            df_raw['Salesman'] = df_raw['Salesman'].astype(str).str.strip()
            df_raw['Pcode_Str'] = df_raw['Pcode'].astype(str).str.strip()
            df_raw['Nama Produk'] = df_raw['Nama Produk'].astype(str).str.strip()
            df_raw['QTYPCS'] = pd.to_numeric(df_raw['QTYPCS'], errors='coerce').fillna(0)
            df_raw['AMOUNT'] = pd.to_numeric(df_raw['AMOUNT'], errors='coerce').fillna(0)
            if 'Salesforce' not in df_raw.columns: df_raw['Salesforce'] = '-'
            df_raw['Salesforce'] = df_raw['Salesforce'].astype(str).str.strip()

            if 'Kabupaten' not in df_raw.columns: df_raw['Kabupaten'] = '-'
            else: df_raw['Kabupaten'] = df_raw['Kabupaten'].fillna('-').astype(str).str.strip()

            if 'Kecamatan' not in df_raw.columns: df_raw['Kecamatan'] = '-'
            else: df_raw['Kecamatan'] = df_raw['Kecamatan'].fillna('-').astype(str).str.strip()

            if 'Kode Pasar' not in df_raw.columns: df_raw['Kode Pasar'] = '-'
            else: df_raw['Kode Pasar'] = df_raw['Kode Pasar'].fillna('-').astype(str).str.strip()

            has_class_col = 'CLASS' in df_raw.columns
            if not has_class_col:
                df_raw['CLASS'] = pd.NA

            df_raw['Class_Code'] = df_raw.apply(get_outlet_class_code, axis=1)

            is_retur = df_raw['TRANSTYPE'].astype(str).str.strip().str.upper() == 'R'
            df_raw['NET_QTY'] = df_raw['QTYPCS'].where(~is_retur, -df_raw['QTYPCS'])
            df_raw['NET_AMOUNT'] = df_raw['AMOUNT'].where(~is_retur, -df_raw['AMOUNT'])
            df_raw['RETUR_AMOUNT'] = df_raw['AMOUNT'].where(is_retur, 0)
            df_raw['BRUTO_AMOUNT'] = df_raw['AMOUNT'].where(~is_retur, 0)

            all_salesmen = sorted(df_raw['Salesman'].dropna().unique().tolist())

        if not has_class_col:
            st.markdown("""<div class="warn-card">⚠️ <b>Kolom CLASS tidak ditemukan</b> di file LBP yang diupload.
            Klasifikasi toko untuk channel 110 (Grosir Modern/Minimarket/Supermarket), 114 dan 115
            (Grosir Kelontong/Snack) <b>tidak bisa ditentukan otomatis</b> dan toko-toko tsb akan
            ditandai "Tidak Terklasifikasi" (tidak dihitung MHS-nya). Sertakan kolom CLASS (kode 1-13
            sesuai "KODE CLASS PER 08.09.26" di Daftar Master Pelanggan) di export LBP untuk hasil yang akurat.</div>""", unsafe_allow_html=True)

        n_unclassified = int(df_raw['Class_Code'].isna().sum())
        if n_unclassified > 0:
            st.markdown(f"""<div class="warn-card">ℹ️ {n_unclassified:,} baris transaksi berasal dari toko yang
            kode class-nya tidak bisa ditentukan, dan dikeluarkan dari perhitungan MHS.</div>""", unsafe_allow_html=True)

        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👥 **Pilih Salesman (Tim SS)**")
            select_all = st.checkbox("Pilih Semua Salesman (Total Area)", value=True)

            if select_all:
                selected_salesmen = st.multiselect("Salesman Terpilih:", options=all_salesmen, default=all_salesmen)
            else:
                selected_salesmen = st.multiselect("Salesman Terpilih:", options=all_salesmen, default=all_salesmen[:3] if len(all_salesmen) >= 3 else all_salesmen)

        if not selected_salesmen:
            st.warning("Silakan pilih minimal 1 salesman pada menu di sebelah kiri.")
            st.stop()

        df = df_raw[df_raw['Salesman'].isin(selected_salesmen)].copy()

        base_cols = ['No Outlet', 'Nama Outlet', 'Kode Sales', 'Salesman', 'Channel', 'Salesforce', 'Kabupaten', 'Kecamatan', 'Kode Pasar', 'Class_Code']
        cols_exist = [c for c in base_cols if c in df.columns]
        outlet_master = df[cols_exist].drop_duplicates(subset=['No Outlet']).copy()
        outlet_master['Kelas Toko'] = outlet_master['Class_Code'].apply(get_class_name)

        # 1) Net QTY per (outlet, PCode). Retur mengurangi penjualan.
        # 2) Hanya PCode dengan NET_QTY > 0 yang dianggap benar-benar terjual.
        # 3) PCode -> MHS_KEY.
        # 4) Validasi PCode terhadap CLASS outlet.
        # 5) Hitung DISTINCT MHS_KEY per outlet — BUKAN jumlah PCode/varian.
        outlet_prod_agg = (
            df.groupby(['No Outlet', 'Pcode_Str'])['NET_QTY']
              .sum()
              .reset_index()
        )
        outlet_prod_positive = outlet_prod_agg[outlet_prod_agg['NET_QTY'] > 0].copy()
        outlet_prod_positive['MHS_KEY'] = outlet_prod_positive['Pcode_Str'].map(
            lambda p: PCODE_TO_MHS.get(int(float(p))) if str(p).strip() not in ('', 'nan', 'None') else None
        )

        # PCode yang tidak ada di REF_MHS bukan MHS.
        outlet_prod_positive = outlet_prod_positive[
            outlet_prod_positive['MHS_KEY'].notna()
        ].copy()

        def hitung_mhs_lolos_toko(row):
            no_outlet = row['No Outlet']
            class_code = row['Class_Code']
            if class_code is None or pd.isna(class_code):
                return 0

            prod_toko = outlet_prod_positive[
                outlet_prod_positive['No Outlet'] == no_outlet
            ].copy()

            if prod_toko.empty:
                return 0

            # Validasi per PCode + class, lalu DISTINCT berdasarkan MHS_KEY.
            prod_toko['VALID_MHS'] = prod_toko['Pcode_Str'].apply(
                lambda p: cek_sku_valid(p, int(class_code))
            )
            return prod_toko.loc[prod_toko['VALID_MHS'], 'MHS_KEY'].nunique()

        outlet_master['Realisasi SKU Sold'] = outlet_master.apply(
            hitung_mhs_lolos_toko, axis=1
        )
        calc_toko = outlet_master.copy()

        calc_toko['Target SKU'] = calc_toko['Class_Code'].apply(get_target_sku)
        calc_toko_scoped = calc_toko[calc_toko['Target SKU'].notna()].copy()  # hanya toko yang punya target MHS resmi
        calc_toko_scoped['Target SKU'] = calc_toko_scoped['Target SKU'].astype(int)
        calc_toko_scoped['Status Lolos'] = (calc_toko_scoped['Realisasi SKU Sold'] >= calc_toko_scoped['Target SKU']).astype(int)
        calc_toko_scoped['Gap SKU'] = (calc_toko_scoped['Target SKU'] - calc_toko_scoped['Realisasi SKU Sold']).apply(lambda x: max(0, x))
        calc_toko = calc_toko_scoped  # dari sini & seterusnya, calc_toko = toko yang masuk scope MHS saja

        total_ec = len(calc_toko)
        total_lolos_mhs = calc_toko['Status Lolos'].sum()
        ach_cb_standpro = (total_lolos_mhs / cb_standpro) * 100

        total_net_sales = df['NET_AMOUNT'].sum()
        total_bruto = df['BRUTO_AMOUNT'].sum()
        total_retur = df['RETUR_AMOUNT'].sum()
        retur_rate = (total_retur / total_bruto * 100) if total_bruto > 0 else 0

        if ach_cb_standpro >= 80:
            tier_label = "Tier 4 (≥ 80%)"
            gauge_color = "#16a34a"
        elif ach_cb_standpro >= 70:
            tier_label = "Tier 3 (70% - 79.9%)"
            gauge_color = "#0284c7"
        elif ach_cb_standpro >= 60:
            tier_label = "Tier 2 (60% - 69.9%)"
            gauge_color = "#d97706"
        elif ach_cb_standpro >= 50:
            tier_label = "Tier 1 (50% - 59.9%)"
            gauge_color = "#ca8a04"
        else:
            tier_label = "Belum Masuk Tier"
            gauge_color = "#dc2626"

        target_tier1 = int(cb_standpro * 0.5)
        gap_toko_t1 = max(0, target_tier1 - total_lolos_mhs)

        # Header Utama
        st.title("📊 Monitoring Operasional & MHS Area (SS / HOA MV42)")
        st.caption(f"Cakupan: **{len(selected_salesmen)} Salesman Terpilih** | Target Standpro: **{cb_standpro:,} Toko** | Toko dalam scope MHS: **{total_ec:,}**")

        is_lolos_tier = ach_cb_standpro >= 50.0

        if total_retur > 0:
            delta_omset = f"-{retur_rate:.2f}% Retur"
            delta_color_omset = "normal"
        else:
            delta_omset = "+0.00% Retur"
            delta_color_omset = "normal"

        if is_lolos_tier:
            delta_mhs = f"+{ach_cb_standpro:.2f}% (Target 50%)"
            delta_color_mhs = "normal"
        else:
            delta_mhs = f"-{ach_cb_standpro:.2f}% (Target 50%)"
            delta_color_mhs = "normal"

        if gap_toko_t1 == 0:
            delta_status = "+Tier 1 Tercapai"
            delta_color_status = "normal"
        else:
            delta_status = f"-Kurang {gap_toko_t1:,} Toko"
            delta_color_status = "normal"

        # Kartu Metrik
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            with st.container(border=True):
                st.metric("Omset Bersih (Net)", f"Rp {total_net_sales:,.0f}", delta=delta_omset, delta_color=delta_color_omset)
                st.markdown(f"<div class='metric-subtext'>Bruto: Rp {total_bruto:,.0f}</div>", unsafe_allow_html=True)
        with c2:
            with st.container(border=True):
                st.metric("Toko Dalam Scope MHS", f"{total_ec:,} Toko", delta=f"+{df['Faktur'].nunique():,} Faktur", delta_color="normal")
                st.markdown(f"<div class='metric-subtext'>Total Faktur Terbit</div>", unsafe_allow_html=True)
        with c3:
            with st.container(border=True):
                st.metric("Toko Lolos MHS", f"{total_lolos_mhs:,} Toko", delta=delta_mhs, delta_color=delta_color_mhs)
                st.markdown(f"<div class='metric-subtext'>Target Base: {cb_standpro:,} Toko</div>", unsafe_allow_html=True)
        with c4:
            with st.container(border=True):
                st.metric("Status Insentif", tier_label, delta=delta_status, delta_color=delta_color_status)
                st.markdown(f"<div class='metric-subtext'>Target Min Tier 1: {target_tier1:,} Toko</div>", unsafe_allow_html=True)

        st.markdown("---")

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Kinerja Salesman",
            "📍 Omset & Wilayah",
            "📦 Subbrand & Divisi",
            "🏬 Tipe Toko (Channel)",
            "🎯 Action Plan Toko",
            "📑 Master Mapping & List SKU"
        ])

        # TAB 1: KINERJA SALESMAN
        with tab1:
            st.subheader("Pencapaian Insentif & Kinerja Tim")
            cg, cb = st.columns([1, 2])
            with cg:
                fig_g = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = ach_cb_standpro,
                    number = {'suffix': "%", 'font': {'size': 26}},
                    title = {'text': "Pencapaian vs Standpro", 'font': {'size': 14}},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickwidth': 1},
                        'bar': {'color': gauge_color},
                        'steps': [
                            {'range': [0, 50], 'color': "#fee2e2"},
                            {'range': [50, 70], 'color': "#fef3c7"},
                            {'range': [70, 80], 'color': "#e0f2fe"},
                            {'range': [80, 100], 'color': "#dcfce7"}
                        ],
                        'threshold': {'line': {'color': "#0f172a", 'width': 3}, 'thickness': 0.75, 'value': 50}
                    }
                ))
                fig_g.update_layout(height=260, margin=dict(l=20, r=20, t=30, b=10))
                st.plotly_chart(fig_g, use_container_width=True)
            with cb:
                chart_df = calc_toko.groupby('Salesman').agg(
                    Covered=('No Outlet', 'count'),
                    Lolos=('Status Lolos', 'sum')
                ).reset_index()
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(name='Toko Tercover (EC)', x=chart_df['Salesman'], y=chart_df['Covered'], marker_color='#94a3b8'))
                fig_bar.add_trace(go.Bar(name='Toko Lolos MHS', x=chart_df['Salesman'], y=chart_df['Lolos'], marker_color='#0284c7'))
                fig_bar.update_layout(height=260, margin=dict(l=10, r=10, t=35, b=10), barmode='group', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown("#### Tabel Rincian Kinerja Salesman")
            sales_val = df.groupby(['Kode Sales', 'Salesman']).agg(Net_Sales=('NET_AMOUNT', 'sum'), Total_Faktur=('Faktur', 'nunique')).reset_index()
            sales_agg = calc_toko.groupby(['Kode Sales', 'Salesman']).agg(EC=('No Outlet', 'count'), Toko_Lolos_MHS=('Status Lolos', 'sum'), Avg_SKU=('Realisasi SKU Sold', 'mean')).reset_index()
            sales_perf = pd.merge(sales_val, sales_agg, on=['Kode Sales', 'Salesman'])
            sales_perf['% Strike Rate MHS'] = ((sales_perf['Toko_Lolos_MHS'] / sales_perf['EC']) * 100).round(1)
            sales_perf['Drop Size / Faktur'] = (sales_perf['Net_Sales'] / sales_perf['Total_Faktur']).round(0)
            sales_perf['Avg_SKU'] = sales_perf['Avg_SKU'].round(1)

            display_sales = sales_perf.copy()
            display_sales['Net_Sales (Rp)'] = display_sales['Net_Sales'].apply(lambda x: f"Rp {x:,.0f}")
            display_sales['Drop Size / Faktur'] = display_sales['Drop Size / Faktur'].apply(lambda x: f"Rp {x:,.0f}")
            display_sales['% Strike Rate MHS'] = display_sales['% Strike Rate MHS'].apply(lambda x: f"{x:.1f}%")

            tbl_sales = beri_nomor_urut(display_sales[['Kode Sales', 'Salesman', 'Net_Sales (Rp)', 'EC', 'Toko_Lolos_MHS', '% Strike Rate MHS', 'Avg_SKU', 'Drop Size / Faktur']])
            st.dataframe(tbl_sales, use_container_width=True, hide_index=True)
            st.download_button("📥 Download Tabel Salesman (.xlsx)", data=convert_df_to_excel({'KINERJA_SALESMAN': tbl_sales}), file_name="Kinerja_Salesman.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # TAB 2: OMSET & WILAYAH (TERMASUK PASAR)
        with tab2:
            st.subheader("Analisis Penjualan Berdasarkan Wilayah & Pasar")
            col_kab, col_kec = st.columns(2)
            with col_kab:
                st.markdown("#### Penjualan per Kabupaten")
                kab_val = df.groupby('Kabupaten')['NET_AMOUNT'].sum().reset_index()
                kab_out = calc_toko.groupby('Kabupaten').agg(Total_Toko=('No Outlet', 'count'), Toko_Lolos=('Status Lolos', 'sum')).reset_index()
                kab_merge = pd.merge(kab_val, kab_out, on='Kabupaten').sort_values(by='NET_AMOUNT', ascending=False)
                kab_merge['Kontribusi (%)'] = ((kab_merge['NET_AMOUNT'] / total_net_sales) * 100).round(1)
                kab_merge['Strike Rate (%)'] = ((kab_merge['Toko_Lolos'] / kab_merge['Total_Toko']) * 100).round(1)
                kab_merge['Omset (Rp)'] = kab_merge['NET_AMOUNT'].apply(lambda x: f"Rp {x:,.0f}")

                tbl_kab = beri_nomor_urut(kab_merge[['Kabupaten', 'Omset (Rp)', 'Kontribusi (%)', 'Total_Toko', 'Toko_Lolos', 'Strike Rate (%)']])
                st.dataframe(tbl_kab, use_container_width=True, hide_index=True)
                st.download_button("📥 Download Excel Kabupaten", data=convert_df_to_excel({'KABUPATEN': tbl_kab}), file_name="Omset_Kabupaten.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

                fig_kab = px.pie(kab_merge, names='Kabupaten', values='NET_AMOUNT', hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe, title="Porsi Omset per Kabupaten")
                fig_kab.update_layout(height=280, margin=dict(l=10, r=10, t=35, b=10))
                st.plotly_chart(fig_kab, use_container_width=True)

            with col_kec:
                st.markdown("#### Top 10 Kecamatan berdasarkan Omset")
                kec_val = df.groupby('Kecamatan')['NET_AMOUNT'].sum().reset_index()
                kec_out = calc_toko.groupby('Kecamatan').agg(Total_Toko=('No Outlet', 'count'), Toko_Lolos=('Status Lolos', 'sum')).reset_index()
                kec_merge = pd.merge(kec_val, kec_out, on='Kecamatan').sort_values(by='NET_AMOUNT', ascending=False).head(10)
                kec_merge['Kontribusi (%)'] = ((kec_merge['NET_AMOUNT'] / total_net_sales) * 100).round(1)
                kec_merge['Strike Rate (%)'] = ((kec_merge['Toko_Lolos'] / kec_merge['Total_Toko']) * 100).round(1)
                kec_merge['Omset (Rp)'] = kec_merge['NET_AMOUNT'].apply(lambda x: f"Rp {x:,.0f}")

                tbl_kec = beri_nomor_urut(kec_merge[['Kecamatan', 'Omset (Rp)', 'Kontribusi (%)', 'Total_Toko', 'Toko_Lolos', 'Strike Rate (%)']])
                st.dataframe(tbl_kec, use_container_width=True, hide_index=True)
                st.download_button("📥 Download Excel Kecamatan", data=convert_df_to_excel({'KECAMATAN': tbl_kec}), file_name="Omset_Kecamatan.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

                fig_kec = px.bar(kec_merge.sort_values(by='NET_AMOUNT', ascending=True), x='NET_AMOUNT', y='Kecamatan', orientation='h', labels={'NET_AMOUNT': 'Omset Bersih (Rp)'}, color_discrete_sequence=['#0284c7'], title="Grafik Omset Top 10 Kecamatan")
                fig_kec.update_layout(height=280, margin=dict(l=10, r=10, t=35, b=10))
                st.plotly_chart(fig_kec, use_container_width=True)

            if 'Kode Pasar' in df.columns and (df['Kode Pasar'] != '-').any():
                st.markdown("---")
                st.markdown("#### 🛒 Analisis Omset Berdasarkan Kode Pasar / Rayon")
                pasar_val = df.groupby('Kode Pasar')['NET_AMOUNT'].sum().reset_index()
                pasar_out = calc_toko.groupby('Kode Pasar').agg(
                    Total_Toko=('No Outlet', 'count'),
                    Toko_Lolos=('Status Lolos', 'sum')
                ).reset_index()
                pasar_merge = pd.merge(pasar_val, pasar_out, on='Kode Pasar').sort_values(by='NET_AMOUNT', ascending=False)
                pasar_merge['Kontribusi (%)'] = ((pasar_merge['NET_AMOUNT'] / total_net_sales) * 100).round(1)
                pasar_merge['Strike Rate (%)'] = ((pasar_merge['Toko_Lolos'] / pasar_merge['Total_Toko']) * 100).round(1)
                pasar_merge['Omset (Rp)'] = pasar_merge['NET_AMOUNT'].apply(lambda x: f"Rp {x:,.0f}")

                tbl_pasar = beri_nomor_urut(pasar_merge[['Kode Pasar', 'Omset (Rp)', 'Kontribusi (%)', 'Total_Toko', 'Toko_Lolos', 'Strike Rate (%)']])
                st.dataframe(tbl_pasar, use_container_width=True, hide_index=True)
                st.download_button("📥 Download Excel Omset per Pasar", data=convert_df_to_excel({'OMSET_PASAR': tbl_pasar}), file_name="Omset_per_Pasar.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # TAB 3: SUBBRAND & DIVISI
        with tab3:
            st.subheader("Kontribusi Produk & Divisi")
            col_sb1, col_sb2 = st.columns(2)
            with col_sb1:
                st.markdown("#### Top 10 Subbrand berdasarkan Omset")
                if 'SUBBRANDNAME' in df.columns:
                    top_sb = df.groupby('SUBBRANDNAME')['NET_AMOUNT'].sum().reset_index().sort_values(by='NET_AMOUNT', ascending=False).head(10)
                    top_sb['Omset (Rp)'] = top_sb['NET_AMOUNT'].apply(lambda x: f"Rp {x:,.0f}")
                    top_sb['Kontribusi (%)'] = ((top_sb['NET_AMOUNT'] / total_net_sales) * 100).round(2)
                    tbl_sb = beri_nomor_urut(top_sb[['SUBBRANDNAME', 'Omset (Rp)', 'Kontribusi (%)']])
                    st.dataframe(tbl_sb, use_container_width=True, hide_index=True)
                    st.download_button("📥 Download Excel Subbrand", data=convert_df_to_excel({'SUBBRAND': tbl_sb}), file_name="Top_Subbrand.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

                    fig_pie = px.pie(top_sb.head(6), names='SUBBRANDNAME', values='NET_AMOUNT', hole=0.45, color_discrete_sequence=px.colors.qualitative.Prism, title="Porsi 6 Brand Terbesar")
                    fig_pie.update_layout(height=260, margin=dict(l=10, r=10, t=35, b=10))
                    st.plotly_chart(fig_pie, use_container_width=True)

            with col_sb2:
                st.markdown("#### Penjualan per Divisi")
                if 'Divisi' in df.columns:
                    div_sales = df.groupby('Divisi')['NET_AMOUNT'].sum().reset_index().sort_values(by='NET_AMOUNT', ascending=False)
                    div_sales['Divisi'] = "Divisi " + div_sales['Divisi'].astype(str)
                    div_sales['Omset (Rp)'] = div_sales['NET_AMOUNT'].apply(lambda x: f"Rp {x:,.0f}")
                    div_sales['Kontribusi (%)'] = ((div_sales['NET_AMOUNT'] / total_net_sales) * 100).round(2)
                    tbl_div = beri_nomor_urut(div_sales[['Divisi', 'Omset (Rp)', 'Kontribusi (%)']])
                    st.dataframe(tbl_div, use_container_width=True, hide_index=True)
                    st.download_button("📥 Download Excel Divisi", data=convert_df_to_excel({'DIVISI': tbl_div}), file_name="Omset_Divisi.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

                    fig_div = px.bar(div_sales, x='Divisi', y='NET_AMOUNT', color='Divisi', color_discrete_sequence=px.colors.qualitative.Safe, title="Omset per Divisi")
                    fig_div.update_layout(height=260, margin=dict(l=10, r=10, t=35, b=10))
                    st.plotly_chart(fig_div, use_container_width=True)

        # TAB 4: CHANNEL & TERRITORY
        with tab4:
            st.subheader("Performa Kelas Toko (Class)")
            channel_val = df.groupby('Channel')['NET_AMOUNT'].sum().reset_index()
            channel_rep = calc_toko.groupby('Kelas Toko').agg(Total_EC=('No Outlet', 'count'), Toko_Lolos=('Status Lolos', 'sum')).reset_index()
            channel_rep['% Lolos Kelas'] = ((channel_rep['Toko_Lolos'] / channel_rep['Total_EC']) * 100).round(1)

            tbl_channel = beri_nomor_urut(channel_rep[['Kelas Toko', 'Total_EC', 'Toko_Lolos', '% Lolos Kelas']])
            st.dataframe(tbl_channel, use_container_width=True, hide_index=True)
            st.download_button("📥 Download Excel Kelas Toko", data=convert_df_to_excel({'KELAS_TOKO': tbl_channel}), file_name="Performa_Kelas_Toko.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            fig_ch = px.bar(channel_rep, x='Kelas Toko', y='Total_EC', color='% Lolos Kelas', labels={'Total_EC': 'Jumlah Toko Tercover', '% Lolos Kelas': '% Lolos MHS'}, color_continuous_scale='Blues', title="Jumlah Toko Tercover & Kelulusan per Kelas Toko")
            fig_ch.update_layout(height=280, margin=dict(l=10, r=10, t=35, b=10))
            st.plotly_chart(fig_ch, use_container_width=True)

            st.markdown("---")
            st.markdown("#### Omset per Kode Channel Mentah (referensi, tidak dipakai untuk MHS)")
            channel_val['Omset (Rp)'] = channel_val['NET_AMOUNT'].apply(lambda x: f"Rp {x:,.0f}")
            st.dataframe(beri_nomor_urut(channel_val[['Channel', 'Omset (Rp)']]), use_container_width=True, hide_index=True)

        # TAB 5: ACTION PLAN GAP MHS
        with tab5:
            st.subheader("🎯 Action Plan: Toko Belum Lolos & Detail SKU Masuk/Belum Masuk")
            sls_options = ['SEMUA TIM SS'] + selected_salesmen
            pilih_sales = st.selectbox("Filter Berdasarkan Salesman:", sls_options)

            df_action = calc_toko if pilih_sales == 'SEMUA TIM SS' else calc_toko[calc_toko['Salesman'] == pilih_sales]
            gap_outlets = df_action[df_action['Status Lolos'] == 0].sort_values(by=['Gap SKU', 'Realisasi SKU Sold'], ascending=[True, False])

            st.write(f"Ditemukan **{len(gap_outlets):,}** toko (dalam scope MHS) yang belum lolos target:")
            cols_gap = ['No Outlet', 'Nama Outlet', 'Salesman', 'Kelas Toko', 'Kabupaten', 'Target SKU', 'Realisasi SKU Sold', 'Gap SKU']

            tbl_gap = beri_nomor_urut(gap_outlets[cols_gap])
            st.dataframe(tbl_gap, use_container_width=True, hide_index=True)
            st.download_button("📥 Download Excel Gap Toko", data=convert_df_to_excel({'GAP_TOKO': tbl_gap}), file_name="Gap_Toko_Action_Plan.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            st.markdown("---")
            st.markdown("### 🔍 **Pemeriksaan Detail SKU & Referensi Push Order Toko**")
            st.caption("Pilih salah satu toko di bawah untuk melihat rincian seluruh varian SKU yang SUDAH masuk sesuai realisasi:")

            if len(gap_outlets) > 0:
                gap_outlets = gap_outlets.copy()
                gap_outlets['Pilihan_Label'] = gap_outlets['No Outlet'].astype(str) + " - " + gap_outlets['Nama Outlet'] + " (Kurang " + gap_outlets['Gap SKU'].astype(str) + " SKU | " + gap_outlets['Salesman'] + ")"
                outlet_options = gap_outlets['Pilihan_Label'].tolist()

                selected_outlet_label = st.selectbox("Pilih Toko untuk Melihat Detail SKU:", outlet_options)
                selected_no_outlet = int(selected_outlet_label.split(" - ")[0])

                toko_info = gap_outlets[gap_outlets['No Outlet'] == selected_no_outlet].iloc[0]
                class_code_toko = int(toko_info['Class_Code'])

                st.markdown(f"""
                <div class="outlet-card">
                    <h4 style="margin:0; color:#0f172a;">🏪 {toko_info['Nama Outlet']} (No: {toko_info['No Outlet']})</h4>
                    <p style="margin:4px 0 0 0; font-size:0.85rem; color:#475569;">
                        Salesman: <b>{toko_info['Salesman']}</b> | Kelas Toko: <b style="color:#0284c7;">{toko_info['Kelas Toko']}</b><br>
                        Target Wajib: <b>{toko_info['Target SKU']} SKU</b> | Sudah Masuk: <b style="color:#0284c7;">{toko_info['Realisasi SKU Sold']} SKU</b> |
                        Kekurangan: <b style="color:#dc2626;">{toko_info['Gap SKU']} SKU Lagi</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # Detail MHS: tampilkan DISTINCT MHS, bukan seluruh PCode/varian.
                df_outlet_tx = outlet_prod_positive[
                    outlet_prod_positive['No Outlet'] == selected_no_outlet
                ].copy()
                df_outlet_tx = df_outlet_tx[
                    df_outlet_tx['Pcode_Str'].apply(
                        lambda p: cek_sku_valid(p, class_code_toko)
                    )
                ]

                # Gabungkan beberapa PCode yang mewakili MHS yang sama.
                df_sku_sudah = (
                    df_outlet_tx.groupby('MHS_KEY', as_index=False)
                    .agg(
                        PCode=('Pcode_Str', lambda s: ', '.join(sorted(set(map(str, s))))),
                        Net_Qty=('NET_QTY', 'sum')
                    )
                    .sort_values('MHS_KEY')
                    .rename(columns={'MHS_KEY': 'MHS'})
                    .reset_index(drop=True)
                )

                # Referensi MHS wajib untuk class ini.
                wajib_mhs = sorted({
                    PCODE_TO_MHS[p]
                    for p, classes in PCODE_ELIGIBLE_CLASS.items()
                    if class_code_toko in classes and p in PCODE_TO_MHS
                })
                sudah_mhs = set(df_sku_sudah['MHS'])
                belum_mhs = [m for m in wajib_mhs if m not in sudah_mhs]
                df_sku_belum = pd.DataFrame({'MHS': belum_mhs})

                col_sudah, col_belum = st.columns(2)
                with col_sudah:
                    st.markdown(f"#### ✅ MHS yang SUDAH Masuk ({len(df_sku_sudah)} MHS)")
                    if len(df_sku_sudah) > 0:
                        st.dataframe(
                            beri_nomor_urut(df_sku_sudah),
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("Belum ada MHS yang masuk.")

                with col_belum:
                    st.markdown(f"#### ❌ MHS yang BELUM Masuk ({len(df_sku_belum)} MHS)")
                    if len(df_sku_belum) > 0:
                        st.dataframe(
                            beri_nomor_urut(df_sku_belum),
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("Semua MHS wajib sudah masuk di toko ini.")

                buf_toko = io.BytesIO()
                with pd.ExcelWriter(buf_toko, engine='openpyxl') as writer:
                    df_sku_sudah.to_excel(writer, sheet_name='MHS_SUDAH_MASUK', index=False)
                    df_sku_belum.to_excel(writer, sheet_name='MHS_BELUM_MASUK', index=False)

                st.download_button(
                    label=f"📥 Download Excel Detail & Referensi MHS ({toko_info['Nama Outlet']})",
                    data=buf_toko.getvalue(),
                    file_name=f"Mapping_MHS_{toko_info['No Outlet']}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.success("🎉 Seluruh toko yang tercover sudah lolos target SKU!")

        # TAB 6: MASTER MAPPING & LIST SKU CHANNEL
        with tab6:
            st.subheader("📑 Master Mapping & Daftar Wajib SKU per Kelas Toko")
            st.caption("Daftar ini bersumber langsung dari REF_MHS resmi. PCode dipakai untuk validasi, tetapi daftar dan hitungan MHS menggunakan identitas MHS yang DISTINCT:")

            class_pick = st.selectbox("Kelas Toko:", options=[f"{code} - {name} (Target {target} SKU)" for code, (name, target) in CLASS_INFO.items()])
            picked_code = int(class_pick.split(" - ")[0])
            list_mhs = sorted({
                PCODE_TO_MHS[p]
                for p, classes in PCODE_ELIGIBLE_CLASS.items()
                if picked_code in classes and p in PCODE_TO_MHS
            })
            df_list = pd.DataFrame({'MHS': list_mhs}).sort_values('MHS')
            st.dataframe(beri_nomor_urut(df_list), use_container_width=True, hide_index=True)
            st.download_button("📥 Download Daftar MHS Wajib Kelas Ini", data=convert_df_to_excel({'MUST_HAVE_MHS': df_list}), file_name=f"MHS_Class_{picked_code}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except Exception as err:
        st.error(f"Gagal memproses file LBP: {str(err)}")
else:
    st.info("👈 Silakan upload file **LBP.txt** pada menu sebelah kiri untuk memproses dashboard monitoring.")
