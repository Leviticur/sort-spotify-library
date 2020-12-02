import os
import spotipy


def authenticate():

    scope = "user-library-read, user-library-modify"

    sp_oauth = spotipy.SpotifyOAuth(
        'aa6ca077fe264b92aa2445d9ed4ff674',
        os.environ.get('SPOTIFY_SECRET'), 
        'https://ethangomez.com',
        scope=scope,
        )  

    token_info = sp_oauth.get_cached_token()

    if token_info:
        if sp_oauth.is_token_expired(token_info):
            token_info = refresh_access_token(token_info['refresh_token'])
        access_token = token_info['access_token']  
        return access_token
    else:

        auth_url = sp_oauth.get_authorize_url()  
        print(auth_url)
        url = input('Url: ')  

        code = sp_oauth.parse_response_code(url)  
        token_info = sp_oauth.get_access_token(code)  

        access_token = token_info['access_token']  
        return access_token
