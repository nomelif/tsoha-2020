# Käyttötapauksia

Erilaisia käyttäjäryhmiä ei ole, mutta jotkin kirjautuneen käyttäjän toiminnot saavat kohdistua vain omiin viesteihin tai tiliasetuksiin.

## Tilinhallinta ✓

* Käyttäjä tahtoo luoda värkkiin tunnuksen lukeakseen Värkki-viestejä. ✓

Käytännössä tämä menee oliorelationaalisesti, mutta SQL-mielessä kyseessä on yksinkertainen rivin lisäys:

```sql

INSERT INTO account (user_name, password_hash)
VALUES (<käyttäjätunnus>, <salasanan tiiviste>)
```

* Käyttäjä tahtoo kirjautua tunnukseen jonka loi. ✓

Käytännössä tämä menee oliorelationaalisesti, mutta SQL-mielessä kyseessä on yksinkertainen hakukysely:

```sql

SELECT id, user_name, password_hash FROM account WHERE user_name = <käyttäjätunnus>
```

Tarkistan sitten bcryptillä salasanan oikeellisuuden. Sinänsä olisi nättiä tehdä tämä laajentamalla WHERE-lausetta, mutta SQLAlchemyn kanssa tulee merkistökoodaussäätöä ja tämä osoittautui toimivaksi ratkaisuksi.

* Käyttäjä tahtoo kirjautua ulos, ettei joku muu käyttäisi Värkkiä hänen nimissään. ✓

Tässä ei tapahdu mitään SQL-kyselyä. Vain flaskin sisäistä tilaa päivitetään.

* Käyttäjä tahtoo vaihtaa tilinsä näkyvän nimen, kuten Twitterissä tavataan tehdä. ✓

Lopulta nimi ei näy kuin itselle, mutta sen voi vaihtaa. Tässä tulee kaksi kyselyä:

Ensiksi tarkistetaan, ettei kellään muulla ole samaa nimeä:

```sql

SELECT COUNT(*) FROM account WHERE user_name = <uusi tunnus> AND NOT id = <käyttäjän tunniste>
```

Jos tämän jälkeen päivitetään tunnus:

```sql

UPDATE account SET user_name = <uusi_tunnus> WHERE id = <käyttäjän tunniste>
```

Lopulta mikäli myös salasana on pyydetty vaihdettavaksi, se vaihdetaan:

```sql

UPDATE account SET password_hash = <uuden salasanan tiiviste> WHERE id = <tunniste>
```

* Käyttäjä tahtoo vaihtaa tilinsä salasanan, koska kirjoitti sen post-it lapulle ja perheen koira on painanut sen mieleensä. ✓

Sisäisesti tämä tapahtuu samaa polkua pitkin kuin käyttäjätunnuksen päivittäminen.

* Käyttäjä tahtoo poistaa tilinsä ja kaikki siihen liittyvät tiedot värkistä, koska hänen Värkkiinsä tekemänsä postaukset eivät enää heijasta hänen nykyisiä kantojaan ja saavat hänet vaikuttamaan epäammattimaiselta mahdollisen työnantajan silmissä. ✓

Tämä on mutkikas sarja kyselyitä. Aluksi poistetaan kaikki versiot käyttäjän kirjoittamista viesteistä. Ensiksi etsitään kaikki käyttäjän kirjoittamat viestit:

```sql

SELECT id FROM entry WHERE (SELECT account_id FROM post WHERE post.id = entry.post_id) = <tunniste>
```

Sitten tuhotaan jokainen viestiversio yksitelleen. Tässä kyselyiden sarja vastaa postauksen poistamista.

Sitten jokaisesta postauksesta poistetaan käyttäjätieto. Näin postaus säilyy sellaisena, että sen vastaukset voisi vielä näyttää.

```sql

UPDATE post SET account_id = NULL WHERE account_id = <tunniste>
```

Sitten poistetaan kaikki käyttäjään yhdistettävissä olevat äänet.

```sql

DELETE FROM vote WHERE vote.account_id = <tunniste>
```

