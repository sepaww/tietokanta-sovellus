# tietokanta-sovellus

## Kauppakassi sovellus
- Sovelluksen tavoitteena on helpottaa käyttäjän ruokakauppa käyntejä.
- Sovellukseen kirjaudutaan omilla käyttäjätunnuksilla. Kaikki käyttäjät kuuluvat käyttäjä luokaan
  - Käyttäjä luokan oikeuksiin kuuluvat kauppojen tarkastelu, arvostelujen sekä kommenttien jättö kaupoista sekä kauppakassin sovelluksen halvimman kaupan haku ominaisuutta (lisää myöhemmin)
- Sovellukseen voi myös kirjautua admin tunnuksilla, jolla on kaikki käyttäjien oikeudet sekä kommenttien poisto oikeus, tavaroiden hintojen muutto kaupoissa sekä mahdollisesti käyttäjän poistaminen palvelusta pysyvästi.
- Halvimman kaupan haku toteutetaan kauppalistan rakennuksena saatavilla olevista tuotteista, ja kun kauppalista on valmis, käyttäjä voi hakea ilmoittamiensa tuotteiden halvinta kokonaishintaa, eli missä kannattaa käydä ostoksilla, jotta saa tuotteet mahdollisimman halvalla. (Tässä saattaa tulla muutama  hankaluus esim. jos jokin tuote ei ole saatavissa halvimmassa kaupassa, niin kuinka toimitaan tällöin) 
- Tietokannallisesti:
  - Käyttäjät: nimi - hashattau salasana - on admin - käyttäjä_id
  - Tuotteet: tuote_id - nimi - hinta - kauppa_id (saattaa olla järkevämpää tehdä erillinen nimi taulu tuote ideille)
  - Kaupat: nimi - kauppa_id - (sijainti?)
  - Kommentit: käyttäjä_id - kauppa_id - kommentti
  - Arviot: käyttäjä_id - kauppa_id - arvio
