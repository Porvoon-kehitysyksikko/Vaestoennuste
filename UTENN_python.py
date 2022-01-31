# *PKS-kaupunkien uustuotannon väestön osa-alue-ennusteohjelmisto, UUSI VERSIO 2021;
# *Versio 2: muuttoparametrien sijasta sovelletaan jäljellejäämiskertoimia (JJkert);
# *HUOM. VAIN 'Digiajan väestöennustejärjestelmä -Pääkaupunkiseudun mallityö' projektiryhmän käyttöön, ei ulkopuolelle;
# *Seppo Laakso, Kaupunkitutkimus TA, versio 3.5.2021;
# *Uustuotannon ennusteohjelma;
# *Tämän SAS-kooditiedoston nimi: UTENN_uusi_v2021_JJkerr;
# Käännöstä Pythoniin työstänyt Miro Varilo

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")


def main():
    # *VAIHE 1: PARAMETROIDAAN JA NIMETÄÄN LÄHTÖ- JA PARAMETRITIEDOSTOT;

    # *TIEDOSTOT JA YEISPARAMETRIT;
    # *Asuntotuotannon osa-alue-ennusteen tiedosto Excelissä sekä taulun nimi;
    Astuot = 'Parametrit\\Astuot_alue_pilotti.xlsx'
    # /* Vaihtoehto;
    # *Asuntotuotantotiedoston nimi LIB-viiteineen, SAS-data;
    # *Tulostiedoston (Ennuste) nimi polkuineen ja taulun nimi Excelissä;
    utenn_exc = 'Parametrit\\UTenn_alue_pilotti.xlsx'
    # *Lähtövuosi (=1. asuntotuotantovuoden vuosiluku) ja ennustevuosi (=as.tuotannon ja väestöennusteen viimeinen vuosi);
    lvuosi = 2020
    evuosi = 2035
    # *Tuotantovuosien lukumäärä;
    tuotvv = 16
    # *Syntyvien sp-jakauma: poikien osuus;
    Poikaos = 0.51

    # *PARAMETRITIEDOSTOT EXCEL;
    # *Erikseen Excel-tiedoston nimi ja taulun nimi;
    # *hedelmällisyys;
    hed_exc = 'Parametrit\\PKS_Hed_2021.xlsx'
    # *kuolemanvaara;
    kuo_exc = 'Parametrit\\PKS_KV_2021.xlsx'
    # *Jäljellejäämiskertoimet;
    JJ_exc = 'Parametrit\\UT_JJkert_pilotti.xlsx'
    # *Asuntotyyppien parametrit;
    UTtyyp_exc = 'Parametrit\\UT_param_pilotti.xlsx'
    # *Asuntotyyppien ikäjakauma alkutilanteessa;
    UTika_exc = 'Parametrit\\UT_ikajak_pilotti.xlsx'

    # *TÄSTÄ ETEENPÄIN KÄYTTÄJÄN EI TARVITSE MUUTTAA MITÄÄN (JOS HOMMA TOIMII);

    # *VAIHE 2: LUETAAN UUSTUOTANNON ENNUSTE SEKÄ PARAMETRITIEDOSTOT EXCELISTÄ SAS:IIN;
    # *Uustuotannon ennuste alueittain;
    Astuot = pd.read_excel(Astuot)
    # *hedelmällisyys;
    hed = pd.read_excel(hed_exc)
    hed = hed.sort_values(by=['hedtyyp', 'vuosi'])
    hed.dropna(subset=["vuosi"], inplace=True)

    # *kuolemanvaara;
    kuo = pd.read_excel(kuo_exc)
    kuo = kuo.sort_values(by=['kvtyyp', 'vuosi'])
    # *jäljellejäämiskertoimet;
    JJkert = pd.read_excel(JJ_exc)
    JJkert = JJkert.sort_values(by=['Tyyppi'])
    # *UT-tyyppien parametrit;
    tyypit = pd.read_excel(UTtyyp_exc)
    tyypit = tyypit.sort_values(by=['Tyyppi'])
    tyypit = tyypit[tyypit['Tyyppi'] != np.NaN]
    tyypit.dropna(subset=["Tyyppi"], inplace=True)
    print(tyypit)
    # *UT-ikäjakauma parametrit;
    ika = pd.read_excel(UTika_exc)
    ika = ika.sort_values(by=['Tyyppi'])

    # *VAIHE 3: MUOKATAAN ASUNTOTUOTANTOENNUSTE PROJEKTIOMALLIN VAATIMAAN MUOTOON JA GENEROIDAAN ENNUSTEVUODET
    # *tulostetaan s.e. aluettain joka vuodella ja joka tyypillä on oma rivi
    #  *Huom. tuotantovuosien lkm pitää antaa alussa paremetrina
    xx0 = Astuot
    indata = ['Vv' + str(x) for x in range(1, tuotvv)]
    xx0 = Astuot[['alue', 'Tyyppi']]
    vv = Astuot[indata]
    kerala = pd.DataFrame()

    cell = 0
    for i in range(0, len(vv.index)):
        for y in range(1, tuotvv-1):
            kerala.loc[cell, 'alue'] = xx0['alue'].iloc[i]
            kerala.loc[cell, 'Tyyppi'] = xx0['Tyyppi'].iloc[i]
            kerala.loc[cell, 'vuosi'] = lvuosi+y-1
            kerala.loc[cell, 'kerala'] = vv.iloc[i, y]
            cell = cell+1
    print(kerala)
    xx0 = kerala

    # *Mukaan vain rivit joissa kerala>0;
    xx = xx0[xx0['kerala'] > 0]

    # *lajitellaan tyypin mukaan;
    xx = xx.sort_values(by=['Tyyppi'])

    # *Liitetään parametrit;
    # *siirretään tyhjäksi jäävät seur. vuoteen omana tietueenaan;
    # tyhos eli valmistuvien asuntojen tyhjäksi jääminen, tällä hetkellä 5 prosenttia siirretään seuraavaan vuoteen
    # tee seuraava rivi tyhosin mukaan
    apumerge = tyypit[['Tyyppi', 'tyhos']]
    xx2 = xx.merge(apumerge, on=['Tyyppi'])
    kerapu = xx2['kerala']
    print(xx2)

    i = 0
    try:
        while xx2.loc[i, 'kerala'] > 0:
            xx2.loc[i, 'kerala'] = (1-xx2.loc[i, 'tyhos']/100)*kerapu[i]
            seuraavaVuosi = xx2.loc[i]
            seuraavaVuosi.loc['kerala'] = (xx2.loc[i, 'tyhos']/100)*kerapu[i]
            seuraavaVuosi.loc['vuosi'] = seuraavaVuosi.loc['vuosi'] + 1
            seuraavaVuosi.loc['kerala'] = (xx2.loc[i, 'tyhos']/100)*kerapu[i]
            xx2 = xx2.append(seuraavaVuosi)
            i += 1
    except:
        print(xx2)

    # *summataan alueen, tyypin ja vuoden suhteen (samaan rakentamiskohorttiin kuuluvat yhteen);
    xx2b = xx2.sort_values(by=['alue', 'Tyyppi', 'vuosi'])
    print(xx2b.loc[0, 'alue'])
    xx2b = xx2b.groupby(['alue', 'Tyyppi', 'vuosi', 'tyhos'],
                        as_index=False).sum().reset_index()
    print(xx2b)

    # *Annetaan jokaiselle tietueelle koodi (juokseva nro), jonka avulla as.tuot.kohortit voidaan erottaa toisistaan;
    xx3 = xx2b
    for i in range(0, len(xx3.index)):
        xx3.loc[i, 'kohort'] = i
        # 	*poistetaan ennustejakson jälkeen täyttyvät asunnot, jotka siirretty seur. v:lle;
        if(xx3.loc[i, 'vuosi'] > evuosi):
            xx3.drop([i, 'vuosi'])
    print(xx3)

    # *yhdistetään parametrit ja ikäjakaumat tuotantolukuihin sekä lasketaan 1. vuoden asukkaat iän mukaan;
    yy = xx3.merge(tyypit, on=['Tyyppi'])
    yy = yy.merge(ika, on=['Tyyppi'])
    yy['iyht'] = yy['kerala']/yy['alkuvalj']
    yy = yy.sort_values(by=['alue', 'Tyyppi', 'vuosi'])

    print(yy)

    # *osuudet 1-v. ikäryhmittäin;
    indata = ['os' + str(x) for x in range(100)]
    oo = yy[indata]

    #   *asukk. 1-v. ikäryhmittäin;
    iiData = ['i' + str(x) for x in range(100)]
    iiColumns = pd.DataFrame(columns=iiData)
    yy = pd.concat([yy, iiColumns], axis=1)

    ii = yy[iiData]

    #   do i=1 to 100; ii{i}=iyht*oo{i}; end; *lasketaan ikäryhmien asukasmäärät
    #   *vuosi=vuosi+1;             /* muutet. tuot.v. 1. asukaslukuv:ksi   */
    print(yy)
    for x in range(0, len(yy.index)):
        for i in range(0, 100):
            ii.iloc[x, i] = yy.loc[x, 'iyht']*oo.iloc[x, i]
    yy.update(ii)
    print(ii)

    # *Generoidaan vuodet rak.valm.vuodesta e-vuoteen;
    yy2 = yy
    print(yy2)
    men = ['m' + str(x) for x in range(100)]
    women = ['n' + str(x) for x in range(100)]

    menColumns = pd.DataFrame(columns=men)
    womenColumns = pd.DataFrame(columns=women)

    yy2 = pd.concat([yy2, menColumns], axis=1)
    yy2 = pd.concat([yy2, womenColumns], axis=1)

    for i in range(100):
        men = 'm' + str(i)
        yy2.loc[:, men] = 0

    for i in range(100):
        women = 'n' + str(i)
        yy2.loc[:, women] = 0

    yy2 = yy2.sort_values(by=['alue', 'Tyyppi', 'vuosi'])
    print(yy2)

    # Alustetaan arvot ennustevuosille
    valmv = int(yy2.loc[0, 'vuosi'])
    for v in range(valmv+1, evuosi+1):
        vuosi = v
        for i in range(len(yy.index)):
            uusi = yy2.loc[i]
            uusi.loc['iyht'] = 0
            uusi.loc['vuosi'] = vuosi
            uusi.loc[men] = 0
            uusi.loc[women] = 0
            yy2 = yy2.append(uusi, ignore_index=True)

    yy2 = yy2.sort_values(by=['alue', 'Tyyppi', 'vuosi'])
    print(yy2)

    # *YHDISTETÄÄN PARAMETRITIEDOT AS.TUOT.TIETOIHIN;
    hed = hed.sort_values(by=['hedtyyp', 'vuosi'])

    # *Hedelmällisyysparametrit vuosittain;
    h = yy2.merge(hed, on=['hedtyyp', 'vuosi'])
    print(h)

    # *Kuolemanvaaraparametrit vuosittain;
    k = h.merge(kuo, on=['kvtyyp', 'vuosi'])
    print(kuo)

    # *JJkertoimien parametrit;
    utpohja = k.merge(JJkert, on=['Tyyppi'])
    print(utpohja)

    # *VAIHE 4: LASKETAAN JAKSON VUOSIEN ENNUSTEET VUOSI KERRALLAAN;
    # *HUOM. PITÄÄ VIELÄ LISÄTÄ OPISKELIJA- JA SENIORIRAKENNUSTEN KÄSITTELY (IKÄJAKAUMA PIDETÄÄN VAKIONA);

    # data UTenn; set UTpohja; by alue kohort vuosi;
    utenn = utpohja
    utenn = utenn.sort_values(by=['alue', 'kohort', 'vuosi'])
    print(utenn)
    # 	if &lvuosi<=vuosi<=&evuosi;			*poimitaan enn.jakson vuodet, ml. lähtövuosi (norm. ei vaikuta mihinkään);
    # 	*Taulukot joissa väestö- ja parametrimuuttujat ryhmittäin;
    # * asukkaat (m+n) 31.12.vvvv;

    indata = ['i' + str(x) for x in range(100)]
    ii = utenn[indata]

    #     array hed(35)   h15-h49;      		* hedelmällisyydet;
    indata = ['h' + str(x) for x in range(15, 50)]
    hed = utenn[indata]
    #     array apuhn(35) apun15-apun49; 		* apumuuttujat hedelmällisyysikäiset naiset;
    indata = ['n' + str(x) for x in range(15, 50)]
    apuhn = utenn[indata].copy()
    #     array mkv{100}  mkv0-mkv99;  		* miesten kuolemanvaarat, 0-99-v;
    indata = ['mkv' + str(x) for x in range(100)]
    mkv = utenn[indata]
    #     array nkv{100}  nkv0-nkv99;  		* naisten kuolemanvaarat, 0-99-v;
    indata = ['nkv' + str(x) for x in range(100)]
    nkv = utenn[indata]
    # 	array jjk{100} jj0-jj99;			* jäljellejäämiskertoimet, 0-99-v;
    indata = ['jj' + str(x) for x in range(100)]
    jjk = utenn[indata]

    mkvs = utenn['mkvs']
    nkvs = utenn['nkvs']
    iyht = utenn['iyht']

    indata = ['m' + str(x) for x in range(100)]
    mi = utenn[indata]
    indata = ['n' + str(x) for x in range(100)]
    ni = utenn[indata]
    for i in range(0, 100):
        mi.iloc[i] = ii.iloc[i]/2
        ni.iloc[i] = ii.iloc[i]/2

    #  *apumuuttujat joihin viedään ed.v. miehet ja naiset;
    apumi = mi
    apuni = ni

    utennKohort = np.NAN
    firstKohort = True

    print(utenn)

    # print(len(utenn.index))

    for x in range(0, len(utenn.index)):

        if (utennKohort == utenn['kohort'].iloc[x]):
            firstKohort = False
        else:
            utennKohort = utenn['kohort'].iloc[x]
            firstKohort = True

        # 	*Jaetaan 1.vuoden asukkaat (m+n) miehiin ja naisiin;
        if (firstKohort == True):
            indata = ['m' + str(x) for x in range(100)]
            mi = utenn[indata]
            indata = ['n' + str(x) for x in range(100)]
            ni = utenn[indata]
            for i in range(0, 100):
                mi.iloc[i] = ii.iloc[i]/2
                ni.iloc[i] = ii.iloc[i]/2
            #  apumuuttujat miehet;
            apumi = mi
            #  apumuuttujat naiset;
            apuni = ni

        # 	*Korjataan hedelmällisyys- ja kuolemanvaaralukuja alueilla;
        #   * korj. hedelmällisyyttä alueilla, jossa hedero määritelty;
        if (utenn['hedero'].iloc[x] != 0):
            for i in range(0, 35):
                hed.iloc[x, i] = (1+utenn['hedero'].iloc[x]/100)*hed.iloc[x, i]

        # * korj. kuolemanvaaraa alueilla, joissa kvero määritelty;
        if (utenn['kvero'].iloc[x] != 0):
            for i in range(100):
                mkv.iloc[x, i] = (1+utenn['kvero'].iloc[x]/100)*mkv.iloc[x, i]
                nkv.iloc[x, i] = (1+utenn['kvero'].iloc[x]/100)*nkv.iloc[x, i]

       # *ikäryhmien ennusteet 1-98-vuotiaille alkaen rak.kohortin lähtövuotta seuraavasta vuodesta;
        if (firstKohort == False):
            for i in range(0, 99):
                mi.iloc[x, i+1] = apumi.iloc[x-1, i]*jjk.iloc[x, i] - \
                    apumi.iloc[x-1, i]*mkv.iloc[x, i]/1000
                ni.iloc[x, i+1] = apuni.iloc[x-1, i]*jjk.iloc[x, i] - \
                    apuni.iloc[x-1, i]*nkv.iloc[x, i]/1000

    # 	*ennuste 99+ -vuotiaille: ed.v:n 98-vuotiaat + 99+ -vuotiaat;
        if (firstKohort == False):
            mi.loc[x, 99] = apumi.iloc[x-1, 98]*jjk.iloc[x, 98] - \
                -apumi.iloc[x-1, 98]*mkv.iloc[x, 98]/1000 + apumi.iloc[x-1, 99]*jjk.iloc[x, 99] - \
                apumi.iloc[x-1, 99]*mkv.iloc[x, 99]/1000

            ni.loc[x, 99] = apuni.iloc[x-1, 98]*jjk.iloc[x, 98] - \
                -apuni.iloc[x-1, 98]*nkv.iloc[x, 98]/1000 + apuni.iloc[x-1, 99]*jjk.iloc[x, 99] - \
                apuni.iloc[x-1, 99]*nkv.iloc[x, 99]/1000

    # 	*syntyneet summa, huom. hedelmällisyydet 1/1000;
        if(firstKohort == False):
            indata = ['n' + str(x) for x in range(15, 50)]
            apuhn = ni[indata].copy()
            synt = 0
            for i in range(0, 35):
                synt = synt + hed.iloc[x, i]*apuhn.iloc[x, i]/1000
    # 	*vuoden aikana syntyneet 0-vuotiaiksi 31.12.;
    # 	*Otetaan huomioon syntyvien kuolemanvaara syntymävuoden aikana;
    # 	*HUOM. EI OTETA HUOMIOON SYNTYNEIDEN MUUTTOA SYNT.V:N AIKANA;
        if(firstKohort == False):
            mi.iloc[x, 0] = Poikaos*synt*(1-mkvs.iloc[x]/1000)
            ni.iloc[x, 0] = (1-Poikaos)*synt*(1-nkvs.iloc[x]/1000)
    # 	*Kontrolloidaan mahdolliset negatiiviset määrät ikäryhmissä;
        for i in range(100):
            if(mi.iloc[x, i] < 0):
                mi.iloc[x, i] = 0
            if(ni.iloc[x, i] < 0):
                ni.iloc[x, i] = 0
        # Kuolleet summa, sisältää myös syntymävuonna kuolleet pojat ja tytöt, huom. kuolemanvaarat 1/1000;
        #  	  	*Kuolleet ilman synt.v. kuolleita;
        if(firstKohort == False):
            kuol1 = apumi.iloc[x, i]*mkv.iloc[x, 0] / \
                1000+apuni.iloc[x, 0]*nkv.iloc[x, 0]/1000
        # 	*Synt.vuonna kuolleet;
            kuol2 = Poikaos*synt*mkvs.iloc[x]/1000 + \
                (1-Poikaos)*synt*nkvs.iloc[x]/1000
        # 	*Kuolleet yht.;
            kuol = kuol1+kuol2
    # 	*yhteenvetosummia;
    # 		if not(first.kohort) then do;
    # 		    iyht=sum(of m0-m99 n0-n99);		*koko väestö;
    # 		    myht=sum(of m0-m99);			*miehet yht;
    # 		    nyht=sum(of n0-n99);			*naiset yht;
    # 			*tmyht=sum(of myt0-myt99 nyt0-nyt99);	*tulomuutto yht;
    # 			*lmyht=sum(of myl0-myl99 nyl0-nyl99);	*lähtömuutto yht;
        if(firstKohort == False):
            utenn['iyht'].iloc[x] = mi.iloc[x].sum() + ni.iloc[x].sum()
            summa = mi.iloc[x].sum() + ni.iloc[x].sum()
            iyht = summa
    # 	*asukkaat iän mukaan (m+n);
        for i in range(100):
            ii.iloc[x, i] = mi.iloc[x, i]+ni.iloc[x, i]
    # 	*apumuuttujille arvot 31.12.vvvv iän ja sp:n mukaan ja koko väestö;
        apumi = mi
        apuni = ni

    # Väestön päivitys seuraavaa vuotta varten
        utenn.update(mi)
        utenn.update(ni)
        utenn.update(ii)
        utenn.update(iyht)

    # *VAIHE 5: TULOSTETAAN ENNUSTE EXCEL-TAULUKSI

    # *Summataan kohortit aluetasolle;
    # proc summary data=Utenn nway;
    #   class alue vuosi;
    #   var iyht i0-i99 m0-m99 n0-n99 myht nyht synt kuol; *tmyht lmyht;
    #   output out=Ut_alue(drop=_type_ _freq_) sum=;
    # run;
    # lista = ['iyht', iiData, men, women, 'synt', 'kuol', 'iyht']
    # utenn2 = utenn[lista]
    # print(utenn2)

    # *summataan koko kaup. tasolle;
    # proc summary data=Utenn nway;
    #   class vuosi;
    #   var iyht i0-i99 m0-m99 n0-n99 myht nyht synt kuol; *tmyht lmyht;
    #   output out=Ut_kaup(drop=_type_ _freq_) sum=;
    # run;
    # data Ut_kaup; length alue 8; set Ut_kaup; alue=0; run;

    # *Tulostetaan pysyvään tiedostoon parametrit ym. poistettuna;
    # data &UTetied; set UT_alue UT_kaup ; by alue;
    #   *if alue=. then alue=0;	*Aluesumma: alue=0;
    #   muutos=iyht-lag(iyht); if first.alue then muutos=.;
    #   lmuutos=synt-kuol;
    #   nmuutto=muutos-lmuutos;	*lasketaan  nettomuutto muutoksen ja lmuutoksen erotuksena;
    #   keep alue vuosi iyht--n99 myht nyht muutos lmuutos nmuutto synt kuol;
    # run;

    # *Tulostus Excel-tiedostoksi
    # *PILOTTI: Kontrollitulostus toimivuuden tarkistamiseksi: Helsinki yhteensä + muutama alue;

    men = ['m' + str(x) for x in range(100)]
    women = ['n' + str(x) for x in range(100)]
    utenn_exc = 'UTenn_alue_pilotti.xlsx'
    lista = ['alue', 'vuosi', 'iyht']
    lista = lista + men + women
    tulostus = utenn[lista]
    tiedostonNimi = utenn_exc
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