Sitten poistetaan itse tunnus:

```sql

DELETE FROM account WHERE id = <tunniste>
```

* Käyttäjä tahtoo selvittää, mitä kaikkea Värkki hänestä tallentaa. Tähän häntä motivoi yksityisyyden halu. ✓

Tämä on pitkälti oliorelationaalisesti toteutettu, mutta vastaava SQL menisi osapuilleen näin:

Aluksi ongitaan käyttäjän tunnuksen tiedot:

```sql

SELECT id, user_name, password_hash FROM account WHERE id = <tunniste>
```

Sitten ongitaan kaikki postaukset, jotka käyttäjä on tehnyt:

```sql

SELECT id, parent_id FROM post WHERE account_id = <tunniste>
```

Sitten jokaiselle postaukselle ongitaan sen kaikki versiot:

```sql

SELECT id, text, timestamp FROM entry WHERE post_id = <postauksen tunniste>
```

Sitten äänistä ongitaan ne, jotka käyttäjä on antanut:

```sql

SELECT id, upvote, post_id FROM vote WHERE account_id = <tunniste>
```

## Viestittely ✓

* Käyttäjä tahtoo luoda värkkiin postauksen, sillä mieleen juolahti jotain, mitä ei kehtaa paikalle kokoontuneille perheen jäsenille sanoa ääneen. ✓

Käyttäjän tiedot luetaan tietokannasta:

```sql

SELECT id, user_name, password_hash FROM account WHERE id = <tunniste>
```

Mikäli tavoite on näyttää käyttäjälle käyttöliittymä, josta viesti kirjoitetaan niin tarkistetaan, että käyttäjälle löytyy äänestettävää.

Aluksi ongitaan jo valmiiksi allokoidut äänet

```sql

SELECT id, account_id, post_id, upvote FROM vote WHERE account_id=<tunniste> AND upvote IS NULL
```

Sitten katsotaan mitä ääniä pitäisi lisäksi generoida.

```sql

SELECT
  id
FROM
  entry
WHERE

  -- Varotaan, ettei generoida ääniä omiin postauksiin

  (
    SELECT
      post.account_id
    FROM
      post
    WHERE
      post.id = entry.post_id
  ) != <tunniste>

  -- Varotaan, ettei generoida ääniä postauksiin, joihin tälle käyttäjälle on jo generoitu ääni

  AND (
    SELECT 
      COUNT(*)
    FROM 
      vote
    where 
      vote.entry_id = entry.id
      AND vote.account_id = <tunniste>
  ) = 0

  -- Varotaan, ettei generoida ääniä postauksiin, joihin on jo generoitu tarvittavat äänet

  AND (
    SELECT 
      COUNT(*)
    FROM 
      vote
    where 
      vote.entry_id = entry.id
  ) < 3

  -- Varotaan, ettei generoida ääniä äänestyksiin, jotka on jo ratkaistu

  AND (
    SELECT
      COUNT(*)
    FROM
      vote
    WHERE
      vote.entry_id = entry.id
      AND vote.account_id IS NULL
  ) = 0

  LIMIT
    <monta ääntä tarvitaan>
```

Lisätään sitten uudet äänet tietokantaan:

```sql

INSERT INTO vote (id, entry_id, account_id, upvote)
VALUES (<äänen tunniste>, <viestin tunniste>, <käyttäjän tunniste>, NULL)
```

Ongitaan sitten ääniä vastaavat viestit:

```sql

SELECT id, post_id, text, timestamp FROM entry WHERE id = <tunniste>
```

Jos taas tavoite on käsitellä itse viestin lähetys tai muokkaus niin aloitetaan varmistamalla, ettei muokata jonkun toisen viestiä:

```sql

SELECT COUNT(*) FROM post WHERE id = <viestin tunniste> AND account_id = <käyttäjän tunniste>
```

Mikäli viesti on vastaus, tarkastellaan vielä, että viesti on vastaus olemassa olevaan viestiin, että tämä viesti ei ole jo lukkiutunut ja että se ei ole vastaus viesti. Järjestyksessä:

