# Käyttötapauksia

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

TODO: entä toisin päin? Entä vastausviestin siirtäminen vastaukseksi toiseen viestiin

* Käyttäjä tahtoo muokata postausta, sillä hän huomasi siinä ikävän kirjoitusvirheen. ✓
* Käyttäjä tahtoo poistaa postauksen, koska häpeää sitä kuollakseen. Internet ei kuitenkaan ikinä unohda. ✓
* Käyttäjä tahtoo vastata postaukseen, sillä eihän nyt tuollaista roskaa voi internettiin kirjoittaa. ✓
* Käyttäjä tahtoo muokata vastausviestiään, sillä toisen kirjoitusvirheistä valittamisen uskottavuus heikkenee hänen itse tekemiensä näppäilymokien takia. ✓
* Käyttäjä tahtoo poistaa vastausviestinsä, sillä sen sisältö on hänelle jälkikäteen vastenmielinen ja käynnissä olevan poliisikuulustelun kannalta merkittävää todistusaineistoa. ✓

## Moderaatio ✓

* Käyttäjä haluaa, ettei ihan mitä sattuu roskaa osu nokan eteen. Tämän seurauksena hän suostuu hyväksymään tai hylkäämään postauksia ennen kuin itse näpyttää. ✓

## Haku ja selaaminen ✓

* Käyttäjä haluaa kuluttaa Värkkipostauksia peiton alta koronakaranteenissa. Hän ei jaksa etsiä mitään erityistä, vaan mikä tahansa tietovirta auttaa henkiseen väsymykseen. ✓
* Käyttäjä tahtoo hakea kotitekoisen käsidesin reseptejä Värkistä avainsanojen perusteella siinä toivossa, että pöpöt nitistyisivät eteerisillä öljyillä ja suitsukkeella. ✓
