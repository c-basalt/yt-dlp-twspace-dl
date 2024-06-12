import time
from yt_dlp.extractor.twitter import TwitterBaseIE, TwitterSpacesIE
from yt_dlp.utils import traverse_obj, int_or_none, ExtractorError


class TwitterUserSpaceIE(TwitterBaseIE):
    IE_NAME = 'twitter:userspaces'
    _VALID_URL = TwitterBaseIE._BASE_REGEX + r'(?P<id>[^/]+)/?(?:[\?#]|$)'

    def get_user_id(self, screen_name):
        query = {
            'variables': '{"screen_name":"%s","withSafetyModeUserFields":true}' % screen_name,
            'features': '{"hidden_profile_likes_enabled":true,"hidden_profile_subscriptions_enabled":true,"rweb_tipjar_consumption_enabled":true,'
                '"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"subscriptions_verification_info_is_identity_verified_enabled":true,'
                '"subscriptions_verification_info_verified_since_enabled":true,"highlights_tweets_tab_ui_enabled":true,"responsive_web_twitter_article_notes_tab_enabled":true,'
                '"subscriptions_feature_can_gift_premium":false,"creator_subscriptions_tweet_preview_api_enabled":true,'
                '"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true}',
            'fieldToggles': '{"withAuxiliaryUserLabels":false}',            
        }
        data = self._call_api('SjtODv6y4fsa4-zv5sLw5A/UserByScreenName', screen_name, query=query, graphql=True)['data']
        user_id = traverse_obj(data, ('user', 'result', 'rest_id', {int_or_none}))
        if user_id is None:
            raise ExtractorError('Failed to get user id')
        return str(user_id)

    def get_tweets(self, user_id, cursor=None):
        query = {
            'variables': '{"userId":"%s","count":20,"includePromotedContent":true,"withQuickPromoteEligibilityTweetFields":true,"withVoice":true,"withV2Timeline":true}' % user_id,
            'features': '{"rweb_tipjar_consumption_enabled":true,"responsive_web_graphql_exclude_directive_enabled":true,'
                '"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,'
                '"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"communities_web_enable_tweet_community_results_fetch":true,'
                '"c9s_tweet_anatomy_moderator_badge_enabled":true,"articles_preview_enabled":true,"tweetypie_unmention_optimization_enabled":true,'
                '"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,'
                '"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":true,"tweet_awards_web_tipping_enabled":false,'
                '"creator_subscriptions_quote_tweet_preview_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,'
                '"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"rweb_video_timestamps_enabled":true,"longform_notetweets_rich_text_read_enabled":true,'
                '"longform_notetweets_inline_media_enabled":true,"responsive_web_enhance_cards_enabled":false}',
            'fieldToggles': '{"withArticlePlainText":false}',
        }
        if cursor:
            query['variables'] = ('{"userId":"%s","count":20,"cursor":"%s","includePromotedContent":true,'
                '"withQuickPromoteEligibilityTweetFields":true,"withVoice":true,"withV2Timeline":true}' % (user_id, cursor))
        data = self._call_api('V7H0Ap3_Hh2FyS75OCDO3Q/UserTweets', user_id, query=query, graphql=True)['data']
        tweets = traverse_obj(data, ('user', 'result', 'timeline_v2', 'timeline', 'instructions', ..., ('entry', ('entries', ...)), 'content'))
        return tweets

    def parse_tweet_spaces(self, tweets):
        def parse_card_id(card):
            if card['name'].split(':')[-1] == 'audiospace':
                for value in traverse_obj(card['binding_values'], (lambda _, v: v['key'] == 'id', 'value')):
                    return value[value['type'].lower() + '_value']

        url_ids = traverse_obj(tweets, (..., 'itemContent', 'tweet_results', 'result', 'legacy', 'entities', 'urls', ..., 'expanded_url', {TwitterSpacesIE._match_id}))
        card_ids = traverse_obj(tweets, (..., 'itemContent', 'tweet_results', 'result', 'card', 'legacy', {parse_card_id}))
        return {*url_ids, *card_ids}

    def _space_id_to_entry(self, space_id):
        url = f'https://x.com/i/spaces/{space_id}'
        cached = self.cache.load('twspace-cache', space_id)
        if cached:
            return self.url_result(url)
        else:
            return self._downloader.extract_info(url, download=False)

    def _real_extract(self, url):
        display_id = self._match_id(url)
        if not self.is_logged_in:
            self.raise_login_required('Twitter Spaces require authentication')

        user_id = self.get_user_id(display_id)
        if not user_id:
            raise ExtractorError('Failed to get user_id')

        tweets = self.get_tweets(user_id)
        space_ids = self.parse_tweet_spaces(tweets)
        if not space_ids:
            raise ExtractorError('No space link found')
        entries = [self._space_id_to_entry(space_id) for space_id in space_ids]
        return self.playlist_result(entries, id=user_id, title=display_id)
