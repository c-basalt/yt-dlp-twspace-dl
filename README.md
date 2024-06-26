This repository contains a proof-of-concept plugin package for [yt-dlp](https://github.com/yt-dlp/yt-dlp#readme) to enhance Twitter Spaces download. It should work in principle but I have not tested every part of it, and there could be gliches that need fixing before putting into use.

See [installing yt-dlp plugins](https://github.com/yt-dlp/yt-dlp#installing-plugins) for methods this plugin package can be installed.

A bundled version for Windows is provided in Release page to demostrate how to use this plugin along with yt-dlp binary

## Feature and Usage

Apart from existing login and browser cookie support and `TwitterSpacesIE` extractor in main `yt-dlp` branch, this plugin package additionally add these functionalities inspired by [Ryu1845](https://github.com/Ryu1845)'s `twspace-dl`:
- Detect Twitter Space from up to 20 recent tweets in `USER_URL` like `https://x.com/xxx`
- Use built-in filesystem cache of yt-dlp to automatically save dynamic urls and `info_dict` for later retrival of replays.
- Allows manually assign dynamic url or master url for ended spaces that do not have replays

Install this plugin and use yt-dlp as usual. Refer to [Readme of `yt-dlp`](https://github.com/yt-dlp/yt-dlp#readme) for [filename formatting](https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#output-template), use of [archive file](https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#video-selection) (to prevent repeated download), proxies, cookies, etc.
```bash
# To download spaces within an account
yt-dlp --cookies-from firefox https://x.com/xxx --write-meta --download-archive downloaded-ids.txt

# To cache space info and download later
yt-dlp --cookies curl-cookies.txt https://x.com/xxx --skip-download --write-meta

# To use dynamic url to download an ended space without replay enabled
yt-dlp --username aaabbb@gmail.com --password ABcd5678 https://x.com/i/spaces/xxxxx --TwitterSpaces:dynamic_url "https://xxxx/xxx.../audio-space/dynamic_playlist.m3u8?type=live"
```
