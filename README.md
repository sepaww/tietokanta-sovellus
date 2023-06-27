## Testausohje
- kun käyttöönotto on onnistunut, ensimmäisestä rekisteröidystä käyttäjästä tulee sivun admin. adminilla pääsee sivulle /adminpage, missä kannattaa lisätä vaikka 3 uutta kauppaa sovellukseen. Kauppojen lisäämisen jälkeen kannattaa painaa massadd näppäintä muutaman kerran. Nyt sovelluksen tulisi pyöriä järkevästi ja kauppojen tulisi olla täynnä tuotteita eri hinnoilla. Kauppoja voi luoda lisää mieleisen määrän sekä lisätä niihin haluttuja tuotteita adminpagella joko manuaalisesti add product formilla tai välittömästi massadd näppäimellä.

# Kauppakassi sovellus
- Sovelluksen tavoitteena on helpottaa käyttäjän ruokakauppa käyntejä.
- Sovellukseen kirjaudutaan omilla käyttäjätunnuksilla. Kaikki käyttäjät kuuluvat käyttäjä luokkaan
  - Käyttäjä luokan oikeuksiin kuuluvat kauppojen tarkastelu, arvostelujen sekä kommenttien jättö kaupoista sekä kauppakassin sovelluksen halvimman kaupan haku ominaisuuden käyttö
- Sovellukseen voi myös kirjautua admin tunnuksilla, jolla on kaikki käyttäjien oikeudet sekä kommenttien poisto oikeus, tavaroiden hintojen muutto kaupoissa, kauppojen lisäys sekä tavaroiden lisäys.
- Halvimman kaupan haku toteutetaan kauppalistan muodossa saatavilla olevista tuotteista, ja kun kauppalista on valmis, käyttäjä voi hakea ilmoittamiensa tuotteiden halvinta kokonaishintaa, eli missä kannattaa käydä ostoksilla, jotta saa tuotteet mahdollisimman halvalla.
- Tietokannan rakenne löytyy schema.sql tiedostosta


## Toiminnot
-Koostuu sivuista:
  - login/register:
    - kirjautuminen sekä rekisteröityminen. 
  - home
    - luettelo saatavilla olevista kaupoista sekä linkit niiden sivuille
    - hintalaskurin aktivointi boksi
    - nappi admin sivulle jos käyttä on ylläpitäjä
  - shop_page
    - mahdollisuus tarkastella kaupan tuotteita
    - mahdollisuus arvioida kauppa
    - mahdollisuus jättää komentti kaupasta ja tykätä muiden/omasta kommentista.
  - adminpage
    - ylläpitäjälle tehty työkalu sivu, josta voi lisätä kauppoja sovellukseen sekä tuotteita. Sisältää myös massadd napin jolla voi helposti täyttää sovelluksen sisäisen products taulukon
  - hintalaskurin form
    - "kauppalista" formi, jolla voi hakea halvinta kauppaa
  - hintalaskuri result
    - näyttää hintalaskurin tulokset sekä linkkaa kaupan sivuille ja takaisin homeen.
  
  ## Käyttöönotto
  -luo kansio projektille
  - siirry kansioon
  ```bash
git clone https://github.com/sepaww/tietokanta-sovellus.git
```
  - luo kansioon oma venv sekä .env tiedosto
  ```bash
  python3 -m venv venv
  ```
  - Aktivoi venv:
  ```bash
  (linux): source venv/bin/activate
  (windows): venv\Scripts\activate
  ```
  - sijoita .env tiedostoon postgresql tietokannan nimi muodossa DATABASE_URL="(nimi)" ja SECRET_KEY='(oma avain)'
  - asenna virtuaaliympäristöön riippuvuudet:
  ```bash
  pip install -r requirements.txt
  ```
  - alusta tietokanta:
  ```bash
  psql < schema.sql
   ```
  - käynnistä app.py ja rekisteröi käyttäjä. Ensimmäisestä käyttäjästä tulee ylläpitäjä
  
