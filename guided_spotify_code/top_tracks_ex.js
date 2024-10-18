// Authorization token that must have been created previously. See : https://developer.spotify.com/documentation/web-api/concepts/authorization
const token = 'BQAIzuMRyvZg9W2kwH0ENlvi0kmrN78H8nZesg1c10zPYrShloFCB0A5bCzdMz3B2lMVkmeYTveWLhHSlm9uf1aVLzJXDHmUt8YJRPgPDBfwLVcVRyXShX4ds-SE1dsR2ISgFCUBneXBF6lkw9QKC-Z7NwbrRMqWAkfg_uHgYGOqdzGvtxSNek6tycIMVrs6OWQmyDB1XPtn6610OSa7QzmlW8zw-9nZSxrDNkij7E0W_wvXPTIKzfUI8cJ_mGKKHEUpdH_2fb1tWw';
// replace this token above with your own
async function fetchWebApi(endpoint, method, body) {
  const res = await fetch(`https://api.spotify.com/${endpoint}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    method,
    body:JSON.stringify(body)
  });
  return await res.json();
}

async function getTopTracks(){
  // Endpoint reference : https://developer.spotify.com/documentation/web-api/reference/get-users-top-artists-and-tracks
  return (await fetchWebApi(
    'v1/me/top/tracks?time_range=long_term&limit=5', 'GET'
  )).items;
}

const topTracks = await getTopTracks();
console.log(
  topTracks?.map(
    ({name, artists}) =>
      `${name} by ${artists.map(artist => artist.name).join(', ')}`
  )
);


// My top tracks as of 10/9/24 by this code
// 1. Intermission by Strawberry Guy
// 2. Cold Bones by The Symposium
// 3. Valley Ghoul by Provoker
// 4. Twin Flames by Midrift
// 5. Late Nigh Waltz by Silk Skin Lovers