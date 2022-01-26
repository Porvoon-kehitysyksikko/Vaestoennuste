# *Vanhan kannan ja uustuotannon ennusteen yhdistäminen ja täsmääminen koko kaup. ennusteeseen, UUSI VERSIO 2021;
# *HUOM. VAIN 'Digiajan väestöennustejärjestelmä -Pääkaupunkiseudun mallityö' projektiryhmän käyttöön, ei ulkopuolelle;
# *Seppo Laakso, Kaupunkitutkimus TA, versio 3.5.2021;
# *Tämän SAS-kooditiedoston nimi: ENN_tasmays;
# Käännöstä Pythoniin työstänyt Miro Varilo


from functools import reduce
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# *TÄSSÄ VERSIOSSA TÄSMÄYS TEHDÄÄN SEKÄ VANHAN KANNAN ETTÄ UUSTUOTANNON ENNUSTEESEEN SAMASSA SUHTEESSA;

def main():
    # *TÄSSÄ VERSIOSSA TÄSMÄYS TEHDÄÄN SEKÄ VANHAN KANNAN ETTÄ UUSTUOTANNON ENNUSTEESEEN SAMASSA SUHTEESSA;

    # *VAIHE 1: NIMETÄÄN YHDISTETTÄVÄT JA TÄSMÄTTÄVÄT LÄHTÖTIEDOSTOT SEKÄ TULOSTIEDOSTOT;

    # *Anna alue-ennusteen SAS-tiedostojen nimet ml. LIBname;
    # *Vanhan kannan alueellinen ennustetiedosto;
    VKdata0 = 'VHenn_alue_ylakoulut.xlsx'
    VKdata0 = pd.read_excel(VKdata0)
    # *Uustuotannon alueellinen ennustetiedosto;
    UTdata0 = 'UTenn_alue_ylakoulut.xlsx'
    UTdata0 = pd.read_excel(UTdata0)
    #*Yhdistetty ennustetiedosto ilman täsmäystä;
    YHDdata0 = 'YHD_testi.xlsx'
    # YHDdata0 = pd.read_excel(YHDdata0)
    # *Vanhan kannan alueellinen ennustetiedosto täsmättynä koko kaup. ennusteeseen;
    VKdata1 = 'Vkenn_tasm.xlsx'
    # VKdata1 = pd.read_excel(VKdata1)
    # *Uustuotannon alueellinen ennustetiedosto täsmättynä;
    UTdata1 = 'Utenn_tasm.xlsx'
    # UTdata1 = pd.read_excel(UTdata1)
    # *Yhdistetty ennustetiedosto täsmättynä;
    YHDtasm1 = 'YHDenn_tasm.xlsx'
    # YHDtasm1 = pd.read_excel(YHDtasm1)
    # *Anna koko kaupungin ennusteen (johon alue-ennuste täsmätään) SAS-tiedoston nimi ml.LIBname;
    # *Koko kaup. tason ennuste iän ja sp:n mukaan;
    SUMdata = 'ennusteSeutu.xlsx'
    SUMdata = pd.read_excel(SUMdata)
    # *Anna ennusteen lähtövuosi ja ennustevuosi (=viimeinen vuosi) täsmäyksessä;
    #  *lähtövuosi (vanhan kannan ennusteen lähtövuosi);
    #  *ennustevuosi (viimeinen vuosi josta sekä VK että UT ennuste);
    lvuosi = 2020
    evuosi = 2040

    # *VAIHE 2: YHDISTETÄÄN TIEDOSTOT JA TÄSMÄTÄÄN KOKO KAUPUNGIN ENNUSTEESEEN;

    # *Tulostetaan yhdistetty ennustetiedosto ilman täsmäystä, koko kaup. summa poistettuna;
    #   if &lvuosi<=vuosi<=&evuosi;
    rr = VKdata0.merge(UTdata0, how='outer', on=[
        'alue', 'vuosi'], suffixes=['_vk', '_ut'])
    print(rr)

    men = ['m' + str(x) for x in range(100)]
    women = ['n' + str(x) for x in range(100)]
    menColumns = pd.DataFrame(columns=men)
    womenColumns = pd.DataFrame(columns=women)

    for x in range(100):
        vkmi = rr['m' + str(x) + '_vk'].fillna(0)
        vkni = rr['n' + str(x) + '_vk'].fillna(0)
        utmi = rr['m' + str(x) + '_ut'].fillna(0)
        utni = rr['n' + str(x) + '_ut'].fillna(0)
        menColumns['m' + str(x)] = vkmi + utmi
        womenColumns['n' + str(x)] = vkni + utni

    iyht = rr['iyht_vk'].fillna(0) + rr['iyht_ut'].fillna(0)
    iyht.name = 'iyht'
    print(iyht)
    rr = pd.concat([rr, iyht], axis=1)
    print(rr['iyht'])

    rr = pd.concat([rr, menColumns], axis=1)
    rr = pd.concat([rr, womenColumns], axis=1)

    lista = ['alue', 'vuosi', 'iyht']
    lista = lista + men + women
    rr = rr[lista]
    print(rr)

    rr.drop_duplicates(subset=['alue', 'vuosi'], inplace=True)
    print(rr)

    tulostaTaulukko(rr, YHDdata0)

    # *Korjauskertoimien laskenta, joilla alkuperäisiä alue-ennusteita korjataan;
    # *vanhan kannan summa;
    vkVuosi = VKdata0['vuosi']

    indata = ['m' + str(x) for x in range(100)]
    vkmi = VKdata0[indata]
    # * naiset 31.12.vvvv;
    indata = ['n' + str(x) for x in range(100)]
    vkni = VKdata0[indata]

    VKdata0 = VKdata0.groupby('vuosi').sum().reset_index()

    lista = ['vuosi', 'iyht']
    lista = lista + men + women
    vksum = VKdata0[lista]
    print(VKdata0)

    # * uustuotannon summa;
    indata = ['m' + str(x) for x in range(100)]
    utmi = UTdata0[indata]
    # * naiset 31.12.vvvv;
    indata = ['n' + str(x) for x in range(100)]
    utni = UTdata0[indata]
    utsum = UTdata0['iyht']

    UTdata0 = UTdata0.groupby('vuosi').sum().reset_index()
    utsum = UTdata0[lista]
    print(utsum)
    # *yhdistetään VK & UT;

    yhtsum = pd.merge(vksum, utsum, on='vuosi',
                      how='outer', suffixes=['_vk', '_ut'])
    print(yhtsum)
    yhtsum.fillna(0, inplace=True)

    men = ['m' + str(x) for x in range(100)]
    women = ['n' + str(x) for x in range(100)]
    menColumns = pd.DataFrame(columns=men)
    womenColumns = pd.DataFrame(columns=women)

    for x in range(100):
        vkmi = yhtsum['m' + str(x) + '_vk'].fillna(0)
        vkni = yhtsum['n' + str(x) + '_vk'].fillna(0)
        utmi = yhtsum['m' + str(x) + '_ut'].fillna(0)
        utni = yhtsum['n' + str(x) + '_ut'].fillna(0)
        menColumns['m' + str(x)] = vkmi + utmi
        womenColumns['n' + str(x)] = vkni + utni

    iyht = yhtsum['iyht_vk'].fillna(0) + yhtsum['iyht_ut'].fillna(0)
    iyht.name = 'iyht'
    yhtsum = pd.concat([yhtsum, iyht], axis=1)

    yhtsum = pd.concat([yhtsum, menColumns], axis=1)
    yhtsum = pd.concat([yhtsum, womenColumns], axis=1)

    lista = ['vuosi', 'iyht']
    lista = lista + men + women
    
    # * VK:n + UT:n summa;
    yhtsum = yhtsum[lista]
    print(yhtsum)


    # *Tehdään koko kaupungin ennusteesta Tavoite-data;
    #   if &lvuosi<=vuosi<=&evuosi and alue>0;
    tavoite = SUMdata

    indata = ['m' + str(x) for x in range(100)]
    mm = tavoite[indata]
    indata = ['n' + str(x) for x in range(100)]
    nn = tavoite[indata]
    tmm = mm.copy()
    tnn = nn.copy()
    tmm.columns = ['tm' + str(x) for x in range(100)]
    tnn.columns = ['tn' + str(x) for x in range(100)]
    print(tmm)
    print(tnn)
    tavoite = pd.concat([tavoite, tmm], axis=1)
    tavoite = pd.concat([tavoite, tnn], axis=1)
    var = ['vuosi'] + tmm.columns.tolist() + tnn.columns.tolist()
    tavoite = tavoite[var]
    print(tavoite)
    print(yhtsum)

    # *yhdistetään ennusteiden summa ja tavoite;

    yhd1 = yhtsum.merge(tavoite, on=[
                        'vuosi'])
    print(yhd1)
    indata = ['m' + str(x) for x in range(100)]
    yhd1mm = yhd1[indata]
    indata = ['n' + str(x) for x in range(100)]
    yhd1nn = yhd1[indata]
    print(yhd1mm)
    print(yhd1nn)
    indata = ['tm' + str(x) for x in range(100)]
    tmm = yhd1[indata]
    indata = ['tn' + str(x) for x in range(100)]
    tnn = yhd1[indata]
    iiData = ['kkm' + str(x) for x in range(100)]
    iiColumns = pd.DataFrame(columns=iiData)
    yhd1 = pd.concat([yhd1, iiColumns], axis=1)
    kkmm = yhd1[iiData]

    kkData = ['kkn' + str(x) for x in range(100)]
    kkColumns = pd.DataFrame(columns=kkData)
    yhd1 = pd.concat([yhd1, kkColumns], axis=1)
    kknn = yhd1[kkData]

    # * lasketaan korjauskertoimet siten, että kukin ikä/sp-ryhmä täsmää joka vuosi;
    for x in range(0, len(yhd1.index)):
        for i in range(100):
            kkmm.iloc[x, i] = tmm.iloc[x, i]/yhd1mm.iloc[x, i]
            kknn.iloc[x, i] = tnn.iloc[x, i]/yhd1nn.iloc[x, i]
    print(kkmm)
    print(kknn)
    yhd1.update(kkmm)
    yhd1.update(kknn)

    korjk = yhd1
    print(korjk)
    #   keep vuosi kkm0--kkm99 kkn0-kkn99;
    print('korjk')

    # *Lasketaan täsmätyt ennusteet käyttämällä korjauskertoimia;

    # *Täsmätty vanhan kannan ennuste;
    vk1 = VKdata0.sort_values(by=['vuosi'])


    #   if &lvuosi<=vuosi<=&evuosi and alue>0;
    vk2 = vk1.merge(korjk, on=['vuosi'], suffixes=['', 'korjk'])
    vk3 = vk2
    # * kerrotaan alkuperäiset ennustet korjauskertoimella;
    indata = ['m' + str(x) for x in range(100)]
    mm = vk3[indata]
    indata = ['n' + str(x) for x in range(100)]
    nn = vk3[indata]
    indata = ['kkm' + str(x) for x in range(100)]
    kkmm = vk3[indata]
    indata = ['kkn' + str(x) for x in range(100)]
    kknn = vk3[indata]
    
    iyht = vk3['iyht']

    print(vk3)

    for x in range(0, len(vk3.index)):
        for i in range(100):
            mm.iloc[x, i] = mm.iloc[x, i]*kkmm.iloc[x, i]
            nn.iloc[x, i] = nn.iloc[x, i]*kknn.iloc[x, i]
        summa = mm.iloc[x].sum() + nn.iloc[x].sum()
        iyht.iloc[x] = summa
    vk3.update(mm)
    vk3.update(nn)
    vk3.update(iyht)

    lista = ['alue', 'vuosi', 'iyht']
    lista = lista + men + women
    vk3 = vk3[lista]
    print(vk3)
    # *Täsmätty VK ennuste pysyvään tiedostoon;
    VKdata1 = vk3.sort_values(by=['alue', 'vuosi'])
    tiedostonNimi = 'VKdata1.xlsx'
    tulostaTaulukko(VKdata1, tiedostonNimi)

    # *Täsmätty uustuotannon ennuste;
    ut1 = UTdata0.sort_values(by=['vuosi'])
    ut2 = ut1.merge(korjk, how='outer', on=['vuosi'], suffixes=['', '_korjk'])

    ut3 = ut2
    print(ut3)
    indata = ['m' + str(x) for x in range(100)]
    mm = ut3[indata]
    indata = ['n' + str(x) for x in range(100)]
    nn = ut3[indata]
    indata = ['kkm' + str(x) for x in range(100)]
    kkmm = ut3[indata]
    indata = ['kkn' + str(x) for x in range(100)]
    kknn = ut3[indata]

    iyht = ut3['iyht']

    # * kerrotaan alkuperäiset ennustet korjauskertoimella;
    for x in range(0, len(ut3.index)):
        for i in range(100):
            mm.iloc[x, i] = mm.iloc[x, i]*kkmm.iloc[x, i]
            nn.iloc[x, i] = nn.iloc[x, i]*kknn.iloc[x, i]
        summa = mm.iloc[x].sum() + nn.iloc[x].sum()
        iyht.iloc[x] = summa
    ut3.update(mm)
    ut3.update(nn)
    ut3.update(iyht)

    # *Täsmätty VK ennuste pysyvään tiedostoon;
    lista = ['alue', 'vuosi', 'iyht']
    lista = lista + men + women
    UTdata1 = ut3[lista]
    print(UTdata1)

    # *Korjattujen ennusteiden yhdistäminen;
    vk_ut = VKdata1.merge(UTdata1, on=[
        'alue', 'vuosi'], suffixes=['_vk', '_ut'])
    print(vk_ut)

    men = ['m' + str(x) for x in range(100)]
    women = ['n' + str(x) for x in range(100)]
    menColumns = pd.DataFrame(columns=men)
    womenColumns = pd.DataFrame(columns=women)

    for x in range(100):
        vkmi = vk_ut['m' + str(x) + '_vk'].fillna(0)
        vkni = vk_ut['n' + str(x) + '_vk'].fillna(0)
        utmi = vk_ut['m' + str(x) + '_ut'].fillna(0)
        utni = vk_ut['n' + str(x) + '_ut'].fillna(0)
        menColumns['m' + str(x)] = vkmi + utmi
        womenColumns['n' + str(x)] = vkni + utni

    iyht = vk_ut['iyht_vk'].fillna(0) + vk_ut['iyht_ut'].fillna(0)
    iyht.name = 'iyht'
    print(iyht)
    vk_ut = pd.concat([vk_ut, iyht], axis=1)
    print(vk_ut['iyht'])

    lista = ['alue', 'vuosi', 'iyht']
    vk_ut = vk_ut[lista]
    vk_ut = pd.concat([vk_ut, menColumns], axis=1)
    vk_ut = pd.concat([vk_ut, womenColumns], axis=1)
    print(vk_ut)

    alue_sum = vk_ut
    # proc summary data=vk_ut nway missing;	*summataan täsmätyt VK ja UT alue- ja vuositasolla;
    #   class alue vuosi;
    #   var iyht myht nyht m0-m99 n0-n99;
    #   output out=alue_sum (drop=_type_ _freq_) sum=;
    # run;

    # proc summary data=vk_ut nway missing;	*summataan täsmätyt VK ja UT koko kaup. tasolla vuosittain;
    #   class vuosi;
    #   var iyht myht nyht m0-m99 n0-n99;
    #   output out=kaup_sum (drop=_type_ _freq_) sum=;
    # run;
    vk_ut = VKdata1.merge(UTdata1, how='outer', on=[
        'alue', 'vuosi'], suffixes=['_vk', '_ut'])
    print(vk_ut)

    men = ['m' + str(x) for x in range(100)]
    women = ['n' + str(x) for x in range(100)]
    menColumns = pd.DataFrame(columns=men)
    womenColumns = pd.DataFrame(columns=women)

    for x in range(100):
        vkmi = vk_ut['m' + str(x) + '_vk'].fillna(0)
        vkni = vk_ut['n' + str(x) + '_vk'].fillna(0)
        utmi = vk_ut['m' + str(x) + '_ut'].fillna(0)
        utni = vk_ut['n' + str(x) + '_ut'].fillna(0)
        menColumns['m' + str(x)] = vkmi + utmi
        womenColumns['n' + str(x)] = vkni + utni

    iyht = vk_ut['iyht_vk'].fillna(0) + vk_ut['iyht_ut'].fillna(0)
    iyht.name = 'iyht'
    print(iyht)
    vk_ut = pd.concat([vk_ut, iyht], axis=1)
    print(vk_ut['iyht'])

    vk_ut = pd.concat([vk_ut, menColumns], axis=1)
    vk_ut = pd.concat([vk_ut, womenColumns], axis=1)
    kaup_sum = vk_ut

    YHDtasm1 = kaup_sum
    # *tulostetaan täsmätty aineisto, koko kaup + alueet;

    tulostus = vk_ut[lista]
    tiedostonNimi = 'vk_ut.xlsx'
    lista = lista + men + women
    tulostus = vk_ut[lista]
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

def yhdistys(menColumns, womenColumns, vk_ut):
    for x in range(100):
        vkmi = vk_ut['m' + str(x) + '_vk'].fillna(0)
        vkni = vk_ut['n' + str(x) + '_vk'].fillna(0)
        utmi = vk_ut['m' + str(x) + '_ut'].fillna(0)
        utni = vk_ut['n' + str(x) + '_ut'].fillna(0)
        menColumns['m' + str(x)] = vkmi + utmi
        womenColumns['n' + str(x)] = vkni + utni