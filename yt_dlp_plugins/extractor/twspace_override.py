import re
from yt_dlp.extractor.twitter import TwitterSpacesIE
from yt_dlp.utils import traverse_obj, int_or_none, ExtractorError


class TwitterSpaceCacheIE(TwitterSpacesIE, plugin_name='twspace-cache'):
    def _get_cached_dynamic(self, space_id):
        return traverse_obj(self.cache.load('twspace-cache', space_id), 'formats', ..., 'url', get_all=False)

    def _get_metainfo(self, space_id):
        metainfo = {}
        try:
            if self.is_logged_in:
                space_data = self._call_graphql_api('HPEisOmj1epUNLCWTYhUWw/AudioSpaceById', space_id)['audioSpace']
                metadata = space_data['metadata']
                metainfo = {
                    'title': metadata.get('title'),
                    **traverse_obj(metadata, ('creator_results', 'result', 'legacy', {
                        'uploader': ('name', {str}),
                        'uploader_id': ('screen_name', {str}),
                    })),
                    **traverse_obj(metadata, {
                        'live_status': ('state', {lambda x: self.SPACE_STATUS[metadata[x].lower()]}),
                        'release_timestamp': ('scheduled_start', {lambda x: int_or_none(x, scale=1000)}),
                        'timestamp': ('created_at', {lambda x: int_or_none(x, scale=1000)}),
                    }),
                }
            elif self.cache.load('twspace-cache', space_id):
                return self.cache.load('twspace-cache', space_id)
        except Exception as e:
            self.report_error(f'Failed to get metadata: {e}', e.format_traceback())
        return metainfo

    def _from_cached_or_url(self, space_id):
        headers = {'Origin': 'https://x.com', 'Referer': 'https://x.com/'}
        master_url = self._configuration_arg('master_url')
        if not master_url:
            dynamic_url = self._configuration_arg('dynamic_url', self._get_cached_dynamic(space_id))
            if not dynamic_url:
                self.report_warning(f'No cached info_dict for space {space_id}, provide url using --TwitterSpaces:dynamic_url or --TwitterSpaces:master_url if you have one')
                return
            master_url = re.sub(r"(?<=/audio-space/).*", "master_playlist.m3u8", f['url'])
        formats = self._extract_m3u8_formats(master_url, space_id, headers=headers)
        return {
            **self._get_metainfo(space_id),
            'id': space_id,
            'formats': formats,
            'headers': headers,
        }

    def _real_extract(self, url):
        space_id = self._match_id(url)
        try:
            info = super()._real_extract(url)
            if info.get('formats') and self._should_cache:
                self.to_screen(f'caching info_dict for space {space_id}')
                self.cache.store('twspace-cache', space_id, {'info_dict': info})
            return info
        except ExtractorError:
            info = self._from_cached_or_url(space_id)
            if info:
                return info
            raise
