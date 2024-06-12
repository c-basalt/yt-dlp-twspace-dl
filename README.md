This repository contains a plugin package for [yt-dlp](https://github.com/yt-dlp/yt-dlp#readme) to enhance Twitter Spaces download.

See [installing yt-dlp plugins](https://github.com/yt-dlp/yt-dlp#installing-plugins) for methods this plugin package can be installed.

## Feature and Usage

Apart from login and browser cookie support and Twitter Space extractor in main `yt-dlp` branch, this plugin package additionally add these functionalities inspired by Ryu1845's `twspace-dl`:
- Detect Twitter Space from up to 20 recent tweets in `USER_URL` like `https://x.com/xxx`
- Use built-in filesystem cache of yt-dlp to automatically save dynamic urls and `info_dict`
- Allows manually assign dynamic url or master url for ended spaces that do not have replays

Install this plugin and use yt-dlp as usual
```bash
# To download spaces within an account
yt-dlp --cookies-from firefox https://x.com/xxx --write-meta

# To cache space info and download later
yt-dlp --cookies curl-cookies.txt https://x.com/xxx --skip-download

# To use dynamic url to download an ended space without replay enabled
yt-dlp --cookies-from firefox https://x.com/i/spaces/xxxxx --TwitterSpaces:dynamic_url https://xxxx/xxx.../audio-space/dynamic_playlist.m3u8?type=live
```
