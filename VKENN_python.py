# *PKS-kaupunkien osa-alue-ennusteohjelmisto, UUSI VERSIO 2021;
# *HUOM. VAIN 'Digiajan väestöennustejärjestelmä -Pääkaupunkiseudun mallityö' projektiryhmän käyttöön, ei ulkopuolelle;
# *Seppo Laakso, Kaupunkitutkimus TA, versio 22.3.2021;
# *Vanhan kannan ennusteohjelma;
# *Tämän SAS-kooditiedoston nimi: VKENN_uusi_v2021;
# Käännöstä Pythoniin työstänyt Miro Varilo

from functools import reduce
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")


def main():
    # *VAIHE 1: ANNETAAN PARAMETREILLE ARVOT TAI MUUTETAAN VANHOJA ARVOJA
    # *TIEDOSTOT JA YEISPARAMETRIT
    # *Kunnan osa-aluetiedoston nimi LIB-viiteineen, SAS-data; *Alla esimerkki, ei käytössä
    # ltied = pd.read_sas('Parametrit\\vaesto2019.sas7bdat')
    # /* Vaihtoehto käytössä
    # *Kunnan osa-aluetiedosto Excelissä sekä taulun nimi; *Alla esimerkit
    Vaesto = 'Parametrit\\Lahto_vaesto_2019_pilotti.xlsx'
    # *Tulostiedoston (Ennuste) nimi polkuineen ja taulun nimi Excelissä; *Alla esimerkit;
    enn_exc = 'VKenn_Ve1_2019_2040.xlsx'
    enn_taul = 'Ve1'
    # *Lähtövuosi (=lähtötiedoston vuosiluku) ja ennustevuosi (=ennusteen viimeinen vuosi); *Alla esimerkit
    lvuosi = 2019
    evuosi = 2040
    # *Syntyvien sp-jakauma: poikien osuus;
    Poikaos = 0.51

    # *PARAMETRITIEDOSTOT EXCEL;
    # *Erikseen Excel-tiedoston nimi ja taulun nimi; *Alla pilottiversion parametrit testausta varten
    # *hedelmällisyys;
    hed_exc = 'Parametrit\\PKS_hed_2021.xlsx'
    # *kuolemanvaara;
    kuo_exc = 'Parametrit\\PKS_kv_2021.xlsx'
    # *muuttoliike;
    ml_exc = 'Parametrit\\VK_muutto_pilotti.xlsx'
    # *alueiden tyypittelyparametrit;	*Pilottitaulussa Hgin testiain., Espooseen ja Vantaalle tehtävä oma versio vastaavasti
    alue_exc = 'Parametrit\\VK_param_pilotti.xlsx'

    print('Vaihe 1 onnistui')

    # *TÄSTÄ ETEENPÄIN KÄYTTÄJÄN EI TARVITSE MUUTTAA MITÄÄN (JOS HOMMA TOIMII)
    # *VAIHE 2: LUETAAN LÄHTÖVUODEN VÄESTÖTILASTO (SAS tai Excel) SEKÄ PARAMETRITIEDOSTOT EXCELISTÄ
    # *Lähtövuoden väestötiedosto;
    # vaesto = ltied

    # *Vaihtoehto luku Excelistä;
    vaesto = pd.read_excel(Vaesto)
    vaesto.sort_values(by=['alue', 'vuosi'])

    # *hedelmällisyys;
    hed = pd.read_excel(hed_exc)
    hed = hed.sort_values(by=['hedtyyp', 'vuosi'])

    # *kuolemanvaara;
    kuo = pd.read_excel(kuo_exc)
    kuo = kuo.sort_values(by=['kvtyyp', 'vuosi'])

    # *tulo- ja lähtömuutto;
    muutto = pd.read_excel(ml_exc)
    muutto = muutto.sort_values(by=['muuttotyyp'])

    # *alueiden tyypittelyparametrit;
    alue = pd.read_excel(alue_exc)
    alue = alue.sort_values(by=['alue'])

    print('Vaihe 2 onnistui')
    # *VAIHE 3: YHDISTETÄÄN LÄHTÖTIEDOSTOT JA GENEROIDAAN ENNUSTEVUODET;

    # *Yhdistetään lähtövuoden väestö ja alueparametrit;
    vaes_alue0 = vaesto.merge(alue, on=['alue', 'Aluenimi'], how='inner')
    # *Generoidaan vuodet;
    vaes_alue = vaes_alue0
    men = ['m' + str(x) for x in range(100)]
    women = ['n' + str(x) for x in range(100)]

    # Luodaan uudet vuodet ja niille tyhjät arvot
    for v in range(lvuosi+1, evuosi+1):
        vuosi = v
        for i in range(len(vaes_alue0.index)):
            uusi = vaes_alue.loc[i]
            uusi.loc['iyht'] = 0
            uusi.loc['vuosi'] = vuosi
            uusi.loc[men] = 0
            uusi.loc[women] = 0
            vaes_alue = vaes_alue.append(uusi, ignore_index=True)

    # *Yhdistetään muuttotiedot by muuttotyyp;
    vaes_alue = vaes_alue.sort_values(by=['muuttotyyp'])
    vaes_alue_muut = vaes_alue.merge(muutto, on=['muuttotyyp'])

    # *Yhdistetään hed.data by hedtyyp;
    vaes_alue_muut_hed = vaes_alue_muut.merge(
        hed, on=['hedtyyp', 'vuosi'], how='left')

    # *Yhdistetään KV-data by KVtyyp;
    vaes_alue_muut_hed_KV = vaes_alue_muut_hed.merge(
        kuo, on=['kvtyyp', 'vuosi'], how='left')
    vaes_alue_muut_hed_KV.sort_values(by=['alue', 'vuosi'])

    print('Vaihe 3 onnistui. Aloitetaan ennusteen tekeminen (vie aikaa...)')

    # *VAIHE 4: 	ENNUSTEEN LASKENTA ;
    # Poimitaan ennustejakson vuodet, ml. lähtövuosi;
    ennuste = vaes_alue_muut_hed_KV[(vaes_alue_muut_hed_KV['vuosi'] >= lvuosi) & (
        vaes_alue_muut_hed_KV['vuosi'] <= evuosi)]
    ennuste = ennuste.sort_values(by=['alue', 'vuosi'])

    print(ennuste)
    # *Taulukot joissa väestö- ja parametrimuuttujat ryhmittäin;
    # * miehet 31.12.vvvv;
    indata = ['m' + str(x) for x in range(100)]
    mi = ennuste[indata]
    # * naiset 31.12.vvvv;
    indata = ['n' + str(x) for x in range(100)]
    ni = ennuste[indata]
    # apumuuttujat joihin viedään ed.v. väestö
    # * apumuuttujat miehet
    apumi = mi
    # * apumuuttujat naiset;
    apuni = ni
    # * hedelmällisyydet;
    indata = ['h' + str(x) for x in range(15, 50)]
    hed = ennuste[indata]
    # * apumuuttujat hedelmällisyysikäiset naiset;
    indata = ['n' + str(x) for x in range(15, 50)]
    apuhn = ennuste[indata].copy()

    # * miesten kuolemanvaarat, 0-99-v;
    indata = ['mkv' + str(x) for x in range(100)]
    mkv = ennuste[indata]
    # * naisten kuolemanvaarat, 0-99-v;
    indata = ['nkv' + str(x) for x in range(100)]
    nkv = ennuste[indata]

    # Alustetaan miesten muutto tulo  (lasketaan tulomuutosta ja ikäosuuksista);
    mtmt = mi.copy()
    # Alustetaan naisten muutto tulo  (-"-);
    ntmt = ni.copy()
    # Alustetaan miesten muutto lähtö (lasketaan lähtömuutosta ja ikäosuuksista);
    mtml = mi.copy()
    # Alustetaan naisten muutto lähtö (-"-);
    ntml = ni.copy()
    # * tulomuuttajien (m+n) ikäosuudet;
    indata = ['tmos' + str(x) for x in range(100)]
    tmos = ennuste[indata]
    # * lähtömuuttajien (m+n) ikäosuudet;
    indata = ['lmos' + str(x) for x in range(100)]
    lmos = ennuste[indata]

    # Tulomuutto yhteensä
    tmyht = ennuste['tmyht']
    # Lähtömuutto yhteensä
    lmyht = ennuste['lmyht']

    # Kuolemanvaara syntymävuonna miehillä
    mkvs = ennuste['mkvs']
    # Kuolemanvaara syntymävuonna naisilla
    nkvs = ennuste['nkvs']

    iyht = ennuste['iyht']

    # Apumuuttujat, jotta nähdään ollaanko alueen ensimmäisessä vuodessa
    ennusteAlue = 0
    firstAlue = True

    # Aloitetaan ennusteiden laskeminen vuosittain
    for x in range(0, len(ennuste.index)):

        # Jos alue on sama kuin edellinen, asetetaan ensimmäiseksi alueeksi epätosi, muuten tosi
        if (ennusteAlue == ennuste['alue'].iloc[x]):
            firstAlue = False
        else:
            ennusteAlue = ennuste['alue'].iloc[x]
            firstAlue = True

        # *lasketaan naisten ja miesten tulo- ja lähtömuutto
        # *Oletus: tulo- ja lähtömuutossa miesten ja naisten osuus 1/2 kaikissa ikäryhmissä
        for i in range(100):
            # Naisten ja miesten tulomuutto
            mtmt.iloc[x, i] = tmyht.iloc[x]*tmos.iloc[x, i]/2
            ntmt.iloc[x, i] = tmyht.iloc[x]*tmos.iloc[x, i]/2
            # Naisten ja miesten lähtömuutto
            mtml.iloc[x, i] = lmyht.iloc[x]*lmos.iloc[x, i]/2
            ntml.iloc[x, i] = lmyht.iloc[x]*lmos.iloc[x, i]/2

        # *Korjataan hedelmällisyys- ja kuolemanvaaralukuja alueilla
        # * korj. hedelmällisyyttä alueilla, jossa hedero määritelty
        for i in range(0, 35):
            if (ennuste['hedero'].iloc[x] != 0):
                hed.iloc[x, i] = (
                    1+ennuste['hedero'].iloc[x]/100)*hed.iloc[x, i]

        # * korj. kuolemanvaaraa alueilla, joissa kvero määritelty
        for i in range(100):
            if ennuste['kvero'].iloc[x] != 0:
                mkv.iloc[x, i] = (
                    1+ennuste['kvero'].iloc[x]/100)*mkv.iloc[x, i]
                nkv.iloc[x, i] = (
                    1+ennuste['kvero'].iloc[x]/100)*nkv.iloc[x, i]

       # *ikäryhmien ennusteet 1-98-vuotiaille alkean lähtövuotta seuraavasta vuodesta;
        if (firstAlue == False):
            apumi = mi
            apuni = ni
            for i in range(0, 99):
                mi.iloc[x, i+1] = apumi.iloc[x-1, i]+mtmt.iloc[x, i] - \
                    mtml.iloc[x, i]-apumi.iloc[x-1, i]*mkv.iloc[x, i]/1000
                ni.iloc[x, i+1] = apuni.iloc[x-1, i]+ntmt.iloc[x, i] - \
                    ntml.iloc[x, i]-apuni.iloc[x-1, i]*nkv.iloc[x, i]/1000

        # *ennuste 99+ -vuotiaille: ed.v:n 98-vuotiaat + 99+ -vuotiaat;
        if (firstAlue == False):
            mi.loc[x, 99] = apumi.iloc[x-1, 98]+mtmt.iloc[x, 98] - \
                mtml.iloc[x, 98]-apumi.iloc[x-1, 98]*mkv.iloc[x, 98]/1000 + apumi.iloc[x-1, 99] + \
                mtmt.iloc[x, 99] - mtml.iloc[x, 99] - \
                apumi.iloc[x-1, 99]*mkv.iloc[x, 99]/1000

            ni.loc[x, 99] = apuni.iloc[x-1, 98]+ntmt.iloc[x, 98] - \
                ntml.iloc[x, 98]-apuni.iloc[x-1, 98]*nkv.iloc[x, 98]/1000 + apuni.iloc[x-1, 99] + \
                ntmt.iloc[x, 99] - ntml.iloc[x, 99] - \
                apuni.iloc[x-1, 99]*nkv.iloc[x, 99]/1000

        # *syntyneet summa, huom. hedelmällisyydet 1/1000
        if(firstAlue == False):
            indata = ['n' + str(x) for x in range(15, 50)]
            apuhn = ni[indata].copy()
            synt = 0
            for i in range(0, 35):
                synt = synt + hed.iloc[x, i]*apuhn.iloc[x-1, i]/1000

        # *vuoden aikana syntyneet 0-vuotiaiksi 31.12.;
        # *Otetaan huomioon syntyvien kuolemanvaara syntymävuoden aikana;
        if(firstAlue == False):
            mi.iloc[x, 0] = Poikaos*synt*(1-mkvs.iloc[x]/1000)
            ni.iloc[x, 0] = (1-Poikaos)*synt*(1-nkvs.iloc[x]/1000)

        # *Kontrolloidaan mahdolliset negatiiviset määrät ikäryhmissä;
        for i in range(100):
            if(mi.iloc[x, i] < 0):
                mi.iloc[x, i] = 0
            if(ni.iloc[x, i] < 0):
                ni.iloc[x, i] = 0

    # 	*kuolleet summa, sisältää myös syntymävuonna kuolleet pojat ja tytöt, huom. kuolemanvaarat 1/1000;
        if(firstAlue == False):
            # Kuolleet ilman synt.v. kuolleita;
            kuol1 = apumi.iloc[x, i]*mkv.iloc[x, 0] / \
                1000+apuni.iloc[x, 0]*nkv.iloc[x, 0]/1000
            # Synt.vuonna kuolleet;
            kuol2 = Poikaos*synt*mkvs.iloc[x]/1000 + \
                (1-Poikaos)*synt*nkvs.iloc[x]/1000
            # Kuolleet yht.;
            kuol = kuol1+kuol2

    # yhteenvetosummia;
        if(firstAlue == False):
            summa = mi.iloc[x].sum() + ni.iloc[x].sum()
            iyht.iloc[x] = summa

    # Apumuuttujille arvot 31.12.vvvv
        apumi = mi
        apuni = ni
    # Ikäryhmien päivitys
        ennuste.update(mi)
        ennuste.update(ni)
        ennuste.update(iyht)

    print('Vaihe 4 onnistui')

    # *VAIHE 5: TULOSTETAAN ENNUSTE EXCEL-TAULUKSI
    # Tulostus Excel-tiedostoksi
    lista = ['alue', 'vuosi', 'iyht', 'tmyht', 'lmyht']
    lista = lista + men + women
    tulostus = ennuste[lista]
    tiedostonNimi = enn_exc
    tulostaTaulukko(tulostus, tiedostonNimi)