```sql

SELECT COUNT(*) FROM post WHERE id = <vastattavan viestin tunniste>
```

```sql

SELECT COUNT(*) FROM post WHERE parent_id =<vastattavan viestin tunniste> AND (id != <vastausviestin tunniste> OR <vastausviestin tunniste> IS NULL)
```

```sql

SELECT COUNT(*) FROM post WHERE id = <vastausviestin tunniste> AND parent_id IS NOT NULL
```

Sitten tarkistetaan mahdollinen källiyritys tehdä viestistä vastausviesti takautuvasti.

```sql

SELECT COUNT(*) FROM post WHERE id = <viestin tunniste> AND parent_id IS NULL
```

Jos jokin näistä epäonnistui, niin etsitään ääniä ja viestejä niin, että käyttäjä voi muokata viestiään ja äänestää uudelleen.

Jos tähän asti kaikki on ollut kunnossa, niin äänestys tapahtuu. Tarkistetaan, olivatko äänet kelpoja:

```sql

SELECT COUNT(*) FROM vote WHERE vote.id = <äänen tunniste> AND vote.account_id = <äänestäjän tunniste>
```

Asetetaan ylä-äänet:

```sql

UPDATE vote SET upvote = TRUE WHERE vote.id = <äänen tunniste>
```

Tulkitaan loput äänet alaääniksi:

```sql

UPDATE vote SET upvote = FALSE WHERE vote.account_id = <äänestäjän tunniste> AND vote.upvote IS NULL
```

Merkitään loppuneiden äänestysten ylä-äänet anonyymeiksi:

```sql

UPDATE vote SET account_id = NULL WHERE (SELECT COUNT(*) FROM vote as k WHERE k.upvote = TRUE AND k.entry_id = vote.entry_id GROUP BY k.entry_id) >= 2
```

Etsitään sitten hylätyt viestit.

```sql

SELECT id FROM entry WHERE (SELECT COUNT(*) FROM vote WHERE vote.entry_id = entry.id AND NOT vote.upvote) >= 2
```

Nämä poistetaan sitten samalla tapaa kuin käyttäjä poistaisi viestin.

Sitten itse viesti luodaan tietokantaan. Jos kyseessä ei ole muokkaus, niin uusi postaus lisätään (tämä on ORM-tekninen tosielämässä):

```sql

INSERT INTO post (account_id, reply_id) VALUES (<käyttäjän tunniste>, <mahdollinen vastauksen tunniste>)
```

Sitten viesti lisätään (jälleen ORM-tekninen):

```sql

INSERT INTO entry (post_id, text, timestamp) VALUES (<postauksen tunniste>, <viestin teksti>, <nykyinen aikaleima>
```

* Käyttäjä tahtoo muokata postausta, sillä hän huomasi siinä ikävän kirjoitusvirheen. ✓

Tämä kulkee saman reitin kautta kuin uuden postauksen luominen.

* Käyttäjä tahtoo poistaa postauksen, koska häpeää sitä kuollakseen. Internet ei kuitenkaan ikinä unohda. ✓

Tarkistetaan, että käyttäjällä on luvat poistaa viesti:

```sql

SELECT COUNT(*) FROM entry WHERE (SELECT post.account_id FROM post WHERE post.id = entry.post_id) =  <poistajan tunniste> AND id = <poistettavan viestin tunniste>
```

Poistetaan sitten kaikkien viestiin liittyneiden hakusanojen liitos viestiin:

```sql

DELETE FROM hashtag_link WHERE entry_id = <viestin tunniste>
```

Poistetaan sitten kaikki sellaiset hakusanat, jotka eivät enää liity mihinkään viestiin:

```sql

DELETE FROM hashtag WHERE (SELECT COUNT(*) FROM hashtag_link WHERE hashtag_id = hashtag.id) = 0
```

Poistetaan sitten itse viesti:

```sql

DELETE FROM entry WHERE id = <viestin tunniste>
```

