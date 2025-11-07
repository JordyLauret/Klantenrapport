import streamlit as st
from pdfminer.high_level import extract_text
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(page_title="Balan’z Klantenrapport", page_icon="📊")

st.title("📊 Klantenrapport – Financiële Analyse")
st.markdown("Upload hieronder een financieel PDF-rapport en voeg je persoonlijke commentaar toe.")

uploaded = st.file_uploader("Upload PDF-rapport", type=["pdf"])

def zoek_bedrag(label, tekst):
    patroon = rf"{label}[\s\S]*?([\d\.,]+)"
    match = re.search(patroon, tekst)
    if match:
        bedrag = match.group(1).replace('.', '').replace(',', '.')
        try:
            return float(bedrag)
        except:
            return None
    return None

if uploaded:
    tekst = extract_text(uploaded)
    # Extractie
    omzet = zoek_bedrag("Omzet", tekst)
    brutomarge = zoek_bedrag("Brutomarge", tekst)
    personeelskosten = zoek_bedrag("Bezoldigingen", tekst)
    diensten = zoek_bedrag("Diensten en diverse goederen", tekst)
    afschrijvingen = zoek_bedrag("Afschrijvingen", tekst)
    resultaat = zoek_bedrag("Bedrijfsresultaat", tekst)
    winst = zoek_bedrag("Winst na belastingen", tekst)

    st.header("📈 Automatische analyse")
    if omzet:
        st.metric("Omzet", f"€ {omzet:,.0f}")
    if brutomarge:
        st.metric("Brutomarge", f"€ {brutomarge:,.0f}", f"{brutomarge/omzet*100:.1f}% van omzet")
    if personeelskosten:
        st.metric("Personeelskosten", f"€ {personeelskosten:,.0f}", f"{personeelskosten/omzet*100:.1f}% van omzet")
    if resultaat:
        st.metric("Bedrijfsresultaat", f"€ {resultaat:,.0f}", f"{resultaat/omzet*100:.1f}% van omzet")

    # Automatische tekstanalyse
    analyse = []
    if brutomarge and personeelskosten:
        ratio = personeelskosten / brutomarge
        if ratio > 0.7:
            analyse.append("⚠️ De personeelskost ligt vrij hoog in verhouding tot de marge.")
        else:
            analyse.append("✅ De personeelskost ligt op een gezond niveau.")
    if resultaat and resultaat > 0:
        analyse.append("✅ Het bedrijfsresultaat is positief, wat duidt op winstgevendheid.")
    else:
        analyse.append("⚠️ Het bedrijfsresultaat is negatief, kostenstructuur verdient aandacht.")

    st.markdown("### 📋 Automatische bevindingen")
    for lijn in analyse:
        st.markdown(f"- {lijn}")

    st.markdown("### ✍️ Jouw persoonlijke commentaar")
    extra = st.text_area("Voeg hier je eigen analyse of aanbevelingen toe", height=200)

    if st.button("📄 Genereer klantenrapport (PDF)"):
        bestand = "Klantenrapport_Balanz.pdf"
        doc = SimpleDocTemplate(bestand, pagesize=A4)
        styles = getSampleStyleSheet()
        stijl_titel = ParagraphStyle('Titel', parent=styles['Title'], textColor=colors.HexColor("#2E4053"))
        normaal = styles["Normal"]

        elementen = []
        elementen.append(Paragraph("📊 Klantenrapport – Financiële Analyse", stijl_titel))
        elementen.append(Spacer(1, 12))

        data = [["Categorie", "Bedrag (€)", "% t.o.v. omzet"]]
        def rij(label, waarde):
            return [label, f"{waarde:,.0f}", f"{(waarde/omzet)*100:.1f}%"] if waarde else [label, "-", "-"]

        data.extend([
            rij("Omzet", omzet),
            rij("Brutomarge", brutomarge),
            rij("Personeelskosten", personeelskosten),
            rij("Diensten en diverse goederen", diensten),
            rij("Afschrijvingen", afschrijvingen),
            rij("Bedrijfsresultaat", resultaat),
            rij("Winst na belastingen", winst),
        ])

        tabel = Table(data, colWidths=[6*cm, 4*cm, 4*cm])
        tabel.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2E4053")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey)
        ]))
        elementen.append(tabel)
        elementen.append(Spacer(1, 18))

        elementen.append(Paragraph("<b>Automatische analyse</b>", normaal))
        for lijn in analyse:
            elementen.append(Paragraph(lijn, normaal))
        elementen.append(Spacer(1, 18))

        if extra:
            elementen.append(Paragraph("<b>Persoonlijke commentaar</b>", normaal))
            elementen.append(Paragraph(extra.replace("\n", "<br/>"), normaal))

        doc.build(elementen)
        with open(bestand, "rb") as pdf:
            st.download_button("💾 Download Klantenrapport", pdf, file_name=bestand)
