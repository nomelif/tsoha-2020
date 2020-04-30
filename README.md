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
2. Kirjoittaa viesti (yläoikealla oleva kynäkuvake, tukee [markdownia](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet))
3. Kirjautua ulos (yläoikealla oleva kuvake)
3. Luoda käyttäjä b
4. Kirjoittaa b:llä viesti ja merkitä a:n kommentti rakentavaksi
5. Kirjautua ulos
6. Luoda käyttäjä c
7. Kirjoittaa c:llä viesti ja merkitä a:n kommentti rakentavaksi

Nyt a:n viestin pitäisi näkyä. Viestiä voi muokata vain a:ksi kirjautuneena. __Muokkauksien esiin tuleminen vaatii vastaavat kaksi rakentavuusääntä. Viestin poisto on välitön. Jos viestiä on muokattu, poisto palauttaa viestin sen aikaisempaan tilaan.__

Tiliasetuksiin pääsee oikean ylänurkan rataskuvakkeesta. Sitä kautta voi myös poistaa tilin tai ladata siihen liittyvät tiedot.

Vastausviestin voi luoda vastauskuvakkeella, joka näkyy postauksen vasemmassa alanurkassa. Vastauksia hyväksytään viisi (niitä ei välttämättä näy käyttöliittymässä viittä, sillä osa voi olla moderoimatta) ja niitä voi muokata ja poistaa kuten ylätason postauksia. Vastausviesteihin ei voi vastata. __Vastausviesteistä tulee näkyviä vasta, kun ne ovat saaneet kaksi moderaatioylä-ääntä.__

Viesteihin voi lisätä risuaidalla merkittyjä #hakusanoja. Jotakin hakusanaa sisältäviä ylätason viestejä voi selata hakutoiminnolla. Hakusanat voi hakukentässä erottaa välein.

## Asennuksesta

Omalle palvelimelle Värkin saa asennettua kloonaamalla tämän repositorion ja asentamalla `requirements.txt` -tiedostossa mainitut paketit. Helpoiten se käy komennolla `pip install -r requirements.txt`. venv-virtuaaliympäristöllä riippuvuudet asentuvat nätisti paikallisesti. Itse palvelimen saa käynnistymään komennolla `gunicorn --preload --workers 1 application:app` repositorion ylätasolta. Värkki luo itse käyttämänsä sqlite3 -tietokannan. Tässä tilanteessa värkki kuuntelee porttia 8000.

Jotta Värkin saa toimimaan PostgresSQL-tietokannan kanssa yhteen, tulee antaa `HEROKU`-ympäristömuuttujalle jokin arvo. Lisäksi ympäristömuuttujassa `DATABASE_URL` tulee olla kelpo osoite. Niiden muotoa pui esimerkiksi [tämä StackOverflow-postaus](https://stackoverflow.com/questions/43477244/how-to-find-postgresql-uri-for-sqlalchemy-config). Yleisesti värkki yrittäisi yhdistyä mihin tahansa `DATABASE_URL`-ympäristömuuttujassa määriteltyyn tietokantajärjestelmään. Käytännössä Värkki kuitenkin olettaa kyseessä olevan PostgresSQL.

## Dokumentaation rakenteesta

Dokumentaatiosta löytyy tiedot Värkin:

* [Tietokantarakenteesta](documentation/db.md)
* [Käyttötapauksista](documentation/usecases.md)
* [Nykyisestä kehitysvaiheesta](documentation/status.md)
* [Stressitestauksesta](documentation/stresstest.md)

## Rajoitteet

Tällä hetkellä värkin pitäisi toteuttaa kaikki määritellyt käyttötapaukset tavalla tai toisella. Käyttöliittymää voi toki viilata.

Loppujen lopuksi Värkki oli tutkimus sarjakuvassa pilanpäiten kuvatusta moderaatiomuodosta. Oma mielipiteeni on, ettei se lopulta ole toimiva. Pienellä vaivalla keksii montakin tapaa, jolla jokin bottimaakari voisi paikkoja rikkoa. Esimerkiksi joukko botteja voi jumittaa moderaatioketjun pienellä vaivalla. IP-osoite- ja käyttäjäkohtaiset tapahtumataajuusrajoitteet tai fyysinen rajoite vuorokausittaisiin uusiin käyttäjiin voisivat tehdä tilanteesta hallittavamman, mutta en usko Värkin olevan lopulta toimiva ajatus.

