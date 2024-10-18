// Authorization token that must have been created previously. See : https://developer.spotify.com/documentation/web-api/concepts/authorization
const token = 'BQDsyzoBw38fIXffwn9UOAnntFuWpHlBdvuTpDH3tAnZXsHcD-aS3vHMM1cyb_x3oet_fWqqfYjF6-G0SJwEuUe_KfbbyQGOFzdhgzE-4swCQpEvSGWnMNJT7ZnXwD9H1xQpQm1tl9UTUVmrD46vVnHU9wFQY4-SRIEsmMXH_HWiOGtsuF1amTyI5U3_D3wZV_mgMIj-l-e1eYbJs-Xp8utH21wlnDQ_hK0Tc71odpa9CqxnZX9be8HAIAW5HqTVpWc59ZFvl_A3mw';
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

const tracksUri = [
  'spotify:track:4hm33jVolpa22nzhlY72jD','spotify:track:4CXJANCcGeedkvKllXZmWM','spotify:track:6mgxUcXsFOrXUZvfOQ1OmS','spotify:track:0c59V7elpRHa6NmVH9GtW7','spotify:track:4Gpvffa23tFfBjbusONE01','spotify:track:78GgHOpC6CWvxlhCaVPFV5','spotify:track:4ihiiVAhf3Ta9h7IytC74L','spotify:track:2INGAkBBaIE4WskdmHt7Wg','spotify:track:3F3KtB4KjOyHYkIB7l2LLV','spotify:track:6AwokXE2cYr2YbUcUHg9Bh'
];

async function createPlaylist(tracksUri){
  const { id: user_id } = await fetchWebApi('v1/me', 'GET')

  const playlist = await fetchWebApi(
    `v1/users/${user_id}/playlists`, 'POST', {
      "name": "My recommendation playlist",
      "description": "Playlist created by the tutorial on developer.spotify.com",
      "public": false
  })

  await fetchWebApi(
    `v1/playlists/${playlist.id}/tracks?uris=${tracksUri.join(',')}`,
    'POST'
  );

  return playlist;
}

const createdPlaylist = await createPlaylist(tracksUri);
console.log(createdPlaylist.name, createdPlaylist.id);
