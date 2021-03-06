# Nykytila

Värkkiin kirjautuminen ja tunnuksen luominen on nyt toteutettu ja heroku-sovellus toimii PostgreSQL-tietokannan päällä. Värkkiin voi kirjautunut käyttäjä lähettää viestejä ja äänestysketju toimii. Viestit näkyvät nyt ja omia viestejä voi poistaa ja muokata (muokkaukset tulevat näkyviin vasta kun ne ovat käyneet läpi moderaatioketjun. Muokatun viestin poistaminen palauttaa sen muokkausta edeltäneeseen tilaan). Käyttäjätunnuksen näkyvän nimen voi vaihtaa samoin kuin salasanan. Tilin voi poistaa kokonaan. Ylätason viesteihin voi vastata. Hashtag-haku toimii.

# Viikko 2

Projekti toteuttaa tällä hetkellä viikon 2 vaatimukset (ainakin niin pitkälti kuin ne käsitän). Viestit tietokohteena ovat CRUD-kunnossa (niitä voi luoda, muokata, selata ja poistaa). Toisaalta systeemi säilyttää viestien muokkaushistorian ja muutamien metaolioiden poistoa en ole vielä toteuttanut (niistä ei ole sinänsä haittaa, mutta käsittääkseni tilanne ei muuten täytä crud-vaatimusta) Kierrätin myös saman sivun viestin luomiseen ja muokkaamiseen (asian kanssa tuli kiirettä), niin ei lopullisessa tekeleessä todennäköisesti tule olemaan. (Sen takia muokkaa-namiskan painamisella avautuvalla sivulla on vähän jännä otsikko)

Valikko ei ole oikein mielekäs käyttöliittymän valinta, mutta jokaiselle sivulle on kyllä linkki jostakin relevantista paikasta sovellusta.

# Viikko 3

Viikon 3 tavoitteet olivat:

* Sovelluksessa käytetyt lomakkeet validoivat syötetyn tiedon.
* Sovelluksessa on mahdollisuus rekisteröitymiseen.
* Sovelluksessa on mahdollisuus kirjautumiseen.
    * Kirjoita testitunnusten kirjautumiseen vaaditut tiedot README.md-tiedostoon.
* Sovelluksessa on ainakin kaksi tietokantataulua.
* Ainakin yhden tietokantataulun tietoihin liittyy täysi CRUD-toiminnallisuus sovelluksen kautta (yhden rivin luominen, yhden rivin tietojen näyttö, yhden rivin tietojen muokkaus, yhden rivin tietojen poisto, rivien listaus).
* Githubissa on issuet päällä, jotta koodikatselmointi on mahdollista. 
* Commit-viestit ovat yhä järkeviä ja kuvaavat tehtyjä lisäyksiä ja/tai muutoksia. 
* Herokussa käytetään Herokun tarjoamaa PostgreSQL-tietokannanhallintajärjestelmää.

Näiden tilanne on (järjestyksessä):

* Toteutin tämän uutena ominaisuutena tällä viikolla. Palvelin on kyllä tarkistanut syötetyn tiedon eheyden jo ennenkin.
* Ollut olemassa jo ennestään.
* Ollut olemassa ennestään.
    * Mitään erityistä testitunnusta ei ole, testaaja voi luoda tunnuksen itse sovelluksesta.
* Niitä on neljä.
* Käyttäjätietokantatauluun on ohjaajan mukaan (puitua Telegramissa) riittävä CRUD-toiminnallisuus. "Käyttäjä voi suoraan nähdä käyttäjänimen ja salasana luetaan tietokannasta kirjautuessa" todettiin riittäväksi read-ominaisuudeksi.
* Issuet ovat käsittääkseni päällä.
* Commitit ovat samaa tasoa kuin ennen.
* Hoidin tämän jo aikaisempana viikkona.

# Viikko 4

Viikon 4 tavoitteet olivat:

* Sovelluksessa on ainakin kolme tietokantataulua, joista jokainen on käytössä.
* Sovelluksessa on ainakin yksi monimutkaisempi (SQL-kielellä kirjoitettu) yhteenvetokysely, jonka tulokset näytetään käyttäjälle.
* Ulkoasun viilaus. Sovelluksessa käytetään Bootstrap-kirjastoa (tai muuta vastaavaa) ulkoasun tyylittelyssä.
* Toiminnallisuuden täydentäminen.

Näiden tilanne on (järjestyksessä):

* Tämä piti paikkansa jo viikon alussa. Aktiivisessa käytössä olevia tauluja löytyy peräti neljä.
* Näitä oli jo viime viikon jäljiltä. Hyvähköt esimerkit löytyvät [models.py](../application/varkki/models.py)-tiedoston `get_displayable_posts`-funktiosta.
* Tässä tein omaa CSSää valmiin kirjaston käyttämisen sijaan. Kysyin tämän luvallisuutta 12:09-14:13 17.3.2020 Telegramissa ja sain oman tulkintani mukaan myöntävän vastauksen:

```
Theo Friberg, [17.03.20 13:13]
>  Ulkoasun viilaus. Sovelluksessa käytetään Bootstrap-kirjastoa (tai muuta vastaavaa) ulkoasun tyylittelyssä. 

Eli itse rakkaudella käpistelty minimalistinen CSS ei kelpaa?

Theo Friberg, [17.03.20 13:15]
Katselin tuota nelososaa: https://materiaalit.github.io/tsoha-20/osa4/

Antti Laaksonen, [17.03.20 14:13]
[In reply to Theo Friberg]
Saa tehdä myös omalla tavalla
```

