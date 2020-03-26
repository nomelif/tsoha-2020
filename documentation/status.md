# Nykytila

Värkkiin kirjautuminen ja tunnuksen luominen on nyt toteutettu ja heroku-sovellus toimii PostgreSQL-tietokannan päällä. Värkkiin voi kirjautunut käyttäjä lähettää viestejä ja äänestysketju toimii. Viestit näkyvät nyt ja omia viestejä voi poistaa ja muokata (muokkaukset tulevat näkyviin vasta kun ne ovat käyneet läpi moderaatioketjun. Muokatun viestin poistaminen palauttaa sen muokkausta edeltäneeseen tilaan). Käyttäjätunnuksen näkyvän nimen voi vaihtaa samoin kuin salasanan. Tilin voi poistaa kokonaan.

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
