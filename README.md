### Usecase
imdb, kinopoisk recommendations are suck and searching other's playlists in letterboxd is lame (no society)
=> Export them in criticker.com to get advanced recommendations (though you still have to find movies for a long hours for the rest of your life)

1. Extract imdb ratings:
   go to imdb -> your ratings -> export -> open exports page -> wait and download csv
2. Extract kinopoisk ratings:
It already in there, go to kinopoisk_ratings_parser/ and follow README.md
[link on original github repo](https://github.com/evgenlipin/kinopoisk_ratings_parser.git)

3. log into criticker.com -> f12 -> console -> use this script to get cookies in devtools:
```javascript
const cookies = document.cookie.split(';').map(cookie => {
   const parts = cookie.split('=');
   return { name: parts[0].trim(), value: parts[1].trim() };
});
console.log(JSON.stringify(cookies));
```

Just pass in .env something like:
```bash
COOKIES_FOR_CRITICKER=[{"name":"_sharedid","value":"xd"},{"name":"_sharedid_cst","value":"noway"},{"name":"uid2","value":"stopit"}]
COOKIES_FOR_TASTE_IO=[]
```

4. poetry install
5. python -m src.main