def tulostaTaulukko(tulostus, tiedostonNimi):
    try:
        writer = pd.ExcelWriter(tiedostonNimi)
        tulostus.to_excel(writer, 'output_sheet')
        writer.save()
        print('Ennuste onnistui. Tallennettu tiedostoon ' + tiedostonNimi)
    except PermissionError:
        print(
            'Tallentaminen epäonnistui! Ei oikeuksia tallentaa (tiedosto kenties jo auki).')
        user_input = input("Haluatko yrittää uudelleen? Y/N: ")
        if(user_input == 'Y'):
            tulostaTaulukko(tulostus, tiedostonNimi)

def tulostaTaulukkoCSV(tulostus, tiedostonNimi):
    try:
        tulostus.to_csv(tiedostonNimi)
        print('Ennuste onnistui. Tallennettu tiedostoon ' + tiedostonNimi)
    except PermissionError:
        print(
            'Tallentaminen epäonnistui! Ei oikeuksia tallentaa (tiedosto kenties jo auki).')
        user_input = input("Haluatko yrittää uudelleen? Y/N: ")
        if(user_input == 'Y'):
            tulostaTaulukko(tulostus, tiedostonNimi)


if __name__ == "__main__":
    main()


def indataf(indata, x, function=None):
    if indata == 1:
        if function:
            x = function(x)
        return x
    else:
        return np.NaN
