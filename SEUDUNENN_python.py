import numpy as np
from numpy.lib.shape_base import apply_along_axis
import pandas as pd
from pandas import Series, DataFrame, Index
from functools import reduce
import warnings
warnings.filterwarnings("ignore")


# #Helsingin seudun väestöennusteohjelmisto, UUSI VERSIO 2020;
# #HUOM. VAIN Digiajan väestöennustejärjestelmä -Pääkaupunkiseudun mallityön projektiryhmän käyttöön, ei ulkopuolelle;
# #Seppo Laakso, Kaupunkitutkimus TA, versio 25.11.2020;
# #Tämän SAS-kooditiedoston nimi: Seuenn manual_V2020;
# Käännöstä Pythoniin työstänyt Miro Varilo

def main():
    # #TIEDOSTOT JA YEISPARAMETRIT;
    # #Lähtötiedoston nimi LIB-viiteineen, SAS-data;
    ltied_sas = 'vaesto2019.sas7bdat'
    # #Tulostiedoston (Ennuste) nimi, SAS-data, ei käytössä
    etied = pd.read_sas('hs_ve0_2019_2040.sas7bdat')
    # #Tulostiedoston (Ennuste) nimi polkuineen ja taulun nimi Excelissä;
    enn_exc = 'HS_Ve0_2019_2040.xls'
    enn_taul = 'Ve0'
    # #Lähtövuosi (=lähtötiedoston vuosiluku) ja ennustevuosi (=ennusteen viimeinen vuosi);
    lvuosi = 2019
    evuosi = 2040
    # #Syntyvien sp-jakauma: poikien osuus;
    Poikaos = 0.51

    # #PARAMETRITIEDOSTOT EXCEL;
    # #Erikseen Excel-tiedoston nimi ja taulun nimi;
    # #hedelmällisyys;
    hed_exc = 'SASExcel\\Hedelmallisyys.xls'
    # kuolemanvaara;
    kuo_exc = 'SASExcel\\Kuolemanvaara.xls'
    kuo_taul = 'Ve0'
    # HS sisäinen lähtömuutto;
    hsl_exc = 'SASExcel\\HSsis_lahto_2017_19.xls'
    hsl_taul = 'Ve0'
    # HS sisäinen tulomuutto;
    hst_exc = 'SASExcel\\HSsis_tulo_2017_19.xls'
    hst_taul = 'Ve0'
    # Työmarkkina lähtömuutto;
    tml_exc = 'SASExcel\\Tyomark_lahto_2017_19.xls'
    tml_taul = 'Ve0'
    # Työmarkkina tulomuutto;
    tmt_exc = 'SASExcel\\Tyomark_tulo_2017_19.xls'
    tmt_taul = 'Ve0'
    # Ulkomainen lähtömuutto;
    uml_exc = 'SASExcel\\Ulkom_lahto_2017_19.xls'
    uml_taul = 'Ve0'
    # Ulkomainen tulomuutto;
    umt_exc = 'SASExcel\\Ulkom_tulo_2017_19.xls'
    umt_taul = 'Ve0'

    # TÄSTÄ ETEENPÄIN KÄYTTÄJÄN EI TARVITSE MUUTTAA MITÄÄN (NORMAALITILANTEESSA);

    # VAIHE 2: LUETAAN PARAMETRITIEDOSTOT EXCELISTÄ

    # Lähtöväestö, esimerkkitiedoissa SAS-datasta, vaihda read_excel mikäli luet Excel-tiedostosta
    ltied = pd.read_sas(ltied_sas)
    print(ltied.head())

    # hedelmällisyys;
    hed = pd.read_excel(hed_exc)
    hed.sort_values(by=['alue', 'vuosi'])

    # kuolemanvaara;
    kuo = pd.read_excel(kuo_exc)
    kuo.sort_values(by=['alue', 'vuosi'])
    # HS sisäinen lähtömuutto;
    hsl = pd.read_excel(hsl_exc)
    hsl.sort_values(by=['alue', 'vuosi'])
    # HS sisäinen tulomuutto;
    hst = pd.read_excel(hst_exc)
    hst.sort_values(by=['alue', 'vuosi'])
    # Työmarkkina lähtömuutto;
    tml = pd.read_excel(tml_exc)
    tml.sort_values(by=['alue', 'vuosi'])
    # Työmarkkina tulomuutto;
    tmt = pd.read_excel(tmt_exc)
    tmt.sort_values(by=['alue', 'vuosi'])
    # Ulkomainen lähtömuutto;
    uml = pd.read_excel(uml_exc)
    uml.sort_values(by=['alue', 'vuosi'])
    # Ulkomainen tulomuutto;
    umt = pd.read_excel(umt_exc)
    umt.sort_values(by=['alue', 'vuosi'])

    print('Vaihe 1 ja 2 onnistuivat. Parametritiedostot luettu onnistuneesti. Aloitetaan ennusteen laskeminen (vie aikaa)...')
    # VAIHE 3: LUETAAN TIEDOSTOT ENNUSTEOHJELMAAN JA LASKETAAN ENNUSTEET;

    # Luetaan väestörakenteen lähtötiedosto ja poimitaan ennusteen lähtövuotta vastaava vuosi;

    vaesto = ltied.loc[ltied['vuosi'] == lvuosi]

    # Yhdistetään lähtötiedosto ja parametrit;
    ennuste = [vaesto, hed, kuo, hsl, hst, tml, tmt, uml, umt]
    ennuste = reduce(lambda left, right: pd.merge(left, right, on=['alue', 'vuosi'],
                                                how='outer'), ennuste)
    ennuste = ennuste.sort_values(by=['alue', 'vuosi'])
    ennuste = ennuste.drop(columns=['Kuvaus_x'])
    ennuste = ennuste.drop_duplicates()

    # print(ennuste.head())

    # print(ennuste['tmtyht'])

    # ENNUSTEEN LASKENTA;

    # data ennuste; set yhd0; by alue;
    # 	if &lvuosi<=vuosi<=&evuosi;			#poimitaan ennustejakson vuodet, ml. lähtövuosi;
    # Taulukot joissa väestö- ja parametrimuuttujat ryhmittäin;

    # miehet 31.12.vvvv
    indata = ['m' + str(x) for x in range(100)]
    mi = ennuste[indata]

    # naiset 31.12.vvvv
    indata = ['n' + str(x) for x in range(100)]
    ni = ennuste[indata]

    # apumuuttujat joihin viedään ed.v. väestö;
    # apumuuttujat miehet;
    apumi = mi

    # apumuuttujat naiset;
    apuni = ni

    # hedelmällisyydet;
    indata = ['h' + str(x) for x in range(15, 50)]
    hed = ennuste[indata]

    # # apumuuttujat hedelmällisyysikäiset naiset;
    indata = ['n' + str(x) for x in range(15, 50)]
    apuhn = ennuste[indata].copy()

    #  miesten kuolemanvaarat, 0-99-v;
    indata = ['mkv' + str(x) for x in range(100)]
    mkv = ennuste[indata]
    #  naisten kuolemanvaarat, 0-99-v;
    indata = ['nkv' + str(x) for x in range(100)]
    nkv = ennuste[indata]
    # miesten työm.muutto tulo;
    indata = ['mtt' + str(x) for x in range(100)]
    mtmt = ennuste[indata]
    # naisten työm.muutto tulo;
    indata = ['ntt' + str(x) for x in range(100)]
    ntmt = ennuste[indata]
    # miesten ulkom. muutto tulo;
    indata = ['mut' + str(x) for x in range(100)]
    mumt = ennuste[indata]
    # naisten ulkom. muutto tulo;
    indata = ['nut' + str(x) for x in range(100)]
    numt = ennuste[indata]
    # miesten HS sis. muutto tulo;
    indata = ['mst' + str(x) for x in range(100)]
    msmt = ennuste[indata]
    # naisten HS sis. umuutto tulo;
    indata = ['nst' + str(x) for x in range(100)]
    nsmt = ennuste[indata]
    # miesten työm.muutto lähtö;
    indata = ['mtl' + str(x) for x in range(100)]
    mtml = ennuste[indata]
    # naisten työm.muutto lähtö;
    indata = ['ntl' + str(x) for x in range(100)]
    ntml = ennuste[indata]
    # miesten ulkom. muutto lähtö;
    indata = ['mul' + str(x) for x in range(100)]
    muml = ennuste[indata]
    # naisten ulkom. muutto lähtö;
    indata = ['nul' + str(x) for x in range(100)]
    numl = ennuste[indata]
    # miesten HS sis. muutto lähtö;
    indata = ['msl' + str(x) for x in range(100)]
    msml = ennuste[indata]
    # naisten HA sis. muutto lähtö;
    indata = ['nsl' + str(x) for x in range(100)]
    nsml = ennuste[indata]

    mkvs = ennuste['mkvs']
    nkvs = ennuste['nkvs']

    tmtyht = ennuste['tmtyht']
    umtyht = ennuste['umtyht']
    smtyht = ennuste['smtyht']
    tmlyht = ennuste['tmlyht']
    umlyht = ennuste['umlyht']
    smlyht = ennuste['smlyht']
    iyht = ennuste['iyht']

    counter = 0
    synt = 0


    # *ENNUSTEEN LASKENTA;

    # print(ennuste)
    ennusteAlue = 0
    firstAlue = True

    for x in range(0, len(ennuste.index)):

        if (ennusteAlue == ennuste['alue'].iloc[x]):
            firstAlue = False
        else:
            ennusteAlue = ennuste['alue'].iloc[x]
            firstAlue = True

    # 	*ikäryhmien ennusteet 1-98-vuotiaille;
        if (firstAlue == False):
            apumi = mi
            apuni = ni
            for i in range(0, 99):
                mi.iloc[x, i+1] = apumi.iloc[x-1, i]+tmtyht.iloc[x] * \
                    mtmt.iloc[x, i]+umtyht.iloc[x]*mumt.iloc[x, i] + \
                    smtyht.iloc[x]*msmt.iloc[x, i]-tmlyht.iloc[x] * \
                    mtml.iloc[x, i]-umlyht.iloc[x]*muml.iloc[x, i]-smlyht.iloc[x] * \
                    msml.iloc[x, i]-apumi.iloc[x-1, i]*mkv.iloc[x, i]/1000

                ni.iloc[x, i+1] = apuni.iloc[x-1, i]+tmtyht.iloc[x] * \
                    ntmt.iloc[x, i]+umtyht.iloc[x]*numt.iloc[x, i] + \
                    smtyht.iloc[x]*nsmt.iloc[x, i]-tmlyht.iloc[x] * \
                    ntml.iloc[x, i]-umlyht.iloc[x]*numl.iloc[x, i]-smlyht.iloc[x] * \
                    nsml.iloc[x, i]-apuni.iloc[x-1, i]*nkv.iloc[x, i]/1000

    # 	*ennuste 99+ -vuotiaille;
        if (firstAlue == False):
            mi.iloc[x, 99] = apumi.iloc[x-1, 98]+tmtyht.iloc[x] * \
                mtmt.iloc[x, 98]+umtyht.iloc[x]*mumt.iloc[x, 98] + \
                smtyht.iloc[x]*msmt.iloc[x, 98]-tmlyht.iloc[x] * \
                mtml.iloc[x, 98]-umlyht.iloc[x]*muml.iloc[x, 98]-smlyht.iloc[x] * \
                msml.iloc[x, 98]-apumi.iloc[x-1, 98]*mkv.iloc[x, 98]/1000+apumi.iloc[x-1, 99]+tmtyht.iloc[x] * \
                mtmt.iloc[x, 99]+umtyht.iloc[x]*mumt.iloc[x, 99] + \
                smtyht.iloc[x]*msmt.iloc[x, 99]-tmlyht.iloc[x] * \
                mtml.iloc[x, 99]-umlyht.iloc[x]*muml.iloc[x, 99]-smlyht.iloc[x] * \
                msml.iloc[x, 99]-apumi.iloc[x-1, 99]*mkv.iloc[x, 99]/1000

            ni.iloc[x, 99] = apuni.iloc[x-1, 98]+tmtyht.iloc[x] * \
                ntmt.iloc[x, 98]+umtyht.iloc[x]*numt.iloc[x, 98] + \
                smtyht.iloc[x]*nsmt.iloc[x, 98]-tmlyht.iloc[x] * \
                ntml.iloc[x, 98]-umlyht.iloc[x]*numl.iloc[x, 98]-smlyht.iloc[x] * \
                nsml.iloc[x, 98]-apuni.iloc[x-1, 98]*nkv.iloc[x, 98]/1000+apuni.iloc[x-1, 99]+tmtyht.iloc[x] * \
                ntmt.iloc[x, 99]+umtyht.iloc[x]*numt.iloc[x, 99] + \
                smtyht.iloc[x]*nsmt.iloc[x, 99]-tmlyht.iloc[x] * \
                ntml.iloc[x, 99]-umlyht.iloc[x]*numl.iloc[x, 99]-smlyht.iloc[x] * \
                nsml.iloc[x, 99]-apuni.iloc[x-1, 99]*nkv.iloc[x, 99]/1000


    # 	*syntyneet summa, huom. hedelmällisyydet 1/1000;
    # *hed.ik.naiset (ed.v.31.12) *hedelmällisyys, ikä 15-49;
        if(firstAlue == False):
            indata = ['n' + str(x) for x in range(15, 50)]
            apuhn = ni[indata].copy()
            synt = 0
            for i in range(0, 35):
                synt = synt + hed.iloc[x, i]*apuhn.iloc[x-1, i]/1000
    # 	*vuoden aikana syntyneet 0-vuotiaiksi 31.12.;
    # 	*Otetaan huomioon syntyvien kuolemanvaara syntymävuoden aikana;
        if(firstAlue == False):
            mi.iloc[x, 0] = Poikaos*synt*(1-mkvs.iloc[x]/1000)
            ni.iloc[x, 0] = (1-Poikaos)*synt*(1-nkvs.iloc[x]/1000)
    # 	*kuolleet summa, sisältää myös syntymävuonna kuolleet pojat ja tytöt, huom. kuolemanvaarat 1/1000;
    #  	  		kuol1  *Kuolleet ilman synt.v. kuolleita;
        if(firstAlue == False):
            kuol1 = apumi.iloc[x, i]*mkv.iloc[x, 0] / \
                1000+apuni.iloc[x, 0]*nkv.iloc[x, 0]/1000
    # 		kuol2  *Synt.vuonna kuolleet;
            kuol2 = Poikaos*synt*mkvs.iloc[x]/1000 + \
                (1-Poikaos)*synt*nkvs.iloc[x]/1000
    # 		 *Kuolleet yht.;
            kuol = kuol1+kuol2

    # 	*yhteenvetosummia;
        # if(firstAlue == False):
        summa = mi.iloc[x].sum() + ni.iloc[x].sum()
        iyht.iloc[x] = summa

    # 	*apumuuttujille arvot 31.12.vvvv;
        apumi = mi
        apuni = ni
        # Päivitys seuraavalle vuodelle
        ennuste.update(mi)
        ennuste.update(ni)
        ennuste.update(iyht)

    print('Vaihe 3 onnistui. Tulostetaan ennusteet tiedostoksi...')
    # *VAIHE 4: TULOSTETAAN ENNUSTE EXCEL-TAULUKSI

    # *Tulostetaan pysyvään tiedostoon parametrit ym. poistettuna;

    men = ['m' + str(x) for x in range(100)]
    women = ['n' + str(x) for x in range(100)]
    # var = ['iyht', 'myht', 'nyht', 'synt', 'kuol', 'tmtyht', 'umtyht', 'smtyht', 'tmlyht', 'umlyht', 'smlyht']
    var = ['alue', 'vuosi', 'iyht']
    var = var + men + women
    ennuste = ennuste[var]

    tiedostonNimi = enn_exc
    tulostus = ennuste
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
        # writer = pd.ExcelWriter(tiedostonNimi)
        tulostus.to_csv(tiedostonNimi)
        # writer.save()
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
