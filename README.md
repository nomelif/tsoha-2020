# Värkki

Värkki on yksinkertainen sosiaalisen median palvelu, joka toteuttaa erään XKCD-sarjakuvan esittämän moderaatiomuodon:

![](https://imgs.xkcd.com/comics/constructive.png)

Rekistöröitynyt käyttäjä voi lisätä Värkkiin lyhyen markdowninkielisen ja mahdollisesti risuaidalla merkittyjä hakusanoja sisältävän kirjoituksen. Kirjoituksen lähettäminen vaatii kolmen muun kirjoituksen arvioimisen. Jos lisätty kirjoitus saa muilta käyttäjiltä kaksi positiivista arviota kolmesta, se julkaistaan.

Olemassa olevaan kirjoitukseen voidaan sitten vastaavalla tavalla lisätä viisi kommenttia. Sen jälkeen kirjoitus lukkiutuu, eikä siihen voida lisätä uusia kommentteja. Ylätason kirjoitus ja sen kommentit ovat alkuperäisen kirjoittajan poistettavissa ja muokattavissa vaikka kirjoitus olisikin lukkiutunut.

Kirjoituksia ja kommentteja voidaan hakea tekijän ja ajankohdan mukaan. Pysyväislinkit kirjoituksiin ovat pysyviä niin kauan kuin kirjoitusta ei poisteta.

## Heroku

Värkki elää herokussa [täällä](https://varkki.herokuapp.com/login).

## Käyttöohjetta

Värkkiin voi luoda kirjautunut käyttäjä tunnuksen. Kirjautuneena yläoikealla olevaa kynäkuvaketta painamalla voi luoda uuden viestin. Viestiä luodessa sovellus pyytää arvioimaan nollasta kolmeen kommenttia. Viestistä tulee näkyvä vasta kun kaksi muuta käyttäjää on arvioinut sen rakentavaksi. Mikäli kaksi muuta käyttäjää arvioi viestin ei-rakentavaksi, viesti poistetaan kokonaan. Siis jotta etusivulle ilmestyisi mitään, täytyy:

1. Luoda käyttäjä a
2. Kirjoittaa viesti (yläoikealla oleva kynäkuvake, tukee muuten markdownia)
3. Kirjautua ulos (yläoikealla oleva kuvake)
3. Luoda käyttäjä b
4. Kirjoittaa b:llä viesti ja merkitä a:n kommentti rakentavaksi
5. Kirjautua ulos
6. Luoda käyttäjä c
7. Kirjoittaa c:llä viesti ja merkitä a:n kommentti rakentavaksi

Nyt a:n viestin pitäisi näkyä. Viestiä voi muokata vain a:ksi kirjautuneena. Muokkauksien esiin tuleminen vaatii vastaavat kaksi rakentavuusääntä. Viestin poisto on välitön. Jos viestiä on muokattu, poisto palauttaa viestin sen aikaisempaan tilaan.

## Dokumentaation rakenteesta

Dokumentaatiosta löytyy tiedot Värkin:

* [Tietokantarakenteesta](documentation/db.md)
* [Käyttötapauksista](documentation/usecases.md)
* [Nykyisestä kehitysvaiheesta](documentation/status.md)

