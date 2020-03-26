# Nykytila

Värkkiin kirjautuminen ja tunnuksen luominen on nyt toteutettu ja heroku-sovellus toimii PostgreSQL-tietokannan päällä. Värkkiin voi kirjautunut käyttäjä lähettää viestejä ja äänestysketju toimii. Viestit näkyvät nyt ja omia viestejä voi poistaa ja muokata (muokkaukset tulevat näkyviin vasta kun ne ovat käyneet läpi moderaatioketjun. Muokatun viestin poistaminen palauttaa sen muokkausta edeltäneeseen tilaan).

Projekti toteuttaa tällä hetkellä viikon 2 vaatimukset (ainakin niin pitkälti kuin ne käsitän). Viestit tietokohteena ovat CRUD-kunnossa (niitä voi luoda, muokata, selata ja poistaa). Toisaalta systeemi säilyttää viestien muokkaushistorian ja muutamien metaolioiden poistoa en ole vielä toteuttanut (niistä ei ole sinänsä haittaa, mutta käsittääkseni tilanne ei muuten täytä crud-vaatimusta) Kierrätin myös saman sivun viestin luomiseen ja muokkaamiseen (asian kanssa tuli kiirettä), niin ei lopullisessa tekeleessä todennäköisesti tule olemaan. (Sen takia muokkaa-namiskan painamisella avautuvalla sivulla on vähän jännä otsikko)

Valikko ei ole oikein mielekäs käyttöliittymän valinta, mutta jokaiselle sivulle on kyllä linkki jostakin relevantista paikasta sovellusta.