Jos alla oleva tietokanta on PostgresSQL, niin se poistaa automaattisesti irrelevanteiksi muodostuneet äänet. Jos se on SQLite, niin joudutaan se tekemään käsin:

```sql

DELETE FROM vote WHERE entry_id = <viestin tunniste>
```

* Käyttäjä tahtoo vastata postaukseen, sillä eihän nyt tuollaista roskaa voi internettiin kirjoittaa. ✓

Tämä kulkee saman reitin kautta kuin uuden postauksen luominen.

* Käyttäjä tahtoo muokata vastausviestiään, sillä toisen kirjoitusvirheistä valittamisen uskottavuus heikkenee hänen itse tekemiensä näppäilymokien takia. ✓

Tämä kulkee saman reitin kautta kuin uuden postauksen luominen.

* Käyttäjä tahtoo poistaa vastausviestinsä, sillä sen sisältö on hänelle jälkikäteen vastenmielinen ja käynnissä olevan poliisikuulustelun kannalta merkittävää todistusaineistoa. ✓

Tämä kulkee saman reitin kautta kuin ylätason postauksen poistaminen.

## Moderaatio ✓

* Käyttäjä haluaa, ettei ihan mitä sattuu roskaa osu nokan eteen. Tämän seurauksena hän suostuu hyväksymään tai hylkäämään postauksia ennen kuin itse näpyttää. ✓

Tähän liittyvät kyselyt on kuvattu postauksen tekemiseen liittyvien kyselyjen yhteydessä.

## Haku ja selaaminen ✓

Molemmissa selaustilanteissa nähdään samat SQL-kyselyt. Käyttöliittymän nimissä haetaan käyttäjän tiedot (tämä kulkee ORMin kautta, joten se lataa kaikki käyttäjän tiedot):

```sql

SELECT id, user_name, password_hash FROM account WHERE id = <käyttäjän tunniste>
```

Sitten ongitaan relevantit ylätason postaukset:

```sql

WITH accepted_entry AS
    (
        SELECT text, timestamp, id, post_id FROM entry
        WHERE (SELECT COUNT(*) FROM vote WHERE
            upvote = true
            AND entry_id = entry.id) >= 2
    ), current_accepted_entry AS
    (
        SELECT text, timestamp, id, post_id FROM accepted_entry
        WHERE accepted_entry.timestamp =
            (SELECT MAX(subquery.timestamp) FROM accepted_entry as subquery
                WHERE subquery.post_id = accepted_entry.post_id)
    ), hashtagged_post AS
    (
        SELECT post_id as id, (SELECT parent_id FROM post WHERE post.id = post_id) as parent_id
        FROM current_accepted_entry
        WHERE NOT <oliko kyseessä hakukysely>
              OR (SELECT COUNT(*) FROM hashtag_link WHERE
            entry_id = current_accepted_entry.id
            AND hashtag_id IN (SELECT hashtag.id
                              FROM hashtag
                              WHERE hashtag.text IN <haetut hakusanat>)) > 0
    ), hashtagged_parent AS
    (
        SELECT DISTINCT COALESCE(parent_id, id, parent_id) as id
        FROM hashtagged_post
    )
SELECT current_accepted_entry.text, current_accepted_entry.id, (SELECT account_id FROM post WHERE post.id = hashtagged_parent.id), hashtagged_parent.id
FROM hashtagged_parent INNER JOIN current_accepted_entry
ON current_accepted_entry.post_id = hashtagged_parent.id
ORDER BY current_accepted_entry.timestamp DESC
```

* Käyttäjä haluaa kuluttaa Värkkipostauksia peiton alta koronakaranteenissa. Hän ei jaksa etsiä mitään erityistä, vaan mikä tahansa tietovirta auttaa henkiseen väsymykseen. ✓

* Käyttäjä tahtoo hakea kotitekoisen käsidesin reseptejä Värkistä avainsanojen perusteella siinä toivossa, että pöpöt nitistyisivät eteerisillä öljyillä ja suitsukkeella. ✓