* Toteutin tällä viikolla vastaustoiminnallisuuden, väitän siis täydentäneeni toiminnallisuutta. Lisäsin myös muutamaan kuvakkeeseen alt-tekstin. Liiskasin myös [yhden bugin](https://github.com/nomelif/tsoha-2020/commit/b09a85d69552c84a368c52bef05569b8daaa0dee), joka lienee viikon kaksi palautteessa mainitun virhetoiminnan taustalla:

> En ole ihan varma, mutta viestiä muokatessa viestin omistaja pystyi merkitsemään oman viestin rakentavaksi, ja toinen henkilö ei nähnyt sitä listassa, mutta kolmas näki...

# Viikko 5:

Viikon 5 tavoitteet olivat:

* Autorisointi.
* Käytettävyyden viilausta.
* Toiminnallisuuden täydentäminen (uusia ominaisuuksia).
* Kirjoita työhösi alustava asennusohje ja käyttöohje.

Näiden tilanne on (järjestyksessä):

* Sovelluksessa on ollut autorisointia jo muutaman viikon. Esimerkiksi vain omia viestejä pystyy muokkaamaan ja poistamaan. Ainoastaan oman salasanan vaihtaminen onnistuu, eikä toisen käyttäjänimeä voi muokkata tai tiliä poistaa. Kurssimateriaali määrittelee autorisoinnin näin: "Autorisoinnilla tarkoitetaan varmistusta siitä, että käyttäjällä on oikeus hänen haluamaansa toimintoon." Tulkitsen siis, että sovellus täytti nämä vaatimukset jo ennen tätä viikkoa.
* Eriytin kirjautumissivun uuden käyttäjän luomiseen tarkoitetusta sivusta. Tästä oli tullut käytettävyyspalautetta viime viikolla.
* Kehitin tällä viikolla tilinhallintaominaisuuden, jota olin pitkään kaavaillut. Nyt käyttäjä voi sekä poistaa tietonsa pysyvästi, että ladata kaikki häntä koskevat tallennetut tiedot raakatekstinä.
* README.md-tiedostossa oli jo entuudestaan käyttöohje, jota vähän oikolukaisin. Tulevaisuudessa siitä voisi tehdä sivun itse sovellukseen. Asennusohjetta ei ollut, joten kirjoitin samaan tiedostoon nopeasti lisäkappaleen. Mitään hirveän erikoisia kommervenkkejä siihen ei liity.

Lisäksi korjasin viime viikon palautteessa mainitun bugin, joka heitti virhettä kun käyttäjän salasanaksi yritti vaihtaa alle kahdeksanmerkkistä merkkijonoa. Refaktoroin samaan syssyyn noiden validointia.

# Viikko 6:

Viikon 6 tavoitteet olivat:

* Toiminnallisuuden täydentäminen
* Ulkoasun, käytettävyyden ja toiminnallisuuden viilausta
* Tarvittaessa päivitä jo tehtyjä dokumentaation osia
* Aloita puuttuvan dokumentaation kirjoittaminen
* Koodikatselmointi

Näiden tilanne on (järjestyksessä)

* Toteutin avainsanahaun. Nyt jokainen käyttötapaus on toteutettu ja sainpahan vielä sen monesta moneen -suhteen aikaan.
* Mielestäni käytettävyystilanne oli jo kohtuullinen ennen tätä viikkoa. Nyt kun kaikki perustoiminnallisuudet ovat kunnossa niin voinen ensi viikolla panostaa kaiken yhteen skulaamiseen ja sovelluksen sisäiseen dokumentaatioon.
* Dokumentaatio piti pitkälti paikkansa.
* Kirjoitin nyt pitkälti kaiken sen dokumentaation mitä pyydettiin.
* Koodikatselmoin

# Loppupalautus


Loppupalautuksen tavoitteet olivat:

* Viimeiset viilaukset
* Loppupalautus
* Demo

Näiden tilanne on (järjestyksessä)

* Olen viilaillut tässä kaikenlaista. Suurin osa on ollut dokumentaatioduunia, mutta ihan koodailuakin tuli tehtyä:
    * Korjasin tietoturvabugin, jonka joku oli minulle itse sovellukseen demonstroinut [402844145e11420c720f95c6fbefcf4e54646b30](https://github.com/nomelif/tsoha-2020/commit/402844145e11420c720f95c6fbefcf4e54646b30)
    * Normalisoin kaikki hakusanat pieniksi kirjaimiksi [973646c3b4b9568fd5a09faa6fd9ac1b6ec609cd](https://github.com/nomelif/tsoha-2020/commit/973646c3b4b9568fd5a09faa6fd9ac1b6ec609cd)
    * Muunsin itse postauksien näyttämiseen käytetyn kyselysarjan yhdeksi hirviökyselyksi [b739afb3876463c224e8515f99346f36668ae66c](https://github.com/nomelif/tsoha-2020/commit/b739afb3876463c224e8515f99346f36668ae66c)
    * Stressitestasin Värkkiä ja lisäsin siihen kirjoittamani työkalut repoon [ef0dc01e3a33b396ab836160641416740b102dcb](https://github.com/nomelif/tsoha-2020/commit/ef0dc01e3a33b396ab836160641416740b102dcb)
    * Lisäsin stressitestauksen motivoimana tietokantaan indeksit
    * Lisäsin etusivulle vievän linkin kaikille sivuille [e9d227286990a6499526a67c319b1e9b643fd469](https://github.com/nomelif/tsoha-2020/commit/e9d227286990a6499526a67c319b1e9b643fd469)
    * Lisäsin käyttämiini kuvakkeisiin alt-tekstit [02cb40ad0741fee2776230d5b9cffc26fc4e0758](https://github.com/nomelif/tsoha-2020/commit/02cb40ad0741fee2776230d5b9cffc26fc4e0758)
* Koen nyt saaneeni värkin pitkälti loppupalautuskuntoon
* Demoa ei ilmeisesti pidetä
