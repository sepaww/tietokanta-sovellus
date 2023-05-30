# Kauppakassi sovellus
- Sovelluksen tavoitteena on helpottaa käyttäjän ruokakauppa käyntejä.
- Sovellukseen kirjaudutaan omilla käyttäjätunnuksilla. Kaikki käyttäjät kuuluvat käyttäjä luokaan
  - Käyttäjä luokan oikeuksiin kuuluvat kauppojen tarkastelu, arvostelujen sekä kommenttien jättö kaupoista sekä kauppakassin sovelluksen halvimman kaupan haku ominaisuutta (lisää myöhemmin)
  - Käyttäjä luokan oikeuksiin kuuluvat kauppojen tarkastelu, arvostelujen sekä kommenttien jättö kaupoista sekä kauppakassi sovelluksen halvimman kaupan haku ominaisuuden käyttö (lisää myöhemmin)
- Sovellukseen voi myös kirjautua admin tunnuksilla, jolla on kaikki käyttäjien oikeudet sekä kommenttien poisto oikeus, tavaroiden hintojen muutto kaupoissa, kauppojen lisäys sekä mahdollisesti käyttäjän poistaminen palvelusta pysyvästi.
- Halvimman kaupan haku toteutetaan kauppalistan rakennuksena saatavilla olevista tuotteista, ja kun kauppalista on valmis, käyttäjä voi hakea ilmoittamiensa tuotteiden halvinta kokonaishintaa, eli missä kannattaa käydä ostoksilla, jotta saa tuotteet mahdollisimman halvalla. (Tässä saattaa tulla muutama  hankaluus esim. jos jokin tuote ei ole saatavissa halvimmassa kaupassa, niin kuinka toimitaan tällöin) 
- Tietokannan rakenne löytyy schema.sql tiedostosta

## Tilannekatsauas
- Tällä hetkellä sovelluksesta löytyy lähes kaikki mainitut ominaisuudet. Adminilla ei vielä ole poisto ominaisuutta, jolla poistaa kommentti tai tuote tietokannasta.
- Halvimman tuotteen haku palauttaa onnistuneesti halutun kaupan sekä tuotteiden hinnat yhdessä ja erikseen. Tilanteessa, jossa yksikään kauppa ei tarjoa kauppalistaa kokonaisuudessaan, palautetaan tieto haun epäonnistumisesta
- visuaalinen puoli on suht valmis. Jotain hiomista/polishaamista saattaa tapahtua
- Sovelluksessa on mahdollisuus tallentaa kuvia kaupoille. Tällä hetkellä ominaisuus ei toimmi jostakin syystä. Kaupat, joille ei ole annettu kuvaa käyttävät sovellukseen sijoitettua placeholderia.

## Toiminnot
-Koostuu sivuista:
  - login/register:
    - kirjautuminen sekä rekisteröityminen. 
  - home
    - luettelo saatavilla olevista kaupoista sekä linki niiden sivuille
    - hintalaskurin aktivointi boksi
    - nappi admin sivulle jos käyttä on ylläpitäjä
  - shop_page
    - mahdollisuus arvioida kauppa
    - mahdollisuus jättää komentti kaupasta ja tykätä muiden/omasta kommentista.
  - adminpage
    - ylläpitäjälle tehty työkalu sivu, josta voi lisätä kauppoja sovellukseen sekä tuotteita. Sisältää myös massadd napin jolla voi helposti tehdä products taulukosta täyden
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
  - luo kansioon oma venv sekä .env kansio
  - sijoita .env kansioon postgresql tietokannan nimi
  - asenna virtuaaliympäristöön riippuvuudet:
  ```bash
  pip install -r requirements.txt
  ```
  - alusta tietokanta:
  ```bash
  psql < schema.sql
   ```
  - käynnistä app.py ja rekisteröi käyttäjä. Ensimmäisestä käyttäjästä tulee ylläpitäjä
